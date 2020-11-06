from bot.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BIGINT)
    guild_id = db.Column(db.BIGINT, db.ForeignKey("guilds.id"))
    birthday = db.Column(db.Date)

    _guild_user_uniq = db.UniqueConstraint("user_id", "guild_id", name="guild_user")
