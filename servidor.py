from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Token de acceso de Banxico (Sustituye con tu clave real)
API_TOKEN = "f97e9ded6e03d00d516e37fdf710adb9c87c1aa2f3abe05bc4cb5a1d2c3e608d"
API_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno"

@app.route('/tipo-cambio', methods=['GET'])
def obtener_tipo_cambio():
    headers = {"Bmx-Token": API_TOKEN}
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        serie = data.get("bmx", {}).get("series", [])[0]
        fecha = serie.get("datos", [])[0].get("fecha")
        tipo_cambio = serie.get("datos", [])[0].get("dato")

        return jsonify({"fecha": fecha, "tipo_cambio": tipo_cambio})
    else:
        return jsonify({"error": "No se pudo obtener el tipo de cambio"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
