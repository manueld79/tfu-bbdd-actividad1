# Resultados y pruebas de la entrega

Ejecución comprobada el **13 de noviembre de 2026** en macOS, con PostgreSQL 16 en Docker y Python 3.12 mediante uv. Los datos son los dos Excel históricos publicados el 11 de noviembre de 2025; sus hashes están en `datos/SHA256SUMS`.

## Ejecución comprobada

La demostración completa se ejecutó con `bash demo_videomemoria.sh --pausa 0` y también en modo manual. Estos CSV proceden de aquella ejecución. Para reproducirlos, se pueden seguir los pasos del [README principal](../README.md#preparación); cada ejecución guarda un registro y nuevos CSV en `logs/`.

El recuento inicial fue 0 estaciones y 0 precios. El resultado final fue:

| Tipo | Estaciones | Precios |
|---|---:|---:|
| Terrestre | 12.073 | 43.678 |
| Marítima | 136 | 254 |
| Total | 12.209 | 43.932 |

Cada CSV contiene la salida real de su consulta. No es una tabla transcrita a mano.

## Las cinco consultas

1. [03_consulta_01.csv](03_consulta_01.csv): REPSOL, 2.733 estaciones terrestres.
2. [04_consulta_02.csv](04_consulta_02.csv): REPSOL, 69 estaciones marítimas.
3. [05_consulta_03.csv](05_consulta_03.csv): PLENERGY, Camino del Olivo, 1, Meco (28880), margen D; gasolina 95 E5 a 1,309 EUR/l.
4. [06_consulta_04.csv](06_consulta_04.csv): A&A, Avenida Escritor Rodrigo Rubio, 3, Albacete (02005), margen D; gasóleo A a 1,288 EUR/l, a aproximadamente 2,711 km del punto de referencia.
5. [07_consulta_05.csv](07_consulta_05.csv): dos estaciones empatadas a 1,852 EUR/l: NOU FONTANA en Jávea/Xàbia (Alicante) y MARINA DEL MEDITERRANEO ESTE S.L. en Almuñécar (Granada).

Las consultas conservan los empates mediante `FETCH FIRST 1 ROW WITH TIES`. En la consulta 4 se compara la distancia sin redondear con el límite de 10 km. El punto adoptado es 38.9943, -1.8585; la interpretación es un radio geográfico, no una ruta de conducción.

## Comprobaciones adicionales

- **Contraste independiente de las cinco consultas:** se leyeron directamente las filas con xlrd, sin utilizar las funciones de lectura del importador, y se calcularon agrupaciones, mínimos y máximos en Python. Se compararon las filas completas de ubicación, rótulo, margen e importe que correspondían a cada consulta, incluyendo todos los empates.
- **Distancia:** se contrastó Haversine del SQL con la ley esférica del coseno en Python. Había 41 estaciones con gasóleo A dentro del radio; el mínimo y la distancia mostrada coinciden.
- **Muestra:** en un esquema temporal, Santa Ana y Altea produjeron 2 estaciones y 7 precios. Altea conservó su empresa nula.
- **Repetición:** una segunda carga se rechazó y el recuento permaneció en 2/7.
- **Reversión:** se provocó una inserción con importe negativo. Se rechazó por el CHECK y, tras revertir la transacción de prueba, las seis tablas estaban vacías. El esquema temporal se deshizo al terminar.
- **Modo manual:** se ejecutó también con una terminal interactiva, confirmando las nueve pausas con Enter. Terminó con código 0 y los mismos cinco resultados.
- **Sintaxis y configuración:** revisión de sintaxis Bash y Python, validación de Compose y comprobación de espacios del diff de Git.

El 23 de noviembre de 2026 se verificaron los hashes de los dos Excel y se recalcularon de nuevo los recuentos y las cinco respuestas con una lectura independiente de los archivos. Coinciden con estos CSV. Esta comprobación no repitió la carga en PostgreSQL.

## Límites

La ejecución completa está comprobada en macOS. El recorrido nativo en WSL no se ha probado. Los datos son una instantánea histórica, no precios actuales. La consulta de Albacete usa un radio geográfico de 10 km, no una distancia por carretera. La [videomemoria](../README.md#videomemoria) incluye un tramo con las cinco consultas ejecutándose en PostgreSQL.
