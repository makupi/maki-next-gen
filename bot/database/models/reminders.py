from bot.database import db


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    due_time = db.Column(db.TIMESTAMP)
    reminder = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    channel_id = db.Column(db.BIGINT)
    # guild_id = db.Column(db.BIGINT, db.ForeignKey("guilds.id"))
    send_dm = db.Column(db.Boolean)
