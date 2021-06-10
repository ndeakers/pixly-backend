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

app = Flask(__name__)

client = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)

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
def display_new_photo_form():
    """"""
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
            f.save(os.path.join(filename))
            print("f is", f)

            photo = Photo(
                file_name=f.filename
            )
            db.session.add(photo)
            db.session.commit()

            descending = Photo.query.order_by(Photo.id.desc())
            new_photo = descending.first()
            client.upload_file(filename, BUCKET_NAME, f"{new_photo.id}", ExtraArgs={"ACL":"public-read"}) #break this out

            # aws_object = client.get_object(Bucket=BUCKET_NAME, Key=f"${filename}")
            img_url = f"https://{BUCKET_NAME}.s3.us-east-2.amazonaws.com/{new_photo.id}" #get url from aws
            new_photo.image_path = img_url
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
            img_src=photo.image_path,
            model=model,
            form=form)


@app.route("/image/<int:id>/black_and_white", methods=['POST'])
def convert_to_black_and_white(id):
    # some code to change to black and white
    # source for this is:
    # https://stackoverflow.com/questions/9506841/using-python-pil-to-turn-a-rgb-image-into-a-pure-black-and-white-image
    photo = Photo.query.get_or_404(id)
    img = Image.open(photo.image_path) #TODO pull down actual photo from aws
    image_file = img.convert('1') # convert image to black and white
    filename = secure_filename(image_file.filename)
    # f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    image_file.save(os.path.join(filename))
    client.upload_file(filename, BUCKET_NAME, f"{photo.id}", ExtraArgs={"ACL":"public-read"}) #break this out
    return redirect(f"/image/{id}")










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