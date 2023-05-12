# coding: utf-8
from sqlalchemy import Column, DateTime, String, Text, ForeignKey
from sqlalchemy.schema import FetchedValue
from application import db

class SysUserEvent(db.Model):
    __tablename__ = 'sys_user_event'

    sys_user_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(256), ForeignKey("event.name"), primary_key=True)
    # event = db.relationship("Event", back_populates="sys_user_event", uselist=False)
    # event_count = db.relationship("EventCount", back_populates="sys_user_event", uselist=False)