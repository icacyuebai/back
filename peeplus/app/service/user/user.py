#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.model.SysUser import SysUser
import json


class UserService():
    def __init__(self):
        pass

    '''
    根据用户名和密码获取用户信息
    '''

    @staticmethod
    def is_empty_user(username, password):
        return SysUser.query.filter_by(login_name=username, password=password).first()


    '''
    根据用户ID获取用户信息
    '''

    @staticmethod
    def user_by_id(id):
        return SysUser.query.filter_by(id=id).first()
