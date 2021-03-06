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

from django.conf.urls import patterns, url, include
from django.conf import settings

urlpatterns = patterns(
    'karaage.usage.views',
    url(r'^$', 'usage_index', name='kg_usage_list'),

    url(r'^unknown/$', 'unknown_usage', name='kg_usage_unknown'),

    url(r'^search/$', 'search', name='kg_usage_search'),
    url(r'^jobs/$', 'job_list', name='kg_usage_job_list'),
    url(r'^jobs/(?P<jobid>[-.\w\[\]]+)/$',
        'job_detail', name='kg_usage_job_detail'),

    url(r'^(?P<machine_category_id>\d+)/$', 'index', name='kg_usage_mc'),

    url(r'^(?P<machine_category_id>\d+)/core_report/$',
        'core_report', name='kg_usage_core_report'),
    url(r'^(?P<machine_category_id>\d+)/mem_report/$',
        'mem_report', name='kg_usage_mem_report'),
    url(r'^(?P<machine_category_id>\d+)/trends/$',
        'institute_trends', name='kg_usage_institute_trends'),

    url(r'^(?P<machine_category_id>\d+)/institute/(?P<institute_id>\d+)/$',
        'institute_usage', name='kg_usage_institute'),
    url(r'^(?P<machine_category_id>\d+)/institute/(?P<institute_id>\d+)/users/$',
        'institute_users', name='kg_usage_users'),
    url(r'^(?P<machine_category_id>\d+)/projects/(?P<project_id>%s)/$'
        % settings.PROJECT_VALIDATION_RE,
        'project_usage', name='kg_usage_project'),

    url(r'^(?P<machine_category_id>\d+)/top_users/$',
        'top_users', name='kg_usage_top_users'),
)

urlpatterns = patterns(
    '',
    url(r'^usage/', include(urlpatterns)),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^karaage_graphs/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.GRAPH_ROOT}),
    )
