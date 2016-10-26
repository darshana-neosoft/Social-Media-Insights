from __future__ import unicode_literals

from django.db import models

# Create your models here.

class tasks(models.Model):
	task_id = models.IntegerField(max_length=10)
	task_data = models.CharField(max_length=500)
	task_output = models.CharField(max_length=500)
	task_created_by = models.DateTimeField()

class twitter_data(models.Model):
	twitter_id = models.AutoField(primary_key = True)
	request_id = models.CharField(max_length = 300)
	twitter_text = models.TextField(max_length = 5000)
	twitter_user_screen_name = models.CharField(max_length=5000)
	twitter_favourite_count = models.CharField(max_length = 300)
	twitter_retwited_count = models.CharField(max_length = 300)
	twitter_user_language = models.CharField(max_length = 1000)
	twitter_user_location = models.CharField(max_length = 1000)
	twitter_post_created  = models.CharField(max_length = 1000)

class facebook_data(models.Model):
	facebook_id = models.AutoField(primary_key =True)
	request_id = models.CharField(max_length = 300)
	fb_post_id = models.CharField(max_length = 300)
	fb_post_message = models.TextField(max_length = 5000)
	fb_post_from = models.CharField(max_length=300)
	fb_post_share_count = models.CharField(max_length = 300)
	fb_post_like_count = models.CharField(max_length = 300)
	fb_post_comment_count = models.CharField(max_length = 1000)
	fb_post_created_date = models.CharField(max_length = 1000)


class youtube_data(models.Model):
	youtube_id = models.AutoField(primary_key =True)
	request_id = models.CharField(max_length = 300)
	vedio_id = models.CharField(max_length = 300)
	video_title = models.CharField(max_length = 5000)
	video_description = models.CharField(max_length = 5000)
	video_posted_by = models.CharField(max_length = 1000)
	video_like_count = models.CharField(max_length=300)
	video_share_count = models.CharField(max_length=300)
	video_created_date = models.CharField(max_length =300)

