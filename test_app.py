import pytest
from app import app, db
from models import Usuario, RegistroAmbiental
from werkzeug.security import generate_password_hash
import os

TEST_DB = 'test_terradata.db'

@pytest.fixture
def cliente():
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + TEST_DB,
        'SECRET_KEY': 'prueba_segura'
    })
    with app.test_client() as cliente:
        with app.app_context():
            db.create_all()
        yield cliente
        with app.app_context():
            db.drop_all()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_pagina_inicio(cliente):
    resp = cliente.get('/')
    assert resp.status_code == 200

def test_registro_usuario(cliente):
    datos = {'nombre':'Prueba','correo':'a@b.com','contrasena':'123456'}
    resp = cliente.post('/registro', data=datos, follow_redirects=True)
    assert b'Registro exitoso' in resp.data

def test_login_logout(cliente):
    with app.app_context():
        u = Usuario(nombre='T', correo='t@t.com', contrasena=generate_password_hash('123'))
        db.session.add(u)
        db.session.commit()
    cliente.post('/login', data={'correo':'t@t.com','contrasena':'123'})
    resp = cliente.get('/logout', follow_redirects=True)
    assert resp.status_code == 200

def test_crear_registro(cliente):
    with app.app_context():
        u = Usuario(nombre='T', correo='c@c.com', contrasena=generate_password_hash('123'))
        db.session.add(u)
        db.session.commit()
    cliente.post('/login', data={'correo':'c@c.com','contrasena':'123'})
    datos = {'ubicacion':'Lima','temperatura':22.5,'calidad_aire':'Buena','nivel_agua':1.2}
    resp = cliente.post('/registros/nuevo', data=datos, follow_redirects=True)
    assert b'guardado' in resp.data
