from facepy import GraphAPI
import json

page_id = "muhurtmaza"
access_token = "553332024802624|Y7b5gLLrAkNm-uUsNQ15MPyFE5o"

graph = GraphAPI(access_token)

page_date = graph.get(page_id)
#page_date=str(page_date["founded"])

#data = graph.get(page_id + "/feed", paginate=True,since="", page=True, retry=3,fields='message')
data= graph.get(page_id+'/posts', page=True, retry=5)#data = graph.get(page_id + "/feed", paginate=True, page=True, retry=3,limit=1,fields='message,likes,comments,shares,place')

i = 0
#for p in data:
for post in data:
    print 'Downloading posts', i
    for p in post['data']:
      #print p
      for key in p:
        print key
        if 'message' in key:
          print p['message']
          print p['created_time']
          print p['id']
          #print p['likes']
    i += 1
