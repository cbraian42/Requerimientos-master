from utils.db import db

class UsuarioExterno(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(255))
    usuario = db.Column(db.String(255))
    contrasena = db.Column(db.String(255))
    correo = db.Column(db.String(255))
    tipoUsuario = db.Column(db.String(255))
    cuil = db.Column(db.BigInteger)
    descripcion = db.Column(db.String(255))
    destacado = db.Column(db.String(255))
    empresa = db.Column(db.String(255))

    def __init__(self, nombre, usuario, contrasena, correo, tipoUsuario, cuil, descripcion, destacado, empresa):
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena = contrasena
        self.correo = correo
        self.tipoUsuario = tipoUsuario
        self.cuil = cuil
        self.descripcion = descripcion
        self.destacado = destacado
        self.empresa = empresa

    def verExternos():
        externos = UsuarioExterno.query.all()
        return externos
