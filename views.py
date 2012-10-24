# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import Context, Template
from django.utils.dates import MONTHS, MONTHS_3, WEEKDAYS, WEEKDAYS_ABBR

from django.conf import settings
from django.utils.text import javascript_quote
from django.utils.encoding import smart_unicode
from django.utils.formats import get_format_modules, get_format

import datetime
from django.utils.dateformat import TimeFormat

tmpl = """
{% autoescape off %}
(function(window, undefined) {
    var Globalize = window.Globalize;
    Globalize.addCultureInfo("{{language_code}}", "default", {
        name: "{{language_code}}",
        language: "{{language_code}}",
        numberFormat: {
            ",": "{{thousandseparator}}",
            ".": "{{decimalseparator}}",
            negativeInfinity: "-INF",
            positiveInfinity: "INF",
            percent: {
                ",": "{{thousandseparator}}",
                ".": "{{decimalseparator}}"
            },
            /*
            TODO: Currency support
            currency: {
                pattern: ["-n $","n $"],
                ",": ".",
                ".": ",",
                symbol: "kr"
            }
            */
        },
        calendars: {
            standard: {
                firstDay: 1,
                days: {
                    names: [{{weekdays_full}}],
                    namesAbbr: [{{weekdays_short}}],
                    namesShort: [{{weekdays_short}}]
                },
                months: {
                    names: [{{months_full}}],
                    namesAbbr: [{{months_short}}]
                },

                AM: [{{AM}}],
                PM: [{{PM}}],
                patterns: {
                    d: {{dateformat_short}},
                    D: {{dateformat}},
                    t: {{timeformat}},
                    T: {{timeformat}},
                    f: {{datetimeformat}},
                    F: {{datetimeformat}},
                    M: {{monthdayformat}},
                    Y: {{yearmonthformat}}
                }
            }
        }
    });

    // Global variables about i18n stuff
    window.i18n = {
        language_code: "{{language_code}}"
    };
    // Set the Globalize locale to current language
    Globalize.culture(window.i18n.language_code);

}(this));

{% endautoescape %}
"""


def get_formats():
    FORMAT_SETTINGS = (
        'DATE_FORMAT', 'DATETIME_FORMAT', 'TIME_FORMAT',
        'YEAR_MONTH_FORMAT', 'MONTH_DAY_FORMAT', 'SHORT_DATE_FORMAT',
        'SHORT_DATETIME_FORMAT', 'FIRST_DAY_OF_WEEK', 'DECIMAL_SEPARATOR',
        'THOUSAND_SEPARATOR', 'NUMBER_GROUPING',
        'DATE_INPUT_FORMATS', 'TIME_INPUT_FORMATS', 'DATETIME_INPUT_FORMATS'
    )
    result = {}
    return_result = {}
    for module in [settings] + get_format_modules(reverse=True):
        for attr in FORMAT_SETTINGS:
            result[attr] = get_format(attr)
    for k, v in result.items():
        if isinstance(v, (basestring, int)):
            return_result[k] = smart_unicode(v)
        elif isinstance(v, (tuple, list)):
            v = [javascript_quote(smart_unicode(value)) for value in v]
            return_result[k] = "', '".join(v)
    return return_result


def to_jsonarray(dict):
    """
        Takes the value from a dict and creates a
        json array of strings
    """
    li = []
    for key, val in sorted(dict.iteritems()):
        li.append("\"%s\"" % unicode(val))
    return ",".join(li)


def datetime_to_globalize(val):
    """
        Convert a date representation from django format to Globalize.js format
        E.g.
            Y-m-d => yyyy-MM-dd
    """
    result = val
    result = result.replace('Y', 'yyyy')
    result = result.replace('m', 'MM')
    result = result.replace('d', 'dd')

    result = result.replace('j', 'd')
    result = result.replace('F', 'MMMM')
    result = result.replace('N', 'MMM')

    result = result.replace('H', 'HH')
    result = result.replace('i', 'mm')

    result = result.replace('P', 'h:mm t')
    return '"%s"' % result


def get_ampm_designators():
    am = TimeFormat(datetime.time(11, 00, 00))
    pm = TimeFormat(datetime.time(13, 00, 00))
    result = {}
    result['AM'] = {"1": am.format('A'), "2": am.format('a'), "3": am.format('A')}
    result['PM'] = {"1": pm.format('A'), "2": pm.format('a'), "3": pm.format('A')}
    return result


def javascript_catalog(request):
    fmt = get_formats()
    ampm = get_ampm_designators()

    t = Template(tmpl)
    c = Context({
        'language_code': request.LANGUAGE_CODE,
        'months_full': to_jsonarray(MONTHS),
        'months_short': to_jsonarray(MONTHS_3),
        'weekdays_full': to_jsonarray(WEEKDAYS),
        'weekdays_short': to_jsonarray(WEEKDAYS_ABBR),
        'dateformat_short': datetime_to_globalize(fmt['SHORT_DATE_FORMAT']),
        'dateformat': datetime_to_globalize(fmt['DATE_FORMAT']),
        'timeformat': datetime_to_globalize(fmt['TIME_FORMAT']),
        'datetimeformat': datetime_to_globalize(fmt['DATE_FORMAT'] + ' ' + fmt['TIME_FORMAT']),
        'AM': to_jsonarray(ampm['AM']),
        'PM': to_jsonarray(ampm['PM']),
        'monthdayformat': datetime_to_globalize(fmt['MONTH_DAY_FORMAT']),
        'yearmonthformat': datetime_to_globalize(fmt['YEAR_MONTH_FORMAT']),
        'decimalseparator': fmt['DECIMAL_SEPARATOR'],
        'thousandseparator': fmt['THOUSAND_SEPARATOR'],
    })
    return HttpResponse(t.render(c), "text/javascript")
