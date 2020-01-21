# Imporing Dependencies
from flask import Flask, render_template
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# Using flask_pymongo to establish connection with MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# Creating a root route '/' to query the Mongo database and pass the mars data into an HTML template for display
@app.route("/")
def index():
    mars = mongo.db.mars.find_one()
    return render_template("index.html", mars=mars)

# Creating a route called '/scrape' that will import scrape_mars.py script and call the scrape function
@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape()
    mars.update({}, mars_data, upsert=True)
    return "Scraping Successful!"

if __name__ == "__main__":
    app.run()
