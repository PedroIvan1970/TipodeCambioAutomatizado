from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# Token de acceso de Banxico
API_TOKEN = os.getenv("BANXICO_API_KEY")

# Series de Banxico con los códigos corregidos
SERIES = {
    "USD_HIST": "SF43718",  # Dólar estadounidense (últimos 20 días hábiles)
    "USD_TODAY": "SF43718",  # Dólar estadounidense (hoy)
    "EUR": "SF46410",  # Euro
    "GBP": "SF46407",  # Libra esterlina
    "CNY": "SF290383",  # Yuan chino
    "JPY": "SF46406"  # Yen japonés
}

# URLs para obtener los datos
API_URL_USD_HIST = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{SERIES['USD_HIST']}/datos/20"
API_URL_USD_TODAY = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{SERIES['USD_TODAY']}/datos/oportuno"
API_URL_OTRAS = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{','.join([v for k, v in SERIES.items() if k not in ['USD_HIST', 'USD_TODAY']])}/datos/oportuno"

@app.route('/')
def home():
    return "¡El servidor está funcionando correctamente! Usa /tipo-cambio para obtener datos."

@app.route('/tipo-cambio', methods=['GET'])
def obtener_tipo_cambio():
    headers = {"Bmx-Token": API_TOKEN}
    resultado = {}

    # 1️⃣ Consulta del USD (últimos 20 días hábiles)
    response_usd_hist = requests.get(API_URL_USD_HIST, headers=headers)
    if response_usd_hist.status_code == 200:
        data_usd_hist = response_usd_hist.json()
        serie_usd_hist = data_usd_hist.get("bmx", {}).get("series", [])[0]
        historial_usd = serie_usd_hist.get("datos", [])  # Lista con los últimos 20 días hábiles

        if historial_usd:
            # Convertir valores a float y asegurarnos de que la lista esté ordenada correctamente
            resultado["USD_HIST"] = [
                {"fecha": item["fecha"], "dato": float(item["dato"].replace(',', ''))} 
                for item in historial_usd if item["dato"] not in ["N/E", ""]
            ]

            # 2️⃣ Encontrar el USD del día anterior hábil
            if len(resultado["USD_HIST"]) > 1:
                resultado["USD_YESTERDAY"] = resultado["USD_HIST"][-2]  # El penúltimo valor en la lista

    # 3️⃣ Consulta del USD (hoy)
    response_usd_today = requests.get(API_URL_USD_TODAY, headers=headers)
    if response_usd_today.status_code == 200:
        data_usd_today = response_usd_today.json()
        serie_usd_today = data_usd_today.get("bmx", {}).get("series", [])[0]
        if serie_usd_today.get("datos"):
            dato_usd_today = serie_usd_today.get("datos")[0]
            resultado["USD_TODAY"] = {
                "fecha": dato_usd_today["fecha"],
                "dato": float(dato_usd_today["dato"].replace(',', '')) if dato_usd_today["dato"] not in ["N/E", ""] else None
            }

    # 4️⃣ Consulta de otras divisas (solo la más reciente)
    response_otras = requests.get(API_URL_OTRAS, headers=headers)
    if response_otras.status_code == 200:
        data_otras = response_otras.json()
        series_otras = data_otras.get("bmx", {}).get("series", [])
        
        for serie in series_otras:
            nombre_divisa = next((key for key, value in SERIES.items() if value == serie.get("idSerie")), "Desconocido")
            if serie.get("datos"):
                valor = serie.get("datos")[0].get("dato")
                fecha = serie.get("datos")[0].get("fecha")

                # 🔹 Convertir a float y manejar "N/E" como None
                resultado[nombre_divisa] = {
                    "fecha": fecha,
                    "dato": float(valor.replace(',', '')) if valor not in ["N/E", ""] else None
                }

    return jsonify(resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
