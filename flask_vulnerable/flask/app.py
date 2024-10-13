from flask import Flask, abort, jsonify, redirect, render_template, request, Response, session
from flask.logging import default_handler
from flask.sessions import SessionMixin
from database import Database, Usuario
from http import HTTPStatus
from constants import *
import random
from sys import argv
from os import path
import argparse
import logging

# app
app = Flask(__name__, template_folder='./static/templates')
app.logger.setLevel(logging.INFO)
app.secret_key = SECRET_KEY
generador = random.Random(SEED)

db = Database()

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

def crear_session(session: SessionMixin, usuario: Usuario):
    """
    Carga los datos de una sesión
    """
    session['nombre'] = usuario.nombre
    session['valid'] = True
    
def borrar_session(session: SessionMixin):
    """
    Borra los datos de la sesión
    """
    session.pop('nombre')
    session.pop('valid')

@app.route('/')
def index():
    return Response('<h1>Server Prendido</h1>', HTTPStatus.OK)

@app.route('/mensaje', methods=['POST'])
def mensaje():
    """
    Permite enviar mensajes al servidor
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
    
    res = f"cuentas realizada:\n{calculos_realizar}"
    app.logger.info(res)
    
    return Response(res, HTTPStatus.OK)

@app.route("/info_request", methods=['GET'])
def info_request():
    """
    Recolecta la información del request y la imprime tanto en logs como para el cliente.
    """
    datos = {}
    for key, item in request.headers.items():
        datos[key] = item
    datos['ip'] = request.remote_addr
    
    app.logger.info(f"información de la request de info_request: {request.headers};{request.remote_addr};")
    return render_template('info_request.html', datos=datos)

@app.route('/comentario', methods=['GET', 'POST'])
def comentario():
    """
    Permite que los usuarios manden un mensaje en un formulario insanatizado.
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
def pagina_usuario(usuario: str):
    """
    
    """
    pagina_usuario_file = 'pagina_usuario.html'
    get_nombre = lambda u: u.nombre
    usuarios_nombres = map(get_nombre, db.obtener_usuarios())
    match request.method:
        case 'GET':
            # Vulneralibilidad de ataque de enumeración
            if usuario in usuarios_nombres:
                app.logger.info(f"Se accedio a la pagina del usuario: {usuario}")
                mensaje = "Sesión iniciada" if session.get('nombre') == usuario else ''
                return render_template(pagina_usuario_file, usuario=usuario, mensaje=mensaje)
            
            app.logger.error(f"Se busco un usuario inexistente: {usuario}")
            return Response("<h1>usuario no encontrado</h1>",HTTPStatus.NOT_FOUND)
        
        case 'POST':
            # caso nombre de usuario ya usado
            if usuario in usuarios_nombres:
                app.logger.error(f"El usuario `{usuario_nuevo.nombre}` ya existe, no se pudo crear usuario")
                return Response("<h1>Ese usuario ya esta registrado</h1>", HTTPStatus.CONFLICT)

            import string
            valid_chars = string.ascii_letters + string.digits
            # Vulnerabilidad de generación insegura con seed
            d = {
                "nombre": usuario,
                "password": ''.join(generador.choices(valid_chars, k=15))
            }
            usuario_nuevo = Usuario(None, **d)
            try:
                db.crear_usuario(usuario_nuevo)
            except ValueError:
                app.logger.error(f"El usuario `{usuario_nuevo.nombre}` ya existe, no se pudo crear usuario")
                abort(HTTPStatus.BAD_REQUEST)
            
            app.logger.info(f"Se creo un nuevo usuario: {usuario}")
            return jsonify(d), HTTPStatus.CREATED

@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    match request.method:
        case 'GET':
            return render_template('iniciar_sesion.html')
        case 'POST':
            fields_required = ['nombre', 'password']
            if not request.form or any( (field not in request.form) for field in fields_required ):
                app.logger.error(f"Hubo un error de pasaje del form de inicio de sesión `{request.form}`")
                abort(HTTPStatus.BAD_REQUEST)
                
            data = request.form
            for usuario in db.obtener_usuarios():
                if (usuario.nombre == data['nombre']) and (usuario.password == data['password']):
                    session['valid'] = True
                    return redirect(f'/usuarios/{usuario.nombre}')
            
            return Response("Contraseña incorrecta", HTTPStatus.OK)

@app.route('/admin', methods=['GET'])
def admin_page():
    
    return render_template('admin_page.html')        
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
    
    if not debug_mode:
        db.reiniciar_usuarios()
        
    # running the APP :P
    app.run(host=host_selected, port=port_selected, debug=debug_mode)