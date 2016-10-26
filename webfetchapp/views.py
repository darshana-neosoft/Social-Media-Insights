from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import datetime
import pdb
from webfetchapp.models import *
import uuid 
# Create your views here.
import csv

from twython import Twython
import json
from facepy import GraphAPI

consumer_key = 'rRw2KAgNUREQu5A925b3kJ3vX'
consumer_secret = 'U4JfeGcVtnMdASuawD0QWJKenrGCt9qHQZ4PXLiJqVqS5M2ONR'
access_key = '2658755796-WmzvZae6XLGAd9zhaflkdPoyeIUX1kvaIOhMqBI'
access_secret = 'OAoAFIIqeleJqrCJZ4zHkAWZpgz57bTV8pHkjZg2y78pL'


def home_page(request):
	return render(request,'index.html')

@csrf_exempt
def get_data(request):
	#pdb.set_trace()
	if request.method == "POST":
		print "Hiii"
		media= request.POST.get('media')
		from_date = request.POST.get('from_date')
		to_date = request.POST.get('to_date')
		keyword = request.POST.get('keyword')
		#keyword = "#amitabh"
		twitter_count = 0
		if media=="Twitter":
			twitter_count,request_id = get_twitter_data(from_date,to_date,keyword)
			data = {'success':'true','data':twitter_count,'request_id':str(request_id),'media':media}
			return HttpResponse(json.dumps(data), content_type='application/json')

		elif media=="Facebook":
			fb_count,request_id = get_fb_data(from_date,to_date,keyword)
			data = {'success':'true','data':fb_count,'request_id':str(request_id),'media':media}
			print "Data=========",data
			return HttpResponse(json.dumps(data), content_type='application/json')

		elif media=="Youtube":
			youtube_count,request_id = get_youtube_data(from_date,to_date,keyword)
			data = {'success':'true','data':youtube_count,'request_id':str(request_id),'media':media}
			print "Data=========",data
			return HttpResponse(json.dumps(data), content_type='application/json')



def get_twitter_data(from_date,to_date,keyword):
	#pdb.set_trace()
	TWITTER_APP_KEY = consumer_key
	TWITTER_APP_KEY_SECRET = consumer_secret
	TWITTER_ACCESS_TOKEN = access_key
	TWITTER_ACCESS_TOKEN_SECRET = access_secret

	t = Twython(app_key=TWITTER_APP_KEY, 
	            app_secret=TWITTER_APP_KEY_SECRET, 
	            oauth_token=TWITTER_ACCESS_TOKEN, 
	            oauth_token_secret=TWITTER_ACCESS_TOKEN_SECRET)

	search = t.search(q=keyword,since=from_date,until=to_date,count=5000)
	tweets = search['statuses']
	count=0
	request_id = uuid.uuid4()
	for tweet in tweets:
	    count+=1
	    twitter_obj = twitter_data(
	    	request_id = request_id,
			twitter_text  = tweet['text'],
			twitter_user_screen_name  = tweet['user']['screen_name'], 
			twitter_favourite_count   = tweet['favorite_count'],
			twitter_retwited_count    = tweet['retweet_count'],
			twitter_user_language     = tweet['user']['lang'],
			twitter_post_created      = tweet['created_at'],
			)
	    twitter_obj.save()
	    request_id = twitter_obj.request_id
	    #print "object saved",count
	return count,request_id


def show_tweets(request):
	request_id = request.GET.get('request_id')
	tweet_list =[]
	tweets = twitter_data.objects.filter(request_id = request_id)
	for tweet in tweets:
		tweets_text = tweet.twitter_text
		twitter_user = tweet.twitter_user_screen_name
		tweet_created_date = tweet.twitter_post_created
		tweet_data = {'tweets_text':tweets_text,'twitter_user':twitter_user,
		'tweet_created_date':tweet_created_date}
		tweet_list.append(tweet_data)
		data= {'success':'true','tweet_list':tweet_list,'request_id':request_id,'media':'Twitter'}
	return render(request,'show_data.html',data)	


def export_to_csv(request):
	media = request.GET.get('media')
	request_id = request.GET.get('request_id')
	if media == "Twitter":
		response = export_to_csv_twitter(request_id)
		return response
	elif media == "Facebook":
		response = export_to_csv_fb(request_id)
		return response


def export_to_csv_twitter(request_id):
	#pdb.set_trace()
	tweets = twitter_data.objects.filter(request_id = request_id)
	response =HttpResponse(content_type='text/csv')
	response['content-Disposition']='attachment; filename ="twitter_data.csv"'
	try:
		writer = csv.writer(response)
		row =['tweets_text','twitter_user','tweet_created_date','twitter_favourite_count','twitter_retwited_count','twitter_user_language','twitter_user_location']
		writer.writerow(row)
		for tweet in tweets:
			text = tweet.twitter_text.encode('ascii', 'ignore')
			row =[text,tweet.twitter_user_screen_name,tweet.twitter_post_created,tweet.twitter_favourite_count,tweet.twitter_retwited_count,tweet.twitter_user_language,tweet.twitter_user_location]

			writer.writerow(row)
		return response
	except Exception, e:
		return response
			

def export_to_csv_fb(request_id):
	#pdb.set_trace()
	posts = facebook_data.objects.filter(request_id = request_id)
	response =HttpResponse(content_type='text/csv')
	response['content-Disposition']='attachment; filename ="facebook_data.csv"'
	try:
		writer = csv.writer(response)
		row =['fb_post_id','fb_post_message','fb_post_from','fb_post_share_count','fb_post_created_date']
		writer.writerow(row)
		for post in posts:
			text = post.fb_post_message.encode('ascii', 'ignore')
			row =[post.fb_post_id,text,post.fb_post_from,post.fb_post_share_count,post.fb_post_created_date]

			writer.writerow(row)
		return response
	except Exception, e:
		return response



def get_fb_data(from_date,to_date,keyword):
	#pdb.set_trace()
	request_id = uuid.uuid4()
	try:
		page_id = keyword
		access_token = "854568807915975|Vzdlg3iLBXkJGvN6t326Zf-rc54"

		graph = GraphAPI(access_token)
		page_date = graph.get(page_id)
		#page_date=str(page_date["founded"])
		data= graph.get(page_id+'/posts', since=from_date,untill=to_date,page=True, retry=5)#data 
		count = 0
		
		for post in data:
		    for p in post['data']:
		      for key in p:
		        if 'message' in key:
		        	fb_obj = facebook_data(
		        		request_id = request_id,
						fb_post_id = p['id'],
						fb_post_message = p['message'],
						fb_post_from = p['from']['name'],
						#fb_post_share_count =
						#fb_post_like_count =
						#fb_post_comment_count =
						fb_post_created_date = p['created_time']
		        		)
		        	fb_obj.save()
		    count += 1
		return count,request_id
	except Exception,e:
		return 0,request_id
	
def show_post(request):
	#pdb.set_trace()
	request_id = request.GET.get('request_id')
	post_list =[]
	posts = facebook_data.objects.filter(request_id = request_id)
	for post in posts:
		fb_post_message = post.fb_post_message
		fb_post_from = post.fb_post_from
		fb_post_created_date = post.fb_post_created_date

		post_data = {'tweets_text':fb_post_message,'twitter_user':fb_post_from,
		'tweet_created_date':fb_post_created_date}
		post_list.append(post_data)
		data= {'success':'true','tweet_list':post_list,'request_id':request_id,'media':'Facebook'}
	return render(request,'show_data.html',data)



def get_youtube_data(from_date,to_date,keyword):
	try:
		DEVELOPER_KEY = "AIzaSyAYE8jo-syJIDl6KBzqPGgtC9OMxzEpPtU"
		YOUTUBE_API_SERVICE_NAME = "youtube"
		YOUTUBE_API_VERSION = "v3"
		youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
		videos = []
		from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%SZ")
		to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%SZ")
		search_response = youtube.search().list(
	    	q=keyword,
	    	publishedAfter =from_date,
	    	publishedBefore =to_date,
	    	part="id,snippet",
	    	maxResults=50
	    	).execute()
		request_id = uuid.uuid4()
		count=0
		for search_result in search_response.get("items", []):
			
			if search_result["id"]["kind"] == "youtube#video":
				count =count+1
				youtube_obj = youtube_data(
	    			request_id = request_id,
	    			vedio_id = search_result["id"]["videoId"],
	    			video_title = search_result['snippet']['title'],
	    			video_description =  search_result['snippet']['description'],
	    			video_posted_by = search_result['snippet']['channelTitle'],
	    			video_created_date = search_result['snippet']['publishedAt']
	    			)
	    		youtube_obj.save()
	    	return count, request_id
	except HttpError, e:
		return 0, request_id


def show_video(request):
	#pdb.set_trace()
	request_id = request.GET.get('request_id')
	vedio_title_list =[]
	posts = youtube_data.objects.filter(request_id = request_id)
	for post in posts:
		vedio_id = post.vedio_id
		video_title = post.video_title
		video_description = post.video_description
		video_posted_by = post.video_posted_by
		video_created_date = post.video_created_date

		title_list = {'tweets_text':video_title,'twitter_user':video_posted_by,
		'tweet_created_date':video_created_date}
		vedio_title_list.append(title_list)
		data= {'success':'true','tweet_list':vedio_title_list,'request_id':request_id,'media':'Youtube'}
	return render(request,'show_data.html',data)

