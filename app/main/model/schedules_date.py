from .. import db
from datetime import datetime

class Schedules_date(db.Model):
    """ Schedules_date Model for each alarms related (prescribed) medication """
    __tablename__ = "schedules_date"

    id = db.Column(db.Integer, primary_key=True)
    alarmdate = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    check = db.Column(db.Boolean, nullable=False)
    push = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    schedules_common_id = db.Column(db.Integer, db.ForeignKey('schedules_common.id'), nullable=False)

    def __repr__(self):
        return "<schedules_date '{}'>".format(self.id)