from django.conf.urls import patterns, include, url
from mhf.views import viewWrapper, home, redirect, machine_learning, twitter_visualization,map_reduce, \
    loadingCrazy, theHome, submitEmail, monkeySkull, brocasCoconut, capitalistTees, buyShirt, \
    writing, art, contact, about
from settings.common import LOCAL, STATIC_URL, STATIC_ROOT
from django.conf.urls.static import static
from django.conf import settings

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

                       # pages
                       (r'^capitalist_tees/$', viewWrapper(capitalistTees)),
                       (r'^writing/$', viewWrapper(writing)),
                       (r'^art/$', viewWrapper(art)),
                       (r'^contact/$', viewWrapper(contact)),
                       (r'^about/$', viewWrapper(about)),
                       (r'^buyShirt/$', viewWrapper(buyShirt)),


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
                        url(r'^blog/', include('django_yaba.urls')),
                        )


# patterns for admin
from django.contrib import admin

admin.autodiscover()

urlpatterns += patterns('',
                        (r'^admin/', include(admin.site.urls)),
                        )

#
# # # redirect everything else
urlpatterns += patterns('',
                        (r'^/$',  redirect, {'page':"/~/"}),
                        (r'^$',  redirect, {'page':"/~/"}),
                        # (r'.*$',  redirect, {'page':"/home/"}),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


