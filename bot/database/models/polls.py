from bot.database import db


class Poll(db.Model):
    __tablename__ = "polls"

    id = db.Column(db.Integer, primary_key=True)
    due_time = db.Column(db.TIMESTAMP)
    message_id = db.Column(db.BIGINT)
    options = db.Column(db.ARRAY(db.String))
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    channel_id = db.Column(db.BIGINT)
