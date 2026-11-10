import xlrd
from decimal import Decimal
from datetime import datetime
from unidades import obtener_unidad
import psycopg

def contar_filas(archivo):
    with xlrd.open_workbook(archivo) as libro:
        hoja = libro.sheet_by_index(0)
        total = 0

        for indice in range(4, hoja.nrows):
            fila = hoja.row_values(indice)

            if any(str(valor).strip() for valor in fila):
                total += 1

        return total
    
def mostrar_estacion(archivo, hoja, fila_excel, tipo_estacion, detalle=True):
# with xlrd.open_workbook(archivo) as libro:
#     hoja = libro.sheet_by_index(0)

    cabeceras = hoja.row_values(3)
    fila = hoja.row_values(fila_excel - 1)

    if detalle:
        print(f"\nFila {fila_excel} de {archivo}")

    datos = dict(zip(cabeceras, fila))

    rotulo = datos["Rótulo"].strip() or None
    # precio = Decimal(str(datos["Precio gasolina 95 E5"]).replace(",", "."))

    if detalle:
        print(f"Provincia: {datos['Provincia']}")
        print(f"Municipio: {datos['Municipio']}")
        print(f"Localidad: {datos['Localidad']}")
        print(f"Rótulo: {rotulo}")
    # print(f"Precio gasolina 95 E5: {precio}")

    datos["Rótulo"] = rotulo
    # datos["Precio gasolina 95 E5"] = precio
    datos["tipo_estacion"] = tipo_estacion

    if tipo_estacion == "terrestre":
        fecha_texto = datos["Toma de datos"]
    else:
        fecha_texto = hoja.cell_value(0, 1)
    datos["fecha_actualizacion"] = datetime.strptime(
        fecha_texto, "%d/%m/%Y %H:%M"
    )

    for campo in ("Latitud", "Longitud"):
        valor = str(datos[campo]).strip()
        if valor:
            datos[campo] = Decimal(valor.replace(",", "."))
        else:
            datos[campo] = None
    if detalle:
        print(f"Fecha: {datos['fecha_actualizacion']}")
        print(f"Coordenadas: {datos['Latitud']}, {datos['Longitud']}")

    precios = []

    for cabecera, valor in datos.items():
        if cabecera.startswith("Precio ") and str(valor).strip():
            nombre = " ".join(cabecera[7:].split())
            nombre = nombre[0].upper() + nombre[1:]
            importe = Decimal(str(valor).strip().replace(",", "."))

            precios.append((nombre, importe))

    datos["precios"] = precios

    if detalle:
        print(f"Precios encontrados: {len(precios)}")
        for nombre, importe in precios:
            print(f"  {nombre}: {importe}")
       

    return datos
        

def leer_estaciones(archivo, tipo_estacion, filas=None):
    estaciones = []

    with xlrd.open_workbook(archivo) as libro:
        hoja = libro.sheet_by_index(0)

        if filas is None:
            filas = range(5, hoja.nrows + 1)

        for numero_fila in filas:
            fila = hoja.row_values(numero_fila - 1)

            if any(str(valor).strip() for valor in fila):
                estacion = mostrar_estacion(
                    archivo, hoja, numero_fila, tipo_estacion, detalle=False
                )
                estaciones.append(estacion)

    return estaciones

terrestres = contar_filas("/datos/preciosEESS_es.xls")
maritimas = contar_filas("/datos/embarcacionesPrecios_es.xls")

print(f"Filas terrestres: {terrestres}")
print(f"Filas marítimas: {maritimas}")

ruta_terrestre = "/datos/preciosEESS_es.xls"
ruta_maritima = "/datos/embarcacionesPrecios_es.xls"

todas_terrestres = leer_estaciones(ruta_terrestre, "terrestre")
todas_maritimas = leer_estaciones(ruta_maritima, "maritima")

print(f"Estaciones terrestres leídas: {len(todas_terrestres)}")
print(f"Estaciones marítimas leídas: {len(todas_maritimas)}")

precios_terrestres = sum(len(estacion["precios"]) for estacion in todas_terrestres)
precios_maritimos = sum(len(estacion["precios"]) for estacion in todas_maritimas)

print(f"Precios terrestres leídos: {precios_terrestres}")
print(f"Precios marítimos leídos: {precios_maritimos}")

terrestres_prueba = leer_estaciones(ruta_terrestre, "terrestre", (31,))
maritimas_prueba = leer_estaciones(ruta_maritima, "maritima", (6, 91))

santa_ana = terrestres_prueba[0]
altea, poste_girona = maritimas_prueba

print("\nValores recibidos de las funciones:")
print(f"Provincia de Santa Ana: {santa_ana['Provincia']}")
print(f"Rótulo de Altea: {altea['Rótulo']}")

detalle_insercion = False
detalle_comprobacion = False

with psycopg.connect() as conexion:
    with conexion.cursor() as cursor:
        for numero, estacion in enumerate(todas_terrestres + todas_maritimas, start=1):
            if numero == 1 or numero % 1000 == 0:
                print(f"Procesando estación {numero} de 12209...")
                
            cursor.execute(
                """
                INSERT INTO provincia (nombre)
                VALUES (%s)
                ON CONFLICT (nombre) DO NOTHING
                """,
                (estacion["Provincia"],),
            )
            cursor.execute(
                "SELECT id_provincia FROM provincia WHERE nombre = %s",
                (estacion["Provincia"],),
            )
            id_provincia = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO municipio (id_provincia, nombre)
                VALUES (%s, %s)
                ON CONFLICT (id_provincia, nombre) DO NOTHING
                """,
                (id_provincia, estacion["Municipio"]),
            )

            cursor.execute(
                """
                SELECT id_municipio
                FROM municipio
                WHERE id_provincia = %s AND nombre = %s
                """,
                (id_provincia, estacion["Municipio"]),
            )
            id_municipio = cursor.fetchone()[0]

            if detalle_insercion:
                print(
                    f"Municipio de {estacion['Localidad']}: "
                    f"ID {id_municipio} ({estacion['tipo_estacion']})"
                )

            id_empresa = None

            if estacion["Rótulo"] is not None:
                cursor.execute(
                    """
                    INSERT INTO empresa (rotulo)
                    VALUES (%s)
                    ON CONFLICT (rotulo) DO NOTHING
                    """,
                    (estacion["Rótulo"],),
                )

                cursor.execute(
                    "SELECT id_empresa FROM empresa WHERE rotulo = %s",
                    (estacion["Rótulo"],),
                )
                id_empresa = cursor.fetchone()[0]

            if detalle_insercion:
                print(f"Empresa de {estacion['Localidad']}:"
                        f"{estacion['Rótulo']} (ID: {id_empresa})")

            cursor.execute(
                """
                INSERT INTO estacion (
                    id_municipio, id_empresa, tipo_estacion, localidad,
                    codigo_postal, direccion, margen, latitud, longitud,
                    horario, tipo_venta, remision, tipo_servicio,
                    fecha_ultima_actualizacion
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s
                )
                RETURNING id_estacion
                """,
                (
                    id_municipio,
                    id_empresa,
                    estacion["tipo_estacion"],
                    estacion["Localidad"],
                    estacion["Código postal"],
                    estacion["Dirección"],
                    estacion.get("Margen") or None,
                    estacion["Latitud"],
                    estacion["Longitud"],
                    estacion["Horario"],
                    estacion["Tipo venta"],
                    estacion["Rem."],
                    estacion.get("Tipo servicio") or None,
                    estacion["fecha_actualizacion"],
                ),
            )
            id_estacion = cursor.fetchone()[0]
            if detalle_insercion:
                print(f"Estación insertada con ID: {id_estacion}")

            for nombre, importe in estacion["precios"]:
                cursor.execute(
                    """
                    INSERT INTO tipo_carburante (nombre)
                    VALUES (%s)
                    ON CONFLICT (nombre) DO NOTHING
                    """,
                    (nombre,),
                )

                cursor.execute(
                    "SELECT id_tipo_carburante FROM tipo_carburante WHERE nombre = %s",
                    (nombre,),
                )
                id_carburante = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO precio (
                        id_estacion, id_tipo_carburante, importe, unidad, fecha_dato
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        id_estacion,
                        id_carburante,
                        importe,
                        obtener_unidad(estacion["tipo_estacion"], nombre),
                        estacion["fecha_actualizacion"],
                    ),
                )
        if detalle_comprobacion:
            cursor.execute("SELECT nombre FROM provincia ORDER BY nombre")

            print("\nProvincias durante la transaccion:")
            for fila in cursor.fetchall():
                print(fila[0])

            cursor.execute(
                """
                SELECT municipio.nombre, provincia.nombre
                FROM municipio
                JOIN provincia ON municipio.id_provincia = provincia.id_provincia
                ORDER BY provincia.nombre, municipio.nombre
                """
            )
            
            print("\nMunicipios durante la transaccion:")
            for fila in cursor.fetchall():
                print(f"{fila[0]} ({fila[1]})")

        cursor.execute("SELECT COUNT(*) FROM estacion")
        print(f"\nEstaciones durante la transacción: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM precio")
        print(f"Precios durante la transacción: {cursor.fetchone()[0]}")

        if detalle_comprobacion:
            cursor.execute(
                """
                SELECT e.localidad, c.nombre, p.importe, p.unidad
                FROM precio AS p
                JOIN estacion AS e ON p.id_estacion = e.id_estacion
                JOIN tipo_carburante AS c
                    ON p.id_tipo_carburante = c.id_tipo_carburante
                ORDER BY e.tipo_estacion DESC, c.nombre
                """
            )

            print("\nPrecios por estación durante la transacción:")
            for localidad, carburante, importe, unidad in cursor.fetchall():
                print(f"{localidad} | {carburante} | {importe} {unidad}")


        conexion.commit()
        print("Transacción confirmada: datos guardados")