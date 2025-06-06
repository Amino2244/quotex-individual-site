from flask import Flask, render_template, jsonify
import requests
import datetime
import random

app = Flask(__name__)
price_history = []

def predict_direction(price_series):
    if len(price_series) < 3:
        return "WAIT"
    if price_series[-1] > price_series[-2] > price_series[-3]:
        return "CALL"
    elif price_series[-1] < price_series[-2] < price_series[-3]:
        return "PUT"
    else:
        return random.choice(["CALL", "PUT"])

def get_live_price():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=EURUSDT")
        data = response.json()
        return float(data['price'])
    except:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signal")
def signal():
    price = get_live_price()
    if price:
        price_history.append(price)
        if len(price_history) > 10:
            price_history.pop(0)
        direction = predict_direction(price_history)
    else:
        direction = "WAIT"
    return jsonify({
        "signal": direction,
        "price": price,
        "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S")
    })

if __name__ == "__main__":
    app.run(debug=True)