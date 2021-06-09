"""Flask app for Pixly Backend"""
import os
from flask import Flask, render_template, redirect, request
from werkzeug.utils import secure_filename
from project_secrets import SECRET_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME
from PIL import Image
from PIL.ExifTags import TAGS
import boto3
from models import Photo, connect_db, db

app = Flask(__name__)

client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY )

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///pixly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
UPLOAD_FOLDER = './UPLOAD_FOLDER'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connect_db(app)
db.create_all()


@app.route("/")
def display_new_photo_form():
    """"""

    return render_template("dumby.html")


@app.route('/uploader', methods=['POST'])
def upload_photo():
    """"""

    f = request.files['file']
    print("f is", f)

    # upload original image to AWS
    filename = secure_filename(f.filename)
    f.save(os.path.join(filename))
    print("f is", f)

    photo = Photo(
        file_name=f.filename
    )
    db.session.add(photo)
    db.session.commit()

    descending = Photo.query.order_by(Photo.id.desc())
    new_photo = descending.first()
    # print("new photo from table", new_photo)
    client.upload_file(filename, BUCKET_NAME, f"{new_photo.id}", ExtraArgs={"ACL":"public-read"})

    # aws_object = client.get_object(Bucket=BUCKET_NAME, Key=f"${filename}")
    img_url = f"https://test-pixly.s3.us-east-2.amazonaws.com/{new_photo.id}"
    new_photo.image_path = img_url
    db.session.commit()
    # print("aws object is", aws_object)


    # extract EXIF data and save to db
    img = Image.open(filename)
    os.remove(filename)
    exifdata = img.getexif()
    exif_values = {}
    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        # tag = TAGS.get(tag_id, tag_id)
        if str(tag_id) in ["272"]:
            data = exifdata.get(tag_id)
            exif_values[tag_id] = data
            # new_photo.location = exifdata.get("37396")
            new_photo.model = exifdata.get("272")
            db.session.commit()

    # print("exif_values", exif_values)

    return redirect(f"/image/{new_photo.id}")


@app.route("/image/<int:id>", methods=["GET", "POST"])
def add_photo_info(id):
    """"""

    photo = Photo.query.get_or_404(id)

    if photo.model is None:
        return render_template(
            "image.html",
            id=photo.id
            img_src=photo.image_path,
            model="Enter camera model here!")

    return render_template(
        "image.html",
        id=photo.id,
        img_src=photo.image_path,
        model=photo.model)

    # photo_name = request.form["photo_name"]
    # photo_location = request.form["photo_location"]
    # maybe put some other stuff into the form and grab that here?
    # save to db


# Notes with some code on changing image color configuration

        # some code to change to black and white
        # source for this is:
        # https://stackoverflow.com/questions/9506841/using-python-pil-to-turn-a-rgb-image-into-a-pure-black-and-white-image
        # img = Image.open("./UPLOAD_FOLDER/jpegsystems-home.jpeg")
        # image_file = img.convert('1') # convert image to black and white
        # # f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # image_file.save('result.png')


        # img_color = img.convert("RGBA")
        # w, h = img_color.size
        # cnt = 0
        # for px in img_color.getdata():
        #     img_color.putpixel((int(cnt % w), int(cnt / w)), (0, 0, 0, px[3]))
        #     cnt += 1  
        # print("what is image_color", img_color.getdata())
        # new_filename = secure_filename(f.filename)
        # 
        #                 
        # exif_values = {}
        # for tag in img.getexif().items:
        #     print("exifValues", tag)
        #     # if tag in TAGS:
        #     #     exif_values[TAGS[tag]] = value
        # return jsonify(exif_values)



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
