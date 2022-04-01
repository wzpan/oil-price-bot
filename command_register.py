#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import qqbot


def command(command_str: str, check_param: bool = False, invalid_func=None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if command_str != "" and command_str in args[2].content:
                qqbot.logger.info("command %s" % command_str)
                params = args[2].content.split(command_str)[1].strip()
                if check_param and params == "":
                    return await invalid_func(args[1], args[2])
                return await func(params, args[1], args[2])
            else:
                qqbot.logger.debug("skip command %s" % command_str)
                return None

        return wrapper

    return decorator
