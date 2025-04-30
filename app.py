from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from flask_paginate import Pagination, get_page_parameter
from geopy.distance import geodesic

#.envからAPI取得
load_dotenv()

# Flaskクラスをインスタンス化
app = Flask(__name__)

# 環境変数の取得
API_KEY = os.environ.get("API_KEY")
GOOGLEMAPS_API_KEY = os.environ.get("GOOGLEMAPS_API_KEY")

# URLと実行する関数をマッピング
@app.route("/")
def search_form():
    return render_template('search.html')


@app.route('/search', methods=['GET'])
def result_form():
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        keyword = request.args.get('keyword')
        range_value = request.args.get('range')
        page = request.args.get(get_page_parameter(), type=int, default=1)
        count = 10
        start = (page - 1) * count + 1

        params = {
            'key': API_KEY,
            'lat': lat,
            'lng': lng,
            'keyword': keyword,
            'range': range_value,
            'count': count,
            'start': start,
            'format': 'json'
        }

        url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        response = requests.get(url, params=params)
        data = response.json()
        

        shops = data["results"].get("shop", [])
        Added_shops = []

        # 距離情報を追加
        for shop in shops:
            shop_lat = float(shop["lat"])
            shop_lng = float(shop["lng"])
            distance_km = geodesic((lat, lng), (shop_lat, shop_lng)).km
            shop["distance_km"] = round(distance_km, 2)
            Added_shops.append(shop)
        shops = Added_shops


        total = int(data["results"].get("results_available", 0))

        pagination = Pagination(
            page=page,
            per_page=count,
            total=total,
            record_name='shops'
        )


        return render_template(
            'result.html',
            total=total,
            shops=shops,
            pagination=pagination,
            keyword=keyword,
            lat=lat,
            lng=lng,
            range_value=range_value,
            googlemaps_api_key=GOOGLEMAPS_API_KEY
        )


@app.route("/detail/<shop_id>", methods=['GET'])
def detail_form(shop_id):
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        keyword = request.args.get('keyword')
        range_value = request.args.get('range')

        params = {
            'key': API_KEY,
            'id': shop_id,
            'format': 'json'
        }

        url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        response = requests.get(url, params=params)
        data = response.json()


        if data["results"].get("shop"):
            shop = data["results"]["shop"][0]
        else:
            shop = None

        return render_template(
            'detail.html',
            keyword=keyword,
            lat=lat,
            lng=lng,
            range_value=range_value,
            shop = shop,
            googlemaps_api_key=GOOGLEMAPS_API_KEY
        )

if __name__=='__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)