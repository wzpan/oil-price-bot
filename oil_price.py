#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import qqbot
import os
import pickle

import asyncio
import aiohttp
from bs4 import BeautifulSoup

CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache.pkl")


async def _fetch_data(city_name: str) -> str:
    qqbot.logger.info("解析小熊油耗的数据...")
    url = "https://www.xiaoxiongyouhao.com/fprice/cityprice.php?city=" + city_name
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=url,
            timeout=5,
        ) as resp:
            content = await resp.text()
            return content


def _get_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            cache = pickle.load(f)
            return cache
    else:
        return None


def _update_cache(city_name: str, content: str, cache: dict):
    qqbot.logger.info("更新缓存数据")
    if not cache:
        cache = dict()
    cache[city_name] = {"last_updated": datetime.date.today(), "content": content}
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)


async def get_data(city_name: str) -> str:
    # 判断是否有当天的缓存，有的话就直接从缓存读取；
    # 否则从网页读取并覆盖当天缓存
    cache = _get_cache()
    if cache:
        for city, data in cache.items():
            if city == city_name and data["last_updated"] == datetime.date.today():
                qqbot.logger.info("有缓存，直接从缓存读取")
                return BeautifulSoup(data["content"], "html.parser")
    content = await _fetch_data(city_name)
    _update_cache(city_name, content, cache)
    return BeautifulSoup(content, "html.parser")


def _read_local_data(city_name: str) -> str:
    with open("price.mhtml") as f:
        content = f.readlines()
        return "".join(content)


def get_menu():
    return """功能菜单：
/油价 城市名 
    查询指定城市当天油价
    示例： /油价 深圳
/0号油价 城市名
    查询指定城市当天0号柴油的油价
    示例： /0号油价 深圳
/92油价 城市名
    查询指定城市当天92号汽油的油价
    示例： /92油价 深圳
/95油价 城市名
    查询指定城市当天95号汽油的油价
    示例： /95油价 深圳
/加油优惠 城市名
    查询指定城市的加油优惠信息
    示例：/加油优惠 深圳
"""


def _parse_price(soup: BeautifulSoup) -> dict:
    prices = soup.select(".highlighted-price-high")
    if len(prices) < 2:
        return None
    else:
        last_updated = soup.select_one("h5.text-left.subtitle").text
        response = dict()
        response["title"] = soup.select_one("h3.text-center").text
        response["95#"] = prices[0].text
        response["92#"] = prices[1].text
        if len(prices) > 2:
            response["0#"] = prices[2].text
        response["last_updated"] = last_updated
        return response


def get_prices_str(soup: BeautifulSoup, category: int = 0) -> str:
    """
    获取油价
    :param soup: BeautifulSoup 页面解析内容
    :param category: 分类 0：全部；1：0号柴油 2：92号汽油 3：95号汽油
    :return: 油价字符串
    """
    prices = _parse_price(soup)
    try:
        title = prices["title"]
        if "0#" in prices:
            price_0 = "0号柴油油价：{}".format(prices["0#"])
        else:
            price_0 = "没有当地的0号柴油油价信息"
        price_92 = "92号汽油油价：{}".format(prices["92#"])
        price_95 = "95号汽油油价：{}".format(prices["95#"])
        rets = [title]
        if category == 1:
            rets.append(price_0)
        elif category == 2:
            rets.append(price_92)
        elif category == 3:
            rets.append(price_95)
        else:
            rets.append(price_0)
            rets.append(price_92)
            rets.append(price_95)
        return "\n".join(rets)
    except Exception as e:
        qqbot.logger.error(e)
        return "抱歉，获取不到该地区的油价数据"


def _parse_discount(soup: BeautifulSoup) -> dict:
    tables = soup.select("table")
    if len(tables) < 2:
        # 不存在优惠数据
        return None
    else:
        discount_table = soup.select("table")[1]
        discounts = dict({"title": soup.select_one(".col-xs-12 > h4").text, "data": []})
        data = []
        lines = discount_table.select("tr")
        for i in range(1, len(lines)):
            line = lines[i]
            cols = line.select("td")
            data.append(
                {
                    "zone": cols[1].text.strip(),
                    "name": cols[2].text.strip(),
                    "num": cols[3].text.strip(),
                    "price": cols[4].text.strip(),
                }
            )
        discounts["data"] = data
        return discounts


def get_discount_str(soup: BeautifulSoup) -> str:
    """
    获取优惠信息
    :param soup: BeautifulSoup 页面解析内容
    :return: 优惠信息字符串
    """
    discounts = _parse_discount(soup)
    try:
        ret = discounts["title"] + "\r\n"
        for i in range(len(discounts["data"])):
            discount = discounts["data"][i]
            ret += """
优惠排名：#{}
区县：{}
加油站名称：{}
油价：{}
""".format(
                i + 1, discount["zone"], discount["name"], discount["price"]
            )
        ret += "\n本表出自小熊油耗™。数据根据本次调价后92#/E92#的车友实际支付价格统计。实际优惠政策可能比较复杂，请车友先打加油站电话核实后再前往。"
        return ret
    except Exception as e:
        qqbot.logger.error(e)
        return "抱歉，获取不到该地区的加油优惠信息"


if __name__ == "__main__":
    city = "深圳"
    content = asyncio.run(get_data("深圳"))
    soup = BeautifulSoup(content, "html.parser")
    print(get_prices_str(soup))
    print(get_discount_str(soup))
