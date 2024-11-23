#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json
import yaml
import time

from apiproxy.douyin.douyin import Douyin
from apiproxy.douyin import douyin_headers
from apiproxy.common import utils

configModel = {
    "link": [],
    "path": os.getcwd(),
    "mode": ["post"],
    "number": {
        "post": 0,
        "like": 0,
        "allmix": 0,
        "mix": 0,
        "music": 0,
    },
    'database': True,
    "increase": {
        "post": False,
        "like": False,
        "allmix": False,
        "mix": False,
        "music": False,
    },
    "cookie": None
}

def argument():
    parser = argparse.ArgumentParser(description='抖音数据获取工具')
    parser.add_argument("--cmd", "-C", help="使用命令行(True)或者配置文件(False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--link", "-l",
                        help="作品、直播、合集、音乐集合、个人主页的分享链接或者电脑浏览器网址",
                        type=str, required=False, default=[], action="append")
    parser.add_argument("--path", "-p", help="JSON文件保存位置, 默认当前文件位置",
                        type=str, required=False, default=os.getcwd())
    parser.add_argument("--mode", "-M", help="link是个人主页时, 设置获取发布的作品(post)或喜欢的作品(like)或者用户所有合集(mix), 默认为post, 可以设置多种模式",
                        type=str, required=False, default=[], action="append")
    parser.add_argument("--postnumber", help="主页下作品获取个数设置, 默认为0 全部获取",
                        type=int, required=False, default=0)
    parser.add_argument("--likenumber", help="主页下喜欢获取个数设置, 默认为0 全部获取",
                        type=int, required=False, default=0)
    parser.add_argument("--allmixnumber", help="主页下合集获取个数设置, 默认为0 全部获取",
                        type=int, required=False, default=0)
    parser.add_argument("--mixnumber", help="单个合集下作品获取个数设置, 默认为0 全部获取",
                        type=int, required=False, default=0)
    parser.add_argument("--musicnumber", help="音乐(原声)下作品获取个数设置, 默认为0 全部获取",
                        type=int, required=False, default=0)
    parser.add_argument("--database", "-d", help="是否使用数据库, 默认为True 使用数据库",
                        type=utils.str2bool, required=False, default=True)
    parser.add_argument("--postincrease", help="是否开启主页作品增量获取(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--likeincrease", help="是否开启主页喜欢增量获取(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--allmixincrease", help="是否开启主页合集增量获取(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--mixincrease", help="是否开启单个合集下作品增量获取(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--musicincrease", help="是否开启音乐(原声)下作品增量获取(True/False), 默认为False",
                        type=utils.str2bool, required=False, default=False)
    parser.add_argument("--cookie", help="设置cookie, 格式: \"name1=value1; name2=value2;\" 注意要加冒号",
                        type=str, required=False, default='')
    args = parser.parse_args()
    return args

def yamlConfig():
    curPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    yamlPath = os.path.join(curPath, "config.yml")
    with open(yamlPath, 'r', encoding='utf-8') as f:
        cfg = f.read()
    configDict = yaml.load(stream=cfg, Loader=yaml.FullLoader)

    for key in configModel.keys():
        if key in configDict:
            configModel[key] = configDict[key]
        else:
            print(f"[  警告  ]:{key}未设置, 使用默认值...\r\n")

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    start = time.time()  # 开始时间

    args = argument()

    if args.cmd:
        configModel["link"] = args.link
        configModel["path"] = args.path
        configModel["database"] = args.database
        configModel["increase"]["post"] = args.postincrease
        configModel["increase"]["like"] = args.likeincrease
        configModel["increase"]["allmix"] = args.allmixincrease
        configModel["increase"]["mix"] = args.mixincrease
        configModel["increase"]["music"] = args.musicincrease
        configModel["cookie"] = args.cookie
    else:
        yamlConfig()

    if configModel["link"] == []:
        return

    if configModel["cookie"] is not None and configModel["cookie"] != "":
        douyin_headers["Cookie"] = configModel["cookie"]

    dy = Douyin(database=configModel["database"])

    for link in configModel["link"]:
        print("--------------------------------------------------------------------------------")
        print("[  提示  ]:正在处理链接: " + link + "\r\n")
        url = dy.getShareLink(link)
        key_type, key = dy.getKey(url)
        if key_type == "user":
            print("[  提示  ]:正在处理用户主页数据\r\n")
            data = dy.getUserDetailInfo(sec_uid=key)
            if data is not None and data != {}:
                nickname = utils.replaceStr(data['user']['nickname'])
                print(f"[  提示  ]:用户昵称: {nickname}\r\n")
                save_json(data, os.path.join(configModel["path"], f"{nickname}_user_info.json"))
                
            for mode in configModel["mode"]:
                print("--------------------------------------------------------------------------------")
                print("[  提示  ]:正在处理用户主页模式: " + mode + "\r\n")
                if mode == 'post' or mode == 'like':
                    datalist = dy.getUserInfo(key, mode, 35, configModel["number"][mode], configModel["increase"][mode])
                    save_json(datalist, os.path.join(configModel["path"], f"{nickname}_{mode}_data.json"))
                elif mode == 'mix':
                    mixIdNameDict = dy.getUserAllMixInfo(key, 35, configModel["number"]["allmix"])
                    if mixIdNameDict is not None and mixIdNameDict != {}:
                        for mix_id in mixIdNameDict:
                            print(f'[  提示  ]:正在处理合集 [{mixIdNameDict[mix_id]}] 中的数据\r\n')
                            datalist = dy.getMixInfo(mix_id, 35, 0, configModel["increase"]["allmix"], key)
                            save_json(datalist, os.path.join(configModel["path"], f"{nickname}_mix_{mixIdNameDict[mix_id]}_data.json"))
        elif key_type == "mix":
            print("[  提示  ]:正在处理单个合集数据\r\n")
            datalist = dy.getMixInfo(key, 35, configModel["number"]["mix"], configModel["increase"]["mix"], "")
            save_json(datalist, os.path.join(configModel["path"], f"mix_{key}_data.json"))
        elif key_type == "music":
            print("[  提示  ]:正在处理音乐(原声)数据\r\n")
            datalist = dy.getMusicInfo(key, 35, configModel["number"]["music"], configModel["increase"]["music"])
            save_json(datalist, os.path.join(configModel["path"], f"music_{key}_data.json"))
        elif key_type == "aweme":
            print("[  提示  ]:正在处理单个作品数据\r\n")
            datanew, dataraw = dy.getAwemeInfo(key)
            if datanew is not None and datanew != {}:
                save_json(datanew, os.path.join(configModel["path"], f"aweme_{key}_data.json"))

    end = time.time()  # 结束时间
    print('\n' + '[处理完成]:总耗时: %d分钟%d秒\n' % (int((end - start) / 60), ((end - start) % 60)))

if __name__ == "__main__":
    main()
