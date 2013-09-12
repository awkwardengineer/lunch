import cgi
import urllib
import webapp2
import jinja2
import os
import datetime

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
    orders = ndb.StructuredProperty(MenuItem, repeated=True)
    date = ndb.DateProperty()
    
class Restaurant(ndb.Model):
    menu = ndb.StructuredProperty(MenuItem, repeated=True)
    name = ndb.StringProperty()

class CreateData(webapp2.RequestHandler):
    def get(self):
        
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat()) #use the datestring as the key
        
        makeToday = OrderOfDay(isPicked = False, date = now, key = orderDateKey)
        makeToday.put()
        

        presti_key=ndb.Key(Restaurant, 'Presti')
    
        burger = MenuItem(price= 4.00, hasOption = True, option = 'Enter rare, medium, or well', desc='Burger')
        fries = MenuItem(price= 2.27, hasOption = False, desc='Fries')
        shake = MenuItem(price= 4.00, hasOption = False, desc='Shake')
        drink = MenuItem(price= 1.00, hasOption = True, desc='Drink', option = 'Coke, Pepsi, or Sprite' )
        salad = MenuItem(price= 6.00, hasOption = False, desc='Side Salad')
        
        presti = Restaurant(name = "Presti", menu = [burger,fries,shake,drink,salad], key=presti_key)
        presti.put()
        
        famous_key=ndb.Key(Restaurant, 'Famous')
        
        pizza = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 8.00, hasOption = True, option = 'Enter toppings', desc='Pizza')
        wings = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 7.50, hasOption = True, desc='Wings', option = 'Enter Mild, Medium, or Nuclear')
        nuggets = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 6.00, hasOption = False, desc='Nuggets')
        drink = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 1.00, hasOption = True, desc='Drink', option = 'Coke, Pepsi, or Sprite' )
        salad = MenuItem(parent = ndb.Key('Restaurants','Presti'), price= 6.00, hasOption = False, desc='Side Salad')

        famous = Restaurant(name = "Famous", menu = [pizza,wings,nuggets,drink,salad], key=famous_key)
        famous.put()
        
        self.response.out.write("Did it, bro")
    
    
 
class MainPage(webapp2.RequestHandler):
    def get(self):
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat())
        todaysOrder = orderDateKey.get()
        
        
        if todaysOrder is None:
            items = None
        elif not todaysOrder:
            items = None
        else:
            restaurant = todaysOrder.selectPlace.get()
            items = restaurant.menu
        
        template_values = {"todaysOrder": todaysOrder,
                           "items": items}
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        
class AdminPage(webapp2.RequestHandler):
    def get(self):
    
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat()) #use the datestring as the key
        
        if not orderDateKey.get():
          makeToday = OrderOfDay(isPicked = False, date = now, key = orderDateKey)
          makeToday.put()
          
        checkToday = orderDateKey.get()
        
        restaurants = Restaurant.query()
                
      
        template_values = {"restaurants":restaurants,
                           "todaysOrder":checkToday,
                           "date": now.strftime('%b %d, %Y') }
        
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))
    
    def post(self):
        now = datetime.date.today()
        restaurant = self.request.POST['restaurant']
        
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat())
        todaysOrder= orderDateKey.get()
        
        if restaurant == "Clear restaurant (and reset orders)":
            todaysOrder.isPicked=False
            todaysOrder.put()
        else:
            todaysOrder.isPicked = True
            todaysOrder.selectPlace = ndb.Key(Restaurant, restaurant)
            todaysOrder.put()
        
        self.redirect('/admin.html')
        
  

app = webapp2.WSGIApplication([('/',MainPage),
                               ('/index.html',MainPage),
                               ('/admin.html',AdminPage),
                               ('/data.html', CreateData)],
                              debug=True)