# Copyright 2007-2010 VPAC
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

"""
Methods for getting usage data
uses a database cache to speed up proccess

"""
__author__ = 'Sam Morrison'
from django.db import connection
from django.db.models import Count, Sum

import datetime

from karaage.cache.models import InstituteCache, ProjectCache, UserCache, MachineCache
from karaage.usage.models import CPUJob
from karaage.machines.models import UserAccount

def get_instititue_usage_period(institute, period, machine_category):
    """Return a tuple of cpu hours and number of jobs for an institute

    Keyword arguments:
    institute -- 
    period -- number of days back from today
    machine_category -- MachineCategory object
    
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=int(period))
    return get_institute_usage_date(institute, start, end, machine_category)

def get_institute_usage(institute, start, end, machine_category):
    """Return a tuple of cpu hours and number of jobs for an institute
    for a given period

    Keyword arguments:
    institute -- 
    start -- start date
    end -- end date
    machine_category -- MachineCategory object
    
    """
    try:
        cache = InstituteCache.objects.get(institute=institute, date=datetime.date.today(), start=start, end=end, machine_category=machine_category)
    except:

        data = CPUJob.objects.filter(machine__category=machine_category, 
                                     project__institute=institute, 
                                     date__range=(start, end)).aggregate(usage=Sum('cpu_usage'), jobs=Count('id'))

        cache = InstituteCache.objects.create(institute=institute, 
                                              start=start, 
                                              end=end, 
                                              machine_category=machine_category, 
                                              cpu_hours=data['usage'], 
                                              no_jobs=data['jobs'])
    return cache.cpu_hours, cache.no_jobs


def get_project_usage(project, start, end, machine_category):
    """Return a tuple of cpu hours and number of jobs for a project
    for a given period

    Keyword arguments:
    project -- 
    start -- start date
    end -- end date
    
    """
    try:
        cache = ProjectCache.objects.get(pid=project, date=datetime.date.today(), start=start, end=end, machine_category=machine_category)
    except:

        data = CPUJob.objects.filter(machine__category=machine_category, 
                                     project=project, 
                                     date__range=(start,end)).aggregate(usage=Sum('cpu_usage'), jobs=Count('id'))

        cache =  ProjectCache.objects.create(pid=project, start=start, 
                                             end=end, machine_category=machine_category, 
                                             cpu_hours=data['usage'], no_jobs=data['jobs'])
    return cache.cpu_hours, cache.no_jobs


def get_user_usage_period(user, project, period):
    """Return a tuple of cpu hours and number of jobs for a user in a specific project

    Keyword arguments:
    user -- 
    project -- The project the usage is from 
    period -- number of days back from today  
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=int(period))
    return get_user_usage_date(project, start, end)


def get_user_usage(user, project, start, end):
    """Return a tuple of cpu hours and number of jobs for a user in a specific project

    Keyword arguments:
    user -- 
    project -- The project the usage is from
    start -- start date
    end -- end date 
    """
    try:
        cache = UserCache.objects.get(user=user, project=project, date=datetime.date.today(), start=start, end=end)
    except:
        total_usage = total_jobs = 0
        accounts = UserAccount.objects.filter(user=user)

        data = CPUJob.objects.filter(date__range=(start, end),
                                      project=project,
                                      user__user=user).aggregate(usage=Sum('cpu_usage'), jobs=Count('id'))

        cache = UserCache.objects.create(user=user, project=project, 
                                         start=start, end=end, 
                                         cpu_hours=data['usage'], no_jobs=data['jobs'])

    return cache.cpu_hours, cache.no_jobs



def get_machine_usage(machine, start, end):
    """Return a tuple of cpu hours and number of jobs for a machine
    for a given period

    Keyword arguments:
    machine -- 
    start -- start date
    end -- end date
    
    """
    
    try:
        cache = MachineCache.objects.get(machine=machine, date=datetime.date.today(), start=start, end=end)
    except:
        
        data = CPUJob.objects.filter(machine=machine,
                                     date__range=(start, end)).aggregate(usage=Sum('cpu_usage'), jobs=Count('id'))

        cache =  MachineCache.objects.create(machine=machine, start=start, end=end, cpu_hours=data['usage'], no_jobs=data['jobs'])

    return cache.cpu_hours, cache.no_jobs

