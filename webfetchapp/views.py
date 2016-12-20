from django.shortcuts import render,redirect,render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import datetime
from django.template import RequestContext
import pdb
from django.db import IntegrityError
from webfetchapp.models import *
import uuid 
# Create your views here.
import MySQLdb
import csv
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from twython import Twython
import json
from facepy import GraphAPI

consumer_key = 'rRw2KAgNUREQu5A925b3kJ3vX'
consumer_secret = 'U4JfeGcVtnMdASuawD0QWJKenrGCt9qHQZ4PXLiJqVqS5M2ONR'
access_key = '2658755796-WmzvZae6XLGAd9zhaflkdPoyeIUX1kvaIOhMqBI'
access_secret = 'OAoAFIIqeleJqrCJZ4zHkAWZpgz57bTV8pHkjZg2y78pL'

@login_required(login_url='/')
def home_page(request):
	user_name = request.session['login_user']
	return render(request,'index.html',{'user_name':user_name})

def show_login_page(request):
	return render(request,'login.html')

def signup_page(request):
	return render(request,'signup.html')

@csrf_exempt
def user_login(request):
	#pdb.set_trace()
	if request.POST:
		email = request.POST.get("email")
		password = request.POST.get("password")
		try:
			user = authenticate(username=email,password=password)
			if user is not None:
				if user.is_active:
					user_obj = customers.objects.get(customer_email = user.username)
					request.session['login_user'] = user_obj.customer_first_name + " " + user_obj.customer_last_name
					request.session['user_id'] = user_obj.customer_id
					login(request,user)
					return redirect('/home/')
				else:
					message = "User is not active"
					return render_to_response('login.html',dict(message=message),context_instance=RequestContext(request))
			else: 
				message = 'Invalid Username or Password'
				return render_to_response('login.html',dict(message=message),context_instance = RequestContext(request))
		except User.DoesNotExist:
			message = 'User Not Exit'
		except MySQLdb.OperationalError, e:
			message = 'Internal Server Error'
		except Exception, e:
			message = 'Internal Server Error'
			return render_to_response('login.html', dict(message=message), context_instance=RequestContext(request))


@csrf_exempt
def user_signup(request):
	if request.method == "POST":
		try:
			customer_obj = customers(
			username  = request.POST.get("email"),
			customer_first_name = request.POST.get("firstName"),
			customer_last_name = request.POST.get("lastName"),
			mobile_number = request.POST.get("mobileNumber"),
			customer_email = request.POST.get("email"),
			customer_created_by = request.POST.get("firstName")+request.POST.get("lastName"))
			customer_obj.save()
			customer_obj.set_password(request.POST.get("confpass"))
			customer_obj.save()
			data = {
	            	'success': 'true',
	            	'message': 'User Signed up successfully'
	        	}
		except IntegrityError, e:
			data = {
            	'success': 'false',
            	'message': 'User already exist'
        	}
 		except Exception, e:
 			data = {
	            'success': 'false',
	            'message': 'Sever Error'
	        }
    	return HttpResponse(json.dumps(data), content_type='application/json')

		
@login_required(login_url='/')
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
			twitter_text  = tweet['text'].encode('ascii', 'ignore'),
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
	elif media =="Youtube":
		response = export_to_csv_youtube(request_id)
		return response		

def export_to_csv_youtube(request_id):
	videos = youtube_data.objects.filter(request_id = request_id)
	response=HttpResponse(content_type='text/csv')
	response['content-Disposition']='attachment; filename ="youtube_data.csv"'
	try:
		writer = csv.writer(response)
		row=['vedio_id','vedio_title','video_description','vedio_comment_count','youtube_user','vedio_created_date']
		writer.writerow(row)
		for video in videos:
			row = [video.vedio_id,video.video_title,video.video_description,video.video_comments_count,video.video_posted_by,video.video_created_date]
			writer.writerow(row)
		return response
	except Exception, e:
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
	#try:
	page_id = keyword
	access_token = "854568807915975|Vzdlg3iLBXkJGvN6t326Zf-rc54"

	graph = GraphAPI(access_token)
	page_date = graph.get(page_id)
	#page_date=str(page_date["founded"])
	data= graph.get(page_id+'/posts', since=from_date,untill=to_date,page=True, retry=5)#data 
	count = 0
	
	for post in data:
		for p in post['data']:
	        #print "post===============",p
			fb_message = ""
			share_count = ""
			for key in p:
				#print "key=====",key
				if 'shares' in key:
					share_count  = p['shares']['count']

				if 'message' in key:
					fb_message = str(p['message'].encode('ascii','ignore'))
			

					
			fb_obj = facebook_data(
			request_id = request_id,
			fb_post_id = p['id'],
			fb_post_message = fb_message,
			fb_post_from = p['from']['name'],
			fb_post_share_count =share_count,
			#fb_post_like_count =
			#fb_post_comment_count =
			fb_post_created_date = p['created_time']
			)
			fb_obj.save()
			comment_count = get_fb_comments(p['id'],graph)
			#print "fb_obj=====",fb_obj
			fb_obj.fb_post_comment_count = comment_count
			fb_obj.save()    

	      	count += 1
	return count,request_id
	# except Exception,e:
	# 	return 0,request_id

def get_fb_comments(post_id,graph):
	comment_count =0
	query = post_id+"?comments.limit(1000){created_time,message,id,from}"
	comment_request = graph.get(query,paginate=True)
	if 'comments' in comment_request.keys():
		if 'data' in comment_request['comments'].keys():
			for data in comment_request['comments']['data']:
				if 'from' in data.keys():
					comments_by = data['from']['name']
				if 'created_time' in data.keys():comment_created_date = data['created_time']
				if 'message' in data.keys():
					comment_message = data['message']

				fb_comment_obj = facebook_comments(
				comment_id = data['id'],
				fb_post_id = post_id,
				comment_message = comment_message,
				#commment_like = ,
				comment_created_by = comments_by,
				comment_created_date=comment_created_date
					)
				fb_comment_obj.save()
				comment_count+=1
          	#print comment_count
    	return comment_count


@login_required(login_url='/')
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
	    			video_title = str(search_result['snippet']['title'].encode('ascii', 'ignore')),
	    			video_url = 'https://www.youtube.com/watch?v='+str(search_result["id"]["videoId"]),
	    			video_description =  str(search_result['snippet']['description'].encode('ascii', 'ignore')),
	    			video_posted_by = str(search_result['snippet']['channelTitle'].encode('ascii', 'ignore')),
	    			video_created_date = search_result['snippet']['publishedAt']
	    			)
	    		youtube_obj.save()
	    		video_comment_threads = get_youtube_comment(youtube, search_result["id"]["videoId"])
	    		youtube_obj.video_comments_count = video_comment_threads
	    		youtube_obj.save()
	    	print "count============",count
	    	return count, request_id
	except HttpError, e:
		return 0, request_id


def get_youtube_comment(youtube, video_id):
	#print "inside get_youtube_comment"
	try:
		count =0
		results = youtube.commentThreads().list(
		part="snippet",
		videoId=video_id,
		textFormat="plainText"
		).execute()
		if results["items"]:
			for item in results["items"]:
				#print "item===========",comment["snippet"]["textDisplay"]
				count =count+1
				comment = item["snippet"]["topLevelComment"]
				youtube_comment_obj = youtube_comments(
				comment_id = comment["id"],
				youtube_vedio_id = video_id,
				comment_message = str(comment["snippet"]["textDisplay"].encode("ascii","ignore")),
				commment_like = comment["snippet"]["likeCount"],
				comment_created_by = str(comment["snippet"]["authorDisplayName"].encode("ascii","ignore")),
				comment_created_date = comment["snippet"]["publishedAt"]
					)
				youtube_comment_obj.save()
				#print "Comment by %s: %s" % (author, text)
		return count
	except Exception,e:
		return 0



@login_required(login_url='/')
def show_video(request):
	#pdb.set_trace()
	request_id = request.GET.get('request_id')
	vedio_title_list =[]
	posts = youtube_data.objects.filter(request_id = request_id)
	for post in posts:
		vedio_comment_list =[]
		vedio_id = post.vedio_id
		video_title = post.video_title
		video_description = post.video_description
		video_posted_by = post.video_posted_by
		video_created_date = post.video_created_date
		video_url = post.video_url
		title_list = {'tweets_text':video_title,'twitter_user':video_posted_by,
		'tweet_created_date':video_created_date,'vedio_id':vedio_id,'vedio_url':video_url}
		vedio_title_list.append(title_list)
		youtube_comment = youtube_comments.objects.filter(youtube_vedio_id =vedio_id)
	
	data= {'success':'true','tweet_list':vedio_title_list,'request_id':request_id,'media':'Youtube'}
	return render(request,'show_youtube_data.html',data)



@login_required(login_url='/')
def show_youtube_comments(request):
	vedio_id = request.GET.get("vedio_id")
	comments_list=[]
	comment_objs = youtube_comments.objects.filter(youtube_vedio_id = vedio_id)
	for comment_obj in comment_objs:
		comments = {'comment_id':comment_obj.comment_id,
				'youtube_vedio_id':	comment_obj.youtube_vedio_id,
				'comment_message':comment_obj.comment_message,
				'commment_like':comment_obj.commment_like,
				'comment_created_by':comment_obj.comment_created_by,
				'comment_created_date':comment_obj.comment_created_date}
		comments_list.append(comments)
	data = {'success':'true','comments_list':comments_list}
	return render(request,'show_comments.html',data)