from flask import Flask, render_template, request, redirect, session, jsonify
import requests
import datetime
import random
import os  # ضروري لتحديد البورت الخاص بـ Render

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # يمكنك تغييره لاحقًا

price_history = []

# التنبؤ بالاتجاه (CALL / PUT)
def predict_direction(price_series):
    if len(price_series) < 3:
        return "WAIT"
    if price_series[-1] > price_series[-2] > price_series[-3]:
        return "CALL"
    elif price_series[-1] < price_series[-2] < price_series[-3]:
        return "PUT"
    else:
        return random.choice(["CALL", "PUT"])

# جلب السعر من Binance API
def get_live_price():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=EURUSDT")
        data = response.json()
        return float(data['price'])
    except:
        return None

# صفحة تسجيل الدخول
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '123456':
            session['user'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='بيانات الدخول غير صحيحة')
    return render_template('login.html')

# صفحة الإشارات بعد الدخول
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('index.html')

# API للإشارة اللحظية
@app.route('/signal')
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

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# 🚀 التشغيل على Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
