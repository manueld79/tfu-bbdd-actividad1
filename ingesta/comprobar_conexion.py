import psycopg

with psycopg.connect() as conexion:
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            
            SELECT current_database (),
                current_user,
                (SELECT COUNT(*) FROM estacion),
                (SELECT COUNT(*) FROM precio)
            """
        )
        base, usuario, estaciones, precios = cursor.fetchone()

print(f"Base de datos {base}")
print(f"Usuario: {usuario}")
print(f"Estaciones: {estaciones}")
print(f"Precios: {precios}")
