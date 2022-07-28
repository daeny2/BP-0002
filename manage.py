#서버 실행시 여기가 1번 실행 입니다. 그릐고 main/__init__.py로 가요
import os
import unittest

# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import blueprint
from app.main import create_app, db
from app.main.model import users, medicines, schedules_common, schedules_date

app = create_app(os.getenv('BOILERPLATE_ENV') or 'dev')
app.register_blueprint(blueprint)
app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def run():
    app.run()

@manager.command
def test():

    my_users = users.Users(full_name='Testing', email='sample@gmail.com', password='test@2022', mobile='010-1234-5678', login='basic')
    db.session.add(my_users)
    db.session.commit()

if __name__ == '__main__':
    manager.run()