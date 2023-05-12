# coding: utf-8
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.schema import FetchedValue
from application import db

class EventCount(db.Model):
    __tablename__ = 'event_count'

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(255))
    type = db.Column(db.String(255))
    type_detail = db.Column(db.String(255))
    date = db.Column(db.String(128))
    position = db.Column(db.String(128))
    company = db.Column(db.String(128))
    loss_people = db.Column(db.String(128))
    loss_economic = db.Column(db.String(128))
    is_pass = db.Column(db.String(8))