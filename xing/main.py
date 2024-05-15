#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from xing.conf import Conf
from xing.core import ObjectDict, SubParser
from xing.core import init_args, PluginType, plugin_runner
from xing.utils import get_logger, load_plugins, pattern_match
from xing import utils

settings = ObjectDict()

plugins = load_plugins(os.path.join(Conf.PROJECT_DIRECTORY, "plugins"))


def show_plugins(args):
    cnt = 0
    for plugin in plugins:
        plugin_name = plugin._plugin_name
        if pattern_match(args.plugin_name, plugin_name):
            cnt += 1

            if plugin.plugin_type == PluginType.SNIFFER:
                print("[{}][{}-{}] {} ".format(cnt,plugin.plugin_type,
                    plugin.target_scheme, plugin_name ))
            else:
                print("[{}][{}] {} | {}".format(cnt, plugin.plugin_type,
                plugin_name, plugin.vul_name))


def load_plugin_by_filter(plugin_type, filter_name):
    filter_plugins = []
    for plugin in plugins:
        plugin_name = plugin._plugin_name
        if plugin.plugin_type != plugin_type:
            continue
        
        if not pattern_match(filter_name, plugin_name):
            continue

        filter_plugins.append(plugin)

    return filter_plugins


def scan(args):
    logger = get_logger()
    filter_plugins = load_plugin_by_filter(PluginType.POC,
                                           args.plugin_name)

    logger.info("load plugin {} ".format(len(filter_plugins)))
    plugin_runner(plugins=filter_plugins,
                  targets=load_targets(args.target), concurrency=args.concurrency_count)


def sniffer(args):
    logger = get_logger()
    filter_plugins = load_plugin_by_filter(PluginType.SNIFFER,
                                           args.plugin_name)

    logger.info("load plugin {} ".format(len(filter_plugins)))
    plugin_runner(plugins=filter_plugins,
                  targets=load_targets(args.target), concurrency=args.concurrency_count)


def exploit(args):
    logger = get_logger()
    filter_plugins = load_plugin_by_filter(PluginType.POC,
                                           args.plugin_name)

    plg_list = []
    for plg in filter_plugins:
        if not getattr(plg, "exploit_cmd", None):
            continue
        plg_list.append(plg)

    logger.info("load plugin {} ".format(len(plg_list)))
    for plg in plg_list:
        logger.info("execute cmd: {}".format(args.cmd))
        plg.exploit_cmd(target=args.target, cmd=args.cmd)


def brute(args):
    logger = get_logger()
    username_file = args.username_file
    if username_file:
        username_file = os.path.abspath(username_file)
        if not os.path.isfile(username_file):
            logger.warning("not found user file {}".format(username_file))
            return

    password_file = args.password_file
    if password_file:
        password_file = os.path.abspath(password_file)
        if not os.path.isfile(password_file):
            logger.warning("not found  password_file {}".format(password_file))
            return

    filter_plugins = load_plugin_by_filter(PluginType.BRUTE, args.plugin_name)
    logger.info("load plugin {} ".format(len(filter_plugins)))
    for plg in filter_plugins:
        if username_file:
            plg.username_file = username_file
        if password_file:
            plg.password_file = password_file

    plugin_runner(plugins=filter_plugins,
                  targets=load_targets(args.target), concurrency=args.concurrency_count)


def load_targets(target):
    if os.path.isfile(target):
        return utils.load_file(target)
    else:
        return [target]


def main():
    args, parser = init_args()
    if args.subparser == SubParser.LIST:
        show_plugins(args)
        sys.exit()
    
    elif args.subparser == SubParser.SCAN:
        scan(args)
        sys.exit()

    elif args.subparser == SubParser.SNIFFER:
        sniffer(args)
        sys.exit()

    elif args.subparser == SubParser.EXPLOIT:
        exploit(args)
        sys.exit()

    elif args.subparser == SubParser.BRUTE:
        brute(args)
        sys.exit()

    else:
        parser.print_usage()
        sys.exit()


if __name__ == '__main__':  # pragma: no cover
    main()

