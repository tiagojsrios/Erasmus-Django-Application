from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'blog'
urlpatterns = [
    # ex: /blog/
    path('', views.index, name='index'),
    path('authentication/', views.authentication, name='authentication'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('publish/', views.publish, name='publish'),
    path('search/', views.search, name='search'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    url(r'^post/[1-9]*[0-9]+/$', views.post, name='post'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^profile/[1-9]*[0-9]+/$',
        views.profile, name='profile'),
]