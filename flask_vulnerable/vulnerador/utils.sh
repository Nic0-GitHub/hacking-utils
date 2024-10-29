#!/bin/bash

APP_ROUTE="localhost:5000"
MENSAJE_URL="$APP_ROUTE/mensaje"
CALCULAR_URL="$APP_ROUTE/calcular"
COMENTARIO_URL="$APP_ROUTE/comentario"
USUARIOS_URL="$APP_ROUTE/usuarios"

function crear_usuario() {
    echo "Mandando POST -> $USUARIOS_URL/$1"
    resultado=$(curl -s -X POST "$USUARIOS_URL/$1")
    echo "$resultado"
}

function enviar_mensaje() {
    local mensaje="$1"
    echo "Mandando POST -> $MENSAJE_URL"
    resultado=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"mensaje\": \"$mensaje\"}" "$MENSAJE_URL")
    echo "$resultado"
}

function calcular() {
    local operaciones="$1"
    echo "Mandando POST -> $CALCULAR_URL"
    resultado=$(curl -s -X POST -H "Content-Type: application/json" -d "$operaciones" "$CALCULAR_URL")
    echo "$resultado"
}

function enviar_comentario() {
    local comentario="$1"
    echo "Mandando POST -> $COMENTARIO_URL"
    resultado=$(curl -s -X POST -F "comentario=$comentario" "$COMENTARIO_URL")
    echo "$resultado"
}

function obtener_usuario() {
    local usuario="$1"
    echo "Mandando GET -> $USUARIOS_URL/$usuario"
    resultado=$(curl -s -X GET "$USUARIOS_URL/$usuario")
    echo "$resultado"
}

function formatear_python() {
    if [[ -z "$1" ]]; then
        echo "Uso: formatear_python <nombre_del_archivo>"
        return 1
    fi

    # Procesa el archivo con sed y lo guarda con el mismo nombre pero con la extensión .pyf (python formated)
    archivo_formateado="${1%.*}_formated.pyf"
    sed ':a;N;$!ba;s/\n/\\n/g' "$1" | tee "$archivo_formateado"
    #    echo "Salida guardada en '$archivo_formateado'"
}

# Ejemplo de uso
# crear_usuario "nuevo_usuario"
# enviar_mensaje "Hola, esto es un mensaje."
# calcular '{"suma": 5 + 10, "resta": 10 - 3}'
# enviar_comentario "Este es un comentario."
# obtener_usuario "nuevo_usuario"
