#!/bin/bash
APP_ROUTE="localhost:5000"
MENSAJE_URL="$APP_ROUTE/mensaje"
CALCULAR_URL="$APP_ROUTE/calcular"
COMENTARIO_URL="$APP_ROUTE/comentario"
USUARIOS_URL="$APP_ROUTE/usuarios"

function crear_usuario(){
    echo "mandando POST -> $USUARIOS_URL/$1"
    resultado=$(curl -s -X POST "$USUARIOS_URL/$1")
    echo "$resultado"
}