from flask import Flask, abort, jsonify, redirect, render_template, request, Response, session
from flask.logging import default_handler
import random

from flask.sessions import SessionMixin
from constants import *
from sys import argv
from os import path
from http import HTTPStatus
import argparse
import logging

# app
app = Flask(__name__, template_folder='./static/templates')
app.logger.setLevel(logging.INFO)
app.secret_key = SECRET_KEY
generador = random.Random(SEED)

usuarios = []

# app-logger
bsc_formatter = logging.Formatter("[%(levelname)s] -> [%(asctime)s]: %(message)s", '%Y-%m-%d %H:%M')

file_handler = logging.FileHandler(path.join(LOGS_DIR, 'app.log'))
stream_handler = logging.StreamHandler()

file_handler.setFormatter(bsc_formatter)
stream_handler.setFormatter(bsc_formatter)

app.logger.addHandler(stream_handler)
app.logger.addHandler(file_handler)
app.logger.removeHandler(default_handler)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.disabled = True

def cargar_sesion(session: SessionMixin, usuario):
    session['nombre'] = usuario['nombre']
    session['valid'] = True

def borrar_sesion(session: SessionMixin):
    session.clear()    

@app.route('/')
def index():
    return redirect('/iniciar_sesion')


@app.route('/status')
def status():
    """
        Retorna un 200 para checkear que el server esta encendido
    """
    return Response('<h1>Server Prendido</h1>', HTTPStatus.OK)

@app.route('/mensaje', methods=['POST'])
def mensaje():
    """
        Permite recibir mensajes para imprimirlos en los logs
    """
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)
    
    mensaje:str = request.json['mensaje']
    
    # caso mensaje erroneo
    if mensaje.startswith('/'):
        res = f"Este mensaje no es valido: '{mensaje}'"
        app.logger.info(res)
        return Response(res, HTTPStatus.BAD_REQUEST)
    
    res = f"Mensaje recibido '{mensaje}'"
    app.logger.info(res)
    return Response('Recibido!', HTTPStatus.OK)

@app.route('/calcular', methods=['POST'])
def calcular():
    """
        Recibe un json con varios parametros, compuestos por:
            key: operacion_realizar
        y retorna el resultado de todas las keys
    """
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)
    
    app.logger.info(f"se pidio realizar calcular: {request.json}")
    try:
        calculos_realizar:dict = request.json
        context = {}
        # realizo las cuentas
        for key, value in request.json.items():
            exec(f'{key} = {value}', context)
        
        # actualizo la información
        for key in calculos_realizar:
            calculos_realizar[key] = context[key]
    except Exception as e:
        error_res = f"Excepción de ejecución del mensaje: {e}"
        app.logger.error(error_res)
        return Response(error_res, HTTPStatus.BAD_REQUEST)
    
    res = f"cuentas realizadas:\n{calculos_realizar}"
    app.logger.info(res)
    
    return Response(res, HTTPStatus.OK)

@app.route('/comentario', methods=['GET', 'POST'])
def comentario():
    """
        GET:
            Vista con cuestionario que permite llenar un formulario no sanitizado.
        POST:
            Carga una pagina con la información del formulario obtenido del get.
    """
    match request.method:
        case 'POST':
            # Vulnerabilidad de code injection por falta de sanitización
            comentario = request.form['comentario']
            app.logger.info(f"En `/comentario` se envio como parte del formulario: {comentario}")
            return f"<h1>Comentario recibido: {comentario}</h1>"
        case 'GET':
            comentario_file = 'comentario.html'
            rendered_template = render_template(comentario_file)
            app.logger.info(f"Se renderizo {comentario_file}")
            return Response(rendered_template)
        case _:
            return Response(status=HTTPStatus.METHOD_NOT_ALLOWED)


@app.route('/usuarios/<usuario>', methods=['GET', 'POST'])
def pagina_usuario(usuario):
    """
        GET:
            Carga la pagina del usuario (Si existe, para pedir que inicie sesion)
            En caso de estar loggeado muestra una pagina personalizada para el usuario.
        POST:
            Permite crear un usuario si el username esta disponible, retorna un json con nombre de usuario y pass generada para ese usuario.
    """
    get_nombre = lambda u: u.get('nombre', '')
    match request.method:
        case 'GET':
            pedir_iniciar_sesion_response = Response(render_template("pagina_usuario.html", usuario=usuario, mensaje="¡inicia sesión por favor!"))
            usuario_iniciado_distinto_response = Response(render_template("pagina_usuario.html", usuario=usuario, mensaje="¡Esta NO es tu pagina de usuario!"))
            if usuario in map(get_nombre, usuarios):
                
                # si no inicio sesión
                if not session.get('valid'):
                    app.logger.info(f"Se ingreso a la pagina del usuario: {usuario} (se solicito que el usuario inicie sesión)")
                    # Vulneralibilidad de ataque de enumeración
                    return pedir_iniciar_sesion_response
                
                if (nombre:=session.get('nombre')) != usuario:
                    app.logger.info(f"Se ingreso a la pagina del usuario ({usuario}) desde un usuario logeado ({nombre})")
                    return usuario_iniciado_distinto_response
                
                # respuesta si tiene una sesión valida
                return Response(render_template("pagina_usuario.html", usuario=usuario, mensaje="Bienvenido a tu página personal."))
            
            app.logger.info(f"Se Intento acceder a un usuario inexistente: {usuario}")
            return Response(render_template('usuario_no_encontrado.html'),HTTPStatus.NOT_FOUND)
        
        case 'POST':
            import string
            if usuario in map(get_nombre, usuarios):
                return Response("<h1>usuario invalido</h1>", HTTPStatus.CONFLICT)
            valid_chars = string.ascii_letters + string.digits
            # Vulnerabilidad de generación insegura con seed
            d = {
                "nombre": usuario,
                "password": ''.join(generador.choices(valid_chars, k=15))
            }
            
            app.logger.info(f"Se creo un nuevo usuario: {usuario}")
            usuarios.append(d)
            
            return jsonify(d), HTTPStatus.CREATED

@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    """
        GET:
            vista para iniciar sesion
        POST:
            checkea valores y permite iniciar sesión
    """
    match request.method:
        case 'GET':
            return render_template('iniciar_sesion.html')
        case 'POST':
            fields_required = ['nombre', 'password']
            form = request.form
            if not form or any(field not in form for field in fields_required):
                abort(HTTPStatus.BAD_REQUEST)
            for usuario in usuarios:
                # si el usuario es valido
                if (usuario['nombre'] == form['nombre']) and (usuario['password'] == form['password']):
                    cargar_sesion(session, usuario)
                    app.logger.info(f"El usuario {usuario['nombre']} inicio sesion")
                    return redirect(f'/usuarios/{usuario['nombre']}')
                
            return Response("credenciales no validas", HTTPStatus.UNAUTHORIZED)

@app.route('/cerrar_sesion', methods=['POST'])
def cerrar_sesion():
    """
        Borra las cookies de la sesión, borrando las credenciales para el sistema.
    """
    if not session.get('valid'):
        abort(HTTPStatus.BAD_REQUEST)
    app.logger.info(f"El usuario {session['nombre']} ha cerrado su sesion")
    borrar_sesion(session)
    return Response("Sesión cerrada", HTTPStatus.OK)

def args_parse():
    parser = argparse.ArgumentParser(description="Process command line arguments.")
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port number to run the server on')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-H', '--host', type=str, default='0.0.0.0', help='Host address to run the server on')
    parser.add_argument('-n', '--no-logs', action='store_true', default=False, help='Disable logging output')

    args = parser.parse_args()
    return args.host, args.port, args.debug, args.no_logs

if __name__ == '__main__':
    _, *args = argv
    host_selected, port_selected, debug_mode, no_logs = args_parse()
    
    app.logger.disabled = no_logs
    app.logger.debug(f"Running on http://{host_selected}:{port_selected}")
    
    # running the APP :P
    app.run(host=host_selected, port=port_selected, debug=debug_mode)