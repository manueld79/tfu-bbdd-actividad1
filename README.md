# Actividad 1 · Base de datos de carburantes

Proyecto de laboratorio con PostgreSQL 16 en Docker e ingesta de dos Excel históricos mediante Python y uv.

## Preparación

Se necesitan Docker con Docker Compose, uv y acceso a Internet para obtener las imágenes y las dependencias. El puerto local 55432 debe estar disponible.

En una copia nueva del repositorio, crea la configuración local y elige una contraseña en `.env`.

```bash
cp .env.example .env
```

`.env` queda excluido de Git. La contraseña se utiliza al inicializar PostgreSQL. Si reutilizas un volumen existente, debe coincidir con la contraseña que se configuró al crearlo.

## Demostración

Ejecuta los comandos desde la carpeta del proyecto.

```bash
# Espera a que pulses Enter entre bloques para poder explicarlos en el vídeo.
bash demo_videomemoria.sh --manual

# Ensayo automático con una pausa de ocho segundos entre bloques.
bash demo_videomemoria.sh

# Ensayo automático sin pausas.
bash demo_videomemoria.sh --pausa 0
```

Cada ejecución crea una base `carburantes_demo_<fecha>_<hora>_<proceso>`, aplica el esquema, muestra el recuento inicial, importa los dos Excel, comprueba el reparto y ejecuta las consultas disponibles. La salida queda guardada en `logs/`. Las bases de las ejecuciones anteriores se conservan en el volumen de PostgreSQL.

El Bash ejecuta Python en el ordenador mediante uv. PostgreSQL se ejecuta en Docker. uv instala las dependencias fijadas en `requirements.txt` en su entorno administrado.

## Archivos

- `compose.yaml` configura PostgreSQL y su volumen persistente.
- `sql/01_esquema.sql` crea las seis tablas del modelo.
- `cargar_excel.py` lee, valida y carga los dos Excel en una transacción. Rechaza una base que ya contenga estaciones.
- `modelo-er-borrador.mmd`, `modelo-er.svg` y `modelo-er.png` contienen el diagrama editable y sus exportaciones.
- `modelo-er-notas.md` explica las relaciones y las restricciones.
- `sql/02_muestra.sql` contiene una muestra SQL.
- `sql/03_consulta_01.sql` busca el rótulo con más estaciones terrestres.
- `datos/` contiene las copias de los Excel históricos utilizadas en la práctica.

## Datos de referencia

Los archivos proceden del repositorio docente del curso 2025–2026, en la carpeta `actividades/a1-laboratorio/data`.

Fuente del material de referencia: https://github.com/jarturomora/bases-datos-avanzadas-gii/tree/curso-2025-2026/actividades/a1-laboratorio

| Origen | Estaciones | Precios |
|---|---:|---:|
| Terrestre | 12.073 | 43.678 |
| Marítimo | 136 | 254 |
| Total | 12.209 | 43.932 |

La primera consulta devuelve REPSOL con 2.733 estaciones terrestres en estos archivos. La tabla `empresa` representa el rótulo publicado en el Excel.

## Estado de la actividad

Esta versión recupera el laboratorio anterior para revisarlo con las aclaraciones de clase. Contiene la primera de las cinco consultas de la actividad. Quedan pendientes las otras cuatro, la revisión de la clase del 10 de noviembre de 2026, la prueba en WSL/Linux y la grabación final de la videomemoria.
