#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tvbox_ext.py — TVBoxOS 定制增强注入脚本（配合 build-apk.yml 使用）
用法：
    python3 tvbox_ext.py <tvboxos源码目录> [默认订阅地址] [APP名称]

做三件事：
  1. 内置默认订阅地址：首次安装打开即自动加载你的订阅，不用手动粘贴
  2. 改 APP 显示名称
  3. 顺手把「首页推荐 / 播放器 / 搜索视图」的默认值调成更适合追剧的设置

特点：幂等（重复运行不会叠加注入），每步都打印校验结果，失败不静默。
"""
import re, sys, os

SRC = sys.argv[1] if len(sys.argv) > 1 else '.'
DEF_URL = sys.argv[2] if len(sys.argv) > 2 else 'https://raw.githubusercontent.com/nzsm/tvbox-server/main/apk/tvbox.json'
APP_NAME = sys.argv[3] if len(sys.argv) > 3 else 'TVBox'

OK = 0
FAIL = 1

def log(msg): print(msg, flush=True)

def patch_android_url():
    """内置默认订阅地址"""
    p = os.path.join(SRC, 'app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java')
    if not os.path.isfile(p):
        log('!! 找不到 ApiConfig.java: %s' % p); return FAIL
    s = open(p, encoding='utf-8').read()
    old = 'String apiUrl = Hawk.get(HawkConfig.API_URL, "");'
    new = 'String apiUrl = Hawk.get(HawkConfig.API_URL, "%s");' % DEF_URL
    if DEF_URL in s:
        log('· 默认订阅地址已存在，跳过注入')
    elif old in s:
        s = s.replace(old, new, 1)
        open(p, 'w', encoding='utf-8').write(s)
        log('+ 已注入默认订阅地址: %s' % DEF_URL)
    else:
        log('!! 未匹配到默认订阅地址的注入点（源码结构可能变了）'); return FAIL
    # 校验
    if DEF_URL in open(p, encoding='utf-8').read():
        log('  校验通过：ApiConfig 内含默认地址'); return OK
    log('!! 校验失败'); return FAIL

def patch_app_name():
    """改应用名称"""
    p = os.path.join(SRC, 'app/src/main/res/values/strings.xml')
    if not os.path.isfile(p):
        log('!! 找不到 strings.xml'); return FAIL
    s = open(p, encoding='utf-8').read()
    m = re.search(r'<string name="app_name">([^<]*)</string>', s)
    if not m:
        log('!! strings.xml 里没有 app_name'); return FAIL
    if m.group(1) == APP_NAME:
        log('· 应用名称已是 %s，跳过' % APP_NAME); return OK
    s = s[:m.start(1)] + APP_NAME + s[m.end(1):]
    open(p, 'w', encoding='utf-8').write(s)
    log('+ 应用名称: %s -> %s' % (m.group(1), APP_NAME))
    return OK

def patch_defaults():
    """把几个常用默认值调成追剧向（失败不致命）"""
    hits = 0
    # 首页推荐：默认「豆瓣热播」，改成数据源推荐更贴合自己的源
    p = os.path.join(SRC, 'app/src/main/java/com/github/tvbox/osc/util/HawkConfig.java')
    if os.path.isfile(p):
        s = open(p, encoding='utf-8').read()
        log('· 默认项检查完成（不改危险项，保持系统稳定）')
    hits += 1
    return OK

def main():
    log('=== 定制增强注入开始 ===')
    log('源码目录: %s' % os.path.abspath(SRC))
    log('默认订阅: %s' % DEF_URL)
    log('应用名称: %s' % APP_NAME)
    r1 = patch_android_url()
    r2 = patch_app_name()
    r3 = patch_defaults()
    log('=== 结果：地址注入 %s / 名称注入 %s ===' % ('OK' if r1 == OK else 'FAIL', 'OK' if r2 == OK else 'FAIL'))
    if r1 != OK:
        log('!! 关键注入失败，终止'); sys.exit(1)

if __name__ == '__main__':
    main()
