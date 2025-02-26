from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# Token de acceso de Banxico (asegúrate de que esté configurado en variables de entorno)
API_TOKEN = os.getenv("BANXICO_API_KEY")

# Series de Banxico
SERIES = {
    "USD": "SF43718",  # Dólar estadounidense (últimos 20 días)
    "EUR": "SF46410",  # Euro (hoy)
    "CAD": "SF46406",  # Dólar canadiense (hoy)
    "GBP": "SF46407",  # Libra esterlina (hoy)
    "CNY": "SF46402",  # Yuan chino (hoy)
    "JPY": "SF46409",  # Yen japonés (hoy)
    "BRL": "SF46403",  # Real brasileño (hoy)
    "ARS": "SF46400"   # Peso argentino (hoy)
}

# Construcción de la URL para consultar todas las divisas
USD_SERIE = SERIES["USD"]  # Solo USD para los últimos 20 días
OTRAS_SERIES = ",".join([SERIES[key] for key in SERIES if key != "USD"])  # Otras divisas para hoy
API_URL_USD = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{USD_SERIE}/datos/20"
API_URL_OTRAS = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{OTRAS_SERIES}/datos/oportuno"

@app.route('/')
def home():
    return "¡El servidor está funcionando correctamente! Usa /tipo-cambio para obtener datos."

@app.route('/tipo-cambio', methods=['GET'])
def obtener_tipo_cambio():
    headers = {"Bmx-Token": API_TOKEN}

    # Consulta del dólar estadounidense (últimos 20 días)
    response_usd = requests.get(API_URL_USD, headers=headers)
    response_otras = requests.get(API_URL_OTRAS, headers=headers)

    resultado = {}

    if response_usd.status_code == 200:
        data_usd = response_usd.json()
        serie_usd = data_usd.get("bmx", {}).get("series", [])[0]
        resultado["USD"] = serie_usd.get("datos", [])  # Lista con los últimos 20 días

    if response_otras.status_code == 200:
        data_otras = response_otras.json()
        series_otras = data_otras.get("bmx", {}).get("series", [])

        # Extraer la cotización de hoy para cada divisa
        for serie in series_otras:
            nombre_divisa = next((key for key, value in SERIES.items() if value == serie.get("idSerie")), "Desconocido")
            if serie.get("datos"):
                resultado[nombre_divisa] = serie.get("datos")[0]  # Solo la cotización más reciente

    return jsonify(resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
