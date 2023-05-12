# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import xlrd

from app.model.EventCount import EventCount
from application import app, db
from flask import session, url_for, make_response, request, jsonify, g
from app.helper.AjaxJson import AjaxJson
from app.controller.api import route_api
from app.helper.Auth import *
from app.model.Event import Event
from app.model.SysUserEvent import SysUserEvent
from openpyxl import load_workbook


@route_api.route("/event/detail", methods=["get"])
@auth_jwt
def get_event_detail():
    name = request.args.get('name')
    if not name:
        return jsonify(AjaxJson.jsonFn(message="获取", success=False))

    event = db.session.query(Event).filter(Event.name == name).first()
    return jsonify(AjaxJson.jsonFn(result={"event": {
            "id": event.id,
            "introduction": event.introduction,
            "json": event.json,
            "name": event.name,
            "process": event.process,
            "type": event.type,
            "url": event.url
        }}))


@route_api.route("/event/chart", methods=["get"])
@auth_jwt
def get_event_chart():
    total = db.session.query(Event).count()
    updated_num = db.session.query(Event).filter(Event.is_updated == "1").count()
    return jsonify(AjaxJson.jsonFn(result=[
        {
            "name": "未更新",
            "value": total - updated_num
        },
        {
            "name": "已更新",
            "value": updated_num
        }
    ]))


@route_api.route("/event/list", methods=["get"])
@auth_jwt
def get_event_list():
    user_id = session.get('current_user')

    type = request.args.get('type')
    page_size = int(request.args.get('page_size'))
    page_num = int(request.args.get('page_num'))
    offset_data = page_size * (page_num - 1)
    events = None
    count = 0
    query = db.session.query(Event)
    if type is not None:
        query = query.filter(Event.type == type)
    if user_id != 1:
        query = query\
            .filter(SysUserEvent.sys_user_id == user_id)\
            .join(SysUserEvent, Event.name == SysUserEvent.event_name)
        count = query.count()
        events = query\
            .offset(offset_data) \
            .limit(page_size) \
            .all()
    else:
        count = query.count()
        events = query \
            .offset(offset_data) \
            .limit(page_size) \
            .all()

    event_list = []
    for item in events:
        event_list.append({
            "id": item.id ,
            "introduction": item.introduction,
            "json": item.json,
            "name": item.name,
            "process": item.process,
            "type": item.type,
            "url": item.url
        })
    return jsonify(AjaxJson.jsonFn(result={"events": event_list, "page_size": page_size, "page_num": page_num, "count": count}))


@route_api.route("/event/delete", methods=["POST"])
# @auth_jwt
def delete_event():
    try:
        if session.get('current_user') != 1:
            return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))
        req = request.get_json()
        name = req.get("name").strip()
        db.session.query(Event).filter(Event.name == name).delete()
        db.session.query(SysUserEvent).filter(SysUserEvent.event_name == name).delete()
        db.session.query(EventCount).filter(EventCount.event_name == name).delete()
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="删除成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="删除失败", success=False))


@route_api.route("/event/update", methods=["POST"])
@auth_jwt
def update_event():
    try:
        # if session.get('current_user') != 1:
        #     return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))
        req = request.get_json()
        id = req.get("id")
        event = {
            "name": req.get("name"),
            "introduction": req.get("introduction"),
            "process": req.get("process"),
            "type": req.get("type"),
            "url": req.get("url")
        }

        db.session.query(Event).filter(Event.id == id).update(event)
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="更新成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="更新失败", success=False))


@route_api.route("/event/bindedUserIDList", methods=["GET"])
@auth_jwt
def binded_user_ID_list():
    try:
        event_name = request.args.get("event_name")

        sysUserEvents = db.session.query(SysUserEvent)\
            .filter(SysUserEvent.event_name == event_name).all()
        binded_user_ID_list = []
        for sysUserEvent in sysUserEvents:
            binded_user_ID_list.append(sysUserEvent.sys_user_id)
        return jsonify(AjaxJson.jsonFn(message="获取成功", result={"bindedUserIDList": binded_user_ID_list}))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="获取失败", success=False))


@route_api.route("/event/bind", methods=["POST"])
@auth_jwt
def bind_event():
    try:
        if session.get('current_user') != 1:
            return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))

        req = request.get_json()
        userIDList = req.get("userIDList")
        event_name = req.get("name")

        # 获取已绑定的用户ID列表
        sysUserEvents = db.session.query(SysUserEvent) \
            .filter(SysUserEvent.event_name == event_name).all()
        for sysUserEvent in sysUserEvents:
            if sysUserEvent.sys_user_id not in userIDList:
                db.session.query(SysUserEvent)\
                    .filter(SysUserEvent.sys_user_id == SysUserEvent.sys_user_id, SysUserEvent.event_name == event_name)\
                    .delete()
        db.session.commit()
        for userId in userIDList:
            record = SysUserEvent()
            record.event_name = event_name
            record.sys_user_id = userId
            db.session.add(record)
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="绑定成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="绑定失败", success=False))


@route_api.route("/event/update_json", methods=["POST"])
@auth_jwt
def update_json():
    try:
        # if session.get('current_user') != 1:
        #     return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))

        req = request.get_json()
        id = req.get("id")
        if id is not None:
            db.session.query(Event).filter(Event.id == id).update({"json": req.get("json")})
        jsons = req.get("jsons")
        if jsons is not None:
            for json in jsons:
                name = json.get("name")[0: -5]
                db.session.query(Event).filter(Event.name == name).update({"json": json.get("json")})
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="绑定成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="绑定失败", success=False))


@route_api.route("/event/upload", methods=["POST"])
# @auth_jwt
def upload_event():
    try:
        if session.get('current_user') != 1:
            return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))

        file = request.files.get('file')
        f = file.read()
        clinic_file = xlrd.open_workbook(file_contents=f)
        # for sheet in clinic_file.sheets():
        #     print(sheet)
        # TODO 判断拓展名来决定使用的库
        # file_path = "/Users/movi/Desktop/事故4(2).xls"
        # clinic_file = xlrd.open_workbook(file_path)
        sheet_names = clinic_file.sheet_names()

        # event_ls = []
        for name in sheet_names:
            sheet = clinic_file.sheet_by_name(name)
            for index in range(1, sheet.nrows):
                row = sheet.row(index)
                event = Event()
                event.type = name.strip()
                event.name = row[0].value.strip()
                event.introduction = row[1].value.strip()
                event.url = row[2].value.strip()
                event.process = row[3].value.strip()
                # event_ls.append(event)
                db.session.add(event)
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="上传成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="上传失败", success=False))