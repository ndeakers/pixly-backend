from flask import session
from aws import download_file
from PIL import ImageOps, Image
from pathlib import Path


def add_border(img):
    """Accepts an image and returns that image with a border added."""

    return ImageOps.expand(img, border=15, fill='black')

# adjust this to accept a second parameter instead of utilizing the session in the function
def determine_img_version(id):
    """Pulls in relevant version of photo for editing purposes. """

    #can make a variable for session.get here
    # can also make a variable for filepath
    if not session.get('CURRENT_PHOTO_FILENAME'):
        download_file(id, f'./static/photos/{id}.jpeg')
        img = Image.open(f'./static/photos/{id}.jpeg')
    else:

        img = Image.open(f".{session.get('CURRENT_PHOTO_FILENAME')}")

    return img
# this could be a instance method

def empty_local_photos():
    """Clears out contents in the static/photos folder"""
    [f.unlink() for f in Path("./static/photos").glob("*") if f.is_file()]
