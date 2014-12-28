from django.conf.urls import patterns, include, url
from mhf.views import viewWrapper, home, redirect, machine_learning, twitter_visualization,map_reduce, \
    loadingCrazy, theHome, submitEmail, monkeySkull, brocasCoconut, capitalistTees, buyShirt, \
    writing, art, contact, about, truespeak, truespeakPublicDetail, truespeakSecretLink, publishTexts, \
    projects, store
from settings.common import LOCAL, STATIC_URL, STATIC_ROOT
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponse

# urlpatterns = patterns('',
#     # ... the rest of your URLconf goes here ...
# ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#
# patterns for mhfowler
urlpatterns = patterns('',
                       # (r'^$', viewWrapper(monkeyLoader)),
                       (r'^______/$', viewWrapper(theHome)),
                       (r'^~/$', viewWrapper(monkeySkull)),
                       (r'^brocascoconut/$', viewWrapper(brocasCoconut)),
                       (r'^LOADING/(?P<page>\w+)/$', viewWrapper(loadingCrazy)),

                       # posts
                       (r'^submit_email/$', viewWrapper(submitEmail)),

                       # capitalist products
                       (r'^the_capitalist_tshirt/$', viewWrapper(capitalistTees)),
                       (r'^capitalist_prints/$', viewWrapper(capitalistTees)),
                       (r'^capitalist_booty_shorts/$', viewWrapper(capitalistTees)),

                       # other pages
                       (r'^writing/$', viewWrapper(writing)),
                       (r'^art/$', viewWrapper(art)),
                       (r'^projects/$', viewWrapper(projects)),
                       (r'^store/$', viewWrapper(store)),
                       (r'^contact/$', viewWrapper(contact)),
                       (r'^about_brocas/$', viewWrapper(about)),
                       (r'^buyShirt/$', viewWrapper(buyShirt)),

                       # truespeak
                       (r'^truespeak/$', viewWrapper(truespeak)),
                       (r'^truespeak/(?P<name>\w+)/(?P<appendage>\d+)/$', viewWrapper(truespeakPublicDetail)),
                       (r'^secretlink/(?P<name>\S+)/(?P<appendage>\d+)/$', viewWrapper(truespeakSecretLink)),
                       (r'^publish_texts/$', viewWrapper(publishTexts)),


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


