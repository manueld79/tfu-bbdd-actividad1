-- Consulta 1. Empresa con más estaciones terrestres, según el rótulo del fichero.
SELECT emp.rotulo AS empresa, COUNT(*) AS estaciones_terrestres
FROM estacion AS e
JOIN empresa AS emp ON emp.id_empresa = e.id_empresa
WHERE e.tipo_estacion = 'terrestre'
GROUP BY emp.id_empresa, emp.rotulo
ORDER BY estaciones_terrestres DESC
FETCH FIRST 1 ROW WITH TIES;
