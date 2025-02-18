from flask import Flask, render_template, request, redirect
import json
from datetime import datetime
import os

app = Flask(__name__)

DATA_DIR = '../../data'
SHOPS_FILE = os.path.join(DATA_DIR, 'shops.json')
SALES_FILE = os.path.join(DATA_DIR, 'sales.json')
TOTAL_FILE = os.path.join(DATA_DIR, 'total_shops.json')


def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return []


@app.route('/')
def dashboard():
    # 总店铺数数据
    total_data = sorted(load_json(TOTAL_FILE), key=lambda x: x['timestamp'])
    chart_data = {
        'labels': [datetime.fromtimestamp(d['timestamp']).strftime('%Y-%m-%d %H:%M')
                   for d in total_data],
        'values': [d['total_shops'] for d in total_data]
    }
    return render_template('index.html', chart_data=chart_data)


@app.route('/shops', methods=['GET', 'POST'])
def manage_shops():
    if request.method == 'POST':
        new_shop = request.form['shop_url']
        shops = load_json(SHOPS_FILE)
        if new_shop not in shops:
            shops.append(new_shop)
            with open(SHOPS_FILE, 'w') as f:
                json.dump(shops, f)
        return redirect('/shops')

    # 店铺销量数据
    shops = load_json(SHOPS_FILE)
    sales_data = {}
    for shop in shops:
        sales_data[shop] = []
        for entry in load_json(SALES_FILE):
            if entry['shop_url'] == shop:
                sales_data[shop].append({
                    'time': datetime.fromtimestamp(entry['timestamp']).strftime('%m-%d %H:%M'),
                    'sales': entry['sales']
                })
    return render_template('shops.html', shops=shops, sales_data=sales_data)


@app.route('/delete')
def delete_shop():
    shop_url = request.args.get('url')
    shops = load_json(SHOPS_FILE)
    if shop_url in shops:
        shops.remove(shop_url)
        with open(SHOPS_FILE, 'w') as f:
            json.dump(shops, f)
    return redirect('/shops')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)