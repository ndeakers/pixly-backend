"""Flask app for Pixly Backend"""
import os
from flask import Flask, render_template, redirect, request, flash
from werkzeug.utils import secure_filename
from project_secrets import SECRET_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME
from PIL import Image
from PIL.ExifTags import TAGS
import boto3
from models import Photo, connect_db, db
from forms import UpdatePhotoForm, UploadForm
from aws import generate_aws_url, upload_file, download_file

app = Flask(__name__)

# client = boto3.client('s3',
#                       aws_access_key_id=AWS_ACCESS_KEY,
#                       aws_secret_access_key=AWS_SECRET_KEY)

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
            # upload original image to AWS
            filename = secure_filename(f.filename)

            # resize image
            basewidth = 450
            img = Image.open(f'{filename}')
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)

            img.save(os.path.join(filename))
            print("f is", f)

            photo = Photo(
                file_name=f.filename
            )
            db.session.add(photo)
            db.session.commit()

            descending = Photo.query.order_by(Photo.id.desc())
            new_photo = descending.first()

            img_url = generate_aws_url(new_photo.id)
            upload_file(filename, new_photo.id)
            new_photo.image_url = img_url
            db.session.commit()
            # print("aws object is", aws_object)

            return redirect(f"/image/{new_photo.id}")

        flash("We only accept jpg and jpeg!")
        return render_template("upload.html", form=form)

    return render_template("upload.html", form=form)


@app.route("/image/<int:id>", methods=["GET", "POST"])
def add_photo_info(id):
    """
    ON GET, renders form to add info on photo, displays photo
    ON POST, updats db with form inputs
    """
    form = UpdatePhotoForm()
    photo = Photo.query.get_or_404(id)
    photo.image_url = generate_aws_url(id)
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
            img_src=photo.image_url,
            model=model,
            form=form) # on GET request, pass in relevant information from this image's entry in table


@app.route("/image/<int:id>/black_and_white", methods=['POST'])
def convert_to_black_and_white(id):
    """
    s;kdj;lskad
    """
    photo = Photo.query.get_or_404(id)
    download_file(photo.id, f'{photo.id}.jpg')
    img = Image.open(f'{photo.id}.jpg') #TODO pull down actual photo from aws

    image_file = img.convert('1') # convert image to black and white
    image_file.save(f"{photo.id}test.jpeg")
    # upload_file(f"{photo.id}test.jpeg", photo.id)
    
    return redirect(f"/image/{id}")












# Notes with some code on changing image color configuration


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