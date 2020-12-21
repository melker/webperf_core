# -*- coding: utf-8 -*-
from engines.utils import use_website
import json


def add_site(input_filename, url):
    sites = read_sites(input_filename, 0, -1)
    # print(sites)
    id = len(sites)
    sites.append([id, url])
    write_sites(input_filename, sites)

    print(_('TEXT_WEBSITE_URL_ADDED').format(url))

    return sites


def delete_site(input_filename, url):
    sites = read_sites(input_filename, 0, -1)
    tmpSites = list()
    for site in sites:
        site_id = site[0]
        site_url = site[1]
        if (url != site_url):
            tmpSites.append([site_id, site_url])

    write_sites(input_filename, tmpSites)

    print(_('TEXT_WEBSITE_URL_DELETED').format(site_url))

    return tmpSites


def read_sites(input_filename, input_skip, input_take):

    print('A')

    sites = list()
    with open(input_filename) as json_input_file:
        data = json.load(json_input_file)
        current_index = 0
        for site in data["sites"]:
            if use_website(current_index, input_skip, input_take):
                sites.append([site["id"], site["url"]])
            current_index += 1
    return sites


def write_tests(output_filename, siteTests):
    with open(output_filename, 'w') as outfile:
        # json require us to have an object as root element
        testsContainerObject = {
            "tests": siteTests
        }
        json.dump(testsContainerObject, outfile)


def write_sites(output_filename, sites):
    with open(output_filename, 'w') as outfile:
        # json require us to have an object as root element
        jsonSites = list()
        current_siteid = 0
        for site in sites:
            jsonSites.append({
                'id': site[0],
                'url': site[1]
            })
            current_siteid += 1

        sitesContainerObject = {
            "sites": jsonSites
        }
        json.dump(sitesContainerObject, outfile)
