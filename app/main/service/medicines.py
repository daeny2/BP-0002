#-*- coding: utf-8 -*-
# medicines 테이블에 관련된 쿼리문 작성하는 파일
from flask import request, jsonify, redirect
from flask_restx import Resource, fields, marshal
from sqlalchemy import and_ , create_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from PIL import Image
from datetime import time
from operator import itemgetter
import json ,io
import jwt
import requests, bs4
from lxml import html
import xml.etree
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus, unquote

from app.main import db
from app.main.model.schedules_common import Schedules_common
from app.main.model.medicines import Medicines
from app.main.model.schedules_common import Schedules_common
from app.main.model.users import Users
from ..service.crawling import get_open_api_info
from ..config import jwt_key, jwt_alg , get_s3_connection, S3_BUCKET, S3_REGION, ProductionConfig #배포때는 여기를 ProductionConfig로 해주어야 합니다. 


def strToBool(s):
  return 1 if s=='true' else 0

def post_medicine(data):
  """Post medicine information"""
  try:  
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']

        if decoded_token:
          print('post medi:', user_id)
          """직접등록하는 약에 대한 분기 코드는 비활성화 하겠습니다만, 저의 노고가(저 혼자) 아까워서 삭제는 안할게용 ㅠㅠ"""
          #현재 로그인된 유저아이디 값으로 등록된 모든 약의 아이디 값을 가져옴
          # engine = create_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI) #배포때는 여기를 ProductionConfig.SQLALCHEMY_DATABASE_URI 로 해주어야 합니다. 
          # query_find_medi_id = text("""SELECT medicines_id FROM users_medicines WHERE users_id = :each_users_id""")
          # with engine.connect() as con:
          #   result = con.execute(query_find_medi_id, {'each_users_id': user_id})
          # medicines_id = [row[0] for row in result]

          # #그리고 유저가 등록한 약들 중, 카메라로 촬영되지 않은 약만 가져온다.
          # res = []
          # res_name = []
          # for medicine_id in medicines_id:
          #     saved_medi = Medicines.query.filter(and_(Medicines.id==medicine_id, Medicines.camera==0)).first()
          #     if saved_medi:
          #       saved = {saved_medi.name : medicine_id}
          #       #saved[saved_medi.name] = medicine_id
          #       res_name.append(saved_medi.name)
          #       res.append(saved)
          # print('res:', res)
          print('post medi:', data)
          medicine_ids = []
          for el in data:
            """카메라로 촬영된 경우에는, 유저 id 상관 없이(즉 다른 사람 user id로 등록된 약이더라도) 그냥 중복이 되면 안됩니다! 왜냐면 약에 대한 정보들은 공공API에서 불러오므로
            등록 유저 상관 없이 같은 약이면 모든 정보가 같을 것이니까요"""
            if el['camera']:
              saved_medi = Medicines.query.filter_by(name=el['name']).first()
              print('saved medi:', saved_medi)
              #카메라로 촬영된 약 정보가 이미 DB에 있다면 DB에 있는 id 값만 결과 list에 append
              if saved_medi:
                medicine_ids.append(saved_medi.id)
                print('check:',saved_medi)
              else:
                new_medicine = Medicines(
                  name=el['name'], 
                  title=el['title'],
                  image_dir=el['image_dir'],
                  effect=el['effect'],
                  capacity=el['capacity'],
                  validity=el['validity'],
                  camera=el['camera']
                  )
                db.session.add(new_medicine)
                db.session.commit()
                medicine_ids.append(new_medicine.id)

            else:       
              #아이디 값을 반복문을 돌면서, DB에서 해당하는 데이터를 가지고 나오고, DB에 저장된 약을 가상의 리스트에 저장
              # if el['name'] in res_name:
              #   for res_id in res:
              #     if el['name'] in res_id:
              #       medicine_ids.append(res_id[el['name']])
              new_medicine = Medicines(
                name=el['name'], 
                title=el['title'],
                image_dir=el['image_dir'],
                effect=el['effect'],
                capacity=el['capacity'],
                validity=el['validity'],
                camera=el['camera']
                )
              db.session.add(new_medicine)
              db.session.commit()
              medicine_ids.append(new_medicine.id)
              print(medicine_ids)
          response_object = {
            'status': 'OK',
            'message': 'Successfully post medicine information.',
            'medicine_id': medicine_ids
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


def post_schedules_common_medicines(data):
  """Post schedules_common_id | medicines_id in schedules_medicines table 
  Because that model exists, I wrote the query statement directly, not the ORM syntax.
  reference: https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/
  """
  try:
    schedules_common_id = data['schedules_common_id']
    req_medicines_id = data['medicines_id']
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']

        if decoded_token:
          engine = create_engine(ProductionConfig.SQLALCHEMY_DATABASE_URI)
          query = text("""SELECT medicines_id FROM schedules_medicines WHERE schedules_common_id = :each_schedules_common_id""")
          with engine.connect() as con:
            result = con.execute(query, {'each_schedules_common_id': schedules_common_id})
          res_medicine_ids = [row[0] for row in result]

          for medi_id in req_medicines_id: #client에서 전달준 약 id에 대해 반복문을 돌려서
            if medi_id not in res_medicine_ids: #client에서 전달준 약 id가 DB에서 가지고 있는 약 ID에 없으면 등록하기
              query_insert = text("""INSERT INTO schedules_medicines(schedules_common_id, medicines_id) VALUES (:each_schedules_common_id, :each_medicine_id)""")
              with engine.connect() as con:
                new_users_medicine = con.execute(query_insert, {'each_schedules_common_id': schedules_common_id, 'each_medicine_id': medi_id})

            response_object = {
              'status': 'OK',
              'message': 'Successfully post schedules_common_id, medicines_id in schedules_medicines table.',
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
      print(e)
      response_object = {
        'status': 'Internal Server Error',
        'message': 'Some Internal Server Error occurred.',
      }
      return response_object, 500

def delete_my_medicines(data):
  """ Delete my medicines API """
  try:
    medicine_id = data['id']
    print(medicine_id)
    try:
      token = request.headers.get('Authorization')
      decoded_token = jwt.decode(token, jwt_key, jwt_alg)
      user_id = decoded_token['id']
      if decoded_token:
        engine = create_engine(ProductionConfig.SQLALCHEMY_DATABASE_URI) #배포때는 여기를 ProductionConfig.SQLALCHEMY_DATABASE_URI 로 해주어야 합니다. 
        delete_schedules_medicines_query = text("""DELETE FROM schedules_medicines WHERE medicines_id =  :medicine_id""")
        delete_users_medicines_query = text("""DELETE FROM users_medicines WHERE medicines_id =  :medicine_id""")
        delete_medicine = text("""DELETE FROM medicines WHERE id = :medicine_id""")
        with engine.connect() as con:
          result = con.execute(delete_schedules_medicines_query, {'medicine_id': medicine_id})
          print('first Del:', result)
          result2 = con.execute(delete_users_medicines_query,{'medicine_id': medicine_id} )
          print('second Del:', result2)
          result3 = con.execute(delete_medicine,{'medicine_id': medicine_id} )
          print('third Del:', result3)

        response_object = {
            'status': 'OK',
            'message': 'Successfully delete this medicines.',
          }
        return response_object, 200
    except Exception as e:
      print("401 error: ", e)
      response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.',
      }
      return response_object, 401
  except Exception as e:
    response_object = {
      'status': 'Internal Server Error',
      'message': 'Some Internal Server Error occurred.',
    }
    return response_object, 500 


def upload_medicine(data):
  """ Upload medicine information"""
  try:
    try:
      token = request.headers.get('Authorization')
      decoded_token = jwt.decode(token, jwt_key, jwt_alg)
      user_id = decoded_token['id']
      if decoded_token:

        image = Image.open(data)
        buffer = io.BytesIO()

        image = image.convert("RGB")
        # 해당 코드는 os 환경에서만 필요합니다. 배포시에는 안드로이드 버전 확인후 없애도 될듯합니다.

        image.save(buffer, "JPEG")
        buffer.seek(0)
        s3_connection = get_s3_connection()
        s3_connection.put_object(
              Body        = buffer,
              Bucket      = 'medisharp',
              Key         = f"{data.filename}_L",
              ContentType = data.content_type,
              ACL = 'public-read'
          )
        print('check3') 

        image_L_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{data.filename}_L"

        #print(image_L_url)
        #return image_L_url, 200
        response_object = {
          'status': 'OK',
          'message': 'Successfully upload image to S3',
          'results' : image_L_url
        }
        return response_object, 200
        
    except Exception as e:
      response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.',
      }
      return response_object, 401
  except Exception as e:  
    response_object = {
      'status': 'Internal Server Error',
      'message': 'Some Internal Server Error occurred.',
    }
    return response_object, 500


def get_schedules_common_medicines(data):
  """Get Clicked day Medicines by schedules_common_id | medicines_id in schedules_medicines table 
  Because that model exists, I wrote the query statement directly, not the ORM syntax.
  reference: https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/
  """
  try:
    schedules_common_id = data['schedules_common_id']
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']
        if decoded_token:
          print('get medi:', user_id)
          topic_fields = {
            'name': fields.String(required=True),
            'camera':fields.Boolean(required=True),
            'image_dir': fields.String(required=True),
            'title': fields.String(required=True),
            'effect' : fields.String(required=True),
            'capacity' : fields.String(required=True),
            'validity' : fields.String(required=True),
            }
          results = [marshal(topic, topic_fields) for topic in Medicines.query.filter(Medicines.timetotake.any(id=schedules_common_id)).all()]
          print('get medi:',results)

          response_object = {
            'status': 'OK',
            'message': 'Successfully get clicked day medicines name.',
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


def post_users_medicines(data):
  """Post Users_id | medicines_id in schedules_medicines table"""
  try:
    req_medicines_id = data['medicines_id']
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']      
        if decoded_token:
          engine = create_engine(ProductionConfig.SQLALCHEMY_DATABASE_URI) #배포때는 여기를 ProductionConfig.SQLALCHEMY_DATABASE_URI 로 해주어야 합니다. 
          query = text("""SELECT medicines_id FROM users_medicines WHERE users_id = :each_users_id""")
                
          with engine.connect() as con:
            result = con.execute(query, {'each_users_id': user_id})
          res_medicine_ids = [row[0] for row in result]


          for medi_id in req_medicines_id: #client에서 전달준 약 id에 대해 반복문을 돌려서
            if medi_id not in res_medicine_ids: #client에서 전달준 약 id가 DB에서 가지고 있는 약 ID에 없으면 등록하기
              query_insert = text("""INSERT INTO users_medicines(users_id, medicines_id) VALUES (:each_users_id, :each_medicine_id)""")
              with engine.connect() as con:
                new_users_medicine = con.execute(query_insert, {'each_users_id': user_id, 'each_medicine_id': medi_id})
        

          response_object = {
            'status': 'OK',
            'message': 'Successfully post users_common_id, medicines_id in users_medicines table.',
            'results' : req_medicines_id
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
      print(e)
      response_object = {
        'status': 'Internal Server Error',
        'message': 'Some Internal Server Error occurred.',
      }
      return response_object, 500


def get_my_medicines():
  """ Get my medicines Information"""
  try:
    try:
      token = request.headers.get('Authorization')
      decoded_token = jwt.decode(token, jwt_key, jwt_alg)
      user_id = decoded_token['id']
      print(user_id)

      if decoded_token:
        #reference: https://stackoverflow.com/questions/12593421/sqlalchemy-and-flask-how-to-query-many-to-many-relationship
        topic_fields = {
          'id': fields.Integer(required=True),
          'name': fields.String(required=True),
          'camera': fields.Boolean(required=True),
          'image_dir': fields.String(required=True),
        }
        results = [marshal(topic, topic_fields) for topic in Medicines.query.filter(Medicines.taker.any(id=user_id)).all()]
        print('after res medi:', results)

        response_object = {
          'status': 'OK',
          'message': 'Successfully get my medicines.',
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
      response_object = {
        'status': 'Internal Server Error',
        'message': 'Some Internal Server Error occurred.',
      }
      return response_object, 500 

def get_my_medicines_info(data):
  """ Get my medicines Information by myself """
  try:
    camera = strToBool(data['camera'])
    name = data['name']
    medicine_id = data['id']
    print(data)
    print(data['camera'])
    print(camera)
    try:
      token = request.headers.get('Authorization')
      decoded_token = jwt.decode(token, jwt_key, jwt_alg)
      user_id = decoded_token['id']
      print(user_id)
      if decoded_token:
        if camera == 1: #camera가 true인 경우 image_dir, title, camera값은 Medicines DB에서, 나머지 validity, capacity, effect정보는 openAPI를 통해 가져옵니다. 
          topic_fields = {
            'title': fields.String(description='personal description for this medicines'),
            'image_dir': fields.String(description='medicine image file path'),
          }
          results = [marshal(topic, topic_fields) for topic in Medicines.query.filter(and_(Medicines.taker.any(id=user_id), Medicines.id==medicine_id, Medicines.camera==camera, Medicines.name==name)).all()]
          
          results[0].update(get_open_api_info(name)) #openAPI
          response_object = {
            'status': 'OK',
            'message': 'Successfully get my medicines.',
            'results': results
          }
          return response_object, 200
        else: #camera가 false인 경우 image_dir, title, camera, validity, capacity, effect정보를 Medicines DB에서 가져옵니다. 
          topic_fields = {
            'title': fields.String(description='personal description for this medicines'),
            'image_dir': fields.String(description='medicine image file path'),
            'effect': fields.String(description='medicine efficacy'),
            'capacity': fields.String(description='medicine dosage'),
            'validity': fields.String(description='medicine validity'),
          }
          results = [marshal(topic, topic_fields) for topic in Medicines.query.filter(and_(Medicines.taker.any(id=user_id), Medicines.id==medicine_id, Medicines.camera==camera, Medicines.name==name)).all()]
          response_object = {
            'status': 'OK',
            'message': 'Successfully get my medicines.',
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


def delete_my_medicines(data):
  """ Delete my medicines API """
  try:
    medicine_id = data['id']
    try:
      token = request.headers.get('Authorization')
      decoded_token = jwt.decode(token, jwt_key, jwt_alg)
      user_id = decoded_token['id']
      if decoded_token:
        engine = create_engine(ProductionConfig.SQLALCHEMY_DATABASE_URI) #배포때는 여기를 ProductionConfig.SQLALCHEMY_DATABASE_URI 로 해주어야 합니다. 
        delete_schedules_medicines_query = text("""DELETE FROM schedules_medicines WHERE medicines_id =  :medicine_id""")
        delete_users_medicines_query = text("""DELETE FROM users_medicines WHERE medicines_id =  :medicine_id""")
        delete_medicine = text("""DELETE FROM medicines WHERE id = :medicine_id""")
        with engine.connect() as con:
          result = con.execute(delete_schedules_medicines_query, {'medicine_id': medicine_id})
          result2 = con.execute(delete_users_medicines_query,{'medicine_id': medicine_id} )
          result3 = con.execute(delete_medicine,{'medicine_id': medicine_id} )
          
        response_object = {
            'status': 'OK',
            'message': 'Successfully delete this medicines.',
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
    print(e)
    response_object = {
      'status': 'Internal Server Error',
      'message': 'Some Internal Server Error occurred.',
    }
    return response_object, 500


def edit_my_medicines(data):
  """ Edit My Medicines API """
  try:
    medicine_id = data['id']
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']

        if decoded_token:
          edited_medicine = db.session.query(Medicines).filter(Medicines.id == medicine_id).update(data)
          db.session.commit()
          
          response_object = {
            'status': 'OK',
            'message': 'Successfully Edit My Medicines.',
            'results': edited_medicine
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

