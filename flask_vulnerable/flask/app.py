from flask import Flask, abort, flash, render_template, send_file, request, redirect, url_for, session, Response, Request
from flask.logging import default_handler
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

@app.route('/')
def index():
    return Response('<h1>TODO OK</h1>', HTTPStatus.OK)


@app.route('/mensaje', methods=['POST'])
def mensaje():
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
    """Recibe un json con varios parametros, compuestos por:
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