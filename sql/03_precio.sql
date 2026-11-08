CREATE TABLE IF NOT EXISTS precio (
    id_precio integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_estacion integer NOT NULL REFERENCES estacion (id_estacion),
    id_tipo_carburante integer NOT NULL REFERENCES tipo_carburante (id_tipo_carburante),
    importe numeric(12,6) NOT NULL CHECK (importe >= 0),
    unidad text NOT NULL,
    fecha_dato timestamp NOT NULL,
    UNIQUE (id_estacion, id_tipo_carburante, fecha_dato)
);