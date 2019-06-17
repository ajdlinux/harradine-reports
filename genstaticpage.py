#!/usr/bin/env python3

# Take the output of the report finder script and generate a static web page

# This is provisional until we do something fancier

import sys
import csv

HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
<title>Harradine Reports</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
<style>
BODY { margin: 50px; }
</style>
</head>
<body>
<h1>Harradine Reports</h1>
<p>This page is a work in progress - more exciting stuff to come. Currently it contains links to each Commonwealth agency's Harradine report/index of files. Well, not quite - this is just a guess using a search engine so quite a few of these links are wrong.</p>
"""

ITEM = """
<h3><a href="{}">{}</a></h3>
"""

FOOTER = """
</body>
</html>
"""


def main():
    if len(sys.argv) != 3:
        print("Usage: {} <input CSV> <output HTML>".format(sys.argv[0]))
        return

    output = HEADER

    agencies = []
    with open(sys.argv[1]) as csvfile:
        csvreader = csv.DictReader(csvfile)
        for agency in csvreader:
            if agency['ReportURL'] == 'UNKNOWN':
                continue
            agencies.append((agency['Title'], agency['ReportURL']))

    agencies.sort()
    for agency in agencies:
        output += ITEM.format(agency[1], agency[0])

    output += FOOTER

    with open(sys.argv[2], 'w') as f:
        f.write(output)

if __name__ == '__main__':
    main()
