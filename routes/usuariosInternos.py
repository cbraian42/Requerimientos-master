from flask import Flask, redirect, Blueprint, request, url_for, session, flash
from models.UsuarioInterno import UsuarioInterno
from utils.db import db
from werkzeug.security import generate_password_hash
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Define el blueprint
usuariosInternos = Blueprint('usuariosInternos', __name__)

@usuariosInternos.route('/usuario/registrarInterno', methods= ['POST'])
def RegistrarInterno():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    # Obtengo los datos del formulario
    legajo = request.form['legajo']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']
    contrasenax2 = request.form['contrasenax2']
    correo = request.form['correo']
    cargo = request.form['cargo']
    departamento = request.form['departamento']
    tipoUsuario = "Usuario Interno"
    # Verifico si las contraseñas coinciden
    if contrasena != contrasenax2:
        flash("Las contraseñas no coinciden. Por favor, inténtalo de nuevo.", "danger")
    
    nombre = nombre +" "+ apellido
    
    # Hasheo la contraseña 
    hashed_contrasena = generate_password_hash(contrasena)
    # Creo el usuario
    nuevo_usuario = UsuarioInterno(legajo, nombre, usuario, hashed_contrasena, correo, tipoUsuario, cargo ,departamento)
    # Lo agrego a la base de datos
    db.session.add(nuevo_usuario) # Agrego el nuevo usuario a la base de datos
    db.session.commit()     # Confirmo los cambios

    # ENVIO DE CORREO ---------------------------------------------------------
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

    html = cargar_plantilla('templates/emails/registro.html',nombre = nombre)
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
    return redirect(url_for('usuarios.verUsuarios'))

@usuariosInternos.route('/interno/modificar', methods = ['POST'])
def modInterno():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    id = request.form['id']
    interno = UsuarioInterno.query.get(id)
    # Obtengo los datos del formulario
    interno.usuario = request.form['usuario']
    interno.correo = request.form['correo']
    interno.cargo = request.form['cargo']
    interno.departamento = request.form['departamento']
    # Confirmo los cambios
    db.session.commit()

    return redirect(url_for('usuarios.verUsuarios'))

@usuariosInternos.route('/interno/eliminar', methods = ['POST'])
def eliminarInterno():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    id = request.form.get('id')
    interno = UsuarioInterno.query.get(id)
    db.session.delete(interno)
    db.session.commit()
    return redirect(url_for('usuarios.verUsuarios')) 

