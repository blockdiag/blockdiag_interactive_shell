from google.appengine.ext import db

class Picture(db.Model):
    diagram = db.TextProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
