from datetime import datetime, timedelta
from calendar import HTMLCalendar, calendar, SUNDAY
from dotenv import load_dotenv
from os import getenv

from googleapiclient import discovery
from oauth2client import tools
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
import httplib2

import requests
import json
from .models import Treatments
from registration.views import profile

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.shortcuts import reverse, resolve_url
from nails_project.settings import DEFAULT_FROM_EMAIL


class TreatmentsCalendar(HTMLCalendar):
    
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        self.month_holidays = dict()        
        super(TreatmentsCalendar, self).__init__()
        self.setfirstweekday(SUNDAY) 

    def formatday(self, day):
        if day != 0:
            current_day = str(day)
            day_view_url = f"date_view/{self.year}-{self.month}-{day}"
            day_html = f"<div class='day'><a href='{day_view_url}'>{day}</a></div>"
        else:
            day_html = f"<div class='day'>&nbsp;</div>"

        return day_html

    def formatweek(self, theweek):
        week_html = ''
  
        for day, weekday in theweek:
            week_html += self.formatday(day)

        return f"<div class='days'>{week_html}</div>"

    def formatmonth(self, withyear=True):
        calendar_html = f'<div class="responsive-calendar">\n'
        calendar_html += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        calendar_html += f'{self.formatweekheader()}\n'

        for week in self.monthdays2calendar(self.year, self.month):
            
            calendar_html += f'{self.formatweek(week)}\n'

        calendar_html += '</div>'

        return calendar_html
    
    def formatmonthname(self, theyear, themonth, withyear=True):
        months_to_hebrew = {
            '1': 'ינואר',
            '2': 'פברואר',
            '3': 'מרץ',
            '4': 'אפריל',
            '5': 'מאי',
            '6': 'יוני',
            '7': 'יולי',
            '8': 'אוגוסט',
            '9': 'ספטמבר',
            '10': 'אוקטובר',
            '11': 'נובמבר',
            '12': 'דצמבר',
        }
        
        return f"<div class='day-headers'>{months_to_hebrew[f'{self.month}']} {self.year}</div>"

    def formatweekheader(self):
        week_header_html = f"<div class='day-headers'><div class='day header'>א</div><div class='day header'>ב</div>  \
                             <div class='day header'>ג</div><div class='day header'>ד</div>  \
                             <div class='day header'>ה</div><div class='day header'>ו</div> \
                             <div class='day header'>ש</div></div>"

        return week_header_html

    def format_treatments(self, current_day, user):
        treatments = Treatments.objects.filter(date__year = self.year, date__month = self.month, date__day = current_day)
        treatments_dict = dict()

        for treatment in treatments:
            hour = treatment.time#.strftime("%H:%M")
            #if hour[0] == '0':
                #hour = hour[1:]
            treatments_dict[hour] = treatment

        hours = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00']      
       
        if user.is_staff or user.is_superuser:
            treatments_html = self.format_treatment_for_manager(hours, treatments_dict)
        else:
            treatments_html = self.format_treatment_for_client(hours, treatments_dict)

        return treatments_html

    def format_treatment_for_manager(self, hours, treatments_dict):
            treatments_html = f"<div class='responsive-calendar' dir='rtl'> \
                                <div class='day-headers'> \
                                    <div class='day header' style='border-left: 1px solid gray;'>שעות</div> \
                                    <div class='day header'>שם</div> \
                                    <div class='day header'>סוג טיפול</div> \
                                    <div class='day header'>הערות</div> \
                                </div>"

            for hour in hours:
                # treatments_html += f"<div class='day-headers'> \
                #                         <div class='day header' style='border-left: 1px solid gray;'>{hour}</div>"

                if treatments_dict.get(hour) != None:
                    treatment = treatments_dict.get(hour)
                    
                    treatments_html += f"<div class='day-headers'> \
                                        <a class='header' href='{treatment.get_html_url}'><div class='day header' style='border-left: 1px solid gray;'>{hour}</div> \
                                        <div class='day header' style='color: red;'>{treatment.user.username}</div> \
                                        <div class='day header' style='color: red;'>{treatment.title} </div> \
                                        <div class='day header' style='color: red;'>{treatment.description}</div></a> \
                                        </div>"
                else:
                    treatments_html += f"<div class='day-headers'> \
                                         <div class='day header' style='border-left: 1px solid gray;'>{hour}</div> \
                                        <div class='day header' style='color: green;'>פנוי</div> \
                                        <div class='day header' style='color: red;'>&nbsp;</div> \
                                        <div class='day header' style='color: red;'>&nbsp;</div> \
                                        </div>"

            return treatments_html

    def format_treatment_for_client(self, hours, treatments_dict):
            treatments_html = f"<div class='responsive-calendar' dir='rtl'> \
                                    <div class='day-headers'> \
                                        <div class='day header' style='border-left: 1px solid gray;'>שעות</div> \
                                        <div class='day header'>סטטוס</div> \
                                    </div>"

            for hour in hours:
                treatments_html += f"<div class='day-headers'> \
                                        <div class='day header' style='border-left: 1px solid gray;'>{hour}</div>"

                if treatments_dict.get(hour) != None:
                    treatments_html += f"<div class='day header' style='color: red;'>תפוס</div></div>"
                else:
                    treatments_html += f"<div class='day header' style='color: green;'>פנוי</div></div>"

            return treatments_html

    def format_holidays(self, day):
        current_holidays = self.get_jewish_holidays(day)
        holidays_html = "<div>"

        if len(current_holidays) != 0:
            for key, value in current_holidays.items():
                holidays_html += f"<li>{key} - {value}</li>"
        else:
            holidays_html += f"<li>אין חגים היום</li>"

        holidays_html += '</div>'
        return holidays_html

    def get_jewish_holidays(self, day):
        url = f"https://www.hebcal.com/hebcal/?v=1&cfg=json&year={self.year}&month={self.month}& \
                day={day}&lg=h&maj=on&min=on&mf=on&mod=on"
        request = requests.get(url)
        current_holidays = dict()

        if request.status_code == 200:
            json_data = json.loads(request.content.decode('UTF-8'))
            for item in json_data['items']:
                specific_day = item['date'].split('-')[2]
                if specific_day[0] == '0':
                    specific_day = specific_day[1]
                if specific_day == day: 
                    current_holidays[specific_day] = item['title']

        return current_holidays


def google_calendar_connection():
    """
    This method used for connect with google calendar api.
    """
    
    flags = tools.argparser.parse_args([])
    load_dotenv()
    FLOW = OAuth2WebServerFlow(
        client_id=getenv('GOOGLE_CALENDAR_CLIENT_ID'),
        client_secret=getenv('GOOGLE_CALENDAR_CLIENT_SECRET'),
        scope=getenv('GOOGLE_CALENDAR_SCOPE'),
        user_agent=getenv('GOOGLE_CALENDAR_USER_AGENT'),
        )
    storage = Storage('calendar.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
        credentials = tools.run_flow(FLOW, storage, flags)
    
    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = discovery.build('calendar', 'v3', http=http)
    calendar_id = getenv('GOOGLE_CALENDAR_CALENDAR_ID')

    return service, calendar_id

def google_calendar_add_event(request, service, calendar_id, required_datetime):

    event = {
            'summary': request.POST['title'],
            #'location': "london",
            'description': request.POST['description'],
            
            'start': {
                'dateTime': required_datetime, 

                'timeZone': 'Asia/Jerusalem',
            },
            'end': {
                'dateTime': required_datetime,
                'timeZone': 'Asia/Jerusalem',
            }, 
            'attendees': [
                {'email': request.user.email},
                #{'email': 'sbrin@example.com'},
            ],
            }
        
    event_added = service.events().insert(calendarId=calendar_id, body=event).execute()

    return event_added

def google_calendar_delete_event(service, calendar_id, event_id):
    deleted_event = service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

def send_treatment_email(instance, user_email, path, status):
            html_loader = get_template('treatment_email.html')
            date_format = f"{instance.date.day}/{instance.date.month}/{instance.date.year}"
            full_path = f"{path}{resolve_url('calendar:calendar_my_treatments')}"
            context = dict(date=date_format, time=instance.time, title=instance.title,
             description=instance.description, full_path=full_path, status=status)
  
            subject = None
            if status == 'new':
                subject = 'פרטי הזמנת תור'
            elif status == 'update':
                subject = 'פרטי הזמנת תור עדכניים'
            else:
                subject = 'ביטול תור'

            html_content = html_loader.render(context)
            message = EmailMultiAlternatives(subject, '', DEFAULT_FROM_EMAIL, [user_email])
            message.attach_alternative(html_content, "text/html")
            message.send()