from django.contrib import admin
from webfetchapp.models import *
# Register your models here.

admin.site.register(tasks)
admin.site.register(twitter_data)
admin.site.register(facebook_data)
admin.site.register(youtube_data)
admin.site.register(facebook_comments)