# Decisiones del modelo de carburantes

El diagrama `modelo-er.mmd` y su imagen `modelo-er.png` representan las seis tablas de `sql/01_esquema.sql`. Parto de los dos Excel del material docente de 2025–2026. El modelo de referencia del profesor se cita en el README; esta versión adapta sus decisiones a los campos que realmente contienen esos archivos.

## Por qué estas seis tablas

- **Provincia y municipio:** se guardan una sola vez. Cada municipio pertenece a una provincia. La pareja provincia y nombre es única, porque dos municipios de provincias distintas pueden compartir nombre.
- **Empresa:** guarda el rótulo publicado. Sirve para agrupar estaciones por marca, pero no permite asegurar que tengan el mismo propietario legal. La relación es opcional: Altea, por ejemplo, viene sin rótulo y se guarda con `NULL`.
- **Estación:** reúne ubicación, horario y demás datos de la instalación. `tipo_estacion` distingue terrestre y marítima. Municipio y localidad se conservan separados: la localidad de Santa Ana pertenece al municipio de Albacete.
- **Tipo de carburante:** es el catálogo de productos, para no repetir sus nombres en cada precio.
- **Precio:** relaciona una estación con un carburante, un importe, una unidad y una fecha. Esto permite que una estación tenga tantos precios como productos ofrezca, sin crear una columna por producto en la base de datos.

El horario y el tipo de servicio permanecen como texto dentro de la estación, tal como vienen publicados. No se necesitan tablas adicionales para responder a las consultas del trabajo. Si hubiera que consultar franjas horarias o varios servicios por separado, habría que descomponer esos textos y ampliar el modelo.

## Datos que requieren atención

- El código postal es texto, tiene cinco dígitos y conserva los ceros iniciales.
- Los importes se guardan con `numeric(12,6)`; Python utiliza `Decimal` para leer los decimales.
- La unidad pertenece al precio. Por ejemplo, el gasóleo B terrestre viene en EUR/l y el marítimo en EUR/1000 l. Los productos publicados por peso se conservan en EUR/kg.
- Un precio vacío no se convierte en cero: no se crea esa fila de precio.
- Se admite ausencia de rótulo, margen, coordenadas y tipo de servicio. En los archivos históricos hay cuatro estaciones marítimas sin rótulo y seis sin coordenadas. No se inventan valores para completarlas.
- En terrestres se toma la fecha de la columna «Toma de datos». El archivo marítimo no tiene esa columna: se usa su fecha de publicación como fecha de referencia disponible. No se presenta como una fecha individual de actualización conocida.
- Los `timestamp` no almacenan zona horaria: se conserva la hora publicada sin atribuirle una zona que el fichero no especifica.
- Los campos de porcentaje de mezcla están vacíos en estos Excel. El importador rechaza un archivo que los contenga rellenos, porque este esquema no tiene atributos para guardarlos. No los descarta silenciosamente.
- Esta entrega carga una instantánea. Aunque la clave única de precio incluye la fecha, el importador exige una base sin estaciones; no implementa la actualización periódica ni un historial completo de las instalaciones.

## Relaciones y símbolos

- Provincia `1` — `0..N` municipios.
- Municipio `1` — `0..N` estaciones.
- Empresa `0..1` — `0..N` estaciones: cada estación tiene como máximo un rótulo asociado.
- Estación `1` — `0..N` precios.
- Tipo de carburante `1` — `0..N` precios.

En la notación de pata de gallo, una barra representa uno, un círculo representa cero y la pata de gallo representa muchos. Las líneas discontinuas indican relaciones no identificadoras: las claves foráneas no forman parte de la clave primaria de la tabla hija. Los colores del visor no cambian el significado del modelo.

## Claves y restricciones del DDL

- **PK:** clave primaria que identifica cada fila. Los identificadores se generan con `GENERATED ALWAYS AS IDENTITY`.
- **FK:** clave foránea que exige que exista la fila relacionada.
- **UK:** `UNIQUE` de una columna.
- **UQ_M:** `UNIQUE (id_provincia, nombre)` en municipio. Es única la pareja, no cada columna por separado.
- **UQ_P:** `UNIQUE (id_estacion, id_tipo_carburante, fecha_dato)` en precio.
- **NOT NULL:** el campo no admite nulos. Por sí solo no impide una cadena vacía; el importador comprueba los textos obligatorios.
- **CHECK:** limita el tipo de estación, los cinco dígitos del código postal, los valores de margen, los rangos de coordenadas y los importes no negativos.

La precisión de `numeric` se indica en los comentarios del diagrama para mantener la sintaxis compatible con Mermaid.
