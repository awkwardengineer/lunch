import cgi
import urllib
import webapp2
import jinja2
import os

from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

    
class MenuItem(ndb.Model):
    desc = ndb.StringProperty()
    price = ndb.FloatProperty()
    hasOption = ndb.BooleanProperty()
    option = ndb.StringProperty()
    
class OrderOfDay(ndb.Model):
    isPicked = ndb.BooleanProperty()
    selectPlace =ndb.KeyProperty()
    orders = ndb.StringProperty(MenuItem, repeated=True)
    
class Restaurant(ndb.Model):
    menu = ndb.StructuredProperty(MenuItem, repeated=True)
    name = ndb.StringProperty

class CreateData(webapp2.RequestHandler):
    def get(self):
    
        
    
        burger = MenuItem(parent = ndb.Key('Restaurants','Famous'), price= 4.00, hasOption = True, option = 'Enter rare, medium, or well', desc='Burger')
        fries = MenuItem(parent = ndb.Key('Restaurants','Famous'), price= 2.27, hasOption = False, desc='Fries')
        shake = MenuItem(parent = ndb.Key('Restaurants','Famous'), price= 4.00, hasOption = False, desc='Shake')
        drink = MenuItem(parent = ndb.Key('Restaurants','Famous'), price= 1.00, hasOption = True, desc='Drink', option = 'Coke, Pepsi, or Sprite' )
        salad = MenuItem(parent = ndb.Key('Restaurants','Famous'), price= 6.00, hasOption = False, desc='Side Salad')

        burger.put()
        fries.put()
        shake.put()
        drink.put()
        salad.put()
        
        pizza = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 8.00, hasOption = True, option = 'Enter toppings', desc='Pizza')
        wings = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 7.50, hasOption = True, desc='Wings', option = 'Enter Mild, Medium, or Nuclear')
        nuggets = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 6.00, hasOption = False, desc='Nuggets')
        drink = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 1.00, hasOption = True, desc='Drink', option = 'Coke, Pepsi, or Sprite' )
        salad = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 6.00, hasOption = False, desc='Side Salad')

        pizza.put()
        wings.put()
        nuggets.put()
        drink.put()
        salad.put()
        
        self.response.out.write("Did it, bro")
    
    
 
class MainPage(webapp2.RequestHandler):
    def get(self):
    
        restaurant=self.request.get('menu')
        ancestor_key = ndb.Key('Restaurants',restaurant)
      
        items = MenuItem.query(ancestor = ancestor_key)
        
        #for item in items:
        #  self.response.out.write('%s <br>' % cgi.escape(item.desc))
        
        template_values = {"items": items}
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        
class AdminPage(webapp2.RequestHandler):
    def get(self):
      
        template_values = {}
        
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))
        

app = webapp2.WSGIApplication([('/',MainPage),
                               ('/index.html',MainPage),
                               ('/admin.html',AdminPage),
                               ('/data.html', CreateData)],
                              debug=True)