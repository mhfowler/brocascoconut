from django.conf.urls import patterns, include, url
from mhf.views import viewWrapper, home, redirect
from settings.common import LOCAL, STATIC_URL, STATIC_ROOT




# patterns for mhfowler
urlpatterns = patterns('',
                       (r'^home/$', viewWrapper(home)),
                       )

# if local serve static
if LOCAL:
    urlpatterns += patterns('',
                            (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root': STATIC_ROOT}),
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


# # redirect everything else
urlpatterns += patterns('',
                        (r'^/$',  redirect, {'page':"/home/"}),
                        (r'^$',  redirect, {'page':"/home/"}),
                        # (r'.*$',  redirect, {'page':"/home/"}),
                        )

