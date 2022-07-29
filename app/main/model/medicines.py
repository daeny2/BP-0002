from .. import db, flask_bcrypt
from app.main.model.schedules_common import Schedules_common

schedules_medicines = db.Table('schedules_medicines',
    db.Column('schedules_common_id', db.Integer, db.ForeignKey('schedules_common.id')),
    db.Column('medicines_id', db.Integer, db.ForeignKey('medicines.id'))
)

class Medicines(db.Model):
    # Medicines Model for detail info about each medicines and whos
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    image_dir = db.Column(db.String(100), nullable=True)
    effect = db.Column(db.Text, nullable=True)
    capacity = db.Column(db.Text, nullable=True)
    validity = db.Column(db.String(100), nullable=True)
    camera = db.Column(db.Boolean, nullable=False)

    timetotake = db.relationship('Schedules_common', secondary=schedules_medicines, backref=db.backref('ttt', lazy='dynamic'))


    def __repr__(self):
        return "<medicines '{}'>".format(self.name)
