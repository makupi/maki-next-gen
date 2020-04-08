from maki.database import db


class Guild(db.Model):
    __tablename__ = 'guilds'

    id = db.Column(db.Integer, primary_key=True)
    prefix = db.Column(db.String)

    def __init__(self, guild_id):
        self.id = guild_id
