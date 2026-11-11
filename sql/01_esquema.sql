BEGIN;

CREATE TABLE provincia (
    id_provincia integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre text NOT NULL UNIQUE
);

CREATE TABLE municipio (
    id_municipio integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_provincia integer NOT NULL REFERENCES provincia (id_provincia),
    nombre text NOT NULL,
    UNIQUE (id_provincia, nombre)
);

CREATE TABLE empresa (
    id_empresa integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rotulo text NOT NULL UNIQUE
);

CREATE TABLE estacion (
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

CREATE TABLE tipo_carburante (
    id_tipo_carburante integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre text NOT NULL UNIQUE
);

CREATE TABLE precio (
    id_precio integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_estacion integer NOT NULL REFERENCES estacion (id_estacion),
    id_tipo_carburante integer NOT NULL REFERENCES tipo_carburante (id_tipo_carburante),
    importe numeric(12,6) NOT NULL CHECK (importe >= 0),
    unidad text NOT NULL,
    fecha_dato timestamp NOT NULL,
    UNIQUE (id_estacion, id_tipo_carburante, fecha_dato)
);

COMMIT;
