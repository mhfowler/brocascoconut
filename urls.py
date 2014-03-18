from django.conf.urls import patterns, include, url
from mhf.views import viewWrapper, home, redirect, machine_learning
from settings.common import LOCAL, STATIC_URL, STATIC_ROOT
from django.conf.urls.static import static
from django.conf import settings




# patterns for mhfowler
urlpatterns = patterns('',
                       (r'^home/$', viewWrapper(home)),
                       (r'^machine_learning/$', viewWrapper(machine_learning)),
                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

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
# urlpatterns += patterns('',
#                         (r'^/$',  redirect, {'page':"/home/"}),
#                         (r'^$',  redirect, {'page':"/home/"}),
#                         # (r'.*$',  redirect, {'page':"/home/"}),
#                         )

