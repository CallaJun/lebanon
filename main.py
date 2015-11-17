import webapp2
import os
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images
from PIL import Image
import urllib
import cStringIO
from cStringIO import StringIO

class Photo(ndb.Model):
    title = ndb.StringProperty()
    full_size_image = ndb.BlobProperty()
    lebanon = blobstore.BlobReferenceProperty()

class PhotoUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload_photo')
        self.response.out.write('<html><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css"><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write('''Upload File: <input type="file" name="file"><br> <button type="submit" class="btn btn-default">Submit</button> </form></body></html>''')

class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]

            #url = str(images.get_serving_url(upload.key()))
            url = cStringIO.StringIO(urllib.urlopen(
                'https://cdn.psychologytoday.com/sites/default/files/blogs/38/2008/12/2598-75772.jpg').read())
            """img = images.Image(blob_key=photo_key)
                                                blob_info = blobstore.BlobInfo.get(photo_key)
                                                im = Image.open(blob_info.open()).convert('L')"""
            im = Image.open(url).convert('L')
            
            newimage = StringIO()
            im.save(newimage, 'png')
            image_data = newimage.getvalue()
            #write to a file
            image_file = files.blobstore.create(mime_type='image/png')
            with files.open(image_file, 'a') as f:
              f.write(image_data)
            files.finalize(image_file)
            #put into blobstore
            photo_item = Photo(lebanon = files.blobstore.get_blob_key(image_file))
            photo_item.put()
            
            print "ice cream"
            print image.get_serving_url(files.blobstore.get_blob_key(image_file))
            #print str(files.blobstore.get_blob_key(image_file))
            self.redirect('/view_photo/%s' % upload.key())
        except:
            self.error(500)

class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            
            url = cStringIO.StringIO(urllib.urlopen(
                'https://cdn.psychologytoday.com/sites/default/files/blogs/38/2008/12/2598-75772.jpg').read())
            image = Image.open(url).convert('L')
            newimage = StringIO()
            image.save(newimage,'png')
            image_data = newimage.getvalue()
            image.close()
            
            #self.response.out.write(url)
            #write image_data to a file in blobstore
            self.send_blob(photo_key)

app = webapp2.WSGIApplication([('/', PhotoUploadFormHandler),
                               ('/upload_photo', PhotoUploadHandler),
                               ('/view_photo/([^/]+)?', ViewPhotoHandler)
                              ], debug=True)