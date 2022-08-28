# -*- coding:utf-8 -*-

from flask import Flask, jsonify, request
import requests
import json
import time

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0"}

app = Flask(__name__)
session = requests.Session()
session.headers = header
session.proxies = {"http": None, "https": None}
session.trust_env = False

order_dict = {}


def ForJsonToAssets(suit_json, key):
    list_all = []
    for li in suit_json["data"]["suit_items"].get(key, []):
        card_bg_dict = {"item": li}
        card_bg_dict.update({"id": str(round(time.time()))})
        card_bg_dict.update({"part": key})
        card_bg_dict.update({"state": "active"})
        card_bg_dict.update({"expired_time": 0})
        card_bg_dict.update({"equiped": False})
        list_all.append(card_bg_dict)
    return list_all


@app.route("/x/garb/v2/mall/suit/detail", methods=["GET"])
def garb_v2_mall_suit_detail():
    item_id = request.args.get("item_id")
    url = "https://api.bilibili.com/x/garb/v2/mall/suit/detail"
    response = session.get(url, params={"item_id": item_id})
    suit_json = response.json()
    suit_json['data']['sale_left_time'] = 0
    return jsonify(suit_json)


@app.route("/x/garb/coupon/usable", methods=["GET"])
def garb_coupon_usable():
    return jsonify({"code": 0, "message": "0", "ttl": 1, "data": None})


@app.route("/x/garb/v2/trade/create", methods=["POST"])
def garb_v2_trade_create():
    global order_dict
    item_id = request.form.get("item_id")
    order_id = str(round(time.time() * 100000))
    order_dict[order_id] = int(item_id)
    order_data = {"order_id": order_id, "state": "paying", "bp_enough": 1}
    return jsonify({"code": 0, "message": "0", "ttl": 1, "data": order_data})


@app.route("/x/garb/trade/query", methods=["GET"])
def garb_trade_query():
    order_id = request.args.get("order_id")
    mid = int(request.cookies.get("DedeUserID"))
    suit = order_dict[order_id]
    pay_id = str(round(time.time() * 100000))
    data = {"order_id": order_id, "mid": mid, "platform": "android",
            "item_id": suit, "pay_id": pay_id, "state": "paid"}
    return jsonify({"code": 0, "message": "0", "ttl": 1, "data": data})


@app.route("/x/internal/gaia-gateway/ExClimbWuzhi")
def ExClimbWuzhi():
    return jsonify({"code": 0, "message": "0", "ttl": 1, "data": {}})


@app.route("/x/garb/user/multbuy")
def garb_user_multbuy():
    return jsonify({"code": 0, "message": "0", "ttl": 1, "data": {"buy_num": 0, "sale_buy_num_limit": 100, "own_num": 1, "activity": {"zodiac": None}}})


@app.route("/x/garb/user/wallet")
def garb_user_wallet():
    return jsonify({"code": 0, "message": "0", "ttl": 1, "data": {"bcoin_balance": 0, "coupon_balance": 0}})


@app.route("/x/garb/user/suit/asset", methods=["GET"])
def garb_user_suit_asset():
    item_id = request.args.get("item_id")
    url = "https://api.bilibili.com/x/garb/v2/mall/suit/detail"
    response = session.get(url, params={"item_id": item_id})
    suit_json = response.json()
    return_json = {"code": "0", "ttl": 1}
    data_dict = {"id": round(time.time()), "part": "suit"}
    assets_list = []
    data_dict.update({"state": "active", "expired_time": 0, "equiped": False})
    tab_id = suit_json["data"]["group_id"]
    fan_no_color = suit_json["data"]["properties"]["fan_no_color"]
    suit_name = suit_json["data"]["name"]
    item_dict = {"item_id": item_id, "name": suit_name, "state": "active"}
    item_dict.update({"tab_id": tab_id, "suit_item_id": item_id})
    item_dict.update({"properties": suit_json["data"]["properties"]})
    item_dict.update({"current_activity": suit_json["data"]["current_activity"]})
    item_dict.update({"current_sources": suit_json["data"]["current_sources"]})
    item_dict.update({"finish_sources": suit_json["data"]["finish_sources"]})
    item_dict.update({"sale_left_time": 0})
    item_dict.update({"sale_time_end": 0})
    item_dict.update({"sale_surplus": 0})

    fan_dict = {"is_fan": True, "token": suit_name, "number": 1, "color": fan_no_color}
    suit_date = time.strftime("%Y/%m/%d", time.localtime(time.time()))
    fan_dict.update({"name": suit_name, "luck_item_id": 0, "date": suit_date})

    data_dict.update({"item": item_dict})
    data_dict.update({"fan": fan_dict})

    assets_list += ForJsonToAssets(suit_json, "thumbup")
    assets_list += ForJsonToAssets(suit_json, "emoji_package")
    assets_list += ForJsonToAssets(suit_json, "card")[0]
    assets_list += ForJsonToAssets(suit_json, "pendant")
    assets_list += ForJsonToAssets(suit_json, "play_icon")
    assets_list += ForJsonToAssets(suit_json, "card")[1]

    assets_list += ForJsonToAssets(suit_json, "skin")
    assets_list += ForJsonToAssets(suit_json, "loading")

    assets_list += ForJsonToAssets(suit_json, "space_bg")
    assets_list += ForJsonToAssets(suit_json, "card_bg")

    data_dict.update({"assets": assets_list})
    return_json.update({"data": data_dict})
    return jsonify(return_json)


app.run("0.0.0.0", 80, use_reloader=True)
