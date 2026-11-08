CREATE TABLE IF NOT EXISTS estacion (
    id_estacion integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_municipio integer NOT NULL REFERENCES municipio (id_municipio),
    id_empresa integer REFERENCES empresa (id_empresa),
    tipo_estacion text NOT NULL CHECK (tipo_estacion IN ('terrestre', 'maritima')),
    localidad text NOT NULL,
    codigo_postal text NOT NULL CHECK (codigo_postal ~ '^[0-9]{5}$'),
    direccion text NOT NULL,
    margen text CHECK (margen IN ('D', 'I', 'N')),
    latitud numeric(9,6) CHECK (latitud BETWEEN -90 AND 90),
    longitud numeric(9,6) CHECK (longitud BETWEEN -180 AND 180),
    horario text NOT NULL,
    tipo_venta text NOT NULL,
    remision text NOT NULL,
    tipo_servicio text,
    fecha_ultima_actualizacion timestamp NOT NULL
);