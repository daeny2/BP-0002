from .. import db, flask_bcrypt
from app.main.model.medicines import Medicines

users_medicines = db.Table('users_medicines',
    db.Column('users_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('medicines_id', db.Integer, db.ForeignKey('medicines.id'))
)

class Users(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(100), nullable=False)
    
    mymedicines = db.relationship('Medicines', secondary=users_medicines, backref=db.backref('taker', lazy='dynamic'))
    schedules_dates = db.relationship('Schedules_date', backref='schedules_udate', lazy=True)
    schedules_commons = db.relationship('Schedules_common', backref='schedules_ucommon', lazy=True)

    
    def __init__(self, full_name, email, password, mobile, login):
        self.full_name = full_name
        self.email = email
        self.password = flask_bcrypt.generate_password_hash(password)
        self.mobile = flask_bcrypt.generate_password_hash(mobile)
        self.login = login
        

    def __repr__(self):
        return "<users '{}'>".format(self.full_name)
