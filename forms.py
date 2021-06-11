from flask_wtf import FlaskForm
from wtforms import StringField, FileField


class UpdatePhotoForm(FlaskForm):
    description = StringField("Description")
    location = StringField("Photo Location")
    model = StringField("Camera Model")


class UploadForm(FlaskForm):
    upload_file = FileField()
    # can add file type validation in here


class EditButton(FlaskForm):
    """Protected Button, purposefully blank"""
