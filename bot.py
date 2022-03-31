#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path

import qqbot
from qqbot.core.util.yaml_util import YamlUtil
from qqbot.model.message import CreateDirectMessageRequest

from command_register import command
from oil_price import get_data, get_discount_str, get_menu, get_prices_str

config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config.yml"))
DEFAULT_CITY = config["default_city"]

@command("/菜单")
async def ask_menu(city_name: str, event: str, message: qqbot.Message):
    ret = get_menu()
    await _send_message(ret, event, message)
    return True


@command("/油价")
async def ask_price(city_name: str, event: str, message: qqbot.Message):
    city_name = city_name if city_name.strip() != "" else DEFAULT_CITY
    ret = get_prices_str(await get_data(city_name), 0)
    await _send_message(ret, event, message)
    return True


@command("/0号油价")
async def ask_price0(city_name: str, event: str, message: qqbot.Message):
    city_name = city_name if city_name.strip() != "" else DEFAULT_CITY
    ret = get_prices_str(await get_data(city_name), 1)
    await _send_message(ret, event, message)
    return True


@command("/92油价")
async def ask_price92(city_name: str, event: str, message: qqbot.Message):
    city_name = city_name if city_name.strip() != "" else DEFAULT_CITY
    ret = get_prices_str(await get_data(city_name), 2)
    await _send_message(ret, event, message)
    return True


@command("/95油价")
async def ask_price95(city_name: str, event: str, message: qqbot.Message):
    city_name = city_name if city_name.strip() != "" else DEFAULT_CITY
    ret = get_prices_str(await get_data(city_name), 3)
    await _send_message(ret, event, message)
    return True


@command("/加油优惠")
async def ask_discount(city_name: str, event: str, message: qqbot.Message):
    city_name = city_name if city_name.strip() != "" else DEFAULT_CITY
    ret = get_discount_str(await get_data(city_name))
    await _send_message(ret, event, message)
    return True


async def _send_message(content: str, event: str, message: qqbot.Message):
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    dms_api = qqbot.AsyncDmsAPI(t_token, False)

    send = qqbot.MessageSendRequest(content, message.id)
    if event == "DIRECT_MESSAGE_CREATE":
        await dms_api.post_direct_message(message.guild_id, send)
    else:
        await msg_api.post_message(message.channel_id, send)


async def _message_handler(event: str, message: qqbot.Message):
    """
    定义事件回调的处理
    :param event: 事件类型
    :param message: 事件对象（如监听消息是Message对象）
    """

    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)

    tasks = [
        ask_menu,  # /菜单
        ask_price,  # /油价
        ask_price0,  # /0号油价
        ask_price92,  # /92油价
        ask_price95,  # /95油价
        ask_discount,  # /加油优惠
    ]
    for task in tasks:
        if await task("", event, message):
            return
    await _send_message("抱歉，没明白你的意思呢。" + get_menu(), event, message)


if __name__ == "__main__":
    t_token = qqbot.Token(config["bot"]["appid"], config["bot"]["token"])
    # @机器人后推送被动消息
    qqbot_handler = qqbot.Handler(
        qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler
    )
    # 私信消息
    qqbot_direct_handler = qqbot.Handler(
        qqbot.HandlerType.DIRECT_MESSAGE_EVENT_HANDLER, _message_handler
    )
    qqbot.async_listen_events(t_token, False, qqbot_handler, qqbot_direct_handler)
