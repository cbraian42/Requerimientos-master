from utils.db import db


class Requerimiento (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    asunto = db.Column(db.String(255))
    codigo = db.Column(db.String(255))
    descripcion = db.Column(db.String(255))
    idDestinatario = db.Column(db.Integer)
    idEmisor = db.Column(db.Integer)
    estado = db.Column(db.String(255))
    fechaCierre = db.Column(db.DateTime)
    fechaYhora = db.Column(db.DateTime)
    prioridad = db.Column(db.String(255))
    idTipoRequerimiento = db.Column(db.Integer)
    idCategoriaRequerimiento = db.Column(db.Integer)
    tipoEmisor = db.Column(db.String(255))

    def __init__(self, asunto, codigo, descripcion, idDestinatario, idEmisor, estado, fechaCierre, fechaYhora, prioridad, idTipoRequerimiento, idCategoriaRequerimiento, tipoEmisor):
        self.asunto = asunto
        self.codigo = codigo
        self.descripcion = descripcion
        self.idDestinatario = idDestinatario
        self.idEmisor = idEmisor
        self.estado = estado
        self.fechaCierre = fechaCierre
        self.fechaYhora = fechaYhora
        self.prioridad = prioridad
        self.idTipoRequerimiento = idTipoRequerimiento
        self.idCategoriaRequerimiento = idCategoriaRequerimiento
        self.tipoEmisor = tipoEmisor
    
    # Cambiar el estado del objeto
    def modEstado(self, estado):
        self.estado = estado

    def requerimientosAcargo(idUsuario):
        requerimientos = Requerimiento.query.filter(Requerimiento.idDestinatario == idUsuario).all()
        return requerimientos
    
    def verRequerimiento(id):
        requerimiento = Requerimiento.query.filter_by(id=id).first()
        return requerimiento

class CategoriaRequerimiento(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    idTipo = db.Column(db.Integer)
    descripcion = db.Column(db.String(255))

    def __init__(self, descripcion, idTipo):
        self.descripcion = descripcion
        self.idTipo = idTipo

class TipoRequerimiento(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    codigo = db.Column(db.String(3))
    tipo = db.Column(db.String(255))

    def __init__(self, codigo, tipo):
        self.codigo = codigo
        self.tipo = tipo

class RelacionRequerimiento(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    idRequerimientoNuevo = db.Column(db.Integer)
    idRelacion = db.Column(db.Integer)

    def __init__ (self, idRequerimientoNuevo, idRelacion):
        self.idRequerimientoNuevo = idRequerimientoNuevo
        self.idRelacion = idRelacion

class Archivo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    #idRequerimiento = db.Column(db.Integer)
    nombre = db.Column(db.String(255))
    tipo = db.Column(db.String(255))#Requerimiento o comentario
    idTipo = db.Column(db.Integer)#ID del requerimiento o del comentario

    def __init__(self, nombre, tipo, idTipo):
        #self.idRequerimiento = idRequerimiento
        self.nombre = nombre
        self.tipo = tipo
        self.idTipo = idTipo

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    idRequerimiento = db.Column(db.Integer)
    accion = db.Column(db.String(255))
    fechaYhora = db.Column(db.DateTime)
    idUsuarioResponsable = db.Column(db.Integer)
    tipoUsuarioResponsable = db.Column(db.String(255))

    def __init__(self, idRequerimiento, accion, fechaYhora, idUsuarioResponsable, tipoUsuarioResponsable):
        self.idRequerimiento = idRequerimiento
        self.accion = accion
        self.fechaYhora = fechaYhora
        self.idUsuarioResponsable = idUsuarioResponsable
        self.tipoUsuarioResponsable = tipoUsuarioResponsable

    def verEventos():
        eventos = Evento.query.all()
        return eventos

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    idRequerimiento = db.Column(db.Integer)
    asunto = db.Column(db.String(50))
    descripcion = db.Column(db.String(5000)) #Se define como varchar en la base de datos
    fechaYhora = db.Column(db.DateTime)
    idUsuarioEmisor = db.Column(db.Integer)
    tipoUsuario = db.Column(db.String(255))
    idEvento = db.Column(db.Integer)

    def __init__(self, idRequerimiento, asunto, descripcion, fechaYhora, idUsuarioEmisor, tipoUsuario, idEvento):
        self.idRequerimiento = idRequerimiento
        self.asunto = asunto
        self.descripcion = descripcion
        self.fechaYhora = fechaYhora
        self.idUsuarioEmisor = idUsuarioEmisor
        self.tipoUsuario = tipoUsuario
        self.idEvento = idEvento

    def verComentarios():
        comentarios = Comentario.query.all()
        return comentarios
