#!/bin/bash
set +x
set -euo pipefail

uso() {
    cat <<'AYUDA'
Uso: bash demo_videomemoria.sh [--manual | --pausa SEGUNDOS] [--origen CARPETA]

  --manual          Espera a que pulses Enter entre bloques.
  --pausa SEGUNDOS  Espera ese tiempo entre bloques (por defecto, 8).
  --origen CARPETA  Carpeta con los dos XLS. Por defecto, usa datos/ junto al script.
  --ayuda           Muestra esta ayuda.

Cada ejecución crea una base de demostración y guarda la salida en logs/.
AYUDA
}

error() {
    printf 'Error: %s\n' "$1" >&2
    exit 1
}

directorio=$(cd -- "$(dirname -- "$0")" && pwd)
origen="$directorio/datos"
modo=tiempo
segundos=8

while [[ $# -gt 0 ]]; do
    case "$1" in
        --manual)
            modo=manual
            shift
            ;;
        --pausa)
            [[ $# -ge 2 && $2 =~ ^[0-9]+$ ]] || error "Indica segundos enteros después de --pausa."
            modo=tiempo
            segundos=$2
            shift 2
            ;;
        --origen)
            [[ $# -ge 2 ]] || error "Indica una carpeta después de --origen."
            origen=$2
            shift 2
            ;;
        --ayuda|-h|--help)
            uso
            exit 0
            ;;
        *)
            error "Opción desconocida: $1. Consulta --ayuda."
            ;;
    esac
done

if [[ "$modo" == manual && ! -t 0 ]]; then
    error "Usa --manual en una Terminal interactiva o elige --pausa SEGUNDOS."
fi
command -v docker >/dev/null || error "Docker no está disponible."
command -v uv >/dev/null || error "uv no está disponible."
for fichero in preciosEESS_es.xls embarcacionesPrecios_es.xls; do
    [[ -r "$origen/$fichero" ]] || error "No se puede leer $origen/$fichero."
done
origen=$(cd -- "$origen" && pwd)
cd -- "$directorio"

shopt -s nullglob
consultas=(sql/[0-9][0-9]_consulta_[0-9][0-9].sql)
[[ ${#consultas[@]} -gt 0 ]] || error "No hay consultas SQL numeradas en sql/."

umask 077
sesion="$(date +%Y%m%d_%H%M%S)_$$"
base="carburantes_demo_$sesion"
mkdir -p logs
archivo_log="$directorio/logs/demo_$sesion.log"

log() {
    printf '[%s] %s\n' "$(date +%H:%M:%S)" "$1"
}

pausar() {
    if [[ "$modo" == manual ]]; then
        printf '\nPulsa Enter para continuar…\n'
        IFS= read -r _ || error "No se pudo leer la respuesta de la Terminal."
    elif [[ "$segundos" != 0 ]]; then
        log "Pausa de $segundos segundos."
        sleep "$segundos"
    fi
}

psql_demo() {
    docker compose exec -T db psql -X -U "$usuario" -d "$base" -v ON_ERROR_STOP=1 "$@"
}

ejecutar_demo() {
    trap 'codigo=$?; log "Demostración detenida (código $codigo). Revisa $archivo_log"; exit "$codigo"' ERR

    log "Base de demostración: $base"
    log "Registro: $archivo_log"
    log "1/5 · Arranque de PostgreSQL en Docker"
    docker compose up -d --no-recreate --wait db
    usuario=$(docker compose exec -T db printenv POSTGRES_USER)
    direccion=$(docker compose port db 5432)
    pausar

    recuento_sql='SELECT (SELECT count(*) FROM estacion) AS estaciones,
                         (SELECT count(*) FROM precio) AS precios;'
    printf '\n'
    log "2/5 · Creación del esquema y recuento inicial"
    docker compose exec -T db createdb -U "$usuario" "$base"
    psql_demo -f - < sql/01_esquema.sql
    psql_demo -c "$recuento_sql"
    pausar

    printf '\n'
    log "3/5 · Importación completa de preciosEESS_es.xls y embarcacionesPrecios_es.xls"
    clave=$(docker compose exec -T db printenv POSTGRES_PASSWORD)
    PGHOST="${direccion%:*}" PGPORT="${direccion##*:}" PGUSER="$usuario" PGPASSWORD="$clave" \
        uv run --with-requirements requirements.txt python cargar_excel.py "$origen" --base-datos "$base"
    unset clave
    pausar

    printf '\n'
    log "4/5 · Recuento final y reparto por tipo de estación"
    psql_demo -c "$recuento_sql"
    psql_demo <<'SQL'
SELECT e.tipo_estacion, COUNT(DISTINCT e.id_estacion) AS estaciones,
       COUNT(p.id_precio) AS precios
FROM estacion AS e
LEFT JOIN precio AS p ON p.id_estacion = e.id_estacion
GROUP BY e.tipo_estacion
ORDER BY e.tipo_estacion DESC;
SQL
    pausar

    printf '\n'
    log "5/5 · Consultas SQL disponibles (${#consultas[@]})"
    for consulta in "${consultas[@]}"; do
        log "Ejecutando $consulta"
        psql_demo -a -f - < "$consulta"
        pausar
    done

    printf '\n'
    log "Demostración completada. Registro guardado en $archivo_log"
}

ejecutar_demo 2>&1 | tee "$archivo_log"
