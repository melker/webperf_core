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


def run_test(langCode, url, strategy='mobile', category='accessibility'):

    language = gettext.translation(
        'a11y_lighthouse', localedir='locales', languages=[langCode])
    language.install()
    _ = language.gettext

    print(_('TEXT_RUNNING_TEST'))

    check_url = url.strip()

    pagespeed_api_request = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?locale={3}&category={0}&url={1}&key={2}'.format(
        category, check_url, googlePageSpeedApiKey, langCode)

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
    fails = 0

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

        except:
            # has no 'numericValue'
            #print(item, 'har inget värde')
            pass

    if points >= 5.0:
        review = _("TEXT_REVIEW_A11Y_VERY_GOOD") + review
    elif points >= 4.0:
        review = _("TEXT_REVIEW_A11Y_IS_GOOD") + review
    elif points >= 3.0:
        review = _("TEXT_REVIEW_A11Y_IS_OK") + review
    elif points > 1.0:
        review = _("TEXT_REVIEW_A11Y_IS_BAD") + review
    elif points <= 1.0:
        review = _("TEXT_REVIEW_A11Y_IS_VERY_BAD") + review

    rating = Rating()
    rating.set_overall(points, review)
    rating.set_a11y(points, review)

    return (rating, return_dict)
