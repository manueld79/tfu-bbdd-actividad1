# Notas del diagrama entidad-relacion

El archivo `modelo-er-borrador.mmd` representa el esquema de `sql/01_esquema.sql`.

## Leyenda

- **PK**: clave primaria; identifica una fila y no admite valores nulos.
- **FK**: clave foranea; relaciona la fila con otra tabla.
- **UK**: restriccion UNIQUE de una sola columna.
- **NOT NULL**: el campo es obligatorio. No implica por si solo que un texto no pueda estar vacio.
- **NULL permitido**: el campo puede carecer de valor.
- **IDENTITY ALWAYS**: abreviatura de `GENERATED ALWAYS AS IDENTITY`; PostgreSQL genera el identificador.
- **UQ_M**: restriccion compuesta `UNIQUE (id_provincia, nombre)` de municipio. La pareja es unica; cada columna por separado puede repetirse.
- **UQ_P**: restriccion compuesta `UNIQUE (id_estacion, id_tipo_carburante, fecha_dato)` de precio. La combinacion de las tres columnas es unica.

La precision y escala de los campos `numeric` aparecen en los comentarios del diagrama para mantener una sintaxis compatible con Mermaid.

## Relaciones

- Cada municipio pertenece exactamente a una provincia; una provincia puede tener de cero a muchos municipios registrados.
- Cada estacion pertenece exactamente a un municipio; un municipio puede tener de cero a muchas estaciones registradas.
- Cada estacion puede tener cero o un rotulo asociado; un rotulo puede estar asociado a cero o muchas estaciones.
- Cada precio pertenece exactamente a una estacion y a un tipo de carburante. Una estacion o un tipo de carburante puede tener de cero a muchos precios registrados.
- Las lineas discontinuas indican relaciones no identificadoras: las claves foraneas no forman parte de la clave primaria de las tablas hijas.

## Decisiones del modelo

- `EMPRESA` representa el rotulo disponible en el Excel, no una entidad juridica verificada. Las consultas por empresa agrupan por ese rotulo; dos estaciones con la misma marca no tienen necesariamente el mismo propietario legal.
- `tipo_estacion` diferencia estaciones terrestres y maritimas.
- Se conservan municipio y localidad como datos distintos.
- La unidad pertenece al precio: un mismo carburante puede publicarse en unidades distintas segun el origen. El importador asigna las unidades de los productos conocidos; el DDL no limita `unidad` a una lista cerrada.
- El codigo postal es texto para conservar sus ceros iniciales y esta limitado a cinco digitos por un CHECK.
- Se permite la ausencia de empresa, margen, coordenadas y tipo de servicio, de acuerdo con las columnas y valores disponibles en los dos Excel utilizados.
- Los CHECK del DDL limitan el tipo de estacion, el margen, los rangos de coordenadas y los importes no negativos; estan resumidos en los comentarios del diagrama.
- Los `timestamp` no almacenan zona horaria. Se conserva la fecha y hora de la fuente sin atribuirle una zona que el archivo no especifica.
- El horario se conserva como texto en la estacion, tal como se publica en los Excel.
- Los colores dependen del tema del visor Mermaid y no indican restricciones ni cardinalidades.
