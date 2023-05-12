# coding: utf-8
from sqlalchemy import Column, DateTime, String,func
from application import db

class SysUser(db.Model):
    __tablename__ = 'sys_user'

    id = db.Column(db.Integer, primary_key=True)
    login_name = db.Column(db.String(100, 'utf8_bin'), index=True)
    password = db.Column(db.String(100, 'utf8_bin'))
    role_type = db.Column(db.String(64))
    name = db.Column(db.String(100, 'utf8_bin'))
    mobile = db.Column(db.String(200, 'utf8_bin'))
    avatar = db.Column(db.String(1000, 'utf8_bin'))
    del_flag = db.Column(db.String(1), index=True, server_default=db.FetchedValue())
