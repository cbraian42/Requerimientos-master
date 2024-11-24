from flask import Flask, render_template, redirect, Blueprint, url_for, session
from models.UsuarioInterno import UsuarioInterno
from models.UsuarioExterno import UsuarioExterno
from utils.db import db


# Define el blueprint
usuarios = Blueprint('usuarios', __name__)

@usuarios.route('/verUsuarios')
def verUsuarios():
    # Si no esta iniciada la Sesion, lo redirigo al login
    if session.get('user_active') != True or session.get('user_tipo') != "Interno":
        return redirect(url_for('auth.indexLogin'))
    ubicacion = "Usuarios"
    nombre = session.get('user_nombre')
    tipoUsuario = session.get('user_tipo')
    internos = UsuarioInterno.query.all()
    externos = UsuarioExterno.query.all()
    return render_template('/usuarios/usuarios.html',
                            internos = internos,
                            externos = externos,
                            nombre = nombre,
                            tipoUsuario = tipoUsuario,
                            ubicacion = ubicacion)
