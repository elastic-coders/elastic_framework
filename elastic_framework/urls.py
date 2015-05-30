from django.conf.urls import patterns, include, url

from django.contrib import admin

from elastic_framework.contrib.auth.views import Oauth2ECUserListView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'elastic_framework.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
    #url(r'^', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^$', Oauth2ECUserListView.as_view()),
)
