from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponse

from mhf.views import viewWrapper, home, redirect, machine_learning, twitter_visualization,map_reduce, \
    loadingCrazy, theHome, submitEmail, monkeySkull, brocasCoconut, capitalistTees, buyShirt, \
    writing, art, contact, about, projects, store, vr_landing, helloPage

from truespeak.views import truespeak, truespeakPublicDetail, truespeakSecretLink, publishTexts

from greenlightning.views import fishing2016, fishingAddAlert, fishingRemoveAlert, get_tix_endpoint, get_all_tix

from bots.trashbot import trashBot, check_for_dms_endpoint

from slack_heartbeat.slack import citigroup_slackbot_endpoint


# patterns for mhfowler
urlpatterns = patterns('',
                        # brocas coconut
                       (r'^______/$', viewWrapper(theHome)),
                       (r'^~/$', viewWrapper(monkeySkull)),
                       (r'^brocascoconut/$', viewWrapper(brocasCoconut)),
                       (r'^LOADING/(?P<page>\w+)/$', viewWrapper(loadingCrazy)),
                       (r'^submit_email/$', viewWrapper(submitEmail)),
                       (r'^writing/$', viewWrapper(writing)),
                       (r'^art/$', viewWrapper(art)),
                        (r'^vr/$', viewWrapper(vr_landing)),
                       (r'^projects/$', viewWrapper(projects)),
                       (r'^store/$', viewWrapper(store)),
                       (r'^contact/$', viewWrapper(contact)),
                       (r'^about_brocas/$', viewWrapper(about)),
                       (r'^buyShirt/$', viewWrapper(buyShirt)),
                       (r'^hello/$', viewWrapper(helloPage)),

                        # capitalist products
                       (r'^the_capitalist_tshirt/$', viewWrapper(capitalistTees)),
                       (r'^the_capitalist_print/$', viewWrapper(capitalistTees)),
                       (r'^the_capitalist_booty/$', viewWrapper(capitalistTees)),

                       # trashbot
                       (r'^trashbot/$', viewWrapper(trashBot)),
                       (r'^check_for_dms/$', viewWrapper(check_for_dms_endpoint)),

                       # truespeak
                       (r'^truespeak/$', viewWrapper(truespeak)),
                       (r'^truespeak/(?P<name>\w+)/(?P<appendage>\d+)/$', viewWrapper(truespeakPublicDetail)),
                       (r'^secretlink/(?P<name>\S+)/(?P<appendage>\d+)/$', viewWrapper(truespeakSecretLink)),
                       (r'^publish_texts/$', viewWrapper(publishTexts)),

                       # greenlightining
                       (r'^get_all_tix/$', viewWrapper(get_all_tix)),
                       (r'^get_tix/(?P<event_id>\S+)/(?P<to_phone_number>\S+)/$', viewWrapper(get_tix_endpoint)),
                       (r'^greenlightning/$', viewWrapper(fishing2016)),
                       (r'^bass_remove_alert/$', viewWrapper(fishingRemoveAlert)),
                       (r'^bass_add_alert/$', viewWrapper(fishingAddAlert)),

                       # slack
                       (r'^citigroup_bot/$', viewWrapper(citigroup_slackbot_endpoint)),

                       )

# patterns for blog
urlpatterns += patterns('',
                        (r'^home/$', viewWrapper(home)),
                        (r'^machine_learning/$', viewWrapper(machine_learning)),
                        (r'^twitter_visualization/$', viewWrapper(twitter_visualization)),
                        (r'^map_reduce/$', viewWrapper(map_reduce)),
                        )

# patterns for django_yaba
urlpatterns += patterns('',
                        url(r'^nocss/', include('django_yaba.urls')),
                        )


# patterns for admin
from django.contrib import admin

admin.autodiscover()

urlpatterns += patterns('',
                        (r'^admin/', include(admin.site.urls)),
                        )

urlpatterns += patterns('', (r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")) )

#
# # # redirect everything else
urlpatterns += patterns('',
                        (r'^/$',  redirect, {'page':"/~/"}),
                        (r'^$',  redirect, {'page':"/~/"}),
                        # (r'.*$',  redirect, {'page':"/home/"}),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


