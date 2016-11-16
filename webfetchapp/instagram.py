#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyAYE8jo-syJIDl6KBzqPGgtC9OMxzEpPtU"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def get_comment_threads(youtube, video_id):
  try:
	  results = youtube.commentThreads().list(
	    part="snippet",
	    videoId=video_id,
	    textFormat="plainText"
	  ).execute()
	  if results["items"]:
		  for item in results["items"]:
		  	print "item============",item["snippet"]["topLevelComment"]
		  	comment = item["snippet"]["topLevelComment"]
		  	author = comment["snippet"]["authorDisplayName"]
		  	text = comment["snippet"]["textDisplay"]
        publishedAt = comment["snippet"]["publishedAt"]
        
		  	print "Comment by %s: %s" % (author, text)
		  return results["items"]

  except Exception,e:
  	  pass


def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=options.q,
    part="id,snippet",
    maxResults=options.max_results
  ).execute()

  videos = []
  channels = []
  playlists = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                 search_result["id"]["videoId"]))
      video_comment_threads = get_comment_threads(youtube, search_result["id"]["videoId"])

    elif search_result["id"]["kind"] == "youtube#channel":
      channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                   search_result["id"]["channelId"]))
    elif search_result["id"]["kind"] == "youtube#playlist":
      playlists.append("%s (%s)" % (search_result["snippet"]["title"],
                                    search_result["id"]["playlistId"]))


  print "Videos:\n", "\n".join(videos), "\n"
  print "Channels:\n", "\n".join(channels), "\n"
  print "Playlists:\n", "\n".join(playlists), "\n"


if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default="amitabh")
  argparser.add_argument("--max-results", help="Max results", default=50)
  args = argparser.parse_args()

  try:
    youtube_search(args)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)




    # {u'snippet': {u'thumbnails': {u'default': {u'url': u'https://i.ytimg.com/vi/yflVgnOxNiI/default.jpg', u'width': 120, u'height': 90}, u'high': {u'url': u'https://i.ytimg.com/vi/yflVgnOxNiI/hqdefault.jpg', u'width': 480, u'height': 360}, u'medium': {u'url': u'https://i.ytimg.com/vi/yflVgnOxNiI/mqdefault.jpg', u'width': 320, u'height': 180}}, u'title': u'Shani Grah Shanti Maha Puja - 1 March 2014 at New Delhi - Ph: 9818144257', u'channelId': u'UCDEy8JwgYV2YwU_YyFb2weg', u'publishedAt': u'2014-01-12T08:39:42.000Z', u'liveBroadcastContent': u'none', u'channelTitle': u'Guru Rajneesh Rishi Ji', u'description': u'Special Lord Shani Dev Puja by His Holiness Guru Rajneesh Rishi.'}, u'kind': u'youtube#searchResult', u'etag': u'"sZ5p5Mo8dPpfIzLYQBF8QIQJym0/yqhnCwhbKg2CFkBiA3Xpm1Aa7vs"', u'id': {u'kind': u'youtube#video', u'videoId': u'yflVgnOxNiI'}}