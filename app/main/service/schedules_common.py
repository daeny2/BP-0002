#-*- coding: utf-8 -*-
# medicines 테이블에 관련된 쿼리문 작성하는 파일
from flask import request, jsonify, redirect
from flask_restx import Resource, fields, marshal
from sqlalchemy import and_
import json
import jwt
import datetime
from operator import itemgetter
from app.main import db
from app.main.model.schedules_common import Schedules_common
from app.main.model.schedules_date import Schedules_date
from app.main.model.users import Users
from ..config import jwt_key, jwt_alg
import re

def post_schedules_common(data):
  """ Post Common information of alarm"""
  try:
    try: 
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']
        if decoded_token:
          new_schedules_common = Schedules_common(
            title=data['title'], 
            memo=data['memo'],
            startdate=data['startdate'],
            enddate=data['enddate'],
            cycle=data['cycle'],
            user_id=user_id,
            )
          db.session.add(new_schedules_common)
          db.session.commit()
          
          results = {
            "new_schedules_common_id": new_schedules_common.id
          }
          response_object = {
            'status': 'OK',
            'message': 'Successfully Post Common information of alarm.',
            'results': results
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

def edit_schedules_common(data):
  """ Edit Common information of alarm"""
  try:
    schedules_common_id = data['schedules_common_id']
    try: 
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']
        if decoded_token:
          # 1. 전체 데이터 넘어오고 서버에서 변경된 것만 update 해주는 경우
          #우선 저장되어있는 데이터 select 해오기
          topic_fields = {
            'title' : fields.String(required=True),
            'startdate': fields.String(required=True),
            'enddate': fields.String(required=True),
            'cycle': fields.Integer(required=True),
            'memo': fields.String(required=True),
          }
          saved_schedule = [marshal(topic, topic_fields) for topic in Schedules_common.query.filter(and_(Schedules_common.id==schedules_common_id, Schedules_common.user_id==user_id)).all()]
          print(saved_schedule[0])
          # 전달받아온 데이터를 for 문을 돌면서, 해당 DB에서 대조하지 않아도 되는 키값은 제외하고, 각 value 비교해서 달라진 경우만 update
          for key in data.keys():
            if not key == "schedules_common_id" and not key == "time":
              if not data[key] == saved_schedule[0][key]:
                schedules_common = Schedules_common.query.filter_by(id =schedules_common_id).update({key: data[key]})
                db.session.commit()

          response_object = {
            'status': 'OK',
            'message': 'Successfully Edit Common information of alarm.',
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


def post_schedules_date(data):
  """ Post Schedules Date API"""
  try:
    # medicine_id = data['medicines_id']
    schedules_common_id = data['schedules_common_id']
    startdate=datetime.datetime.strptime(data['startdate'], '%Y-%m-%d')
    enddate=datetime.datetime.strptime(data['enddate'], '%Y-%m-%d')
    cycle=data['cycle']
    time = data['time']
    push_list = data['pushArr']
    print(data)

    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']

        if decoded_token:
          print(user_id)

          #result = db.session.query(Schedules_common.startdate, Schedules_common.enddate, Schedules_common.cycle).filter(and_(Schedules_common.id==schedules_common_id, Schedules_common.user_id==user_id)).all() 
          #일단 startdate, enddate 형변환 
          #print(result)
          #print(result[0])
          # startdate = datetime.datetime.strptime(result[0].startdate, '%Y-%m-%d')
          # enddate = datetime.datetime.strptime(result[0].enddate, '%Y-%m-%d')
          # cycle = result[0].cycle #2
          #print(startdate, enddate, cycle)
          
          #비교연산자로 기저조건을 걸어주고 주기 계산
          currdate = startdate
          i = 0
          while currdate <= enddate:
            #이를 schedules_date 테이블에 넣어주기
            new_schedules_date = Schedules_date(
              alarmdate = currdate,
              time = time,
              check = 0,
              push = push_list[i],
              user_id = user_id,
              schedules_common_id = schedules_common_id
            )
            db.session.add(new_schedules_date)
            db.session.commit()
            currdate = currdate + datetime.timedelta(days=cycle)
            i = i+1

          #response는 medicine_id와 schedules_common_id

          response_object = {
            'status': 'OK',
            'message': 'Successfully post schedules date.',
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

def edit_schedules_date(data):
  """ Edit Schedules Date API"""
  try:
    cycle = data['cycle']
    schedules_common_id = data['schedules_common_id']
    startdate=datetime.datetime.strptime(data['startdate'], '%Y-%m-%d')
    enddate=datetime.datetime.strptime(data['enddate'], '%Y-%m-%d')
    time = data['time']
    push_list = data['pushArr']
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']

        if decoded_token:
          #오늘날짜
          now = datetime.datetime.now()
          today = now.strftime('%Y-%m-%d') #오늘자 기준으로 for loop 돌리기
          currdate = datetime.datetime.strptime(today, '%Y-%m-%d')
          print(currdate)
          # 1. 우선 DB내에서 오늘이후의 schedules_date 지우기
          while currdate <=enddate:
            saved_schedule = Schedules_date.query.filter(and_(Schedules_date.alarmdate==currdate, Schedules_date.schedules_common_id==schedules_common_id)).first()
            if saved_schedule:
              print('delete:',saved_schedule)
              db.session.delete(saved_schedule)
            currdate = currdate + datetime.timedelta(days=1)

          #그리고 오늘 이후 부터 새로운 cycle/time 적용해서 일정 재등록
          currdate_new = datetime.datetime.strptime(today, '%Y-%m-%d')
          print(currdate_new)
          
          #schedule_common에 등록된 startdate로 부터 주기대로 계산하다가 오늘이 넘는 날짜부터 새로 등록하기
          currdate_for_cal = startdate
          i=0
          while currdate_for_cal <= enddate:
            if currdate_for_cal >= currdate_new:
              print('save:',currdate_for_cal)
              #이를 schedules_date 테이블에 넣어주기
              new_schedules_date = Schedules_date(
                alarmdate = currdate_for_cal,
                time = time,
                check = 0,
                push = push_list[i],
                user_id = user_id,
                schedules_common_id = schedules_common_id
              )
              db.session.add(new_schedules_date)
              db.session.commit()
            currdate_for_cal = currdate_for_cal + datetime.timedelta(days=cycle)
            i = i+1
            #print(currdate_for_cal)

          #response는 medicine_id와 schedules_common_id

          response_object = {
            'status': 'OK',
            'message': 'Successfully post schedules date.',
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


def get_schedules_common(data):
  """ Get Common information of alarm"""
  try:
    schedules_common_id =data['schedules_common_id']

    try: 
      token = request.headers.get('Authorization')
      decoded_token = jwt.decode(token, jwt_key, jwt_alg)
      user_id = decoded_token['id']

      if decoded_token:
        topic_fields = {
          'startdate': fields.String(required=True),
          'enddate': fields.String(required=True),
          
        }
        res_date = [marshal(topic, topic_fields) for topic in Schedules_common.query
                                                                        .filter(and_(Schedules_common.id == schedules_common_id,Schedules_common.user_id==user_id))
                                                                        .all()]
        push_res = db.session.query(Schedules_date.push).filter_by(schedules_common_id =schedules_common_id).all()
        push_list = []
        for push in push_res:
          push_list.append(push[0])
        print(push_list)
        results = []
        result = {
          'schedules_common_id' : schedules_common_id,
          'title' : data['title'],
          'startdate': res_date[0]['startdate'],
          'enddate': res_date[0]['enddate'],
          'cycle': data['cycle'],
          'memo': data['memo'],
          'time': data['time'],
          'check': data['check'],
          'push_list' : push_list
        }
        results.append(result)
        response_object = {
          'status': 'OK',
          'message': 'Successfully get schedule common info.',
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
    print(e)
    response_object = {
      'status': 'Internal Server Error',
      'message': 'Some Internal Server Error occurred.',
    }
    return response_object, 500

def delete_all_schedules(data):
  """ delete_all_schedules API"""
  try:
    schedules_common_id = data['schedules_common_id']
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']

        if decoded_token:
          results_date = Schedules_date.query.filter_by(schedules_common_id=schedules_common_id).all() 
          print(results_date)
          for res in results_date:
            db.session.delete(res)
          results_common = Schedules_common.query.filter_by(id=schedules_common_id).first()
          db.session.delete(results_common)
          db.session.commit()

          response_object = {
            'status': 'OK',
            'message': 'Successfully delete all schedules common and date.',
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


def delete_clicked_schedules(data):
  """ Post Schedules Date API"""
  try:
    schedules_common_id = data['schedules_common_id']
    clicked_day = data['date']

    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']

        if decoded_token:
          results_date = Schedules_date.query.filter(and_(Schedules_date.schedules_common_id==schedules_common_id, Schedules_date.alarmdate==clicked_day)).first() 
          db.session.delete(results_date)
          db.session.commit()

          response_object = {
            'status': 'OK',
            'message': 'Successfully delete clicked day schedules common and date.',
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

