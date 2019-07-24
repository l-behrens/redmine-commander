#!/usr/bin/env python
from redmine_commander.utils import *
from redmine_commander.config import *
from dateutil import parser
from dateutil import relativedelta
from datetime import datetime, date, timedelta
from pprint import pprint
import rofi

def fetch_all_issues(base_url, apikey, f_src, cert=None):
    rofi.Rofi().status("downloading issues ... ")
    fltr = [ "status_id=*", "limit=100" ]

    issues=[]
    print(cert)
    for index, page in enumerate(pager(base_url, apikey, *fltr, cert=cert)):
        print(cert)
        i = json.loads(page.text)['issues']
        issues.extend(sorted(i, key=lambda k: k['id']))
        if len(i)<100:
            break

    with shelve.open(f_src) as db:
        db['issues'] = issues


    rofi.Rofi().status(" ... done!")
    return len(issues)

def fetch_all_time(base_url, apikey, f_src, cert=None):
    rofi.Rofi().status("downloading time entries ... ")
    fltr = ["from=2018-04-01", "to=2020-08-01", "limit=100"]
    time_entries=[]
    for index, page in enumerate(pager(base_url, apikey, *fltr, cert=cert, what="time_entries.json")):
        print(cert)
        i = json.loads(page.text)['time_entries']
        #time_entries.extend(sorted(i, key=lambda k: k['id']))
        time_entries.extend(sorted(i, key=lambda k: k['spent_on']))
        if len(i)<100:
            break

    with shelve.open(f_src) as db:
        db['time_entries'] = time_entries

    rofi.Rofi().status(" ... done!")
    return len(time_entries)


def fetch_all_projects(base_url, apikey, f_src, cert=None):
    rofi.Rofi().status("downloading time entries ... ")
    fetch_all_time(base_url, apikey, f_src, cert=cert)
    fltr = [ "status_id=*", "limit=100" ]
    return
    projects=[]
    for index, page in enumerate(pager(base_url, apikey, *fltr, cert=cert, what="projects.json")):
        print(cert)
        i = json.loads(page.text)['projects']
        projects.extend(sorted(i, key=lambda k: k['id']))
        if len(i)<100:
            break

    with shelve.open(f_src) as db:
        db['projects'] = projects

    rofi.Rofi().status(" ... done!")
    return len(projects)

def get_issues(f_src, j='', **kwargs):
       print("issues")
       if not j:
           with shelve.open(f_src) as db:
                issues = db['issues']
       else:
           issues = sorted(j["issues"], key=lambda k: k['id'])
       tmp={}
       for key, value in kwargs.items():
           issues=[issue for issue in issues if str(value) in str(issue[key])]
           print(issues)
       for index, issue in enumerate(reversed(issues)):
           updated_on=parser.parse(issue['updated_on']).replace(tzinfo=None)
           now = datetime.now()
           t_delta=relativedelta.relativedelta(now, updated_on)
           t_int=timedelta_to_int(t_delta)
           ago="weeks ago"
           if (t_delta.weeks==0 and t_delta.months==0 and t_delta.years==0):
               if (t_delta.days==0):
                   if (t_delta.hours==0):
                       ago="%s minutes ago" % t_delta.minutes
                   else:
                       ago="%s hours ago" % t_delta.hours
               else:
                   ago="%s days ago" % t_delta.days
           project=issue["project"]["name"].lower()
           subject=issue["subject"].lower()
           t_id=issue["id"]
           tmp[t_int]=[t_id, '{:8s} {:30.25s} {:85.80s} {:>20s}'.format(
               str(t_id).strip(),
               str(project[:25]).strip().ljust(25),
               str(subject[:80]).strip(),
               ago)]
       return tmp

def get_projects(f_src, j='', **kwargs):
       print("issues")
       if not j:
           with shelve.open(f_src) as db:
                projects = db['projects']
       else:
           projects = sorted(j["projects"], key=lambda k: k['id'])
       tmp={}
       for key, value in kwargs.items():
           projects=[project for project in projects if str(value) in str(issue[key])]

#       projects = sorted(j["projects"], key=lambda k: k['id'])
       tmp={}
       for index, project in enumerate(reversed(projects)):
          name = project["name"].lower()
          p_id = str(project["id"])
          if len(p_id) < 2:
              p_id+='\t'
          tmp[index]=[p_id, 'P {:<6}\t{:<22}'.format(p_id, name)]
       return tmp


def get_time_entries(f_src, j='', interval='day', **kwargs):
       if not j:
           with shelve.open(f_src) as db:
                time_entries = sorted(db["time_entries"], key=lambda k: k['spent_on'])
       else:
           time_entries = sorted(j["time_entries"], key=lambda k: k['spent_on'])

       # pre-select the entries that fall in the range of (today, this week, this month, ...)
       spent_on=[]
       t_entries=[]

       if interval is 'day':
           spent_on.append(f"{datetime.now():%Y-%m-%d}")
       elif interval is 'week':
           di = {}
           for wn,d in enumerate(allsundays(2019)):
               di[wn+1]=[(d + timedelta(days=k)).isoformat() for k in range(0,7)]
           spent_on=[week for week in di.values() if f"{datetime.now():%Y-%m-%d}" in week][0]
       elif interval is 'month':
           spent_on.append(f"{datetime.now():%Y-%m}")
       tmp={}

       for value in spent_on:
           t_entries.extend([entry for entry in time_entries if str(value) in str(entry['spent_on'])])
       time_entries=t_entries

       # Group the entries for presentation of times spent per week over this month
       tmp={}
       hours_sum=sum([entry['hours'] for entry in time_entries])
       entries=[]

       if interval is 'day':
           for index, time_entry in enumerate(time_entries):
               spent_on = time_entry["spent_on"].lower()
               name = time_entry["comments"].lower()
               issue = time_entry["entity_id"]
               hours = time_entry["hours"]
               t_id = str(time_entry["id"])
               entries.append([t_id, issue, name, spent_on, hours])
       elif interval is 'week':
           days=set([d["spent_on"] for d in time_entries])
           for index, day in enumerate(days):
               hours=sum([d['hours'] for d in time_entries if day in str(d['spent_on'])])
               name=day
               entries.append([index, "", name, "",  str(hours)])
       elif interval is 'month':
           di = {}
           for wn,d in enumerate(allsundays(2019)):
               days=[(d + timedelta(days=k)).isoformat() for k in range(0,7)]
               if not f"{datetime.now():%Y-%m}" in str(days):
                  continue
               hours=[]
               for index, day in enumerate(days):
                   hours.append(sum([d['hours'] for d in time_entries if day in str(d['spent_on'])]))
                   entries.append([int(wn+1), "kw: %s" % str(wn+1), "", "", str(sum(hours))])
       for index, entry in enumerate(entries):
           tmp[entry[0]]=[entry[0], '{:8s} {:30.25s} {:85.80s} {:20s}'.format(
               str(entry[1]).strip(),
               str(entry[2])[:25].strip().ljust(25),
               str(entry[3])[:80].strip(),
               str(entry[4]))]
       tmp[99998]=[99998, '{:145s}'.format("-"*145)]
       tmp[99999]=[99999, '{:125s} {:20s}'.format(" "*120, str(hours_sum))]
       return tmp

def print_projects(j):
       projects = sorted(j["projects"], key=lambda k: k['id'])
       for project in reversed(projects):
          name = project["name"]
          p_id = str(project["id"])
          if len(p_id) < 2:
              p_id+='\t'
          print('P {:<6}\t{:<22}'.format(p_id, name))

