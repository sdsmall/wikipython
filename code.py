import os
import time
import webapp2
import cgi
import sys
sys.path.append("C:\Python27\Lib\site-packages")
import wikipedia
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb


def render_template(handler, templatename, templatevalues):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)

def tag_string_to_array(str):
  tag_array = []
  hashtag_found = False
  curr = ""
  for c in str:
    if c=='#':
      hashtag_found = True  
    elif c==' ':
      length = curr.__len__()
      if length>0:
        tag_array.append(curr)
        curr = ""
      hashtag_found = False
    elif hashtag_found == True:
      curr += c
  if curr.__len__()>0 and hashtag_found==True:
    tag_array.append(curr)
  return tag_array

class MessagePost(ndb.Model):
  title = ndb.StringProperty()
  url = ndb.StringProperty()
  comments = ndb.StringProperty()
  user = ndb.StringProperty()
  tags = ndb.StringProperty(repeated=True)
  time = ndb.IntegerProperty()

class SavePost(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if user:
      post = MessagePost()
      post.title = self.request.get('sharetitle')
      post.url = self.request.get('shareurl')
      post.comments = self.request.get('comments')
      post.user = user.nickname()
      tag_string = self.request.get('tags')
      tag_array = tag_string_to_array(tag_string)
      post.tags = tag_array
      post.time = int(time.time())
      post.put()
      self.redirect('/')
    else:
      #There is no user logged in
      s = 'You are not logged in.'
      render_template(self, 'index.html', {
        "username": s
        })

    


class MainPage(webapp2.RequestHandler):
  def get(self):
    
    user = users.get_current_user()
    queryString = ''
    if user:
      query = MessagePost.query(MessagePost.user==user.nickname())
      #query.order('-time')
      for post in query.iter():
        queryString+="<p>"
        queryString+="<a href="
        queryString+= post.url
        queryString+=" target=\"_blank\""
        queryString+=">"
        queryString+= post.title
        queryString+="</a><br>"
        queryString+="Comments: "
        queryString+=post.comments
        queryString+="<br>"
        queryString+="Tags: "
        for tag in post.tags:
          queryString+=" <a href="
          queryString+= "\""
          queryString+="#"
          queryString+="\""
          queryString+=">"
          queryString+= "#"
          queryString+= tag
          queryString+="</a>"
        queryString+="<br>"
        #queryString+=post.tags
        queryString+="<br>"
        queryString+="</p>"

      #The user is already logged in
      render_template(self, 'index.html', {
        "username": user.nickname(),
        "queryString": queryString
        })
    else:
      #There is no user logged in
      s = 'You are not logged in.'
      render_template(self, 'index.html', {
        "username": s,
        "queryString": queryString
        })

class RandomArticle(webapp2.RequestHandler):
  def post(self):
    error = 1
    while (error == 1):
      rand_title = wikipedia.random(pages=1)
      try:
        article = wikipedia.page(rand_title)
        error = 0
      except wikipedia.exceptions.DisambiguationError as e:
        error = 1

    htmlcontent = article.html()
    url = article.url
    render_template(self, 'randomarticle.html', {
      "title": rand_title,
      "content": htmlcontent,
      "url": url
      })

class LogIn(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      #The user is already logged in
      msg = "You're alreay logged in, bro!"
      render_template(self, 'loginerror.html', {
        "message": msg
        })
    else:
      #The user has not logged in
      url = users.create_login_url()
      msg = "Click that ^ sweet farm to log in!"
      render_template(self, 'loginprompt.html', {
        "url": url,
        "message": msg
        })

class LogOut(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      #The user is logged in
      url = users.create_logout_url('/')
      msg = "Click that ^ sweet farm to log out!"
      render_template(self, 'loginprompt.html', {
        "url": url,
        "message": msg
        })
    else:
      #Nobody is logged in
      msg = "You aren't even logged in, bro!"
      render_template(self, 'loginerror.html', {
        "message": msg
        })

class ShareArticle(webapp2.RequestHandler):
  def post(self):
    title = cgi.escape(self.request.get('sharetitle'))
    url = cgi.escape(self.request.get('shareurl'))

    render_template(self, 'sharearticle.html', {
      "url": url,
      "title": title
      })

class Search(webapp2.RequestHandler):
  def get(self):
    render_template(self, 'search.html', {})

class SearchResult(webapp2.RequestHandler):
  def post(self):
    render_template(self, 'searchresult.html', {})

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/random', RandomArticle),
  ('/login', LogIn),
  ('/logout', LogOut),
  ('/share', ShareArticle),
  ('/save', SavePost),
  ('/search', Search),
  ('/searchresult', SearchResult)
])