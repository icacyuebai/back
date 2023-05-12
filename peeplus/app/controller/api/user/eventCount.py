# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import xlrd

from application import app, db
from flask import session, url_for, make_response, request, jsonify, g
from app.helper.AjaxJson import AjaxJson
from app.controller.api import route_api
from app.helper.Auth import *
from app.model.Event import Event
from app.model.EventCount import EventCount
from app.model.SysUserEvent import SysUserEvent
from openpyxl import load_workbook
from xlrd import open_workbook



@route_api.route("/eventCount/list", methods=["get"])
@auth_jwt
def get_eventCount_list():
    user_id = session.get('current_user')

    type = request.args.get('type')
    event_name = request.args.get('event_name')
    page_size = int(request.args.get('page_size'))
    page_num = int(request.args.get('page_num'))
    offset_data = page_size * (page_num - 1)
    events = None
    count = 0
    query = db.session.query(EventCount)
    if type is not None:
        query = query.filter(EventCount.type_detail == type)
    if event_name is not None:
        query = query.filter(EventCount.event_name == event_name)
    if user_id != 1:
        query = query\
            .filter(SysUserEvent.sys_user_id == user_id)\
            .join(SysUserEvent, EventCount.event_name == SysUserEvent.event_name)
        count = query.count()
        events = query\
            .order_by(EventCount.event_name)\
            .offset(offset_data) \
            .limit(page_size) \
            .all()
    else:
        count = query.count()
        events = query\
            .order_by(EventCount.event_name) \
            .offset(offset_data) \
            .limit(page_size) \
            .all()

    event_list = []
    for item in events:
        event_list.append({
            "id": item.id,
            "event_name": item.event_name.strip(),
            "type": item.type.strip(),
            "type_detail": item.type_detail.strip(),
            "date": item.date,
            "position": item.position,
            "company": item.company.strip(),
            "loss_people": item.loss_people,
            "loss_economic": item.loss_economic,
            "is_pass": item.is_pass
        })
    return jsonify(AjaxJson.jsonFn(result={"event_count": event_list, "page_size": page_size, "page_num": page_num, "count": count}))


@route_api.route("/eventCount/delete", methods=["POST"])
@auth_jwt
def delete_eventCount():
    try:
        if session.get('current_user') != 1:
            return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))
        req = request.get_json()
        event_name = req.get("event_name").strip()
        db.session.query(EventCount).filter(EventCount.event_name == event_name).delete()
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="删除成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="删除失败", success=False))


@route_api.route("/eventCount/update", methods=["POST"])
@auth_jwt
def update_eventCount():
    try:
        # if session.get('current_user') != 1:
        #     return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))
        req = request.get_json()
        id = req.get("id")
        eventCount = {
            "event_name": req.get("event_name").strip(),
            "type": req.get("type").strip(),
            "type_detail": req.get("type_detail").strip(),
            "date": req.get("date"),
            "position": req.get("position"),
            "company": req.get("company"),
            "loss_people": req.get("loss_people"),
            "loss_economic": req.get("loss_economic")
        }

        db.session.query(EventCount).filter(EventCount.id == id).update(eventCount)

        db.session.query(Event).filter(Event.name == req.get("event_name").strip()).update({"is_updated": "1"})
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="更新成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="更新失败", success=False))


@route_api.route("/eventCount/pass", methods=["POST"])
@auth_jwt
def pass_eventCount():
    req = request.get_json()
    id = req.get("id")
    query = db.session.query(EventCount).filter(EventCount.id == id)
    query.update({"is_pass": "1"})
    event_count = query.first()
    db.session.query(Event).filter(Event.name == event_count.event_name).update({"is_updated": "1"})

    db.session.commit()
    return jsonify(AjaxJson.jsonFn(message="标记成功"))


@route_api.route("/eventCount/upload", methods=["POST"])
# @auth_jwt
def upload_eventCount():
    try:
        if session.get('current_user') != 1:
            return jsonify(AjaxJson.jsonFn(message="鉴权失败", success=False))

        file = request.files.get('file')
        f = file.read()
        clinic_file = xlrd.open_workbook(file_contents=f)
        # TODO 判断拓展名来决定使用的库
        # file_path = "/Users/movi/Desktop/副本事故抽取版1.xls"
        # clinic_file = xlrd.open_workbook(file_path)
        sheet_names = clinic_file.sheet_names()

        for name in sheet_names:
            sheet = clinic_file.sheet_by_name(name)
            for index in range(1, sheet.nrows):
                row = sheet.row(index)
                event = EventCount()
                event.type_detail = name.strip()

                event.event_name = row[0].value.strip()
                event.type = row[1].value.strip()
                event.date = row[3].value.strip()
                event.position = row[4].value.strip()
                event.company = row[5].value.strip()
                event.loss_people = row[6].value.strip()
                event.loss_economic = row[7].value.strip()
                event.is_pass = "0"
                db.session.add(event)
        db.session.commit()
        return jsonify(AjaxJson.jsonFn(message="上传成功"))
    except Exception:
        return jsonify(AjaxJson.jsonFn(message="上传失败", success=False))