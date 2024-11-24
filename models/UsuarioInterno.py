from utils.db import db

#TIPO DE USUARIO
class UsuarioInterno(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    legajo = db.Column(db.Integer)
    nombre = db.Column(db.String(255))
    usuario = db.Column(db.String(255))
    contrasena = db.Column(db.String(255))
    correo = db.Column(db.String(255))
    cargo = db.Column(db.String(255))
    departamento = db.Column(db.String(255))
    tipoUsuario = db.Column(db.String(255))

    def __init__(self, legajo, nombre, usuario, contrasena, correo, tipoUsuario, cargo, departamento):
        self.legajo = legajo
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena = contrasena
        self.correo = correo
        self.tipoUsuario = tipoUsuario
        self.cargo = cargo
        self.departamento = departamento
        
    def verInternos():
        internos = UsuarioInterno.query.all()
        return internos

    def verInterno(id):
        interno = UsuarioInterno.query.filter_by(id=id).first()
        return interno
    
    def verCorreo(id):
        interno = UsuarioInterno.query.filter_by(id=id).first()
        correo = interno.correo
        return correo