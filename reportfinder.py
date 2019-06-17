#!/usr/bin/env python3

# Takes the list of agencies from the Australian Government Organisations
# Register, and uses Bing to find the best candidate page for
# Harradine reports on that agency's domain.

# We ignore agencies in the AGOR that don't list a website.

import os
import sys
import csv
from time import sleep
from urllib.parse import urlparse

from azure.cognitiveservices.search.websearch import WebSearchAPI
from msrest.authentication import CognitiveServicesCredentials

included_agency_types = ['A', 'B', 'E']

def read_agor(filename):
    """
    Read the AGOR CSV, filter out agencies without a website, return relevant
    information we need (agency name, portfolio, domain name)
    """
    agencies = []
    with open(filename, encoding='ISO-8859-1') as agorfile:
        agorreader = csv.DictReader(agorfile)
        for agency in agorreader:
            if not agency['Website Address']:
                continue

            if agency['Type of Body'][0] not in included_agency_types:
                continue

            # Fixes for silly issues in the data
            if 'http' not in agency['Website Address']:
                agency['Website Address'] = 'http://' + agency['Website Address']
            agency['Website Address'] = agency['Website Address'].replace('http:www', 'http://www')

            parsed_url = urlparse(agency['Website Address'])
            agency_extract = {}
            agency_extract['Title'] = agency['Title']
            agency_extract['Portfolio'] = agency['Portfolio']

            # Extract domain name, and discard everything past the 3rd level
            # (agency.gov.au)
            domain = '.'.join(parsed_url.netloc.split('.')[-3:])
            if not domain:
                print("!!! Empty domain: ", agency['Website Address'])
            agency_extract['Domain'] = domain
            agencies.append(agency_extract)
    return agencies

def find_harradine_reports(agencies, client):
    domains = {agency['Domain'] for agency in agencies}
    print("# agencies:", len(agencies))
    print("# unique domains:", len(domains))
    domain_out = {}
    for domain in domains:
        # TODO: Could we improve accuracy by using multiple search queries and finding the intersection, etc?
        search_terms = "site:{} list of files senate order".format(domain)
        search_result = client.web.search(query=search_terms)
        if hasattr(search_result.web_pages, 'value'):
            page = search_result.web_pages.value[0]
            domain_out[domain] = (page.name, page.url)
            print("Domain:", domain, "Report:", page.url, "Page Title:", page.name)
        else:
            domain_out[domain] = ('UNKNOWN', 'UNKNOWN')
            print("Domain:", domain, "NO RESULTS")
        
        if len(domain_out) % 10 == 0 or len(domain_out) == len(domains):
            print("Domains searched:", len(domain_out))
        #print(domain, domain_out[domain])

    agency_out = []
    for agency in agencies:
        agency_out.append({**agency, 'ReportURL': domain_out[agency['Domain']][1], 'ReportPageTitle': domain_out[agency['Domain']][0]})
    return agency_out

def main():
    if len(sys.argv) != 3:
        print("Usage: {} <AGOR input CSV> <Harradine output CSV>".format(sys.argv[0]))
        return

    # Azure creds
    try:
        subscription_key = os.environ.get('AZURE_KEY')
    except:
        print("Must supply AZURE_KEY environment variable")
        return
    client = WebSearchAPI(CognitiveServicesCredentials(subscription_key), base_url="https://api.cognitive.microsoft.com/bing/v7.0")

    agencies = read_agor(sys.argv[1])
    output = find_harradine_reports(agencies, client)
    # TODO: For agencies/websites without their own Harradine list, we probably want to use the portfolio department's list rather than some random result

    with open(sys.argv[2], 'w') as f:
        writer = csv.DictWriter(f, ['Title', 'Portfolio', 'Domain', 'ReportURL', 'ReportPageTitle'])
        writer.writeheader()
        writer.writerows(output)

if __name__ == '__main__':
    main()
