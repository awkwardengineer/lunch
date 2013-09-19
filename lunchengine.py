import cgi
import urllib
import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

    
class MenuItem(ndb.Model):
    desc = ndb.StringProperty()
    price = ndb.FloatProperty()
    hasOption = ndb.BooleanProperty()
    option = ndb.StringProperty()
    rowNumber = ndb.IntegerProperty()
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
                
        self.response.out.write("Did it, bro")
 
class MainPage(webapp2.RequestHandler):
    def get(self):
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat())
        todaysOrder = orderDateKey.get()
        
        if todaysOrder == None:
            todaysOrder = OrderOfDay(isPicked = False, date = now, key = orderDateKey)
            todaysOrder.put()
          
      #  todaysOrder = orderDateKey.get()  
        
        if todaysOrder == None:  #if it doesn't exist
            items = None
            orders = None
        elif not todaysOrder.isPicked:  #if it doesn't exist and it is false
            items = None
            orders = None
        else:
            restaurant = todaysOrder.selectPlace.get()
            items = MenuItem.query(ancestor=restaurant.key).order(MenuItem.rowNumber)
            orders = Order.query(ancestor = orderDateKey).order(Order.customer)
            
            if orders.count()==0:
                orders = None
        
        template_values = {"todaysOrder": todaysOrder,
                           "items": items,
                           "orders": orders,
                           "date": now.strftime('%b %d, %Y') }
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))



        
    def post(self):
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat())
        todaysOrder = orderDateKey.get()
        
        
        if todaysOrder == None:
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
                    else:
                        option = None
                        
                    order = Order(parent=orderDateKey, item=itemKey,option = option, customer=customer)
                    order.put()
                
        self.redirect('/index.html')
    



    
class AdminPage(webapp2.RequestHandler):
    def get(self):
    
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat())
        todaysOrder = orderDateKey.get()
        
        if todaysOrder == None:
            todaysOrder = OrderOfDay(isPicked = False, date = now, key = orderDateKey)
            todaysOrder.put()
          
      #  todaysOrder = orderDateKey.get()
        if todaysOrder.isPicked is None:
            orders = None
        elif not todaysOrder.isPicked:
            orders = None
        else:
            orders = Order.query(ancestor = orderDateKey).order(Order.customer)
            if orders.count()==0:
                orders = None;

        
        restaurants = Restaurant.query()
                
      
        template_values = {"restaurants":restaurants,
                           "todaysOrder":todaysOrder,
                           "orders":orders,
                           "date": now.strftime('%b %d, %Y') }
        
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))
    
    def post(self):
        now = datetime.date.today()
        restaurant = self.request.POST['restaurant']
        
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat())
        todaysOrder= orderDateKey.get()
        
        if restaurant == "Choose a restaurant":
            self.redirect('/admin.html')
        elif restaurant == "Clear restaurant (and reset orders)":
            todaysOrder.isPicked=False
            todaysOrder.put()
            
            orders = Order.query(ancestor = orderDateKey)
            keys=[]
            for order in orders:
              keys.append(order.key)
            ndb.delete_multi(keys)
            
        else:
            todaysOrder.isPicked = True
            todaysOrder.selectPlace = ndb.Key(Restaurant, restaurant)
            todaysOrder.put()
        
        self.redirect('/admin.html')
        
class ImportData(webapp2.RequestHandler):
    def post(self):
        
        now = datetime.date.today()
        orderDateKey = ndb.Key(OrderOfDay, now.isoformat())
        todaysOrder= orderDateKey.get()
        todaysOrder.isPicked=False
        todaysOrder.put()
        
        orders = Order.query(ancestor = orderDateKey)
        keys=[]
        for order in orders:
            keys.append(order.key)
            ndb.delete_multi(keys)
    
    
        items = MenuItem.query()
        keys=[]
        for item in items:
            keys.append(item.key)
            ndb.delete_multi(keys)
    
        data=self.request.POST['jsonData']
        udata = json.loads(urllib.unquote(data).decode('utf8'))
        
        point = 0
        
        for i in udata:
        
            restaurantKey = ndb.Key(Restaurant, udata[point]['restaurant'] )
            
            restaurant = Restaurant(name=udata[point]['restaurant'], key=restaurantKey)
            restaurant.put()
            
            hasOption=True
            
            if udata[point]['specialrequest']=="":
                udata[point]['specialrequest']=None
                hasOption = False
            
            item = MenuItem(parent = restaurantKey,desc = udata[point]['item'], price = float(udata[point]['price']), hasOption = hasOption, option = udata[point]['specialrequest'], rowNumber = udata[point]['rowNumber'])
            
            item.put()
            
            point = point + 1
            
            
        self.redirect('/admin.html')

app = webapp2.WSGIApplication([('/',MainPage),
                               ('/index.html',MainPage),
                               ('/admin.html',AdminPage),
                               ('/data.html', CreateData),
                               ('/importdata.html', ImportData)],
                              debug=True)