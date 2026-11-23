-- Consulta 3. Gasolina 95 E5 más barata en la Comunidad de Madrid.
-- Madrid es una comunidad uniprovincial. Se muestran todas las estaciones empatadas.
SELECT m.nombre AS municipio, e.localidad, e.direccion, e.codigo_postal,
       e.latitud, e.longitud, emp.rotulo AS empresa, e.margen,
       p.importe, p.unidad
FROM estacion AS e
JOIN municipio AS m ON m.id_municipio = e.id_municipio
JOIN provincia AS pr ON pr.id_provincia = m.id_provincia
JOIN precio AS p ON p.id_estacion = e.id_estacion
JOIN tipo_carburante AS c ON c.id_tipo_carburante = p.id_tipo_carburante
LEFT JOIN empresa AS emp ON emp.id_empresa = e.id_empresa
WHERE pr.nombre = 'MADRID'
  AND e.tipo_estacion = 'terrestre'
  AND c.nombre = 'Gasolina 95 E5'
  AND p.unidad = 'EUR/l'
ORDER BY p.importe
FETCH FIRST 1 ROW WITH TIES;
