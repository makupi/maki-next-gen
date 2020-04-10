from maki.database import db


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    due_time = db.Column(db.Time)
    reminder = db.Column(db.String)
    user_id = db.Column(db.BIGINT)
    channel_id = db.Column(db.BIGINT)
    guild_id = db.Column(db.BIGINT)
    send_dm = db.Column(db.Boolean)
