#!/usr/bin/env python3
"""
History library

Copyright (c) 2020 Nicolas Beguier
Licensed under the MIT License
Written by Nicolas BEGUIER (nicolas_beguier@hotmail.com)
"""

# Third party library imports
from requests import Session
import urllib3

# Own library
# pylint: disable=E0401
import lib.analysis as analysis
import lib.common as common

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SESSION = Session()
HEADERS = common.gen_headers()

def get(isin, years=3):
    """
    Get 3 years history of this ISIN
    """
    url = common.decode_rot(
        'uggcf://yrfrpubf-obhefr-sb-pqa.jyo.nj.ngbf.arg/SQF/uvfgbel.kzy?' +
        'ragvgl=rpubf&ivrj=NYY&pbqvsvpngvba=VFVA&rkpunatr=KCNE&' +
        'nqqQnlYnfgCevpr=snyfr&nqwhfgrq=gehr&onfr100=snyfr&' +
        'frffJvguAbDhbg=snyfr&crevbq={}L&tenahynevgl=&aoFrff=&'.format(years) +
        'vafgeGbPzc=haqrsvarq&vaqvpngbeYvfg=&pbzchgrIne=gehr&' +
        'bhgchg=pfiUvfgb&') + 'code={}'.format(isin)
    req = SESSION.get(url, verify=False)
    if req.ok:
        return req.text.split('\n')
    return False

def dividendes(parameters, infos_boursiere):
    """
    Returns extra info about dividendes
    """
    report = dict()
    report['last_rendement'] = 'Unknown'
    report['last_val'] = 'Unknown'
    report['latest_val'] = 'Unknown'
    report['average_val'] = 'Unknown'
    report['last_detach'] = 'Unknown'
    report['latest_detach'] = 'Unknown'
    report['last_year'] = 'Unknown'
    if 'Détachement' not in infos_boursiere:
        return report
    history = get(parameters['isin'])
    if history and infos_boursiere['Détachement'] != '-':
        matching_date = infos_boursiere['Détachement'].split('/')
        latest_matching_date = '20{:02d}/{}/'.format(
            int(matching_date[2])-1, matching_date[1])
        matching_date = '20{}/{}/{}'.format(
            matching_date[2], matching_date[1], matching_date[0])
        open_value = None
        latest_open_value = None
        for line in history:
            date = line.split(';')[0]
            if date == matching_date:
                open_value = float(line.split(';')[1])
            elif latest_matching_date in date:
                latest_matching_date = date
                latest_open_value = float(line.split(';')[1])
        if open_value is not None and latest_open_value is not None:
            div = float(infos_boursiere['Dividendes'].split()[0])
            average_val = (open_value+latest_open_value)/2
            rendement = 100 * div / average_val
            report['last_rendement'] = round(rendement, 2)
            report['last_val'] = round(open_value, 2)
            report['latest_val'] = round(latest_open_value, 2)
            report['average_val'] = round(average_val, 2)
            report['last_detach'] = matching_date
            report['latest_detach'] = latest_matching_date
            report['last_year'] = latest_matching_date.split('/')[0]
    return report

def per(parameters, simple_report):
    """
    Display the differents stage of the PER and when
    it was reach for the last time
    """
    report = dict()
    if 'PER' not in simple_report or 'valorisation' not in simple_report:
        return report
    current_per = float(simple_report['PER'])
    if current_per == 0:
        return report
    current_val = float(simple_report['valorisation'])

    report = analysis.per_by_value(current_per, current_val)
    for _per in report:
        report[_per]['date'] = analysis.get_last_val_date(
            parameters['isin'], report[_per]['value'])
    return report

def peg(parameters, simple_report, current_peg):
    """
    Display the differents stage of the PEG and when
    it was reach for the last time
    """
    report = dict()
    if 'valorisation' not in simple_report:
        return report
    if current_peg == 0:
        return report
    current_val = float(simple_report['valorisation'])

    report = analysis.peg_by_value(float(current_peg), current_val)
    for _peg in report:
        report[_peg]['date'] = analysis.get_last_val_date(
            parameters['isin'], report[_peg]['value'])
    return report
