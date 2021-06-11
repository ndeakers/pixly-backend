from flask import session
from aws import download_file
from PIL import ImageOps, Image


def add_border(img):
  """Accepts an image and returns that image with a border added."""

  return ImageOps.expand(img, border=15, fill='black')


def determine_img_version(id):
  """"""

  if not session.get('CURRENT_PHOTO_FILENAME'):
      download_file(id, f'./static/photos/{id}.jpeg')
      img = Image.open(f'./static/photos/{id}.jpeg')
  else:

      img = Image.open(f".{session.get('CURRENT_PHOTO_FILENAME')}")

  return img
