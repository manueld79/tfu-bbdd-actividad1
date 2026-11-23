-- Consulta 4. Gasóleo A más barato en un radio de 10 km del centro de Albacete.
-- Punto de referencia adoptado para el ejercicio: 38.9943, -1.8585 (WGS84).
-- Distancia geográfica con Haversine y radio terrestre medio de 6371 km.
-- No calcula rutas por carretera. Se filtra antes de redondear la distancia.
WITH referencia AS (
    SELECT 38.9943::double precision AS latitud,
           -1.8585::double precision AS longitud
), distancias AS (
    SELECT e.*,
           2 * 6371 * ASIN(SQRT(LEAST(1.0, GREATEST(0.0,
               POWER(SIN(RADIANS(e.latitud::double precision - r.latitud) / 2), 2)
               + COS(RADIANS(r.latitud)) * COS(RADIANS(e.latitud::double precision))
               * POWER(SIN(RADIANS(e.longitud::double precision - r.longitud) / 2), 2)
           )))) AS distancia_km
    FROM estacion AS e
    CROSS JOIN referencia AS r
    WHERE e.tipo_estacion = 'terrestre'
      AND e.latitud IS NOT NULL AND e.longitud IS NOT NULL
)
SELECT m.nombre AS municipio, e.localidad, e.direccion, e.codigo_postal,
       e.latitud, e.longitud, emp.rotulo AS empresa, e.margen,
       ROUND(e.distancia_km::numeric, 3) AS distancia_km,
       p.importe, p.unidad
FROM distancias AS e
JOIN municipio AS m ON m.id_municipio = e.id_municipio
LEFT JOIN empresa AS emp ON emp.id_empresa = e.id_empresa
JOIN precio AS p ON p.id_estacion = e.id_estacion
JOIN tipo_carburante AS c ON c.id_tipo_carburante = p.id_tipo_carburante
WHERE e.distancia_km <= 10
  AND c.nombre = 'Gasóleo A'
  AND p.unidad = 'EUR/l'
ORDER BY p.importe
FETCH FIRST 1 ROW WITH TIES;
