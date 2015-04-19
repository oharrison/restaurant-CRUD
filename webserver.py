#!/usr/bin/env python

from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/")
def index():
	# Output all restaurants
	restaurants = session.query(Restaurant).all()
	return render_template("restaurants.html", title = "Restaurants", restaurants = restaurants)

@app.route("/restaurants/new/", methods=["GET", "POST"])
def newRestaurant():
	if request.method == "POST":
		# Create and save new Restaurant with name from form
		restaurant = Restaurant(name = request.form["restaurant-name"])
		session.add(restaurant)
		session.commit()
		# Redirect to homepage
		return redirect(url_for('index'))
	else:
		return render_template("new-restaurants.html", title="Add A New Restaurant")

@app.route("/restaurants/<int:restaurant_id>/edit/", methods=["GET", "POST"])
def editRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == "POST":
		# Edit restaurant
		if request.form["restaurant-name"]:
			restaurant.name = request.form["restaurant-name"]
		session.add(restaurant)
		session.commit()
		# Redirect to homepage
		return redirect(url_for('index'))
	else:
		return render_template("edit-restaurants.html", title="Edit Restaurant", restaurant = restaurant)

@app.route("/restaurants/<int:restaurant_id>/delete/", methods=["GET", "POST"])
def deleteRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == "POST":
		# Delete restaurant
		session.delete(restaurant)
		session.commit()
		# Redirect to homepage
		return redirect(url_for('index'))
	else:
		return render_template("delete-restaurants.html", title="Delete Restaurant", restaurant = restaurant)

@app.route("/restaurants/<int:restaurant_id>/menu/")
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	menu_items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return render_template("menus.html", title="%s Menu" % restaurant.name, items = menu_items, restaurant = restaurant)

@app.route("/restaurants/<int:restaurant_id>/menu/new/", methods=["GET", "POST"])
def newMenuItem(restaurant_id):
	if request.method == "POST":
		# Create and save new menu item
		new_menu = MenuItem(name = request.form["menu-name"], description = request.form["menu-description"], 
							price = request.form["menu-price"], restaurant_id = restaurant_id)
		session.add(new_menu)
		session.commit()
		# Redirect to parent menu page	
		return redirect(url_for("restaurantMenu", restaurant_id = restaurant_id))
	else:
		return render_template("new-menus.html", title="Add a New Menu", restaurant_id = restaurant_id)

@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/", methods=["GET", "POST"])
def editMenuItem(restaurant_id, menu_id):
	menu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id = menu_id).one()
	# Edit menu item
	if request.method == "POST":
		if request.form["menu-name"]:
			menu.name = request.form["menu-name"]
		if request.form["menu-description"]:
			menu.description = request.form["menu-description"]
		if request.form["menu-price"]:
			menu.price = request.form["menu-price"]
		session.add(menu)
		session.commit()
		#Redirect to parent menu page
		return redirect(url_for("restaurantMenu", restaurant_id = restaurant_id))
	else:
		return render_template("edit-menus.html", title="Edit Menu", menu = menu, restaurant_id = restaurant_id)

@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/", methods=["GET", "POST"])
def deleteMenuItem(restaurant_id, menu_id):
	menu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id = menu_id).one()
	if request.method == "POST":
		# Delete menu item
		session.delete(menu)
		session.commit()
		# Redirect to parent menu page
		return redirect(url_for("restaurantMenu", restaurant_id = restaurant_id))
	else:
		return render_template("delete-menus.html", title="Delete Menu", menu = menu, restaurant_id = restaurant_id)

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
