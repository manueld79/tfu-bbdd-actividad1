-- Muestra manual de preciosEESS_es.xls (fila 31) y embarcacionesPrecios_es.xls (fila 6).
BEGIN;

INSERT INTO provincia (nombre) VALUES ('ALBACETE'), ('ALICANTE');

INSERT INTO municipio (id_provincia, nombre)
SELECT p.id_provincia, origen.municipio
FROM (VALUES ('ALBACETE', 'ALBACETE'), ('ALICANTE', 'ALTEA')) AS origen (provincia, municipio)
JOIN provincia p ON p.nombre = origen.provincia;

INSERT INTO empresa (rotulo) VALUES ('REPSOL');

INSERT INTO tipo_carburante (nombre)
VALUES ('Gasolina 95 E5'), ('Gasolina 98 E5'), ('Gasóleo A'), ('Gasóleo Premium'), ('Gasóleo B');

WITH nuevas_estaciones AS (
    INSERT INTO estacion (
        id_municipio, id_empresa, tipo_estacion, localidad, codigo_postal, direccion,
        margen, latitud, longitud, horario, tipo_venta, remision, tipo_servicio,
        fecha_ultima_actualizacion
    )
    SELECT
        m.id_municipio, e.id_empresa, origen.tipo_estacion, origen.localidad,
        origen.codigo_postal, origen.direccion, origen.margen, origen.latitud,
        origen.longitud, origen.horario, origen.tipo_venta, origen.remision,
        origen.tipo_servicio, origen.fecha_dato
    FROM (VALUES
        ('ALBACETE', 'ALBACETE', 'REPSOL', 'terrestre', 'SANTA ANA', '02328',
         'AVENIDA PRINCIPE, 2', 'D', 38.900944, -1.994028, 'L-D: 08:00-16:00',
         'P', 'OM', 'L-D: 08:00-16:00 (A)', TIMESTAMP '2025-11-08 00:00:00'),
        ('ALICANTE', 'ALTEA', NULL, 'maritima', 'ALTEA', '03590',
         'PUERTO DEPORTIVO LUIS CAMPOMANES, S/N - PARTIDA MASCARAT', NULL,
         38.629556, -0.003833, 'M-D: 10:00-18:00',
         'Suministro a barcos deportivos o de recreo', 'dm', NULL,
         TIMESTAMP '2025-11-11 16:00:00')
    ) AS origen (
        provincia, municipio, rotulo, tipo_estacion, localidad, codigo_postal, direccion,
        margen, latitud, longitud, horario, tipo_venta, remision, tipo_servicio, fecha_dato
    )
    JOIN provincia p ON p.nombre = origen.provincia
    JOIN municipio m ON m.id_provincia = p.id_provincia AND m.nombre = origen.municipio
    LEFT JOIN empresa e ON e.rotulo = origen.rotulo
    RETURNING id_estacion, tipo_estacion, fecha_ultima_actualizacion
)
INSERT INTO precio (id_estacion, id_tipo_carburante, importe, unidad, fecha_dato)
SELECT e.id_estacion, c.id_tipo_carburante, origen.importe, 'EUR/l', e.fecha_ultima_actualizacion
FROM (VALUES
    ('terrestre', 'Gasolina 95 E5', 1.469),
    ('terrestre', 'Gasolina 98 E5', 1.579),
    ('terrestre', 'Gasóleo A', 1.455),
    ('terrestre', 'Gasóleo Premium', 1.545),
    ('terrestre', 'Gasóleo B', 1.145),
    ('maritima', 'Gasolina 95 E5', 1.680),
    ('maritima', 'Gasóleo A', 1.630)
) AS origen (tipo_estacion, carburante, importe)
JOIN nuevas_estaciones e ON e.tipo_estacion = origen.tipo_estacion
JOIN tipo_carburante c ON c.nombre = origen.carburante;

COMMIT;
