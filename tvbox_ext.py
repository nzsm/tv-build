#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tvbox_ext.py — TVBoxOS 定制增强注入（v2 全面版）
用法: python3 tvbox_ext.py <源码目录> [默认订阅地址] [APP名称]

注入 4 项：
  1. 内置默认订阅地址（装上即自动加载你的订阅）
  2. APP 显示名称
  3. 播放页右上角实时网速常显（原版只在弹出底栏时才显示）
  4. 播放页标题追加解码标识（硬解/软解）
  5. 安全 DNS 默认开启腾讯（原版默认关闭）

全部为幂等替换，每步打印校验，失败不静默。
"""
import os, re, sys, json

SRC = sys.argv[1] if len(sys.argv) > 1 else '.'
DEF_URL = sys.argv[2] if len(sys.argv) > 2 else ''
APP_NAME = sys.argv[3] if len(sys.argv) > 3 else '影视仓定制版'

fails = []

def read(p):
    return open(p, encoding='utf-8').read()

def write(p, s):
    open(p, 'w', encoding='utf-8').write(s)

def jpath(*parts):
    return os.path.join(SRC, *parts)

def brace_delta(s):
    """花括号净差值（源码字符串里也含花括号，故只比较注入前后差值是否一致）"""
    return s.count('{') - s.count('}')

def delta_ok(before, after):
    return brace_delta(before) == brace_delta(after)

# ---------- 1. 内置默认订阅 ----------
def inject_sub():
    p = jpath('app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java')
    if not os.path.isfile(p):
        print('!! 找不到 ApiConfig.java'); fails.append('ApiConfig'); return
    s = read(p)
    if 'HawkConfig.API_URL, "http' in s:
        print('· 默认订阅已存在，跳过'); return
    old = 'String apiUrl = Hawk.get(HawkConfig.API_URL, "");'
    new = 'String apiUrl = Hawk.get(HawkConfig.API_URL, "%s");' % DEF_URL
    if old not in s:
        print('!! 未匹配默认订阅注入点'); fails.append('ApiConfig'); return
    before = s
    s = s.replace(old, new, 1)
    if not delta_ok(before, s):
        print('!! 注入后括号结构改变'); fails.append('ApiConfig-brace'); return
    write(p, s)
    print('+ 默认订阅已注入: %s' % DEF_URL)

# ---------- 2. APP 名称 ----------
def inject_name():
    p = jpath('app/src/main/res/values/strings.xml')
    if not os.path.isfile(p):
        print('!! 找不到 strings.xml'); fails.append('strings'); return
    s = read(p)
    m = re.search(r'<string name="app_name">([^<]*)</string>', s)
    if not m:
        print('!! strings.xml 无 app_name'); fails.append('app_name'); return
    if m.group(1) == APP_NAME:
        print('· APP 名称已是目标值，跳过'); return
    s = s[:m.start(1)] + APP_NAME + s[m.end(1):]
    write(p, s)
    print('+ APP 名称: %s -> %s' % (m.group(1), APP_NAME))

# ---------- 3. 网速常显 ----------
def inject_netspeed_always():
    p = jpath('app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java')
    if not os.path.isfile(p):
        print('!! 找不到 VodController.java'); fails.append('VodController'); return
    s = read(p)
    old_block = '''case 1003: { // 隐藏底部菜单
                        mBottomRoot.setVisibility(GONE);
                        mTopRoot1.setVisibility(GONE);
                        mPlayLoadNetSpeedRightTop.setVisibility(GONE);'''
    new_block = '''case 1003: { // 隐藏底部菜单
                        mBottomRoot.setVisibility(GONE);
                        mTopRoot1.setVisibility(GONE);
                        /*TVBOX_MOD: 网速常显，隐藏底栏时不再隐藏右上角速度*/
                        mPlayLoadNetSpeedRightTop.setVisibility(VISIBLE);'''
    if 'TVBOX_MOD: 网速常显' in s:
        print('· 网速常显已注入，跳过')
    elif old_block in s:
        before = s
        s = s.replace(old_block, new_block, 1)
        if not delta_ok(before, s):
            print('!! 括号结构改变'); fails.append('netspeed-brace'); return
        write(p, s)
        print('+ 已注入：播放页右上角网速常显')
    else:
        print('!! 未匹配网速显隐代码块'); fails.append('netspeed')

    # 顺带：显示底部菜单时也保证速度控件可见（原逻辑已 VISIBLE，此处做兜底校验）
    if 'mPlayLoadNetSpeedRightTop.setVisibility(VISIBLE);' not in read(p):
        print('!! 兜底校验失败'); fails.append('netspeed-verify')

# ---------- 4. 标题解码标识 ----------
def inject_codec_title():
    p = jpath('app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java')
    s = read(p)
    old = '''public void setTitle(String playTitleInfo) {
        mPlayTitle.setText(playTitleInfo);
        mPlayTitle1.setText(playTitleInfo);
    }'''
    new = '''public void setTitle(String playTitleInfo) {
        /*TVBOX_MOD: 标题追加解码标识（硬解/软解）*/
        try {
            String _codec = "";
            if (mPlayerConfig != null && mPlayerConfig.has("ijk")) {
                _codec = getCodecShortName(mPlayerConfig.optString("ijk", ""));
            }
            if (_codec != null && (_codec.indexOf("硬") >= 0 || _codec.indexOf("软") >= 0) && playTitleInfo != null && playTitleInfo.length() > 0) {
                playTitleInfo = playTitleInfo + " · " + _codec;
            }
        } catch (Exception ignored) {
        }
        mPlayTitle.setText(playTitleInfo);
        mPlayTitle1.setText(playTitleInfo);
    }'''
    if 'TVBOX_MOD: 标题追加解码标识' in s:
        print('· 解码标识已注入，跳过'); return
    if old not in s:
        print('!! 未匹配 setTitle 方法'); fails.append('setTitle'); return
    before = s
    s = s.replace(old, new, 1)
    if not delta_ok(before, s):
        print('!! 括号结构改变'); fails.append('codec-brace'); return
    write(p, s)
    print('+ 已注入：播放标题显示 硬解/软解')

# ---------- 5. 安全 DNS 默认腾讯 ----------
def inject_dns_default():
    p = jpath('app/src/main/java/com/github/tvbox/osc/util/OkGoHelper.java')
    if not os.path.isfile(p):
        print('!! 找不到 OkGoHelper.java'); fails.append('OkGoHelper'); return
    s = read(p)
    old = 'Integer dohSelector=Hawk.get(HawkConfig.DOH_URL, 0);'
    new = 'Integer dohSelector=Hawk.get(HawkConfig.DOH_URL, 1);/*TVBOX_MOD: 默认开启腾讯DoH*/'
    if 'TVBOX_MOD: 默认开启腾讯DoH' in s:
        print('· DNS 默认已注入，跳过'); return
    if old not in s:
        print('!! 未匹配 DNS 默认值'); fails.append('dns'); return
    before = s
    s = s.replace(old, new, 1)
    if not delta_ok(before, s):
        print('!! 括号结构改变'); fails.append('dns-brace'); return
    write(p, s)
    print('+ 已注入：安全 DNS 默认开启（腾讯）')

def main():
    print('=== TVBoxOS 定制增强 v2 ===')
    print('源码:', os.path.abspath(SRC))
    print('订阅:', DEF_URL or '(未传)')
    print('名称:', APP_NAME)
    if DEF_URL:
        inject_sub()
    else:
        print('· 未传订阅地址，跳过内置订阅注入')
    inject_name()
    inject_netspeed_always()
    inject_codec_title()
    inject_dns_default()
    print('=== 汇总：%s ===' % ('全部成功' if not fails else '失败项 ' + ','.join(fails)))
    if fails:
        sys.exit(1)

if __name__ == '__main__':
    main()
