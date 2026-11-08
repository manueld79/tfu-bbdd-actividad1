CREATE TABLE IF NOT EXISTS provincia (
    id_provincia integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS municipio (
    id_municipio integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_provincia integer NOT NULL REFERENCES provincia (id_provincia),
    nombre text NOT NULL,
    UNIQUE (id_provincia, nombre)
);

CREATE TABLE IF NOT EXISTS empresa (
    id_empresa integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rotulo text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tipo_carburante (
    id_tipo_carburante integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre text NOT NULL UNIQUE
);