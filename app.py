"""Flask app for Pixly Backend"""
from flask import Flask, url_for, render_template, redirect, flash, jsonify, request
from models import Photo, connect_db

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///cupcakes"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


@app.route('/api/photos')
def list_all_cupcakes():
    """
    Return JSON 
    {photos: [{id, flavor, size, rating, image}, ...]}.
    """

    photos = Photo.query.all()
    serialized = [p.serialize() for p in photos]

    return jsonify(photos=serialized)

    
@app.route("/api/photos", methods=["POST"])
def create_photo():
    """
    THIS IS EXAMPLE: 
    Returns JSON 
    
    {cupcake: {id, flavor, size, rating, image}}.
    """

    flavor = request.json["flavor"]
    size = request.json["size"]
    rating = request.json["rating"]
    # image = request.json["image"] OR default
    if not request.json["image"]:
        image = 'https://tinyurl.com/demo-cupcake'
    else:
        image = request.json["image"]

    cupcake = Cupcake(
        flavor=flavor, 
        size=size,
        rating=rating,
        image=image
    )

    db.session.add(cupcake)
    db.session.commit()

    serialized = cupcake.serialize()

    # Return w/status code 201 --- return tuple (json, status)
    return (jsonify(cupcake=serialized), 201)
