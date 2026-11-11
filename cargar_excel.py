"""Carga en PostgreSQL los dos Excel de estaciones del laboratorio."""

import argparse
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from getpass import getpass
from pathlib import Path

import psycopg
import xlrd


ARCHIVOS = (
    ("preciosEESS_es.xls", "terrestre", 31),
    ("embarcacionesPrecios_es.xls", "maritima", 6),
)
CAMPOS_TEXTO = {
    "localidad": "localidad",
    "direccion": "dirección",
    "horario": "horario",
    "tipo_venta": "tipo venta",
    "remision": "rem.",
}
PRODUCTOS_POR_KILO = {
    "gas natural comprimido", "gas natural licuado", "hidrógeno",
    "metanol", "amoniaco", "bgnc", "bgnl",
}


@dataclass
class EstacionExcel:
    provincia: str
    municipio: str
    rotulo: str | None
    datos: dict
    precios: list[tuple[str, Decimal, str]]


def texto(valor):
    return str(valor).strip()


def numero(valor):
    if not texto(valor):
        return None
    resultado = Decimal(texto(valor).replace(",", "."))
    if not resultado.is_finite():
        raise ValueError(f"Número inválido: {valor!r}")
    return resultado


def fecha(valor, datemode):
    if isinstance(valor, (int, float)):
        return xlrd.xldate_as_datetime(valor, datemode)
    return datetime.strptime(texto(valor), "%d/%m/%Y %H:%M")


def unidad_precio(producto, tipo_estacion):
    nombre = producto.casefold()
    if nombre in PRODUCTOS_POR_KILO:
        return "EUR/kg"
    if tipo_estacion == "maritima" and nombre in {"gasóleo b", "gasóleo de uso marítimo"}:
        return "EUR/1000 l"
    return "EUR/l"


def leer_excel(ruta, tipo, fila_muestra):
    estaciones = []
    with xlrd.open_workbook(str(ruta), on_demand=True) as libro:
        hoja = libro.sheet_by_index(0)
        cabeceras = [" ".join(texto(celda).split()) for celda in hoja.row_values(3)]
        claves = [nombre.casefold() for nombre in cabeceras]
        columnas_precio = {}
        for i, nombre in enumerate(cabeceras):
            prefijo, _, producto = nombre.partition(" ")
            if prefijo.casefold() == "precio" and producto:
                columnas_precio[i] = producto[0].upper() + producto[1:]
        obligatorias = {"provincia", "municipio", "código postal", *CAMPOS_TEXTO.values()}
        requeridas = obligatorias | {"rótulo", "latitud", "longitud"}
        if tipo == "terrestre":
            requeridas |= {"toma de datos", "margen", "tipo servicio"}
        faltan = requeridas - set(claves)
        if not columnas_precio:
            faltan.add("columnas de precio")
        if faltan:
            raise ValueError(f"{ruta.name}: cabecera incompleta, faltan {', '.join(sorted(faltan))}")
        fecha_publicacion = fecha(hoja.cell_value(0, 1), libro.datemode)
        indices = [fila_muestra - 1] if fila_muestra else range(4, hoja.nrows)

        for indice in indices:
            try:
                valores = hoja.row_values(indice)
                if not any(texto(valor) for valor in valores):
                    continue
                fila = dict(zip(claves, valores))
                vacias = [nombre for nombre in sorted(obligatorias) if not texto(fila[nombre])]
                if vacias:
                    raise ValueError(f"Campos obligatorios vacíos: {', '.join(vacias)}")
                if any(texto(fila.get(nombre, "")) for nombre in ("% bioalcohol", "% éster metílico")):
                    raise ValueError("El esquema actual no tiene campos para los porcentajes de mezcla")

                codigo_postal = fila["código postal"]
                if isinstance(codigo_postal, float) and codigo_postal.is_integer():
                    codigo_postal = f"{int(codigo_postal):05d}"
                datos = {campo: texto(fila[columna]) for campo, columna in CAMPOS_TEXTO.items()}
                datos.update(
                    tipo_estacion=tipo,
                    codigo_postal=texto(codigo_postal),
                    margen=texto(fila.get("margen", "")) or None,
                    latitud=numero(fila["latitud"]),
                    longitud=numero(fila["longitud"]),
                    tipo_servicio=texto(fila.get("tipo servicio", "")) or None,
                    fecha_ultima_actualizacion=(
                        fecha(fila["toma de datos"], libro.datemode)
                        if tipo == "terrestre" else fecha_publicacion
                    ),
                )
                precios = [
                    (producto, numero(valores[i]), unidad_precio(producto, tipo))
                    for i, producto in columnas_precio.items() if texto(valores[i])
                ]
                estaciones.append(EstacionExcel(
                    texto(fila["provincia"]), texto(fila["municipio"]),
                    texto(fila["rótulo"]) or None, datos, precios
                ))
            except (ValueError, InvalidOperation, IndexError) as error:
                raise ValueError(f"{ruta.name}, fila {indice + 1}: {error}") from error

    if not estaciones:
        raise ValueError(f"{ruta.name}: no se encontraron estaciones en las filas seleccionadas")
    return estaciones


def cargar_catalogos(cursor, estaciones):
    provincias = sorted({(e.provincia,) for e in estaciones})
    cursor.executemany("INSERT INTO provincia (nombre) VALUES (%s) ON CONFLICT DO NOTHING", provincias)
    ids_provincia = dict(cursor.execute("SELECT nombre, id_provincia FROM provincia"))

    municipios = sorted({(ids_provincia[e.provincia], e.municipio) for e in estaciones})
    cursor.executemany(
        "INSERT INTO municipio (id_provincia, nombre) VALUES (%s, %s) ON CONFLICT DO NOTHING", municipios
    )
    ids_municipio = {
        (provincia, nombre): identificador
        for provincia, nombre, identificador in cursor.execute(
            "SELECT id_provincia, nombre, id_municipio FROM municipio"
        )
    }

    rotulos = sorted({(e.rotulo,) for e in estaciones if e.rotulo})
    cursor.executemany("INSERT INTO empresa (rotulo) VALUES (%s) ON CONFLICT DO NOTHING", rotulos)
    ids_empresa = dict(cursor.execute("SELECT rotulo, id_empresa FROM empresa"))

    carburantes = sorted({(nombre,) for e in estaciones for nombre, _, _ in e.precios})
    cursor.executemany(
        "INSERT INTO tipo_carburante (nombre) VALUES (%s) ON CONFLICT DO NOTHING", carburantes
    )
    ids_carburante = dict(cursor.execute("SELECT nombre, id_tipo_carburante FROM tipo_carburante"))
    return ids_provincia, ids_municipio, ids_empresa, ids_carburante


def cargar_estaciones(cursor, estaciones):
    # Serializa las cargas y comprueba el destino antes de insertar ninguna fila.
    cursor.execute("LOCK TABLE estacion IN SHARE ROW EXCLUSIVE MODE")
    if cursor.execute("SELECT EXISTS (SELECT 1 FROM estacion)").fetchone()[0]:
        raise ValueError("La base ya contiene estaciones. Usa una base vacía para importar.")
    provincias, municipios, empresas, carburantes = cargar_catalogos(cursor, estaciones)

    for estacion in estaciones:
        datos = estacion.datos | {
            "id_municipio": municipios[provincias[estacion.provincia], estacion.municipio],
            "id_empresa": empresas.get(estacion.rotulo),
        }
        identificador = cursor.execute(
            """
            INSERT INTO estacion (
                id_municipio, id_empresa, tipo_estacion, localidad, codigo_postal,
                direccion, margen, latitud, longitud, horario, tipo_venta, remision,
                tipo_servicio, fecha_ultima_actualizacion
            ) VALUES (
                %(id_municipio)s, %(id_empresa)s, %(tipo_estacion)s, %(localidad)s,
                %(codigo_postal)s, %(direccion)s, %(margen)s, %(latitud)s, %(longitud)s,
                %(horario)s, %(tipo_venta)s, %(remision)s, %(tipo_servicio)s,
                %(fecha_ultima_actualizacion)s
            ) RETURNING id_estacion
            """,
            datos,
        ).fetchone()[0]
        cursor.executemany(
            """
            INSERT INTO precio (id_estacion, id_tipo_carburante, importe, unidad, fecha_dato)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [
                (identificador, carburantes[nombre], importe, unidad, datos["fecha_ultima_actualizacion"])
                for nombre, importe, unidad in estacion.precios
            ],
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directorio_excel", type=Path, help="Carpeta que contiene los dos .xls")
    parser.add_argument("--base-datos", required=True, help="Base PostgreSQL vacía, con el esquema creado")
    parser.add_argument("--muestra", action="store_true", help="Carga las filas 31 y 6 de los Excel históricos")
    parser.add_argument("--pedir-clave", action="store_true", help="Pide la contraseña sin mostrarla")
    args = parser.parse_args()

    try:
        cargas = [
            leer_excel(args.directorio_excel / nombre, tipo, fila if args.muestra else None)
            for nombre, tipo, fila in ARCHIVOS
        ]
        estaciones = [estacion for carga in cargas for estacion in carga]
        conexion = {"dbname": args.base_datos, "connect_timeout": 5}
        if args.pedir_clave:
            conexion["password"] = getpass("Contraseña de PostgreSQL: ")

        # El contexto confirma todo al salir y revierte la carga si falla un INSERT.
        with psycopg.connect(**conexion) as conn, conn.cursor() as cursor:
            cargar_estaciones(cursor, estaciones)
            total = cursor.execute(
                "SELECT (SELECT count(*) FROM estacion), (SELECT count(*) FROM precio)"
            ).fetchone()
    except (OSError, ValueError, xlrd.XLRDError, psycopg.Error) as error:
        parser.exit(1, f"Error al cargar los Excel: {error}\n")

    for (_, tipo, _), carga in zip(ARCHIVOS, cargas):
        precios = sum(len(estacion.precios) for estacion in carga)
        print(f"{tipo}: estaciones={len(carga)}, precios={precios}")
    print(f"Total en {args.base_datos}: {total[0]} estaciones, {total[1]} precios")


if __name__ == "__main__":
    main()
