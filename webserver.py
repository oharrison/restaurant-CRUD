#!/usr/bin/env python

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



""" JSON ENDPOINTS """

# JSON endpoint for Restaurants
@app.route("/restaurants/JSON")
def restaurantsJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])

# JSON endpoint for Menus
@app.route("/restaurants/<int:restaurant_id>/menu/JSON")
def restaurantsMenuJSON(restaurant_id):
	menus = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return jsonify(Menus=[menu.serialize for menu in menus])

# JSON endpoint for menu items
@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON")
def restaurantsMenuItemJSON(restaurant_id, menu_id):
	menu = session.query(MenuItem).filter_by(id = menu_id).one()
	return jsonify(MenuItem=[menu.serialize])


""" VIEWS/ROUTES """

# Display Restaurants
@app.route("/")
@app.route("/restaurants/")
def index():
	restaurants = session.query(Restaurant).all()
	return render_template("restaurants.html", title = "Restaurants", restaurants = restaurants)

# Add a new Restaurant
@app.route("/restaurants/new/", methods=["GET", "POST"])
def newRestaurant():
	if request.method == "POST":
		restaurant = Restaurant(name = request.form["restaurant-name"], thumbnail_url = request.form["restaurant-image-url"])
		if request.form["restaurant-description"]:
			restaurant.description = request.form["restaurant-description"]
		session.add(restaurant)
		session.commit()
		flash("New Restaurant Added")
		return redirect(url_for('index'))
	else:
		return render_template("new-restaurants.html", title="Add A New Restaurant")

# Edit an existing Restaurant
@app.route("/restaurants/<int:restaurant_id>/edit/", methods=["GET", "POST"])
def editRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == "POST":
		if request.form["restaurant-name"]:
			restaurant.name = request.form["restaurant-name"]
		if request.form["restaurant-description"]:
			restaurant.description = request.form["restaurant-description"]
		if request.form["restaurant-image-url"]:
			restaurant.thumbnail_url = request.form["restaurant-image-url"]
		session.add(restaurant)
		session.commit()
		flash("Restaurant Successfully Edited")
		return redirect(url_for('index'))
	else:
		return render_template("edit-restaurants.html", title="Edit Restaurant", restaurant = restaurant)

# Delete an existing Restaurant
@app.route("/restaurants/<int:restaurant_id>/delete/", methods=["GET", "POST"])
def deleteRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == "POST":
		menu_items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
		for item in menu_items:
			session.delete(item)
		session.delete(restaurant)
		session.commit()
		flash("Restaurant Successfully Deleted")
		return redirect(url_for('index'))
	else:
		return render_template("delete-restaurants.html", title="Delete Restaurant", restaurant = restaurant)

# Display Menu for a Restaurant
@app.route("/restaurants/<int:restaurant_id>/menu/")
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	menu_items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	courses = []
	for item in menu_items:
		if item.course not in courses:
			courses.append(item.course)
	return render_template("menus.html", title="%s Menu" % restaurant.name, items = menu_items, restaurant = restaurant, courses = courses)

# Add a new menu item
@app.route("/restaurants/<int:restaurant_id>/menu/new/", methods=["GET", "POST"])
def newMenuItem(restaurant_id):
	if request.method == "POST":
		new_menu = MenuItem(name = request.form["menu-name"], description = request.form["menu-description"], 
							price = request.form["menu-price"], restaurant_id = restaurant_id, course = request.form["menu-course"])
		session.add(new_menu)
		session.commit()
		flash("New Menu Item Added")
		return redirect(url_for("restaurantMenu", restaurant_id = restaurant_id))
	else:
		return render_template("new-menus.html", title="Add a New Menu Item", restaurant_id = restaurant_id)

# Edit an existing menu item
@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/", methods=["GET", "POST"])
def editMenuItem(restaurant_id, menu_id):
	menu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id = menu_id).one()
	if request.method == "POST":
		if request.form["menu-name"]:
			menu.name = request.form["menu-name"]
		if request.form["menu-description"]:
			menu.description = request.form["menu-description"]
		if request.form["menu-price"]:
			menu.price = request.form["menu-price"]
		session.add(menu)
		session.commit()
		flash("Menu Item Successfully Edited")
		return redirect(url_for("restaurantMenu", restaurant_id = restaurant_id))
	else:
		return render_template("edit-menus.html", title="Edit Menu", menu = menu, restaurant_id = restaurant_id)

# Delete an existing menu item
@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/", methods=["GET", "POST"])
def deleteMenuItem(restaurant_id, menu_id):
	menu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id = menu_id).one()
	if request.method == "POST":
		session.delete(menu)
		session.commit()
		flash("Menu Item Successfully Deleted")
		return redirect(url_for("restaurantMenu", restaurant_id = restaurant_id))
	else:
		return render_template("delete-menus.html", title="Delete Menu", menu = menu, restaurant_id = restaurant_id)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
