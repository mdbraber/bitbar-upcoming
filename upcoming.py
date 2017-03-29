#!/usr/local/bin/python

# <bitbar.title>upcoming</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Maarten den Braber</bitbar.author>
# <bitbar.author.github>mdbraber</bitbar.author.github>
# <bitbar.desc>Show upcoming items from Calendar and Reminders</bitbar.desc>
# <bitbar.image>http://www.hosted-somewhere/pluginimage</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/mdbraber/bitbar-upcoming</bitbar.abouturl>

import time, subprocess, re, dateutil
from datetime import datetime, timedelta

# number of days to look ahead
look_ahead = 7 

# we show events as 'NOW' if nothing else happens in n minutes
minutes_slack = 30

# support links to fantastical?
fantastical = True
# if we show fantastical link - show 'mini' or 'calendar'
fantastical_type = 'mini'

# we need this because icalbuddy lacks decent timezone support
HOUR_OFFSET = -time.altzone // 3600
# ansi codes for bold
BOLD_START = '\033[1m'
BOLD_END = '\033[0m'
# time and date formats
ABSOLUTE_SHORT = '%H:%M'
ABSOLUTE_LONG = '%a %H:%M'
# item types
TASK = 'task'
EVENT = 'event'

events = filter(None,subprocess.check_output(['/usr/local/bin/icalbuddy','eventsToday+'+str(look_ahead)]).split('\n'))
tasks = filter(None,subprocess.check_output(['/usr/local/bin/icalbuddy','tasksDueBefore:today+'+str(look_ahead)]).split('\n'))
items = events+tasks

total = []
upcoming = []

# parse the script output
for i in events:
    m = re.match('(\d{4}-\d{2}-\d{2}) (at )*(\d{2}:\d{2}) (.*)', i)
    if m:
        total.append({
            'datetime': datetime.strptime(m.group(1) + ' ' + m.group(3),'%Y-%m-%d %H:%M'),
            'title': m.group(4),
            'type': EVENT,
            'relative': '',
            'absolute_short': '',
            'absolute_long': '',
            'style': ''})

for i in tasks:
    m = re.match('(\d{4}-\d{2}-\d{2}) (at )*(\d{2}):(\d{2}) (.*)', i)
    if m:
        hour_fixed = str(int(m.group(3)) + HOUR_OFFSET)
        total.append({
            'datetime': datetime.strptime(m.group(1) + ' ' + hour_fixed + ':' + m.group(4) ,'%Y-%m-%d %H:%M'),
            'title': m.group(5),
            'type': TASK,
            'relative': '',
            'absolute_short': '',
            'absolute_long': '',
            'style': ''})

total.sort()

now = datetime.now()
count = 0

# create upcoming items
for t in total:
    d = t['datetime']-now
    dt = t['datetime'].date()
    s = d.seconds
    hours = s // 3600
    s = s - hours * 3600
    minutes = s // 60

    if (t['datetime'] + timedelta(minutes=minutes_slack) > now):

        t['absolute_short'] = t['datetime'].strftime(ABSOLUTE_SHORT)
        t['absolute_long'] = t['datetime'].strftime(ABSOLUTE_LONG)

        if d.days < 0:
            t['relative'] = 'NOW'
            t['absolute_short'] = t['relative']
            t['absolute_long'] = t['relative']
            t['style']= '|color=green'
        elif d.days < 1:
            if (hours == 0 and minutes < 15):
                t['relative'] = 'in %d min' % minutes
                t['style'] = '|color=red'
            elif hours < 1:
                t['relative'] = 'in %d min' % minutes
                t['style'] = '|color=orange'
            elif hours < 6 or now.date() == t['datetime'].date():
                t['relative'] = 'in %d hr %d min' % (hours,minutes)
            else:
                t['relative'] = 'at %s' % t['datetime'].strftime('%H:%M')
        elif d.days == 1 and now.date() == t['datetime'].date():
                t['relative'] = 'tomorrow %s' % t['datetime'].strftime('%H:%M')
        else:
            t['relative'] = t['datetime'].strftime('%a %H:%M')

        # print separators
        if count >= 1 and count < len(total) and t['datetime'].date() != total[count-1]['datetime'].date():
            print '---'
            print BOLD_START + t['datetime'].strftime('%A %e %B').replace('  ',' ') + BOLD_END
        elif count == 1:
            print '---'
        
        # print items
        type_string = ' :ballot_box_with_check:' if t['type'] == TASK else ''
        if count == 0:
            print t['title'] + ' ' + t['relative'] + t['style']
        elif count >= 1:
            fantastical_link = '|href=x-fantastical2://show/%s/%d-%02d-%02d' % (fantastical_type,dt.year,dt.month,dt.day) if fantastical else ''
            print t['absolute_short'] + ' ' + t['title'] + type_string + t['style'] + fantastical_link 

        count = count + 1
