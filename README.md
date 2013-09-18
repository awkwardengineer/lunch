lunch
=====
The Lunch Engine system is a small web app for organizing lunch menus and orders. The app is deployed to Google's [App Engine](https://developers.google.com/appengine/). The backend uses the appengine Webapp2 framework, is written in Python, and uses App Engine's built in database system.

The front end appearance uses .css taken fron [Bootstrap](http://getbootstrap.com/).

Rather than build out an interface for uploading / editing menu's, the system uses [Tabletop.js](https://github.com/jsoma/tabletop) to parse a Google Spreadsheet where all the menu entries are stored. The resulting JSON object is then POSTed to the server and written to the App Engine database.
