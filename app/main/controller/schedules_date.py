from flask import request, redirect, jsonify, make_response
from flask_restx import Resource

from ..util.dto import Schedules_dateDto
import requests
from ..service.schedules_date import get_monthly_checked, get_alarms_list, get_today_checked, patch_check

api = Schedules_dateDto.api
_schedules_date = Schedules_dateDto.schedules_date

"""
client에서 
{
  "schedules_common": 
    {"schedules_common_id": 1, 
      "clickdate": '2020-12-12',
    }
}
의 형태로 보내준다고 생각하고 구현
"""
@api.route('/check')
class PatchCheck(Resource):
  def patch(self):
    """Patch Check API"""
    data = request.get_json().get('schedules_common') 
    return patch_check(data)

@api.route('/check/month') 
class Check(Resource):
  def get(self):
    """Get Montly Checked API"""
    data = request.args.to_dict()
    return get_monthly_checked(data)


@api.route('/schedules-commons/alarm')
class TodayAlarmList(Resource):
  def get(self):
    """Get Alarms List on Clicked date"""
    data = request.args.to_dict()
    return get_alarms_list(data)
  

@api.route('/check/today') 
class Check(Resource):
  def get(self):
    """Get Today Checked API"""
    data = request.args.to_dict()
    return get_today_checked(data)



