from flask import Flask, render_template, request, redirect, url_for, Blueprint, session, send_from_directory, abort
from models.Requerimiento import Requerimiento, Comentario, Evento, CategoriaRequerimiento, TipoRequerimiento, Archivo, RelacionRequerimiento
from models.UsuarioInterno import UsuarioInterno
from models.UsuarioExterno import UsuarioExterno
from werkzeug.utils import secure_filename
from utils.db import db
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Define el blueprint
requerimiento = Blueprint('requerimiento', __name__)

# Define la ruta del blueprint de REQUERIMIENTO
@requerimiento.route('/requerimiento/nuevo')
def nuevoRequerimiento():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True:
        return redirect(url_for('auth.indexLogin'))
    ubicacion = "Requerimiento"
    nombre = session.get('user_nombre')
    tipoUsuario = session.get('user_tipo')
    requerimientos = Requerimiento.query.all()
    categoriasRequerimientos = CategoriaRequerimiento.query.all()
    tiposRequerimientos = TipoRequerimiento.query.all()
    usuariosInternos = UsuarioInterno.query.all()
    usuariosExternos = UsuarioExterno.query.all()
    reqExternos = Requerimiento.query.filter_by(tipoEmisor="Externo").all()
    tipoEmisor = session.get('user_tipo')
    idEmisor = session.get('user_id')
    #BUSCAR ID DE EMISOR POR CODIGO
    return render_template('/requerimientos/nuevo.html',
                            requerimientos = requerimientos,
                            categoriasRequerimientos = categoriasRequerimientos,
                            tiposRequerimientos = tiposRequerimientos,
                            usuariosInternos = usuariosInternos,
                            usuariosExternos = usuariosExternos,
                            tipoEmisor = tipoEmisor,
                            idEmisor = idEmisor,
                            reqExternos = reqExternos,
                            nombre = nombre,
                            tipoUsuario = tipoUsuario,
                            ubicacion = ubicacion)

@requerimiento.route('/requerimiento/registrar', methods= ['POST'])
def registrarRequerimiento():
    # Si no está iniciada la sesión, lo redirijo al login
    if session.get('user_active') != True:
        return redirect(url_for('auth.indexLogin'))

    # Obtengo los datos del formulario
    idTipoRequerimiento = request.form.get('idTipo')
    idCategoriaRequerimiento = request.form.get('idCategoria')
    idDestinatario = request.form.get('idDestinatario')
    if idDestinatario == '':
        idDestinatario = None
    prioridad = request.form.get('prioridad')

    # Determino el estado del requerimiento
    estado = "Asignado" if idDestinatario else "Abierto"

    # Obtener datos del emisor y fecha
    idEmisor = session.get('user_id')
    tipoEmisor = session.get('user_tipo')
    fechaYhora = datetime.now().strftime("%Y-%m-%d %H:%M")
    fechaCierre = None

    # Obtener asunto y descripción
    asunto = request.form.get('asunto', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    # Obtener el id más alto de requerimiento
    max_id = db.session.query(db.func.max(Requerimiento.id)).scalar() or 0
    nuevo_id = str(max_id + 1).zfill(10)  # Asegura que tenga 10 dígitos
    año = datetime.now().year
    codigo = f"{idTipoRequerimiento}-{año}-{nuevo_id}"

    # Crear nuevo requerimiento
    nuevo_requerimiento = Requerimiento(asunto, codigo, descripcion, idDestinatario, idEmisor, estado, fechaCierre, fechaYhora, prioridad, idTipoRequerimiento, idCategoriaRequerimiento, tipoEmisor)

    # Agregar a la base de datos
    db.session.add(nuevo_requerimiento)
    db.session.commit()
    idRequerimiento = nuevo_requerimiento.id

    # Manejo de archivos
    if 'archivos' in request.files:
        archivos = request.files.getlist('archivos')
        upload_folder = 'statics/img/archivos'
        # Si no existe la carpeta, se crea
        os.makedirs(upload_folder, exist_ok=True)  

        for archivo in archivos:
            # Comprobar si el archivo tiene un nombre y si es un tipo permitido
            if archivo and '.' in archivo.filename and archivo.filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx', 'xls', 'xlsx'}:
                # Obtener el nombre seguro del archivo
                original_filename = secure_filename(archivo.filename)
                # Crear un nuevo nombre con el ID del requerimiento
                nombre = f"{nuevo_requerimiento.id}_{original_filename}"
                archivo.save(os.path.join(upload_folder, nombre))  # Guarda el archivo

                # Crear Archivo
                nuevo_archivo = Archivo(nuevo_requerimiento.id, nombre)
                db.session.add(nuevo_archivo)

        db.session.commit()

    # Manejo de vinculación con otro requerimiento
    idRequerimientoExistente = request.form.get('idRequerimiento')
    if idRequerimientoExistente:
        try:
            idRequerimientoExistente = int(idRequerimientoExistente)
            relacionRequerimiento = RelacionRequerimiento(nuevo_requerimiento.id, idRequerimientoExistente)
            db.session.add(relacionRequerimiento)
            db.session.commit()
        except ValueError:
            return "ID de requerimiento existente no válido.", 400
    
    # Creacion del evento
    idUsuarioResponsable = session.get('user_id')
    tipoUsuarioResponsable = session.get('user_tipo')
    accion = "Alta de Requerimiento" 
    evento = Evento(idRequerimiento , accion, fechaYhora, idUsuarioResponsable, tipoUsuarioResponsable)
    db.session.add(evento)
    db.session.commit()

    # Envio de correo
    # Función para cargar la plantilla y reemplazar variables
    def cargar_plantilla(ruta_plantilla, **kwargs):
        with open(ruta_plantilla, 'r') as archivo:
            plantilla = archivo.read()
        # Reemplazar las variables en la plantilla
        for clave, valor in kwargs.items():
            plantilla = plantilla.replace(f"{{{{{clave}}}}}", str(valor))
        return plantilla

    # Datos del correo
    asunto = "Registro de requerimiento"
    mensaje = "Este es un mensaje de prueba"

    # Cargar la plantilla HTML y reemplazar variables
    categorias = CategoriaRequerimiento.query.all()
    for cat in categorias:
        if cat.id == idCategoriaRequerimiento:
            categoria = categoria.nombre
    tipos = TipoRequerimiento.query.all()
    for tip in tipos:
        if tip.id == idTipoRequerimiento:
            tipo = tip.nombre
    tipo = "Requerimiento de hardware"
    categoria = "Solicitud nuevo hardware"
    print(tipo)
    html = cargar_plantilla('templates/emails/nuevoRequerimiento.html', asunto=asunto, mensaje=mensaje, codigo=codigo, tipo=tipo, categoria=categoria, descripcion = descripcion)
    # Obtengo el correo del emisor
    if tipoEmisor == "Interno":
        emisor = UsuarioInterno.query.get(idEmisor)
        correo = emisor.correo
    elif tipoEmisor == "Externo":
        emisor = UsuarioExterno.query.get(idEmisor)
        correo = emisor.correo
    print(correo)
    # Configuración del servidor SMTP
    servidor = smtplib.SMTP("smtp.gmail.com", 587)
    servidor.starttls()
    servidor.login("aguspascual2001@gmail.com", "isqy rsxw laps hnqq")

    # Crear el mensaje con formato HTML
    msg = MIMEMultipart("alternative")
    msg["From"] = "aguspascual2001@gmail.com"
    msg["To"] = correo
    msg["Subject"] = asunto

    # Adjuntar el mensaje en formato HTML
    parte_html = MIMEText(html, "html")
    msg.attach(parte_html)

    # Enviar el correo
    servidor.sendmail("aguspascual2001@gmail.com", correo, msg.as_string())

    # Cerrar la conexión con el servidor SMTP
    servidor.quit()
    return redirect(url_for('requerimiento.misSolicitudes'))

@requerimiento.route('/cerrarRequerimiento', methods= ['POST'])
def cerrarRequerimiento():
    id_requerimiento = request.form['idRequerimiento']
    requerimiento = Requerimiento.query.filter_by(id=id_requerimiento).one()
    requerimiento.modEstado("Cerrado")
    requerimiento.idEmisor = None
    db.session.commit()
    return redirect(url_for('requerimiento.misSolicitudes'))

@requerimiento.route('/MisSolicitudes')
def misSolicitudes():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True:
        return redirect(url_for('auth.indexLogin'))
    ubicacion = "MisSolicitudes"
    nombre = session.get('user_nombre')
    tipoUsuario = session.get('user_tipo')
    user_id = session.get('user_id')
    if tipoUsuario == "Interno":
        usuarios = UsuarioInterno.query.all()
    elif tipoUsuario == "Externo":
        usuarios = UsuarioExterno.query.all()
    internos = UsuarioInterno.query.all()
    externos = UsuarioExterno.query.all()
    requerimientos = Requerimiento.query.filter(Requerimiento.idEmisor == user_id, Requerimiento.tipoEmisor == tipoUsuario).all()
    tiposRequerimientos = TipoRequerimiento.query.all()
    catRequerimientos = CategoriaRequerimiento.query.all()
    comentarios = Comentario.query.all()
    eventos = Evento.query.filter(Requerimiento.idEmisor == user_id, Requerimiento.tipoEmisor == tipoUsuario).all()
    for req in requerimientos:
        req.archivos = Archivo.query.filter(Archivo.idRequerimiento == req.id).all()
    return render_template('/requerimientos/misSolicitudes.html',
                           requerimientos = requerimientos,
                           tiposRequerimientos = tiposRequerimientos,
                           catRequerimientos = catRequerimientos,
                           usuarios = usuarios,
                           nombre = nombre,
                           tipoUsuario = tipoUsuario,
                           eventos = eventos,
                           comentarios = comentarios,
                           internos = internos,
                           externos = externos,
                           ubicacion = ubicacion)

@requerimiento.route('/solicitudesAcargo')
def solicitudesAcargo():
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    ubicacion = "Requerimiento"
    nombre = session.get('user_nombre')
    idUsuario = session.get('user_id')
    tipoUsuario = session.get('user_tipo')
    requerimientos = Requerimiento.requerimientosAcargo(idUsuario)
    tiposRequerimientos = TipoRequerimiento.query.all()
    catRequerimientos = CategoriaRequerimiento.query.all()
    internos = UsuarioInterno.verInternos()
    externos = UsuarioExterno.verExternos()
    comentarios = Comentario.verComentarios()
    eventos = Evento.verEventos()
    # Obtener archivos asociados a cada requerimiento
    for req in requerimientos:
        req.archivos = Archivo.query.filter(Archivo.idRequerimiento == req.id).all()

    return render_template('/requerimientos/solicitudesAcargo.html',
                           requerimientos = requerimientos,
                           tiposRequerimientos = tiposRequerimientos,
                           catRequerimientos = catRequerimientos,
                           internos = internos,
                           externos = externos,
                           nombre = nombre,
                           tipoUsuario = tipoUsuario,
                           comentarios = comentarios,
                           eventos = eventos,
                           ubicacion = ubicacion)

@requerimiento.route('/verSolicitudes')
def verSolicitudes():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    ubicacion = "Requerimiento"
    nombre = session.get('user_nombre')
    tipoUsuario = session.get('user_tipo')
    requerimientos = Requerimiento.query.all()
    tiposRequerimientos = TipoRequerimiento.query.all()
    catRequerimientos = CategoriaRequerimiento.query.all()
    internos = UsuarioInterno.query.all()
    externos = UsuarioExterno.query.all()
    comentarios = Comentario.query.all()
    eventos = Evento.query.all()
    # Obtener archivos asociados a cada requerimiento
    for req in requerimientos:
        req.archivos = Archivo.query.filter(Archivo.idRequerimiento == req.id).all()
        if not req.archivos:  # Si la lista está vacía
            req.archivos = [] 
    return render_template('/requerimientos/verSolicitudes.html',
                           requerimientos = requerimientos,
                           tiposRequerimientos = tiposRequerimientos,
                           catRequerimientos = catRequerimientos,
                           internos = internos,
                           externos = externos,
                           nombre = nombre,
                           tipoUsuario = tipoUsuario,
                           comentarios = comentarios, 
                           eventos = eventos,
                           ubicacion = ubicacion
                           )

@requerimiento.route('/asignacionSolicitudes')
def asignacionSolici():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    ubicacion = "Requerimiento"
    nombre = session.get('user_nombre')
    tipoUsuario = session.get('user_tipo')
    requerimientos = Requerimiento.query.filter(Requerimiento.idDestinatario == None).all()
    tiposRequerimientos = TipoRequerimiento.query.all()
    catRequerimientos = CategoriaRequerimiento.query.all()
    internos = UsuarioInterno.query.all()
    externos = UsuarioExterno.query.all()
    return render_template('/requerimientos/asignacionSoli.html',
                           requerimientos = requerimientos,
                           tiposRequerimientos = tiposRequerimientos,
                           catRequerimientos = catRequerimientos,
                           internos = internos,
                           externos = externos, 
                           nombre = nombre,
                           tipoUsuario = tipoUsuario,
                           ubicacion = ubicacion)

@requerimiento.route('/requerimiento/asignar', methods = ['POST'])
def asignarRequerimiento():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    interno = request.form['interno']
    idRequerimiento = request.form['idRequerimiento']
    requerimiento = Requerimiento.query.get(idRequerimiento)
    requerimiento.modEstado("Asignado")
    requerimiento.idDestinatario = interno
    db.session.commit()
    # Creacion del evento
    fechaYhora = datetime.now().strftime("%Y-%m-%d %H:%M")
    idUsuarioResponsable = session.get('user_id')
    tipoUsuarioResponsable = session.get('user_tipo')
    accion = "Asignacion de Caso" 
    evento = Evento(idRequerimiento , accion, fechaYhora, idUsuarioResponsable, tipoUsuarioResponsable)
    db.session.add(evento)
    db.session.commit()

    # ENVIO DE CORREO
    #Función para cargar la plantilla y reemplazar variables
    def cargar_plantilla(ruta_plantilla, **kwargs):
        with open(ruta_plantilla, 'r') as archivo:
            plantilla = archivo.read()
        # Reemplazar las variables en la plantilla
        for clave, valor in kwargs.items():
            plantilla = plantilla.replace(f"{{{{{clave}}}}}", str(valor))
        return plantilla
#
    ## Datos del correo
    asunto = "Asignacion de requerimiento"
    fecha = datetime.now().strftime("%Y-%m-%d")
    usuario = UsuarioInterno.verInterno(interno)
    nombre = usuario.nombre
    correo = UsuarioInterno.verCorreo(interno)
    html = cargar_plantilla('templates/emails/asignacionRequerimiento.html', fecha=fecha, nombre=nombre)
    # Configuración del servidor SMTP
    servidor = smtplib.SMTP("smtp.gmail.com", 587)
    servidor.starttls()
    servidor.login("aguspascual2001@gmail.com", "isqy rsxw laps hnqq")
#
    ## Crear el mensaje con formato HTML
    msg = MIMEMultipart("alternative")
    msg["From"] = "aguspascual2001@gmail.com"
    msg["To"] = correo
    msg["Subject"] = asunto
#
    ## Adjuntar el mensaje en formato HTML
    parte_html = MIMEText(html, "html")
    msg.attach(parte_html)
#
    ## Enviar el correo
    servidor.sendmail("aguspascual2001@gmail.com", correo, msg.as_string())
#
    ## Cerrar la conexión con el servidor SMTP
    servidor.quit()
    return redirect(url_for('requerimiento.asignacionSolici'))

# Define el blueprint para CATEGORIA
categoriaRequerimiento = Blueprint('categoriaRequerimiento', __name__)

@categoriaRequerimiento.route('/categoriaRequerimiento')
def indexcategoriaRequerimiento():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    ubicacion = "Requerimiento"
    nombre = session.get('user_nombre')
    tipoUsuario = session.get('user_tipo')
    tiposRequerimientos = TipoRequerimiento.query.all()
    categoriasRequerimientos = CategoriaRequerimiento.query.all()
    return render_template('/requerimientos/categoriaRequerimiento.html',
                           categoriasRequerimientos = categoriasRequerimientos,
                           tiposRequerimientos = tiposRequerimientos,
                           nombre = nombre,
                           tipoUsuario = tipoUsuario,
                           ubicacion = ubicacion)

@categoriaRequerimiento.route('/categoriaRequerimiento/registrar', methods = ['POST'])
def registrarCategoriaRequerimiento():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    # Obtengo los datos del formulario
    descripcion = request.form['descripcion']
    idTipo = request.form['idTipo']
    # Creo la instancia de CategoriaRequerimiento
    catRequerimiento = CategoriaRequerimiento(descripcion, idTipo)
    # Guardo en la base de datos
    db.session.add(catRequerimiento)
    db.session.commit()
    return redirect(url_for('categoriaRequerimiento.indexcategoriaRequerimiento'))

@categoriaRequerimiento.route('/categoria/modificar', methods = ['POST'])
def modificarCategoriaRequerimiento():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    id = request.form['id']
    descripcion = request.form['descripcion']
    categoria = CategoriaRequerimiento.query.filter_by(id=id).one()
    categoria.descripcion = descripcion
    db.session.commit()
    return redirect(url_for('categoriaRequerimiento.indexcategoriaRequerimiento'))

@categoriaRequerimiento.route('/categoria/eliminar', methods = ['POST'])
def eliminarCategoriaRequerimiento():
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    id = request.form['id']
    categoria = CategoriaRequerimiento.query.filter_by(id=id).one()
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categoriaRequerimiento.indexcategoriaRequerimiento'))

# Define el blueprint para TIPO
tipoRequerimiento = Blueprint('tipoRequerimiento', __name__)

@tipoRequerimiento.route('/tipoRequerimiento')
def indexTipoRequerimiento():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    ubicacion = "Requerimiento"
    nombre = session.get('user_nombre')
    tipoUsuario = session.get('user_tipo')
    tiposrequerimientos = TipoRequerimiento.query.all()
    return render_template('/requerimientos/tipoRequerimiento.html',
                           tiposrequerimientos = tiposrequerimientos,
                           nombre = nombre,
                           tipoUsuario = tipoUsuario,
                           ubicacion = ubicacion)

@tipoRequerimiento.route('/tipoRequerimiento/registrar', methods = ['POST'])
def registrarTipoRequerimiento():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    # Obtengo los datos del formulario
    codigo = request.form['codigo']
    tipo = request.form['tipo']
    # Creo la instancia de tipoRequerimiento
    print(tipo)
    tipoRequerimiento = TipoRequerimiento(codigo, tipo)
    # Guardo en la base de datos
    db.session.add(tipoRequerimiento)
    db.session.commit()
    return redirect(url_for('tipoRequerimiento.indexTipoRequerimiento'))

@tipoRequerimiento.route('/tipo/modificar', methods = ['POST'])
def modificarTipoRequerimiento():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    id = request.form['id']
    codigo = request.form['codigo']
    tipo = request.form['tipo']
    tipoReq = TipoRequerimiento.query.filter_by(id=id).one()
    tipoReq.codigo = codigo
    tipoReq.tipo = tipo
    db.session.commit()
    return redirect(url_for('tipoRequerimiento.indexTipoRequerimiento'))

@tipoRequerimiento.route('/tipo/eliminar', methods = ['POST'])
def eliminarTipoRequerimiento():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    # Obtengo el id del formulario
    id = request.form['id']
    # Obtengo el tipo de requerimiento y elimino
    tipo = TipoRequerimiento.query.filter_by(id=id).one()
    db.session.delete(tipo)
    db.session.commit()
    return redirect(url_for('tipoRequerimiento.indexTipoRequerimiento'))

# Define el blueprint para EVENTO
evento = Blueprint('evento', __name__)

@evento.route('/evento')
def indexEvento():
    requerimientos = requerimiento.query.all()
    return render_template('/requerimientos/tipoRequerimiento.html', requerimientos = requerimientos)

@evento.route('/evento/registrar')
def registrarEvento():
    # Obtengo los datos del formulario
    idRequerimiento = request.form['idRequerimiento']
    accion = request.form['accion']
    fechaYhora = datetime.now()
    idUsuarioResponsable = request.form['idUsuarioResponsable']
    # Creo la instancia de evento
    evento = Evento(idRequerimiento, accion, fechaYhora, idUsuarioResponsable)
    # Guardo en la base de datos
    db.session.add(evento)
    db.session.commit()
    return redirect(url_for('evento.registrarEvento'))


# Define el blueprint para COMENTARIO
comentario = Blueprint('comentario', __name__)

@comentario.route('/comentario/registrar', methods = ['POST'])
def registrarComentario():
    if session.get('user_active') != True:
        return redirect(url_for('auth.indexLogin'))
    
    # Obtengo los datos del formulario
    idRequerimiento = request.form['idRequerimiento']
    asunto = request.form['asunto']
    descripcion = request.form['descripcion']
    fechaYhora = datetime.now().strftime("%Y-%m-%d %H:%M")
    idUsuarioEmisor = session.get('user_id')
    idUsuarioResponsable = session.get('user_id')
    tipoUsuarioResponsable = session.get('user_tipo')
    accion = "Emisión de Respuesta" 
    
    # Creación del evento
    evento = Evento(idRequerimiento, accion, fechaYhora, idUsuarioResponsable, tipoUsuarioResponsable)
    db.session.add(evento)
    db.session.commit()
    
    idEvento = evento.id
    
    # Creo la instancia de comentario
    comentario = Comentario(idRequerimiento, asunto, descripcion, fechaYhora, idUsuarioEmisor, tipoUsuarioResponsable, idEvento)
    
    # Guardo en la base de datos
    db.session.add(comentario)
    db.session.commit()
    
    #Redireccion segun donde este
    if request.form['ubicacion'] == "misSolicitudes":
        return redirect(url_for('requerimiento.misSolicitudes'))
    elif request.form['ubicacion'] == "solicitudesAcargo":
        return redirect(url_for('requerimiento.solicitudesAcargo'))


# Define el blueprint para ARCHIVO
archivo = Blueprint('archivo', __name__)

@archivo.route('/archivo/registrar')
def registrarArchivo():
    # Obtengo los datos del formulario
    nombre = request.form['nombre']
    # Creo la instancia de CategoriaRequerimiento
    archivo = Archivo(nombre)
    # Guardo en la base de datos
    db.session.add(archivo)
    db.session.commit()
#ANDA MAL ARREGLAR
@archivo.route('/statics/img/archivos/<path:filename>')
def descargar_archivo(filename):
    # Ruta del directorio donde están los archivos
    directorio_archivos = os.path.join(archivo.static_folder, 'img', 'archivos')
    try:
        return send_from_directory(directorio_archivos, filename)
    except FileNotFoundError:
        abort(404)
