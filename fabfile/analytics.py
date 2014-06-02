#!/usr/bin/env python

"""
Analytics reporting tasks
"""

from collections import OrderedDict
import json
import os

from fabric.api import task

import app_config
from etc.ga import GoogleAnalytics

@task
def machine(path):
    """
    Write current analytics to a JSON file.
    """
    ga = GoogleAnalytics(slug=app_config.PROJECT_SLUG)
    #ga = GoogleAnalytics(slug='tshirt')

    output = {}
    print 'Getting totals'
    output['totals'] = ga.totals()
    print 'Getting top devices'
    output['top_devices'] = ga.totals_by_device_category(output['totals'])
    print 'Getting top sources'
    output['top_sources'] = ga.totals_by_source(output['totals'])
    print 'Getting top browsers'
    output['top_browsers'] = ga.totals_by_browser(output['totals'])
    print 'Getting top pages'
    output['top_pageviews'] = ga.top_pageviews()
    print 'Getting performance data'
    output['performance'] = ga.performance()
    print 'Getting time on site'
    output['time_on_site'] = ga.time_on_site()
    print 'Getting time on site by devices'
    output['time_on_site_devices'] = ga.time_on_site_by_device_category()

    with open(path, 'w') as f:
        json.dump(output, f)

def _format_duration(secs):
    secs = int(secs)

    if secs > 60:
        mins = secs / 60
        secs = secs - (mins * 60)

        return '%im %02is' % (mins, secs)

    return '%02is' % secs  

@task
def human(path):
    """
    Print analytics from a saved file.
    """
    with open(path) as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    print 'Totals:'

    totals = data['totals'] 

    for k, v in totals.items():
        print '{:>15,d}    {:s}'.format(v, k)

    print ''
    print '{:>15s}    {:s}'.format(_format_duration(data['time_on_site']), 'ga:avgSessionDuration')
    
    print ''
    print 'Top devices:'

    for column, devices in data['top_devices'].items():
        print '    %s' % column

        for d, v in devices.items():
            print '{:>15.1%}    {:s}'.format(v, d)

    print ''
    print '    ga:avgSessionDuration'
    
    for d, v in data['time_on_site_devices'].items(): 
        print '{:>15s}    {:s}'.format(_format_duration(v), d)

    print ''
    print 'Top sources (pageviews):'

    sources = data['top_sources']['ga:pageviews']

    for d, v in sources.items():
        print '{:>15.1%}    {:s}'.format(v, d)

    print ''
    print 'Top browsers (pageviews):'

    browsers = data['top_browsers']['ga:pageviews']

    for d, v in browsers.items():
        print '{:>15.1%}    {:s}'.format(v, d)

    print ''
    print 'Top pageviews:'

    for page, pageviews in data['top_pageviews'].items():
        print '{:>15,d}    {:s}'.format(pageviews, page)

    print ''
    print 'Performance (seconds):'

    metrics = data['performance'] 

    for k, v in metrics.items():
        print '{:>15.1f}    {:s}'.format(v, k)


@task(default=True)
def report():
    """
    Print current analytics to the console.
    """
    machine('.temp_report.json')
    human('.temp_report.json')
    os.remove('.temp_report.json')


