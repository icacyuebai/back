# coding: utf-8
from application import db

class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32, 'utf8_bin'))
    name = db.Column(db.String(256), primary_key=True)
    introduction = db.Column(db.Text(400))
    url = db.Column(db.String(128))
    process = db.Column(db.Text(800))
    json = db.Column(db.Text(400))
    is_updated = db.Column(db.String(8))
