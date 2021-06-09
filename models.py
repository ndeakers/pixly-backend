# """Models for Pixly app."""
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# def connect_db(app):
#     """Connect this database to provided Flask app.
#     You should call this in your Flask app.
#     """
#     db.app = app
#     db.init_app(app)


# class Photo(db.Model):
#     "data on a photo"

#     __tablename__ = "photos"

#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     location = db.Column(db.String(100), nullable=False)
#     # colorData= db.Column(db.String(100), nullable=False)
#     height = db.Column(db.String(100), nullable=False)
#     width = db.Column(db.String(100), nullable=False)
#     image_path = db.Column(db.String(100), nullable=False)

#     def serialize(self):
#         """Serialize to dictionary."""

#         return {
#             "id": self.id,
#             "location": self.flavor,
#             "height": self.size,
#             "width": self.rating,
#             "image_path": self.image,
#         }

#     def get_photo_from_aws(self):
#         return
        