-- Consulta 5. Provincia de la estación marítima con Gasolina 95 E5 más cara.
-- Se añade la ubicación para identificar la estación y se conservan los empates.
SELECT pr.nombre AS provincia, m.nombre AS municipio, e.direccion,
       emp.rotulo AS empresa, p.importe, p.unidad
FROM estacion AS e
JOIN municipio AS m ON m.id_municipio = e.id_municipio
JOIN provincia AS pr ON pr.id_provincia = m.id_provincia
LEFT JOIN empresa AS emp ON emp.id_empresa = e.id_empresa
JOIN precio AS p ON p.id_estacion = e.id_estacion
JOIN tipo_carburante AS c ON c.id_tipo_carburante = p.id_tipo_carburante
WHERE e.tipo_estacion = 'maritima'
  AND c.nombre = 'Gasolina 95 E5'
  AND p.unidad = 'EUR/l'
ORDER BY p.importe DESC
FETCH FIRST 1 ROW WITH TIES;
