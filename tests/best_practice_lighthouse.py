# -*- coding: utf-8 -*-
from models import Rating
import sys
import socket
import ssl
import json
import requests
import urllib  # https://docs.python.org/3/library/urllib.parse.html
import uuid
import re
from bs4 import BeautifulSoup
import config
from tests.utils import *
import gettext
_ = gettext.gettext

# DEFAULTS
googlePageSpeedApiKey = config.googlePageSpeedApiKey


def run_test(langCode, url, strategy='mobile', category='best-practices'):
    language = gettext.translation(
        'best_practice_lighthouse', localedir='locales', languages=[langCode])
    language.install()
    _ = language.gettext

    print(_('TEXT_RUNNING_TEST'))

    check_url = url.strip()

    pagespeed_api_request = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?locale={4}&category={0}&url={1}&strategy={2}&key={3}'.format(
        category, check_url, strategy, googlePageSpeedApiKey, langCode)

    get_content = ''

    try:
        get_content = httpRequestGetContent(pagespeed_api_request)
    except:  # breaking and hoping for more luck with the next URL
        print(
            'Error! Unfortunately the request for URL "{0}" failed, message:\n{1}'.format(
                check_url, sys.exc_info()[0]))
        pass

    json_content = ''

    try:
        json_content = json.loads(get_content)
    except:  # might crash if checked resource is not a webpage
        print('Error! JSON failed parsing for the URL "{0}"\nMessage:\n{1}'.format(
            check_url, sys.exc_info()[0]))
        pass

    return_dict = {}

    review = ''
    score = 0
    # look for words indicating item is insecure
    insecure_strings = ['security', 'säkerhet',
                        'insecure', 'osäkra', 'unsafe']

    rating = Rating()
    rating.set_integrity_and_security(5.0)

    # Service score (0-100)
    score = json_content['lighthouseResult']['categories'][category]['score']
    # change it to % and convert it to a 1-5 grading
    points = 5.0 * float(score)

    for item in json_content['lighthouseResult']['audits'].keys():
        try:
            return_dict[item] = json_content['lighthouseResult']['audits'][item]['score']

            if int(json_content['lighthouseResult']['audits'][item]['score']) == 1:
                continue

            item_review = ''
            if 'displayValue' in json_content['lighthouseResult']['audits'][item]:
                item_displayvalue = json_content['lighthouseResult']['audits'][item]['displayValue']
                item_review = _("* {0} - {1}\r\n").format(
                    json_content['lighthouseResult']['audits'][item]['title'], item_displayvalue)
            else:
                item_review = _(
                    "* {0}\r\n").format(json_content['lighthouseResult']['audits'][item]['title'])
            review += item_review

            for insecure_str in insecure_strings:
                if insecure_str in item_review:
                    rating.set_integrity_and_security(
                        rating.integrity_and_security - 1.0, rating.integrity_and_security_review + item_review)
                    break
        except:
            # has no 'numericValue'
            #print(item, 'har inget värde')
            pass

    if points >= 5.0:
        review = _("TEXT_REVIEW_PRACTICE_VERY_GOOD") + review
    elif points >= 4.0:
        review = _("TEXT_REVIEW_PRACTICE_IS_GOOD") + review
    elif points >= 3.0:
        review = _("TEXT_REVIEW_PRACTICE_IS_OK") + review
    elif points > 1.0:
        review = _("TEXT_REVIEW_PRACTICE_IS_BAD") + review
    elif points <= 1.0:
        review = _("TEXT_REVIEW_PRACTICE_IS_VERY_BAD") + review

    rating.set_overall(points, review)

    return (rating, return_dict)
