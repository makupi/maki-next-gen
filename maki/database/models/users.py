from maki.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BIGINT, primary_key=True)
    guild_id = db.Column(db.BIGINT, primary_key=True)
    birthday = db.Column(db.Date)
