"""Flask app for Pixly Backend"""
# rename aws to something more specific
from flask import Flask, render_template, redirect, flash, session
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS
from models import Photo, connect_db, db
from forms import UpdatePhotoForm, UploadForm, EditButton
from aws import generate_aws_url, upload_file
from edit_photo_functions import add_border, determine_img_version, empty_local_photos
from project_secrets import SECRET_KEY

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///pixly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}


connect_db(app)
db.create_all()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def display_homepage():
    """
    Renders homepage for Pixly.
    """
    return render_template("landing.html")


@app.route('/upload', methods=['POST', 'GET'])
def upload_photo():
    """
    On GET, renders form to upload a photo
    ON POST, validates the filetype, adds to s3, adds to db
    """
    form = UploadForm()
    if form.validate_on_submit():

        f = form.upload_file.data
        print("f is", f)
        # can make validation below part of the WTForm validation
        if f and allowed_file(f.filename):
            session.clear()
            # change this to session pop to remove specific keys

            # upload original image to AWS
            filename = secure_filename(f.filename)
            f.save(f'./static/photos/{filename}')

            # resize image
            basewidth = 450
            img = Image.open(f'./static/photos/{filename}')
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)

            img.save(f'./static/photos/{filename}')
            # TODO there's another library in python called tempdirectory, which provides fake folders
            # to store things on disc in memory instead of what we're doing here

            # create new photo record with the filename
            photo = Photo(
                file_name=f.filename
            )
            db.session.add(photo)
            db.session.commit()

            uploaded_photo = Photo.query.order_by(Photo.id.desc()).first()

            upload_file(f"./static/photos/{filename}", uploaded_photo.id)
            img_url = generate_aws_url(uploaded_photo.id)
            uploaded_photo.image_url = img_url
            db.session.commit()

            return redirect(f"/image/{uploaded_photo.id}")

        flash("We only accept jpg and jpeg photos!")
        return render_template("upload.html", form=form)

    return render_template("upload.html", form=form)


@app.route("/image/<int:id>", methods=["GET", "POST"])
def add_photo_info(id):
    """
    ON GET, renders form to add info on photo, displays photo
    ON POST, updates db with form inputs
    """
    photo = Photo.query.get_or_404(id)
    form = UpdatePhotoForm(obj=photo)

    photo.image_url = generate_aws_url(id)
    session['ORIGINAL_IMAGE_URL'] = photo.image_url
    db.session.commit()

    if form.validate_on_submit():
        photo.description = form.description.data
        photo.location = form.location.data
        photo.model = form.model.data
        db.session.commit()
        return redirect(f"/image/{id}")

    return render_template(
        "image.html",
        id=photo.id,
        img_src=session['ORIGINAL_IMAGE_URL'],
        form=form)


@app.route("/image/<int:id>/edit", methods=['POST', 'GET'])
def edit_image(id):
    """ On GET show what is the photo session"""
    form = EditButton()

    photo_to_display = session.get(
        'CURRENT_PHOTO_FILENAME',
        session.get('ORIGINAL_IMAGE_URL'))

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
# TODO adjust photo storing and editing to be depending on EXIFdata
# if EXIFdata doesn't exist, we can write it ourselves

@app.route("/image/<int:id>/border", methods=['POST'])
def add_border_to_image(id):
    """Adds a border to an image."""

    img = determine_img_version(id)

    # add border to image, save to server/session and redirect
    img_with_border = add_border(img)
    img_with_border.save(f'./static/photos/{id}w_border.jpeg')
    session['CURRENT_PHOTO_FILENAME'] = f"/static/photos/{id}w_border.jpeg"

    return redirect(f"/image/{id}/edit")
# TODO combine border/bw editing routes to be one route that takes
# <type_of_edit> at the end of the path and then have some logic
# in the view function that detemrines what should occur at each


@app.route("/image/<int:id>/revert", methods=["POST"])
def revert_to_original_image_URL(id):
    """
    Wipes current edits made to photo and resets back to original.
    Redirects back to editing page.
    """
    image_url = generate_aws_url(id)
    session["ORIGINAL_IMAGE_URL"] = image_url
    session.pop('CURRENT_PHOTO_FILENAME', None)
    return redirect(f"/image/{id}/edit")


@app.route("/image/<int:id>/save", methods=["POST"])
def save_image(id):
    """
    Saves current version of photo to AWS, redirects to photo's landing page.
    """
    current_photo = session.get('CURRENT_PHOTO_FILENAME', None)
    upload_file(f".{current_photo}", id)

    empty_local_photos()
    session.pop('CURRENT_PHOTO_FILENAME', None)
    return redirect(f"/image/{id}")

# TODO expand Photo class to include editing, uploading, saving methods
# TODO adjust homepage to display most recent 10 photos as thumbnails & links to edit them
# TODO full text search
# TODO throw any exifdata into separate table, foreign key being id

# EXIF data logic
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