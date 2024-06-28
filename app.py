import os
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from response import download_instagram_video
from geocode import geocode_address

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "project.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'de81a877e9046fe91c43384afa100627'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)

class URL(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    location = db.Column(db.String)
    cuisine = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    city = db.Column(db.String)

def get_unique_cities():
    cities = db.session.query(URL.city).distinct().all()
    return [city[0] for city in cities if city[0] is not None]

def get_unique_cuisines():
    cuisines = db.session.query(URL.cuisine).distinct().all()
    return [cuisine[0] for cuisine in cuisines if cuisine[0] is not None]

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        submitted_url = request.form.get("url", "").strip()
        
        if not submitted_url.startswith("https://www.instagram.com/reel/"):
            flash("Must enter a valid Instagram Reel URL.", "danger")
            return redirect(url_for('index'))
        
        existing_url = URL.query.filter_by(url=submitted_url).first()
        if existing_url:
            flash("URL is already in your list.", "warning")
            return redirect(url_for('index'))

        response = download_instagram_video(submitted_url)
        if response:
            for eatery in response:
                if len(eatery) == 4:
                    geocode_result = geocode_address(eatery[1])
                    if geocode_result:
                        new_url = URL(
                            url=submitted_url,
                            name=eatery[0],
                            location=eatery[1],
                            city=eatery[2],
                            cuisine=eatery[3],
                            latitude=geocode_result['lat'],
                            longitude=geocode_result['lng']
                        )
                        db.session.add(new_url)
                    else:
                        flash("Geocoding failed for address: " + eatery[1], "danger")
                        continue
                else:
                    flash(f"Invalid data format in response: {eatery}", "danger")
                    continue

            db.session.commit() 
            flash("New Pin Added!", "success")
        else:
            flash("Failed to process the video. Response was: " + str(response), "danger")
    
    return render_template("index.html")

@app.route("/list")
def list_view():
    city = request.args.get('city', '')
    cuisine = request.args.get('cuisine', '')

    urls = URL.query
    if city:
        urls = urls.filter(URL.city == city)
    if cuisine:
        urls = urls.filter(URL.cuisine == cuisine)
    urls = urls.all()

    unique_cities = get_unique_cities()
    unique_cuisines = get_unique_cuisines()

    return render_template("list.html", urls=urls, unique_cities=unique_cities, unique_cuisines=unique_cuisines)


@app.route("/map")
def map_view():
    urls = URL.query.all()
    urls_data = [
        {
            'id': url.id,
            'url': url.url,
            'name': url.name,
            'location': url.location,
            'city': url.city,
            'cuisine': url.cuisine,
            'latitude': float(url.latitude),
            'longitude': float(url.longitude)
        } for url in urls if url.latitude and url.longitude]
    
    return render_template("map.html", urls=urls_data)

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/delete/<int:url_id>", methods=["POST"])
def delete_url(url_id):
    url_to_delete = URL.query.get_or_404(url_id)
    db.session.delete(url_to_delete)
    db.session.commit()
    return redirect(url_for('list_view'))

@app.route("/about")
def about_view():
    return render_template("about.html")