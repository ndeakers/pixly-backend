from flask_wtf import FlaskForm
from wtforms import StringField, FileField


class UpdatePhotoForm(FlaskForm):
    description = StringField("Description")
    photo_location = StringField("Photo Location")
    camera_model = StringField("Camera Model")


class UploadForm(FlaskForm):
    upload_file = FileField()
