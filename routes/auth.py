from flask import Flask, render_template, redirect, url_for, Blueprint, request, session
from models.UsuarioInterno import UsuarioInterno
from models.UsuarioExterno import UsuarioExterno
from utils.db import db
from werkzeug.security import check_password_hash, generate_password_hash

# Define el blueprint
auth = Blueprint('auth', __name__)

# Define la ruta del blueprint
@auth.route('/login')
def indexLogin():
    return render_template('/auth/auth.html')

@auth.route('/admin/login/iniciar', methods = ['POST'])
def inicio():
    # Obtengo los datos del formulario
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']
    # Busco si es un usuario Externo
    user = UsuarioExterno.query.filter_by(usuario=usuario).first()
    if user and check_password_hash(user.contrasena, contrasena):
        session['user_id'] = user.id  # Guardar el ID del usuario en la sesión
        session['user_active'] = True
        session['user_tipo'] = "Externo"
        session['user_usuario'] = user.usuario
        session['user_nombre'] = user.nombre
        return redirect(url_for('requerimiento.misSolicitudes'))
    
    # Busco si es un usuario Interno
    user = UsuarioInterno.query.filter_by(usuario=usuario).first()
    if user and check_password_hash(user.contrasena, contrasena):
        session['user_id'] = user.id  # Guardar el ID del usuario en la sesión
        session['user_active'] = True
        session['user_tipo'] = "Interno"
        session['user_usuario'] = user.usuario
        session['user_nombre'] = user.nombre
        return redirect(url_for('requerimiento.misSolicitudes'))
    
    # En caso de que no exista el usuario redirijo a login
    return redirect(url_for('auth.indexLogin'))

# Redirigo a registro de Externo
@auth.route('/registrarExterno')
def indexUsuarioExterno():
    return render_template('/auth/registrarExterno.html')

# Redirigo a registro de interno
@auth.route('/registrarInterno')
def indexUsuarioInterno():
    return render_template('/auth/registrarInterno.html')

@auth.route('/cambiarContraseña')
def cambiarContraseña():
    usuario = session.get('user_usuario')
    return render_template('/auth/cambiarContraseña.html', usuario = usuario)

@auth.route('/cambiarContraseña/modificar', methods = ['POST'])
def cambiarContraseñaModificar():
    # Obtengo datos del formulario
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']
    contrasenaNueva = request.form['contrasenaNueva']
    contrasenaNueva2 = request.form['contrasenaNueva2']
    
    usuario_id = session.get('user_usuario')
    print (usuario)
    # Verifica que la nueva contraseña coincida
    if contrasenaNueva == contrasenaNueva2:
        if session.get('user_tipo') == "Interno":
            usuario = UsuarioInterno.query.filter_by(correo=usuario_id).first()
        elif session.get('user_tipo') == "Externo":
            usuario = UsuarioExterno.query.filter_by(usuario=usuario).first()
            #usuario = UsuarioExterno.query.filter_by(correo=usuario_id).first()
        
        # Verifica la contraseña actual
        if usuario and check_password_hash(usuario.contrasena, contrasena):
            # Si la contraseña actual es correcta, actualiza la nueva contraseña
            usuario.contrasena = generate_password_hash(contrasenaNueva)
            # Guarda los cambios
            db.session.commit()  
            
    return redirect(url_for('requerimiento.misSolicitudes'))

@auth.route('/logout')
def logout():
    # Eliminar datos específicos de la sesión
    session.pop('user_id', None)
    session.pop('user_tipo', None)
    # O limpiar toda la sesión
    session.clear()

    # Redirigir a la página de inicio o login
    return redirect(url_for('auth.indexLogin'))