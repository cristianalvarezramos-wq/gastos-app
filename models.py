from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), default='usuario')

class RegistroAmbiental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ubicacion = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)
    temperatura = db.Column(db.Float, nullable=False)
    calidad_aire = db.Column(db.String(50))
    nivel_agua = db.Column(db.Float)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
