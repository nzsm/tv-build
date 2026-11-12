#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tvbox_ext.py — TVBoxOS 定制增强注入（v4）
用法: python3 tvbox_ext.py <源码目录> [默认订阅地址] [APP名称]

注入 6 项：
  1. 内置默认订阅地址（装上即自动加载你的订阅）
  2. APP 显示名称
  3. 播放页右上角实时网速常显（原版只在弹出底栏时才显示）
  4. 播放页标题前置「站点名」+ 后缀「播放器/解码方式」（全部在 PlayFragment 拼，走 Hawk 兜底，不依赖播放器对象）
  5. 安全 DNS 默认开启腾讯（原版默认关闭）
  6. APP 图标替换（仓库根目录放 app_icon.png 即自动生效，不放则跳过）

v4 相比 v3 的变化：
  · 解码标识不再注入 VodController.setTitle（那个 mPlayerConfig 在部分路径为空，会导致不显示），
    改为在 PlayFragment 标题拼接处直接读 Hawk 设置 → 只要装进新包就一定显示。
  · 一次编译内可重复执行，幂等。

失败不静默（exit 1 让工作流标红）。
"""
import os, re, sys, shutil

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
        return

    if 'mPlayLoadNetSpeedRightTop.setVisibility(VISIBLE);' not in read(p):
        print('!! 兜底校验失败'); fails.append('netspeed-verify')


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


# ---------- 4. 标题：源名前缀 + 播放器/解码后缀（PlayFragment，全走设置兜底） ----------
def inject_title_tags():
    p = jpath('app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java')
    if not os.path.isfile(p):
        print('!! 找不到 PlayFragment.java'); fails.append('PlayFragment'); return
    s = read(p)
    if 'TVBOX_MOD: 标题源名与解码' in s:
        print('· 标题标识已注入，跳过'); return

    anchor = '    public void setPlayTitle(boolean show)'

    helpers = (
        '    private String getSourcePrefix() {\n'
        '        /*TVBOX_MOD: 标题源名与解码 - 前缀*/\n'
        '        try {\n'
        '            if (sourceBean == null && mVodInfo != null) {\n'
        '                sourceBean = ApiConfig.get().getSource(mVodInfo.sourceKey);\n'
        '            }\n'
        '            if (sourceBean != null) {\n'
        '                String _n = sourceBean.getName();\n'
        '                if (_n != null && _n.length() > 0) {\n'
        '                    return "[" + _n + "] ";\n'
        '                }\n'
        '            }\n'
        '        } catch (Exception ignored) {\n'
        '        }\n'
        '        return "";\n'
        '    }\n\n'
        '    private String getCodecSuffix() {\n'
        '        /*TVBOX_MOD: 标题源名与解码 - 后缀（走 Hawk 兜底，保证一定显示）*/\n'
        '        try {\n'
        '            int _pl = -1;\n'
        '            if (mVodPlayerCfg != null && mVodPlayerCfg.has("pl")) {\n'
        '                _pl = mVodPlayerCfg.optInt("pl", 2);\n'
        '            }\n'
        '            if (_pl < 0) {\n'
        '                _pl = (int) Hawk.get(HawkConfig.PLAY_TYPE, 2);\n'
        '            }\n'
        '            if (_pl == 1) {\n'
        '                String _ijk = "";\n'
        '                if (mVodPlayerCfg != null && mVodPlayerCfg.has("ijk")) {\n'
        '                    _ijk = mVodPlayerCfg.optString("ijk", "");\n'
        '                }\n'
        '                if (_ijk.length() == 0) {\n'
        '                    _ijk = Hawk.get(HawkConfig.IJK_CODEC, "硬解码");\n'
        '                }\n'
        '                if (_ijk != null && _ijk.indexOf("硬") >= 0) return " · 硬解";\n'
        '                if (_ijk != null && _ijk.indexOf("软") >= 0) return " · 软解";\n'
        '                return " · IJK";\n'
        '            }\n'
        '            if (_pl == 2) return " · EXO";\n'
        '            if (_pl == 10) return " · MX";\n'
        '        } catch (Exception ignored) {\n'
        '        }\n'
        '        return "";\n'
        '    }\n\n'
    )

    if anchor not in s:
        print('!! 未找到 setPlayTitle 锚点'); fails.append('title-anchor'); return

    t1_old = '                playTitleInfo = mVodInfo.name + " " + mVodInfo.seriesMap.get(mVodInfo.playFlag).get(mVodInfo.playIndex).name;'
    t1_new = '                playTitleInfo = getSourcePrefix() + mVodInfo.name + " " + mVodInfo.seriesMap.get(mVodInfo.playFlag).get(mVodInfo.playIndex).name + getCodecSuffix();'
    t2_old = '        String playTitleInfo = mVodInfo.name + " " + vs.name;'
    t2_new = '        String playTitleInfo = getSourcePrefix() + mVodInfo.name + " " + vs.name + getCodecSuffix();'

    hit1 = t1_old in s
    hit2 = t2_old in s
    if not (hit1 and hit2):
        print('!! 标题拼接点匹配不全 hit1=%s hit2=%s' % (hit1, hit2))
        fails.append('title-points')
        return

    before = s
    s = s.replace(anchor, helpers + anchor, 1)
    s = s.replace(t1_old, t1_new, 1)
    s = s.replace(t2_old, t2_new, 1)
    if not delta_ok(before, s):
        print('!! 括号结构改变'); fails.append('title-brace'); return
    write(p, s)
    print('+ 已注入：标题 [源名] 前缀 + 播放器/解码 后缀')


# ---------- 6. 图标替换 ----------
def inject_icon():
    src_icon = None
    for cand in ['app_icon.png', os.path.join(os.path.dirname(os.path.abspath(SRC)), 'app_icon.png')]:
        if os.path.isfile(cand):
            src_icon = cand
            break
    if not src_icon:
        print('· 未找到 app_icon.png（可选，跳过图标替换）')
        return
    res = jpath('app/src/main/res')
    target = os.path.join(res, 'drawable-xxxhdpi', 'app_icon.png')
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copyfile(src_icon, target)
    removed = []
    for d in ['drawable-mdpi', 'drawable-hdpi', 'drawable-xhdpi', 'drawable-xxhdpi', 'drawable']:
        f = os.path.join(res, d, 'app_icon.png')
        if os.path.isfile(f) and os.path.abspath(f) != os.path.abspath(target):
            try:
                os.remove(f)
                removed.append(d)
            except Exception:
                pass
    print('+ 图标已替换: %s -> drawable-xxxhdpi/app_icon.png (%d 字节)' % (src_icon, os.path.getsize(target)))
    if removed:
        print('  已移除旧密度图标: %s（系统会自动缩放 xxxhdpi 版本）' % ','.join(removed))


def main():
    print('=== TVBoxOS 定制增强 v4 ===')
    print('源码:', os.path.abspath(SRC))
    print('订阅:', DEF_URL or '(未传)')
    print('名称:', APP_NAME)
    if DEF_URL:
        inject_sub()
    else:
        print('· 未传订阅地址，跳过内置订阅注入')
    inject_name()
    inject_netspeed_always()
    inject_dns_default()
    inject_title_tags()
    inject_icon()
    print('=== 汇总：%s ===' % ('全部成功' if not fails else '失败项 ' + ','.join(fails)))
    if fails:
        sys.exit(1)


if __name__ == '__main__':
    main()
