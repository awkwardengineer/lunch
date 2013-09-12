import cgi
import urllib
import webapp2
import jinja2
import os
import datetime
import logging

from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

    
class MenuItem(ndb.Model):
    desc = ndb.StringProperty()
    price = ndb.FloatProperty()
    hasOption = ndb.BooleanProperty()
    option = ndb.StringProperty()
    #when created, MenuItem's designate a parent restaurant as part of their "key"

class Order(ndb.Model):
    item = ndb.KeyProperty()
    customer = ndb.StringProperty()
    option = ndb.StringProperty()
    #when created, Order's designate a parent OrderOfDay as part of their "key"
    
class OrderOfDay(ndb.Model):
    isPicked = ndb.BooleanProperty()
    selectPlace =ndb.KeyProperty()
    date = ndb.DateProperty()
    
class Restaurant(ndb.Model):
    name = ndb.StringProperty()

class CreateData(webapp2.RequestHandler):
    def get(self):
        
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat()) #use the datestring as the key
        
        makeToday = OrderOfDay(isPicked = False, date = now, key = orderDateKey)
        makeToday.put()
        

        presti_key=ndb.Key(Restaurant, 'Presti')
        presti = Restaurant(name = "Presti",  key=presti_key)
        presti.put()
    
        burger = MenuItem(parent = presti_key, price= 4.00, hasOption = True, option = 'Enter rare, medium, or well', desc='Burger')
        fries = MenuItem(parent = presti_key, price= 2.27, hasOption = False, desc='Fries')
        shake = MenuItem(parent = presti_key, price= 4.00, hasOption = False, desc='Shake')
        drink = MenuItem(parent = presti_key, price= 1.00, hasOption = True, desc='Drink', option = 'Coke, Pepsi, or Sprite' )
        salad = MenuItem(parent = presti_key, price= 6.00, hasOption = False, desc='Side Salad')
        
        burger.put()
        fries.put()
        shake.put()
        drink.put()
        salad.put()
        
        
        famous_key=ndb.Key(Restaurant, 'Famous')
        famous = Restaurant(name = "Famous", key=famous_key)
        famous.put()
        
        pizza = MenuItem(parent = famous_key, price= 8.00, hasOption = True, option = 'Enter toppings', desc='Pizza')
        wings = MenuItem(parent = famous_key, price= 7.50, hasOption = True, desc='Wings', option = 'Enter Mild, Medium, or Nuclear')
        nuggets = MenuItem(parent = famous_key, price= 6.00, hasOption = False, desc='Nuggets')
        drink = MenuItem(parent = famous_key, price= 1.00, hasOption = True, desc='Drink', option = 'Coke, Pepsi, or Sprite' )
        salad = MenuItem(parent = famous_key, price= 6.00, hasOption = False, desc='Side Salad')

        pizza.put()
        wings.put()
        nuggets.put()
        drink.put()
        salad.put()
        
        self.response.out.write("Did it, bro")
 
class MainPage(webapp2.RequestHandler):
    def get(self):
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat())
        todaysOrder = orderDateKey.get()
        
        
        if todaysOrder.isPicked is None:
            items = None
            orders = None
        elif not todaysOrder.isPicked:
            items = None
            orders = None
        else:
            restaurant = todaysOrder.selectPlace.get()
            items = MenuItem.query(ancestor=restaurant.key)
            orders = Order.query(ancestor = orderDateKey)
        
        template_values = {"todaysOrder": todaysOrder,
                           "items": items,
                           "orders": orders}
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))



        
    def post(self):
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat())
        todaysOrder = orderDateKey.get()
        
        
        if todaysOrder.isPicked is None:
            choices = None
        elif not todaysOrder.isPicked:
            choices = None
        else:
            restaurant = todaysOrder.selectPlace.get()
            choices = MenuItem.query(ancestor=restaurant.key)
            
            responses = self.request.POST
            
            customer=''
            option = None
            
            for response in responses.iterkeys():
                if (response == 'customer'):
                    customer = responses['customer']
                elif not ("option" in response):
                    itemKey = ndb.Key(urlsafe=response)
                    
                                        
                    myItem = itemKey.get()
                    
                    if myItem.hasOption:
                        option = responses['option'+ response]
                        
                    order = Order(parent=orderDateKey, item=itemKey,option = option, customer=customer)
                    order.put()
                
        self.redirect('/index.html')
    



    
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