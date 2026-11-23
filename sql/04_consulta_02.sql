-- Consulta 2. Empresa con más estaciones marítimas, según el rótulo del fichero.
-- Las estaciones sin rótulo no se atribuyen a una empresa inventada.
SELECT emp.rotulo AS empresa, COUNT(*) AS estaciones_maritimas
FROM estacion AS e
JOIN empresa AS emp ON emp.id_empresa = e.id_empresa
WHERE e.tipo_estacion = 'maritima'
GROUP BY emp.id_empresa, emp.rotulo
ORDER BY estaciones_maritimas DESC
FETCH FIRST 1 ROW WITH TIES;
