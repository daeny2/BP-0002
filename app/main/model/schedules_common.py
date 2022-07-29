from .. import db

class Schedules_common(db.Model):
        # Schedules_common Model for bundle of each alarms related (prescribed) medication
        __tablename__ = "schedules_common"

        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        memo = db.Column(db.String(100), nullable=True)
        startdate = db.Column(db.String(100), nullable=True)
        enddate = db.Column(db.String(100), nullable=True)
        cycle = db.Column(db.Integer, nullable=True)

        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

        schedules_dates = db.relationship('Schedules_date', backref='schedules_codate', lazy=True)

        def __repr__(self):
            return "<schedules_common '{}'>".format(self.title)