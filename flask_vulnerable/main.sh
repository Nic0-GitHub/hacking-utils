#!/bin/bash

APP_ROUTE="localhost:5000"
MENSAJE_URL="$APP_ROUTE/mensaje"
CALCULAR_URL="$APP_ROUTE/calcular"

# Función para mostrar el uso
mostrar_uso() {
  echo "Uso: $0 [-m mensaje] [-c calcular]"
  echo "  -m, --mensaje      Archivo de datos para /mensaje"
  echo "  -c, --calcular     Archivo de datos para /calcular"
  exit 1
}

# Comprobamos que se pase al menos un argumento
if [ $# -eq 0 ]; then
  mostrar_uso
fi

# Variables para almacenar los archivos de datos
DATA_MENSAJE=""
DATA_CALCULAR=""

# Parseo de opciones
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -m|--mensaje)
      DATA_MENSAJE="$2"
      shift 2 ;;
    -c|--calcular)
      DATA_CALCULAR="$2"
      shift 2 ;;
    *)
      mostrar_uso ;;
  esac
done

# Verificar si se seleccionó algún archivo de mensaje
if [ -n "$DATA_MENSAJE" ]; then
  if [ -f "$DATA_MENSAJE" ]; then
    echo "Enviando $DATA_MENSAJE a $MENSAJE_URL"
    curl -s -X POST -H "Content-Type: application/json" --data-binary @"$DATA_MENSAJE" $MENSAJE_URL
  else
    echo "Archivo de mensaje no encontrado: $DATA_MENSAJE"
    exit 1
  fi
fi

# Verificar si se seleccionó algún archivo de cálculo
if [ -n "$DATA_CALCULAR" ]; then
  if [ -f "$DATA_CALCULAR" ]; then
    echo "Enviando $DATA_CALCULAR a $CALCULAR_URL"
    curl -s -X POST -H "Content-Type: application/json" --data-binary @"$DATA_CALCULAR" $CALCULAR_URL
  else
    echo "Archivo de cálculo no encontrado: $DATA_CALCULAR"
    exit 1
  fi
fi
