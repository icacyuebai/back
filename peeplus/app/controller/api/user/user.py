#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from application import app, db
from flask import session, send_from_directory
from app.helper.AjaxJson import AjaxJson
from app.controller.api import route_api
from app.helper.Auth import *
from app.model.SysUser import SysUser
from app.service.user.user import UserService

from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.parse import quote_plus
from moviepy.editor import *
from uuid import uuid4

from moviepy.config import change_settings

change_settings({"IMAGEMAGICK_BINARY": "/usr/local/Cellar/imagemagick/7.1.1-5/bin/convert"})
from moviepy.video.tools.subtitles import SubtitlesClip
from app.utils.utils import replace_str

'''
@url /api/auth/login
@des 登录
'''


@route_api.route("/auth/login", methods=['POST'])
def auth_login():
    try:
        req = request.get_json()
        user = UserService.is_empty_user(req['username'], req['password'])
        if user is None:
            return jsonify(AjaxJson.jsonFn(message='用户不存在或密码错误', success=False))
        else:
            str_token = create_token(user.id, user.login_name)
            # str_token = str(create_token(user.id, user.login_name), encoding="utf-8")
            session['current_user'] = user.id
            return jsonify(AjaxJson.jsonFn(message="登录成功", token=str_token, name=user.name))
    except Exception as e:
        return jsonify(AjaxJson.jsonFn(message='用户不存在或密码错误', success=False))


def fetch_token():
    print("fetch token begin")

    TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'
    SCOPE = 'audio_tts_post'
    params = {'grant_type': 'client_credentials',
              'client_id': '5plPNbmu7LGG0EuWGm4IYLfo',
              'client_secret': 'kAvNrYgtOl1ESKhrfGxNSwTZwcvEeRat'}
    post_data = urlencode(params)

    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    result_str = result_str.decode()

    print(result_str)
    result = json.loads(result_str)
    print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not SCOPE in result['scope'].split(' '):
            print('scope is not correct')
        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise print('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


'''
添加用户
'''


@route_api.route("/user/add", methods=["POST"])
@auth_jwt
def add_user():
    try:
        if session.get('current_user') != 1:
            return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))
        req = request.get_json()
        record = SysUser()
        record.name = req.get('name')
        record.login_name = req.get('login_name')
        record.password = req.get('password')
        record.role_type = "user"
        # SysUser.add(record)
        db.session.add(record)
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="添加成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="添加失败", success=False))


'''
修改用户
'''


@route_api.route("/user/update", methods=["POST"])
@auth_jwt
def update_user():
    try:
        if session.get('current_user') != 1:
            return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))
        req = request.get_json()
        id = req.get("id")
        user = {
            "name": req.get("name"),
        }
        if req.get("password") is not None:
            user.update({"password": req.get("password")})

        db.session.query(SysUser).filter(SysUser.id == id).update(user)
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="更新成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="更新失败", success=False))


'''
删除用户
'''


@route_api.route("/user/delete", methods=["POST"])
@auth_jwt
def delete_user():
    try:
        if session.get('current_user') != 1:
            return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))
        req = request.get_json()
        id = req.get("id")
        if int(id) == 1:
            return jsonify(AjaxJson.jsonFn(message="删除失败，管理员不允许删除", success=False))

        db.session.query(SysUser).filter(SysUser.id == id).delete()
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="删除成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="删除失败", success=False))


'''
获取用户信息
'''


@route_api.route("/user/info", methods=['GET'])
@auth_jwt
def user_info():
    user_id = session['current_user']
    user_info = UserService.user_by_id(user_id)
    info = {
        "name": user_info.name,
        "id": user_info.id,
        "avatar": user_info.avatar,
        "role_type": user_info.role_type
    }
    return jsonify(AjaxJson.jsonFn(result=info))


'''
获取用户列表
'''


@route_api.route("/user/list", methods=["get"])
@auth_jwt
def get_user_list():
    if session.get('current_user') != 1:
        return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))
    page_size = int(request.args.get('page_size'))
    page_num = int(request.args.get('page_num'))
    offset_data = page_size * (page_num - 1)
    # users = UserService.get_user_list(offset_data, page_size)
    query = db.session.query(SysUser).filter(SysUser.role_type != "admin")
    count = query.count()
    users = query.order_by(SysUser.id).offset(offset_data).limit(page_size).all()
    user_list = []
    for item in users:
        user_list.append({
            "name": item.name,
            "id": item.id,
            "role_type": item.role_type,
            "login_name": item.login_name
        })
    return jsonify(
        AjaxJson.jsonFn(result={"users": user_list, "page_size": page_size, "page_num": page_num, "count": count}))


'''
退出登录
'''


@route_api.route("/user/logout", methods=["POST"])
def logout():
    session['current_user'] = None
    g.current_user = None
    return jsonify(AjaxJson.jsonFn(message='退出成功', success=True))
