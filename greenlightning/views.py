import re, json

from django.http import HttpResponse
from django.shortcuts import render

from greenlightning.check_for_ps1 import check_for_ps1
from greenlightning.cronbox_s3 import remove_facebook_cron_alert, add_facebook_cron_alert, get_facebook_active_alerts


# greenlightning
def get_all_tix(request):
    active_alerts = get_facebook_active_alerts()
    to_return = ': getting all tix :'
    for alert in active_alerts:
        event_id = alert[0]
        to_phone_number = alert[1]
        check_for_ps1(fb_event_id=event_id, to_phone_number=to_phone_number)
        to_return += ' {}, {} |'.format(event_id, to_phone_number)
    return HttpResponse(to_return)


def get_tix_endpoint(request, event_id, to_phone_number):
    check_for_ps1(fb_event_id=event_id, to_phone_number=to_phone_number)
    return HttpResponse(': checking for tix: {}, {}'.format(event_id, to_phone_number))


def fishingRemoveAlert(request):
    phone = request.POST['phone']
    fb_id = request.POST['fblink']
    remove_facebook_cron_alert(phone=phone, fb_id=fb_id)
    return HttpResponse('removed')


def fishingAddAlert(request):
    phone = request.POST['phone']
    fb_link = request.POST['fblink']
    phone = phone.strip()
    fb_link = fb_link.strip()
    matched = re.match('.*www\.facebook\.com/events/(\d+)/', fb_link)
    if not matched:
        return HttpResponse(json.dumps({
            'message': 'Invalid format of fb events link'
        }))
    fb_id = matched.group(1)
    add_facebook_cron_alert(phone=phone, fb_id=fb_id)
    return HttpResponse(json.dumps({
        'message': 'added new alert'
    }))


def fishing2016(request):
    active_alerts = get_facebook_active_alerts()
    return render(request, 'fishing2016.html', {
        'active_alerts': active_alerts
    })