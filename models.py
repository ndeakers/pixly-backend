"""Models for Pixly app."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """
    db.app = app
    db.init_app(app)


class Photo(db.Model):
    "data on a photo"

    __tablename__ = "photos"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    file_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String, nullable=True)

    def serialize(self):
        """Serialize to dictionary."""

        return {
            "id": self.id,
            "location": self.location,
            "name": self.name,
            "model": self.model,
            "image_path": self.image_path
        }

    # def get_photo_from_aws(self):
    #     return

# aws class should go in here