from bot.database import db


class Emote(db.Model):
    __tablename__ = "emotes"

    # id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.BIGINT, db.ForeignKey("guilds.id"))
    name = db.Column(db.String)
    count = db.Column(db.Integer)

    _pk = db.PrimaryKeyConstraint("guild_id", "name", name="guild_id_emote")
