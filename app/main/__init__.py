#요기는 2번으로 한번 스쳐지나가주고 본격적으로 라우팅을 위해 app/__init__.py 로 갑니다

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from .config import config_by_name

db = SQLAlchemy()
flask_bcrypt = Bcrypt()


def create_app(config_name):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_by_name[config_name])
    app.config['JSON_AS_ASCII'] = False
    db.init_app(app)
    flask_bcrypt.init_app(app)

    return app