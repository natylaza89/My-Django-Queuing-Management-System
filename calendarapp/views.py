from datetime import datetime, timedelta, date
from dateutil.parser import parse

import calendar
from operator import attrgetter

from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin 
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages




from .models import Treatments
from .utils import TreatmentsCalendar, google_calendar_connection, \
     google_calendar_add_event, google_calendar_delete_event, send_treatment_email
from .forms import TreatmentForm



# class TreatmentCreateView(LoginRequiredMixin, CreateView):
#     model = Treatments
#     fields = ['title', 'description', 'date', 'time']

#     #overridng
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)  

class CalendarMyTreatmentsView(LoginRequiredMixin, generic.ListView):
    model = Treatments
    template_name = 'calendarapp/my_treatments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        treatments = Treatments.objects.filter(user__username=self.request.user.username)
        #treatments = sorted(treatments, key = attrgetter('time')  )
        treatments = treatments.order_by('date', 'time')
        context['treatments'] = treatments
        today_date = date.today()
        context['today_date'] = today_date

        return context

class CalendarView(LoginRequiredMixin, generic.ListView):
    model = Treatments
    template_name = 'calendarapp/calendar.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today_date = get_date(self.request.GET.get('month', None))
        calendar = TreatmentsCalendar(today_date.year, today_date.month)
        html_calendar = calendar.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_calendar)
        context['prev_month'] = prev_month(today_date)
        context['next_month'] = next_month(today_date)
        context['month'] = self.formatmonthname(today_date.month)
        context['year'] = today_date.year

        return context

    def formatmonthname(self, today_month):
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
        
        return months_to_hebrew[f'{today_month}']
    
def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = f'month={prev_month.year}-{prev_month.month}'
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = f'month={next_month.year}-{next_month.month}'
    return month

@login_required
def treatment(request, treatment_id=None,):

    instance = Treatments()
    if treatment_id:
        instance = get_object_or_404(Treatments, pk=treatment_id)
        treatment_exist = True
    else:
        instance = Treatments()
        treatment_exist = False

    instance.user = request.user
    
    form = TreatmentForm(request.POST or None, instance=instance)
    
    result = render(request, 'calendarapp/treatment_form.html', {'form': form, 'treatment_exist': treatment_exist, 'treatment_id': treatment_id})
    if request.POST and form.is_valid():
        date = request.POST['date'].split('-')
        time = request.POST['time']

        treatments = Treatments.objects.filter(date__year=date[0], date__month=date[1], date__day=date[2])
        treatment_in_same_time = treatments.filter(time__contains=time)

        today_date = datetime.today()
        required_date = datetime(int(date[0]), int(date[1]), int(date[2]))
        
        if required_date < today_date:
            messages.error(request, "התאריך שבחרת עבר ולא ניתן לתת בו שירות.")
            result = render(request, 'calendarapp/treatment_form.html', {'form': form})

        elif treatment_in_same_time.count() !=0 : # found treatment
            messages.error(request, "השעה שבחרת תפוסה, אנא נסו שנית!")
            result = render(request, 'calendarapp/treatment_form.html', {'form': form})
        else:
            service, calendar_id = google_calendar_connection()
            date = request.POST['date']
            required_datetime = parse(f"{date} {time}:00").isoformat()

            status = None
            if treatment_exist is True:
                google_calendar_delete_event(service, calendar_id, instance.google_event_id)
                messages.info(request, 'הזמנתך עודכנה במערכת - מייל עם פרטי ההזמנה נשלחו לתיבת המייל שלך!')
                status = 'update'
            else:
                messages.success(request, 'הזמנתך נקלטה במערכת - מייל עם פרטי ההזמנה נשלחו לתיבת המייל שלך!')
                status = 'new'

            event = google_calendar_add_event(request, service, calendar_id, required_datetime)
            instance.google_event_id = event['id']
            #event.get('htmlLink') -> for future automation telegram, log file or whatever...
            #html_dir = os.path.join(BASE_DIR, 'calendarapp/templates/emails/')
            send_treatment_email(instance, request.user.email, request.get_host(), status)

            form.save()
            
            result = HttpResponseRedirect(reverse('calendar:calendar'))
    
    return result
    #return render(request, 'calendarapp/treatment_form.html', {'form': form})

@login_required
def day_treatment(request, treatment_date=None):
    required_date = treatment_date.split('-')
    today_date = datetime.today()
    required_date = datetime(int(required_date[0]), int(required_date[1]), int(required_date[2]))
        
    if required_date < today_date and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "התאריך שבחרת עבר ולא ניתן לתת בו שירות.")
        result = HttpResponseRedirect(reverse('calendar:calendar'))
    
    else:
        context = dict()
        # test = get_object_or_404(Treatments, date=treatment_date) // for 1 item only!
        required_date = treatment_date.split('-')
        day = required_date[2]
        context['day'] = day
        context['month'] = CalendarView().formatmonthname(required_date[1])
        context['year'] = required_date[0]
        calendar = TreatmentsCalendar(int(required_date[0]), int(required_date[1]))
        html_calendar = calendar.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_calendar)
        html_holidays = calendar.format_holidays(day)
        context['holidays'] = mark_safe(html_holidays)
        html_treatments = calendar.format_treatments(day, request.user)
        context['treatments'] = mark_safe(html_treatments)
        path_previous_month_format = f"?month={required_date[0]}-{required_date[1]}"
        context['previous'] = path_previous_month_format

        result = render(request, 'calendarapp/calendar_day_treatments.html', context)

    return result

class TreatmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Treatments
    success_url = reverse_lazy('calendar:calendar_my_treatments')

    def test_func(self):
        treatment = self.get_object()
        if self.request.user == treatment.user:
            return True
        return False

    def post(self, request, *args, **kwargs):
        requested_event = get_object_or_404(Treatments, pk=kwargs['pk'])
        service, calendar_id = google_calendar_connection()
        google_calendar_delete_event(service, calendar_id, requested_event.google_event_id)        
        status = 'delete'

        
        messages.success(request, "התור בוטל בהצלחה! מייל עדכון יצא!")
        send_treatment_email(requested_event, request.user.email, request.get_host(), status)
        return self.delete(request, *args, **kwargs)

# @login_required
# def delete_treatment(request, treatment_id=None):
#     print("treatment_id: ", treatment_id)
#     instance = Treatments()
#     if treatment_id:
#         instance = get_object_or_404(Treatments, pk=treatment_id)
#         instance.delete()
#         messages.success(request, 'התור בוטל בהצלחה!')
        
#     else:
#         #return reverse('calendar:calendar_delete_treatment', args=(treatment_id,))
#         messages.error(request, 'התור לא בוטל ושמור במערכת.!')

#     return redirect('calendar:calendar')


