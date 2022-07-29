from flask import request, redirect, jsonify, make_response
from flask_restx import Resource

from ..util.dto import Schedules_commonDto
import requests

from ..service.schedules_common import edit_schedules_common, edit_schedules_date, get_schedules_common, post_schedules_common, post_schedules_date, delete_all_schedules, delete_clicked_schedules

api = Schedules_commonDto.api
_schedules_common = Schedules_commonDto.schedules_common

@api.route('') 
class SchedulesCommon(Resource):
  def get(self):
    """Get Schedules Common API"""
    data = request.args.to_dict()
    print(data)
    return get_schedules_common(data)
  def post(self):
    """Post Schedules Common API"""
    data = request.get_json().get('schedules_common') 
    return post_schedules_common(data) 
  def patch(self):
    """Patch Schedules Common API"""
    data = request.get_json().get('schedules_common') 
    return edit_schedules_common(data)


@api.route('/schedules-dates') 
class SchedulesDate(Resource):
  def post(self):
    """Post Schedules Date API"""
    data = request.get_json().get('schedules_common') 
    return post_schedules_date(data) 
  def patch(self):
    """Edit Schedules Date API"""
    data = request.get_json().get('schedules_common') 
    return edit_schedules_date(data) 
  def delete(self):
    """delete Schedules Date API"""
    data = request.args.to_dict()
    if 'date' not in data.keys():
      return delete_all_schedules(data)
    else:
      return delete_clicked_schedules(data)

