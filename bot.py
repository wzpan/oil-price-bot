#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path
import threading

import aiohttp
import qqbot

from qqbot.core.util.yaml_util import YamlUtil
from qqbot.model.message import CreateDirectMessageRequest

from oil_price import get_data, get_prices_str, get_discount_str

config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config.yml"))


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

async def _message_handler(event, message: qqbot.Message):
    """
    定义事件回调的处理
    :param event: 事件类型
    :param message: 事件对象（如监听消息是Message对象）
    """
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    dms_api = qqbot.AsyncDmsAPI(t_token, False)

    # 打印返回信息
    content = message.content
    qqbot.logger.info("event %s" % event + ",receive message %s" % content)

    ret = "抱歉，没明白你的意思呢。" + get_menu()

    # 根据指令触发不同的推送消息
    if "/菜单" in content:
        ret = get_menu()

    elif "/0号油价" in content:
        split = content.split("/0号油价 ")
        soup = await get_data(split[1] if len(split)>1 else '深圳')
        ret = get_prices_str(soup, 1)
        #await send_weather_ark_message(weather, message.channel_id, message.id)
    
    elif "/92油价" in content:
        split = content.split("/92油价 ")
        soup = await get_data(split[1] if len(split)>1 else '深圳')
        ret = get_prices_str(soup, 2)
        #await send_weather_ark_message(weather, message.channel_id, message.id)

    elif "/95油价" in content:
        split = content.split("/95油价 ")
        soup = await get_data(split[1] if len(split)>1 else '深圳')
        ret = get_prices_str(soup, 3)

    elif "/油价" in content:
        split = content.split("/油价 ")
        soup = await get_data(split[1] if len(split)>1 else '深圳')
        ret = get_prices_str(soup, 0)
    
    elif "/加油优惠" in content:
        split = content.split("/加油优惠 ")
        soup = await get_data(split[1] if len(split)>1 else '深圳')
        ret = get_discount_str(soup)

    send = qqbot.MessageSendRequest(ret, message.id)

    if (event == 'DIRECT_MESSAGE_CREATE'):
        await dms_api.post_direct_message(message.guild_id, send)
    else:
        await msg_api.post_message(message.channel_id, send)



# async的异步接口的使用示例
if __name__ == "__main__":
    t_token = qqbot.Token(config["token"]["appid"], config["token"]["token"])
    # @机器人后推送被动消息
    qqbot_handler = qqbot.Handler(
        qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler
    )    
    qqbot_direct_handler = qqbot.Handler(
        qqbot.HandlerType.DIRECT_MESSAGE_EVENT_HANDLER, _message_handler
    )
    qqbot.async_listen_events(t_token, False, qqbot_handler, qqbot_direct_handler)