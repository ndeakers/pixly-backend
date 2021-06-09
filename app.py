"""Flask app for Pixly Backend"""
import os
from flask import Flask, url_for, render_template, jsonify, request
from werkzeug.utils import secure_filename
from project_secrets import SECRET_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME
from PIL import Image
from PIL.ExifTags import TAGS
import boto3
# from models import Photo, connect_db

app = Flask(__name__)

client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY )

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///cupcakes"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


@app.route("/")
def display_new_photo_form():
    """"""

    return render_template("dumby.html")


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    """"""

    if request.method == 'POST':
        f = request.files['file']
        print("f is", f)

        filename = secure_filename(f.filename)
        f.save(os.path.join(filename))
        img = Image.open(filename)
        client.upload_file(filename, BUCKET_NAME, "something", ExtraArgs={"ACL":"public-read"})
        os.remove(filename)

        exif_values = {}
        for tag, value in img.getexif().items():
            if tag in TAGS:
                exif_values[TAGS[tag]] = value
        return jsonify(exif_values)

# loop over all tags in list of items from img.

# @app.route('/api/photos')
# def list_all_cupcakes():
#     """
#     Return JSON 
#     {photos: [{id, flavor, size, rating, image}, ...]}.
#     """

#     photos = Photo.query.all()
#     serialized = [p.serialize() for p in photos]

#     return jsonify(photos=serialized)

    
# @app.route("/api/photos", methods=["POST"])
# def create_photo():
#     """
#     THIS IS EXAMPLE: 
#     Returns JSON 
    
#     {cupcake: {id, flavor, size, rating, image}}.
#     """

#     flavor = request.json["flavor"]
#     size = request.json["size"]
#     rating = request.json["rating"]
#     # image = request.json["image"] OR default
#     if not request.json["image"]:
#         image = 'https://tinyurl.com/demo-cupcake'
#     else:
#         image = request.json["image"]

#     cupcake = Cupcake(
#         flavor=flavor, 
#         size=size,
#         rating=rating,
#         image=image
#     )

#     db.session.add(cupcake)
#     db.session.commit()

#     serialized = cupcake.serialize()

#     # Return w/status code 201 --- return tuple (json, status)
#     return (jsonify(cupcake=serialized), 201)
