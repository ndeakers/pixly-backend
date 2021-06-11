"""Flask app for Pixly Backend"""
import os
from flask import Flask, render_template, redirect, request, flash, session
from werkzeug.utils import secure_filename
from project_secrets import SECRET_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS
from models import Photo, connect_db, db
from forms import UpdatePhotoForm, UploadForm, EditButton
from aws import generate_aws_url, upload_file, download_file
from edit_photo_functions import add_border, determine_img_version
import glob

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///pixly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
UPLOAD_FOLDER = './UPLOAD_FOLDER'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}


connect_db(app)
db.create_all()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def display_homepage():
    """

    """
    return render_template("landing.html")


@app.route('/uploader', methods=['POST', 'GET']) ## TODO abstract querying to model
def upload_photo():
    """
    On GET, renders form to upload a photo
    ON POST, validates the filetype, adds to s3, adds to db
    """
    form = UploadForm()
    if form.validate_on_submit():

        f = form.upload_file.data
        print("f is", f)
        if f and allowed_file(f.filename):
            session.clear()
            # upload original image to AWS
            filename = secure_filename(f.filename)
            f.save(f'./static/photos/{filename}')
            # resize image
            basewidth = 450
            img = Image.open(f'./static/photos/{filename}')
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)

            # img.save(os.path.join(filename)) prob removing this
            img.save(f'./static/photos/{filename}')

            photo = Photo(
                file_name=f.filename
            )
            db.session.add(photo)
            db.session.commit()

            descending = Photo.query.order_by(Photo.id.desc())
            new_photo = descending.first()

            upload_file(f"./static/photos/{filename}", new_photo.id)
            img_url = generate_aws_url(new_photo.id)
            new_photo.image_url = img_url
            db.session.commit()
            # print("aws object is", aws_object)

            return redirect(f"/image/{new_photo.id}")

        flash("We only accept jpg photos!")
        return render_template("upload.html", form=form)

    return render_template("upload.html", form=form)


@app.route("/image/<int:id>", methods=["GET", "POST"])
def add_photo_info(id):
    """
    ON GET, renders form to add info on photo, displays photo
    ON POST, updates db with form inputs
    """
    form = UpdatePhotoForm()
    photo = Photo.query.get_or_404(id)

    photo.image_url = generate_aws_url(id)
    session['ORIGINAL_IMAGE'] = photo.image_url
    print("session in IMAGE/id", session)
    db.session.commit()

    if form.validate_on_submit(): 
        photo.description = form.description.data
        photo.location = form.photo_location.data
        photo.model = form.camera_model.data
        db.session.commit()
        return redirect("/")
    else:    
        if photo.model is None: #check here
            model = "Enter camera model here!"
        else:
            model = photo.model
        return render_template(
            "image.html",
            id=photo.id,
            img_src=session['ORIGINAL_IMAGE'],
            model=model,
            form=form) # on GET request, pass in relevant information from this image's entry in table


@app.route("/image/<int:id>/edit", methods=['POST', 'GET'])
def edit_image(id):
    """ On GET show what is the current photo in g"""
    form = EditButton()

    if session.get('CURRENT_PHOTO_FILENAME'):
        photo_to_display = f"{session.get('CURRENT_PHOTO_FILENAME')}"
    else:
        photo_to_display = session.get('ORIGINAL_IMAGE')

    # if POST
    if form.validate_on_submit():
        upload_file(session['CURRENT_PHOTO_FILENAME'], id)
        return redirect(f"/image/{id}")

    # if GET
    return render_template(
            "edit.html",
            id=id,
            img_src=photo_to_display,
            form=form)


@app.route("/image/<int:id>/black_and_white", methods=['POST'])
def convert_to_black_and_white(id):
    """Converts an image to black-and-white."""

    img = determine_img_version(id)

    # convert image to black and white, save to server/session and redirect
    image_file = img.convert('1')
    image_file.save(f"./static/photos/{id}test.jpeg")
    session['CURRENT_PHOTO_FILENAME'] = f"/static/photos/{id}test.jpeg"

    return redirect(f"/image/{id}/edit")


@app.route("/image/<int:id>/border", methods=['POST'])
def add_border_to_image(id):
    """Adds a border to an image."""

    img = determine_img_version(id)

    # add border to image, save to server/session and redirect
    img_with_border = add_border(img)
    img_with_border.save(f'./static/photos/{id}w_border.jpeg')
    session['CURRENT_PHOTO_FILENAME'] = f"/static/photos/{id}w_border.jpeg"
    return redirect(f"/image/{id}/edit")


@app.route("/image/<int:id>/revert", methods=["POST"])
def revert_to_original_image(id):
    image_url = generate_aws_url(id)
    session["ORIGINAL_IMAGE"] = image_url
    session.pop('CURRENT_PHOTO_FILENAME', None)
    return redirect(f"/image/{id}/edit")


@app.route("/image/<int:id>/save", methods=["POST"])
def save_image(id):
    current_photo = session.get('CURRENT_PHOTO_FILENAME', None)
    upload_file(current_photo, id)

    files = glob.glob('./static/photos')
    for f in files:
        os.remove(f)
    return redirect(f"/image/{id}/")


# TODO Add routes for reverting to original and saving any edits
# TODO full text search
# TODO throw any exifdata into separate table
# TODO look into WTForms placeholders



# extract EXIF data and save to db
            # img = Image.open(filename)
            # os.remove(filename)
            # exifdata = img.getexif()
            # exif_values = {}
            # # iterating over all EXIF data fields
            # for tag_id in exifdata:
            #     # get the tag name, instead of human unreadable tag id
            #     # tag = TAGS.get(tag_id, tag_id)
            #     if str(tag_id) in ["272"]:
            #         data = exifdata.get(tag_id)
            #         exif_values[tag_id] = data
            #         # new_photo.location = exifdata.get("37396")
            #         new_photo.model = exifdata.get("272")
            #         db.session.commit()