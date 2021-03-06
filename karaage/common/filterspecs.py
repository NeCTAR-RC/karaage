# Copyright 2007-2014 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

from django.utils.safestring import mark_safe
from django.db.models.query import QuerySet, ValuesQuerySet
import datetime
from operator import itemgetter


def get_query_string(qs):
    return '?' + '&amp;'.join(
        [u'%s=%s' % (k, v) for k, v in qs.items()]).replace(' ', '%20')


class Filter(object):
    multi = False

    def __init__(self, request, name, filters, header=''):

        if header == '':
            self.header = name
        else:
            self.header = header

        if isinstance(filters, tuple):
            filters = dict(filters)

        if isinstance(filters, ValuesQuerySet):
            f = {}
            for i in filters:
                f[str(i)] = str(i)
            filters = f

        if isinstance(filters, QuerySet):
            f = {}
            for i in filters:
                f[i.pk] = str(i)
            filters = f

        self.name = name
        self.filters = filters
        self.selected = None
        if name in request.GET:
            self.selected = request.GET[name]

    def output(self, qs):

        try:
            del(qs[self.name])
        except:
            pass

        filters = sorted(self.filters.iteritems(), key=itemgetter(1))

        selected = None
        for k, v in filters:
            if str(self.selected) == str(k):
                selected = v
        if selected is None:
            selected = "all"

        output = '<li>'
        output += '<a href="#">By %s (%s)</a>\n' % (
            self.header.replace('_', ' '), selected)
        output += '<ul>\n'

        if self.selected is not None:
            output += (
                """<li><a href="%s">All</a></li>\n"""
                % get_query_string(qs)
            )
        else:
            output += (
                """<li class="selected"><a href="%s">All</a></li>\n"""
                % get_query_string(qs)
            )
        for k, v in filters:
            if str(self.selected) == str(k):
                style = """class="selected" """
            else:
                style = ""
            qs[self.name] = k
            output += (
                """<li %s><a href="%s">%s</a></li>\n"""
                % (style, get_query_string(qs), v)
            )

        output += '</ul></li>'

        return output


class DateFilter(object):
    multi = True

    def __init__(self, request, name, header=''):
        self.name = name
        if header == '':
            self.header = name
        else:
            self.header = header
        params = dict(request.GET.items())

        self.field_generic = '%s__' % self.name

        self.date_params = dict(
            [(k, v) for k, v in params.items()
                if k.startswith(self.field_generic)])

        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        today_str = today.strftime('%Y-%m-%d')

        self.links = (
            ('Any date',
                {}),
            ('Today', {
                '%s__year' % self.name: str(today.year),
                '%s__month' % self.name: str(today.month),
                '%s__day' % self.name: str(today.day)}),
            ('Past 7 days', {
                '%s__gte' % self.name: one_week_ago.strftime('%Y-%m-%d'),
                '%s__lte' % self.name: today_str}),
            ('This month', {
                '%s__year' % self.name: str(today.year),
                '%s__month' % self.name: str(today.month)}),
            ('This year', {
                '%s__year' % self.name: str(today.year)})
        )

    def choices(self):
        for title, param_dict in self.links:
            yield {'selected': self.date_params == param_dict,
                   'query_dict': param_dict,
                   'display': title}

    def output(self, qs):
        choices = list(self.choices())

        selected = None
        for choice in choices:
            if choice['selected']:
                selected = choice['display']
        if selected is None:
            selected = "all"

        output = ''
        output += '<li>\n'
        output += (
            '<a href="#">By %s (%s)</a>\n'
            % (self.header.replace('_', ' '), selected)
        )
        output += '<ul>\n'

        for choice in choices:
            for k, v in qs.items():
                if k.startswith(self.field_generic):
                    del(qs[k])

            for k, v in choice['query_dict'].items():
                qs[k] = v

            output += """<li %s><a href="%s">%s</a></li>\n""" % (
                choice['selected'] and "class='selected'" or '',
                get_query_string(qs), choice['display'])

        output += '</ul></li>'
        return output


class FilterBar(object):

    def __init__(self, request, filter_list):

        self.request = request
        self.filter_list = filter_list
        raw_qs = request.META.get('QUERY_STRING', '')
        qs = {}
        if raw_qs:
            for i in raw_qs.replace('?', '').split('&'):
                if i:
                    k, v = i.split('=')
                    if k != 'page':
                        qs[k] = v

        for f in self.filter_list:
            if f.multi:
                params = dict(request.GET.items())
                field_generic = '%s__' % f.name
                m_params = dict(
                    [(k, v) for k, v in params.items()
                        if k.startswith(field_generic)])
                for k, v in m_params.items():
                    qs[k] = v

            else:
                if f.name in self.request.GET:
                    qs[f.name] = self.request.GET[f.name]

        self.qs = qs

    def output(self):

        output = ''

        for f in self.filter_list:
            output += f.output(self.qs.copy())

        return output

    def __str__(self):
        return mark_safe(self.output())


class ObjectList(object):

    def __init__(self, request, object_list, headers, filters):

        self.headers = headers
        self.object_list = object_list
