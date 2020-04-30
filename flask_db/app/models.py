from . import db

class Plants(db.Model):
    __tablename__ = 'PLANTS'
    __table_args__ = { 'extend_existing' : True}
    id = db.Column(db.Integer,primary_key=True)
    plant = db.Column(db.String(100),unique=True)
    portal_name = db.Column(db.String(100))
    country_id = db.Column(db.Integer)
    ppc_meter_id = db.Column(db.Integer)
    pcc_meter_id = db.Column(db.Integer)
    inverter_id = db.Column(db.Integer)
    grid_code_id = db.Column(db.Integer)
    ppc_ip_id = db.Column(db.Integer)
    nominal_power = db.Column(db.Float)
    ppc_controller =db.Column(db.String(100))


class Countries(db.Model):
    __tablename__ = 'COUNTRIES'
    __table_args__ = { 'extend_existing' : True}
    id = db.Column(db.Integer,primary_key=True)
    country = db.Column(db.String(50),unique=True)

class Inverters(db.Model):
    __tablename__ = 'INVERTER_MODELS'
    __table_args__ = { 'extend_existing' : True}
    id = db.Column(db.Integer,primary_key=True)
    model = db.Column(db.String(100),unique=True)
    man_id = db.Column(db.Integer)

class Inverter_Mans(db.Model):
    __tablename__ = 'INVERTER_MANUFACTURERS'
    __table_args__ = { 'extend_existing' : True}
    id = db.Column(db.Integer,primary_key=True)
    manufacturer = db.Column(db.String(100),unique=True)

class Meters(db.Model):
    __tablename__ = 'METER_MODELS'
    __table_args__ = { 'extend_existing' : True}
    id = db.Column(db.Integer,primary_key=True)
    model = db.Column(db.String(100),unique=True)
    man_id = db.Column(db.Integer)

class Meter_Mans(db.Model):
    __tablename__ = 'METER_MANUFACTURERS'
    __table_args__ = { 'extend_existing' : True}
    id = db.Column(db.Integer,primary_key=True)
    manufacturer = db.Column(db.String(100),unique=True)

class IPs(db.Model):
    __tablename__ = 'IPS'
    __table_args__ = { 'extend_existing' : True}
    id = db.Column(db.Integer,primary_key=True)
    ip = db.Column(db.String(100),unique=True)
    plant_id = db.Column(db.Integer)


class Grid_Codes(db.Model):
    __tablename__ = 'GRID_CODES'
    __table_args__ = { 'extend_existing' : True}
    id = db.Column(db.Integer,primary_key=True)
    grid_code = db.Column(db.String(100),unique=True)
