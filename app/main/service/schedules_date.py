#-*- coding: utf-8 -*-
#schedules_date 테이블에 관련된 쿼리문 작성하는 파일
from flask import request, jsonify, redirect
from flask_restx import Resource, fields, marshal
from sqlalchemy import and_
import json
import jwt
import re
import datetime
from operator import itemgetter
from app.main import db
from app.main.model.schedules_date import Schedules_date
from app.main.model.schedules_common import Schedules_common
from app.main.model.users import Users
from ..config import jwt_key, jwt_alg
import re

class TimeFormat(fields.Raw):
    def format(self, value):
        return datetime.time.strftime(value, "%H:%M")


class DateFormat(fields.Raw):
    def format(self, value):
        return datetime.datetime.strftime(value, "%d")

def sorting_alarmdate_time(data):
  """ date로 오름차순 정렬 후 time으로 오름차순 정렬하는 함수 """
  data = sorted(data, key=itemgetter('alarmdate', 'time'))
  return data

def sorting_time(data):
  """ time으로 오름차순 정렬하는 함수 """
  data = sorted(data, key=itemgetter('time'))
  return data


def get_monthly_checked(data): 
  """ Get monthly checked API for calendar"""
  try: 
    start_day = datetime.datetime.strptime(data['start_day'], '%Y-%m-%d')
    end_day = datetime.datetime.strptime(data['end_day'], '%Y-%m-%d')

    try: 
      token = request.headers.get('Authorization')
      decoded_token = jwt.decode(token, jwt_key, jwt_alg)
      user_id = decoded_token['id']
      
      if decoded_token: 
        topic_fields = {
          'alarmdate': DateFormat(readonly=True, description='Date in DD', default='DD'),
          'time': TimeFormat(readonly=True, description='Time in HH:MM', default='HH:MM'),
          'check': fields.Boolean(required=True),
        }
        data = [marshal(topic, topic_fields) for topic in Schedules_date.query
                                                                        .filter(and_(Schedules_date.alarmdate>=start_day, Schedules_date.alarmdate<end_day, Schedules_date.user_id==user_id))
                                                                        .all()]
        results = sorting_alarmdate_time(data)
        print('test')
        response_object = {
          'status': 'OK',
          'message': 'Successfully get monthly checked.',
          'results': results
        }
        return response_object, 200
    except Exception as e:
      db.session.rollback()
      raise
      response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.',
      }
      return response_object, 401
    finally:
      db.session.close()
  except Exception as e:
    print(e)
    response_object = {
      'status': 'Internal Server Error',
      'message': 'Some Internal Server Error occurred.',
    }
    return response_object, 500


def get_alarms_list(data): 
  """ Get Alarms List on Clicked date for main page and calendar page"""
  try:
    alarmdate = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
    try:
      token = request.headers.get('Authorization')
      decoded_token = jwt.decode(token, jwt_key, jwt_alg)
      user_id = decoded_token['id']
      if decoded_token:
        """
        schedules_date와 schedules_common을 innerjoin하여서 
        schedules_date에서는 check, time
        schedules_common에서는 title, cycle, memo
        데이터를 가져와야한다. 
        """
        #data = db.session.query(Schedules_date.check, Schedules_date.id, Schedules_date.schedules_common_id, Schedules_date.time, Schedules_common.title, Schedules_common.cycle, Schedules_common.memo).filter(and_(Schedules_date.alarmdate==alarmdate, Schedules_date.user_id==user_id, Schedules_common.user_id==user_id)).all() 
        
        data = db.session.query(Schedules_common.id,Schedules_common.title, Schedules_common.cycle, Schedules_common.memo, Schedules_date.time, Schedules_date.check, Schedules_date.push).join(Schedules_common).filter(and_(Schedules_date.alarmdate==alarmdate, Schedules_date.user_id==user_id)).all()

        print(data)
        results = []
        for el in data:
          result = {}
          result['schedules_common_id'] = el.id
          result['title'] = el.title
          result['cycle'] = el.cycle
          result['memo'] = el.memo
          result['time'] = datetime.time.strftime(el.time, "%H:%M")
          result['check'] = el.check
          result['push'] = el.push
          results.append(result)

        results = sorting_time(results)
        response_object = {
          'status': 'OK',
          'message': 'Successfully Get Alarms List on Clicked date for main page and calendar page.',
          'results': results
        }
        return response_object, 200
    except Exception as e:
      db.session.rollback()
      raise
      print(e)
      response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.',
        }
      return response_object, 401
    finally:
      db.session.close()
  except Exception as e:
    response_object = {
      'status': 'Internal Server Error',
      'message': 'Some Internal Server Error occurred.',
    }
    return response_object, 500


def get_today_checked(data): 
  """ Get today checked API for calendar"""
  try: 
    start_day = datetime.datetime.strptime(data['start_day'], '%Y-%m-%d')
    end_day = datetime.datetime.strptime(data['end_day'], '%Y-%m-%d')
    try: 
      token = request.headers.get('Authorization')

      decoded_token = jwt.decode(token, jwt_key, jwt_alg)
      user_id = decoded_token['id']

      if decoded_token:
        print('get today checked')
        topic_fields = {
          'check': fields.Boolean(required=True),
        }
        data = [marshal(topic, topic_fields) for topic in Schedules_date.query
                                                                        .filter(and_(Schedules_date.alarmdate.between(start_day, end_day), Schedules_date.user_id==user_id))
                                                                        .all()]
                                                                        
        print(data)
        response_object = { 
          'status': 'OK', 
          'message': 'Successfully get today checked.',
          'results': data
        }
        return response_object, 200
    except Exception as e:
      db.session.rollback()
      raise
      response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.',
      }
      return response_object, 401
    finally:
      db.session.close()
  except Exception as e:
    response_object = {
      'status': 'Internal Server Error',
      'message': 'Some Internal Server Error occurred.',
    }
    return response_object, 500


def patch_check(data):
  """ Convert check False to True or True to False"""
  try:
    schedules_common_id = data['schedules_common_id']
    alarmdate = datetime.datetime.strptime(data['clickdate'], '%Y-%m-%d')
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']
        if decoded_token:
          #check가 true이면 false로, false이면 true로 update시켜주어야 하니까, 먼저 select 후 update하는 방식으로 진행
          this_schedules_date = db.session.query(Schedules_date).filter(and_(Schedules_date.schedules_common_id==schedules_common_id,Schedules_date.alarmdate==alarmdate,Schedules_date.user_id==user_id)).first()
          if this_schedules_date.check == True:
            this_schedules_date.check = False
          else:
            this_schedules_date.check = True
          db.session.commit()
          response_object = {
              'status': 'OK',
              'message': 'Successfully Convert check False to True or True to False.',
              'results' : {'check': this_schedules_date.check},
            }
          return response_object, 200
    except Exception as e:  
      print(e)
      db.session.rollback()
      raise
      response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.',
      }
      return response_object, 401
    finally:
      db.session.close()
  
  except Exception as e:
      response_object = {
        'status': 'Internal Server Error',
        'message': 'Some Internal Server Error occurred.',
      }
      return response_object, 500   