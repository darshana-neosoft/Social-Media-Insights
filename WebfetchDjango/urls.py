"""WebfetchDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.contrib import admin
from WebfetchDjango import settings
import webfetchapp

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'home/','webfetchapp.views.home_page'),
    url(r'get_data/','webfetchapp.views.get_data'),
    url(r'show-tweets/','webfetchapp.views.show_tweets'),
    url(r'export-to-csv/','webfetchapp.views.export_to_csv'),
    url(r'show-post/','webfetchapp.views.show_post'),
    url(r'show-video/','webfetchapp.views.show_video')
]
