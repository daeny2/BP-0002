from flask_restx import Api
from flask import Blueprint

from .main.controller.users import api as users
#from .main.controller.user_controller import api as users_ns


blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='FLASK RESTPLUS(RESTX) API BOILER-PLATE WITH JWT',
          version='1.0',
          description='a boilerplate for flask restplus (restx) web service'
          )

api.add_namespace(users, path="/users")