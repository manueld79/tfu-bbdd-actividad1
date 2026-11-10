def obtener_unidad(tipo_estacion, carburante):
    if tipo_estacion == "maritima" and carburante in (
        "Gasóleo B",
        "Gasóleo de uso marítimo",
    ):
        return "EUR/1000 l"

    if carburante in (
        "Gas natural comprimido",
        "Gas natural licuado",
        "Hidrógeno",
        "Metanol",
        "Amoniaco",
        "BGNC",
        "BGNL",
    ):
        return "EUR/kg"

    return "EUR/l"


if __name__ == "__main__":
    print("Gasóleo B terrestre:", obtener_unidad("terrestre", "Gasóleo B"))
    print("Gasóleo B marítimo:", obtener_unidad("maritima", "Gasóleo B"))
    print("Gas natural comprimido:", obtener_unidad("terrestre", "Gas natural comprimido"))