import flask
from flask import request, redirect, jsonify, make_response, render_template
from flask_restx import Resource
from werkzeug.utils import secure_filename
import tensorflow as tf
from keras.models import load_model
from keras.applications import ResNet50, imagenet_utils
from keras.preprocessing.image import img_to_array
from PIL import Image
import requests

from ..service.medicines import post_medicine, post_schedules_common_medicines, upload_medicine , get_schedules_common_medicines, post_users_medicines, get_my_medicines, get_my_medicines_info, delete_my_medicines, edit_my_medicines

import numpy as np
# import cv2
import os
import sys
import io
import jwt

from ..config import jwt_key, jwt_alg
from ..util.dto import MedicineDto
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from cnn.class_list import get_class_list

interpreter = None

#Load TFLite model and allocate tensors.
def load_model():
  global interpreter
  currdir = os.getcwd()
  print("currdir: ", currdir)
  modeldir = os.path.join(currdir+"/cnn/model/medisharp_tflite_model.tflite")
  interpreter = tf.lite.Interpreter(model_path=modeldir)

print(("* Loading Keras model and Flask starting server..."
		"please wait until server has fully started"))
load_model()

api = MedicineDto.api
# _medicines = MedicineDto.medicines

def prepare_image(image, target):
	if image.mode != "RGB":
		image = image.convert("RGB")
	image = image.resize(target)
	image = img_to_array(image)
	image = np.expand_dims(image, axis=0)
	return image

@api.route('/image')
class PredictMedicineName(Resource):
  def post(self):
    """카메라로 촬영한 이미지를 서버로 보내오고, 학습된 모델에서 예측결과를 client에게 전달해주는 API"""
    try: 
      class_list =  get_class_list()
      try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, jwt_key, jwt_alg)
        user_id = decoded_token['id']
        if decoded_token: 
          if 'image' not in request.files:
            response_object = {
            'status': 'Bad Request',
            'message': 'No File Part.',
            }
            return response_object, 400
          file = request.files['image']
          if file.filename == '':
            response_object = {
              'status': 'Bad Request',
              'message': 'No Selected File.',
              }
            return response_object, 400
          elif file and file.filename:
            interpreter.allocate_tensors()
            #Get input and output tensors.
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            #Ready for the Data
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image))
            image = prepare_image(image, target=(224, 224))
            #input
            interpreter.set_tensor(input_details[0]['index'], image)
            interpreter.invoke()
            #output
            output_data = interpreter.get_tensor(output_details[0]['index'])
            
            pred_class = np.argmax(output_data, axis=-1)
            prediction_result = class_list[int(pred_class)]
            print("prediction: ", class_list[int(pred_class)])
            
            response_object = {
              'status': 'OK',
              'message': 'Successfully predict image class.',
              'prediction': prediction_result
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


@api.route('')
class Medicine(Resource):
  def get(self):
    data = request.args.to_dict()
    if data:
      """Get Clicked day Medicines Through Schedules-medicines API"""
      return get_schedules_common_medicines(data)
    else:
      """Get My Medicine API"""
      return get_my_medicines()

  def post(self):
    """Post Medicine API"""
    data = request.get_json().get('medicine') 
    return post_medicine(data)

  def patch(self):
    """Edit My Medicine API"""
    data = request.get_json().get('medicine') 
    return edit_my_medicines(data)

  def delete(self):
    """Delete User Medicine API"""
    data = request.args.to_dict()
    return delete_my_medicines(data)


@api.route('/upload')
class UploadMedicine(Resource):
  def post(self):
    """Upload Medicine API"""
    print("request: ", request.files)
    if 'image' not in request.files:
      print('No File Part')
    file = request.files['image']
    if file.filename == '':
      print('No Selected File')
    elif file and file.filename:
      filename = secure_filename(file.filename)
      filestr = request.files['image'].read()
      print('file:',file)
      print('filename:',filename)
      print('type:',file.content_type)
      #print('filestr:',filestr)
      return upload_medicine(file)

@api.route('/users-medicines')
class PostUsersMedicines(Resource):
  def post(self):
    """Post Users Medicines API"""
    data = request.get_json().get('medicines')
    return post_users_medicines(data)

@api.route('/schedules-medicines')
class SchedulesCommonMedicines(Resource):
  # def get(self):
  #   """Get Clicked day Medicines Through Schedules-medicines API"""
  #   data = request.args.to_dict()
  #   return get_schedules_common_medicines(data)

  def post(self):
    """Post Schedules Common Medicines API"""
    data = request.get_json().get('schedules_common_medicines')
    return post_schedules_common_medicines(data)

@api.route('/name')
class GetMyMedicineInfo(Resource):
  def get(self):
    """Get My Medicines Info API"""
    """현재(2020/12/14)API 문서에 있는 Get My Medicine_camera_info와 Get My Medicine_write_info의 uri를 합쳐준 것입니다.
    camera의 true/false에 따라 service 의 get_my_medicines_info 코드 분기가 이루어집니다. """
    data = request.args.to_dict()
    return get_my_medicines_info(data)