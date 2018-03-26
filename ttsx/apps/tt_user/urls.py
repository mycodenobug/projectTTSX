# *_*coding:utf-8 *_*
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register$', views.RegisterView.as_view()),
    url(r'^active/(.*)', views.active),
    url(r'^exists', views.exists),
    url(r'login', views.LoginView.as_view()),
]
