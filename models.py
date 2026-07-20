from extensions import db, bcrypt


# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'supervisor'), default='supervisor')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Zone(db.Model):
    __tablename__ = 'zones'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False)
    status = db.Column(db.Enum('safe', 'alert', 'evacuated', 'offline'), default='safe')
    zone = db.relationship('Zone', backref='workers')


class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False)
    gas_level = db.Column(db.DECIMAL(6, 2))
    temp = db.Column(db.DECIMAL(5, 2))
    humidity = db.Column(db.DECIMAL(5, 2))
    timestamp = db.Column(db.DateTime)


class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False)
    reading_id = db.Column(db.Integer, db.ForeignKey('sensor_readings.id'), nullable=False)
    severity = db.Column(db.Enum('low', 'medium', 'high', 'critical'))
    message = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    resolved = db.Column(db.Boolean, default=False)
