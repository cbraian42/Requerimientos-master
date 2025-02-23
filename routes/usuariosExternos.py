from flask import Flask, render_template, request, redirect, url_for, Blueprint, session, flash
from models.UsuarioExterno import UsuarioExterno
from utils.db import db
from werkzeug.security import generate_password_hash
import smtplib
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart

# Define el blueprint
usuarioExterno = Blueprint('usuarioExterno', __name__)

@usuarioExterno.route('/usuario/registrarExterno', methods= ['POST'])
def RegistrarExterno():
    # Obtengo los datos del formulario
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']
    contrasenax2 = request.form['contrasenax2']
    correo = request.form['correo']
    tipoUsuario = "Usuario Externo"
    cuil = request.form['cuil']
    descripcion = request.form['descripcion']
    destacado = request.form.get('destacado')
    if destacado:
    # El checkbox está marcado
        destacado = True
    else:
        # El checkbox no está marcado
        destacado = False
    empresa = request.form['empresa']
    if contrasena != contrasenax2:
        flash("Las contraseñas no coinciden. Por favor, inténtalo de nuevo.", "danger")
    
    nombre = nombre +" "+ apellido
    # Hashear la contraseña antes de crear el usuario
    hashed_contrasena = generate_password_hash(contrasena)
    # Creo el usuario
    nuevo_usuario = UsuarioExterno(nombre, usuario, hashed_contrasena, correo, tipoUsuario ,cuil, descripcion, destacado, empresa)
    # Lo agrego a la base de datos
    db.session.add(nuevo_usuario)
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

@usuarioExterno.route('/externo/modificar', methods = ['POST'])
def modInterno():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    id = request.form['id']
    externo = UsuarioExterno.query.get(id)
    # Obtengo los datos del formulario
    externo.nombre = request.form['nombre']
    externo.usuario = request.form['usuario']
    contrasena = request.form['contrasena']
    if contrasena != "":
        hashed_contrasena = generate_password_hash(contrasena)
        externo.contrasena = hashed_contrasena
    externo.correo = request.form['correo']
    externo.tipoUsuario = request.form['tipoUsuario']
    externo.cuil = request.form['cuil']
    externo.descripcion = request.form['descripcion']
    externo.empresa = request.form['empresa']
    externo.destacado = request.form.get('destacado')
    # Confirmo los cambios
    db.session.commit()

    return redirect(url_for('usuarios.verUsuarios'))

@usuarioExterno.route('/externo/eliminar', methods = ['POST'])
def eliminarExterno():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    id = request.form.get('id')
    externo = UsuarioExterno.query.get(id)
    db.session.delete(externo)
    db.session.commit()
    return redirect(url_for('usuarios.verUsuarios')) 