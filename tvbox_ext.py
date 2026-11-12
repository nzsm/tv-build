#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tvbox_ext.py — TVBoxOS 定制增强注入（v7）
用法: python3 tvbox_ext.py <源码目录> [默认订阅地址] [APP名称]

注入 6 项：
  1. 内置默认订阅地址（装上即自动加载你的订阅）
  2. APP 显示名称
  5. 安全 DNS 默认开启腾讯（原版默认关闭）
  6. APP 图标替换（仓库根目录放 app_icon.png 即自动生效，不放则跳过）

v6 相比 v5 的变化：
  · 取消「标题源名前缀 + 解码标识」：标题恢复原版「片名 + 第几集」。
    理由：底部控制栏本身已显示播放器与解码方式（如「IJK播放器 硬解」），标题重复显示多余。
  · v5 已取消「网速常显」：右上角速度只在调出控制栏时显示，收起即隐藏。
  · 保留：内置默认订阅、APP 名称、安全DNS默认腾讯、APP 图标。
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
ICON_URL = 'https://aka.doubaocdn.com/s/8VHjcVC0xe'
ICON_URL_FALLBACK = 'https://aka.doubaocdn.com/s/yq36qVaKVf'


def _is_png(path):
    try:
        with open(path, 'rb') as f:
            return f.read(8) == b'\x89PNG\r\n\x1a\n' and os.path.getsize(path) > 2000
    except Exception:
        return False


def _download_icon(dst):
    import urllib.request
    for url in (ICON_URL, ICON_URL_FALLBACK):
        try:
            print('· 尝试下载图标: %s' % url)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=60).read()
            if data[:8] != b'\x89PNG\r\n\x1a\n' or len(data) < 2000:
                print('  !! 下载到的不是有效 PNG（%d 字节），换下一个源' % len(data))
                continue
            with open(dst, 'wb') as f:
                f.write(data)
            print('  ✅ 图标下载成功（%d 字节）' % len(data))
            return True
        except Exception as e:
            print('  !! 下载失败: %s' % e)
    return False


def inject_icon():
    src_icon = None
    for cand in ['app_icon.png', os.path.join(os.path.dirname(os.path.abspath(SRC)), 'app_icon.png')]:
        if os.path.isfile(cand) and _is_png(cand):
            src_icon = cand
            print('· 使用仓库内的 app_icon.png（%d 字节）' % os.path.getsize(cand))
            break
    res = jpath('app/src/main/res')
    target = os.path.join(res, 'drawable-xxxhdpi', 'app_icon.png')
    os.makedirs(os.path.dirname(target), exist_ok=True)

    if not src_icon:
        print('· 仓库里没有可用的 app_icon.png，改为从内置地址下载')
        tmp = os.path.join('/tmp', 'tvbox_icon_dl.png')
        if not _download_icon(tmp):
            print('· 图标获取失败（不影响编译，仍用原版图标）')
            return
        src_icon = tmp

    shutil.copyfile(src_icon, target)
    if not _is_png(target):
        print('!! 目标图标校验失败'); fails.append('icon'); return
    removed = []
    for d in ['drawable-mdpi', 'drawable-hdpi', 'drawable-xhdpi', 'drawable-xxhdpi', 'drawable']:
        f = os.path.join(res, d, 'app_icon.png')
        if os.path.isfile(f) and os.path.abspath(f) != os.path.abspath(target):
            try:
                os.remove(f)
                removed.append(d)
            except Exception:
                pass
    print('+ 图标已替换: -> drawable-xxxhdpi/app_icon.png (%d 字节)' % os.path.getsize(target))
    if removed:
        print('  已移除旧密度图标: %s（系统会自动缩放 xxxhdpi 版本）' % ','.join(removed))



# ---------- 8. 播放面板 UI：文字按钮 -> 图标在上 + 最小汉字在下（控件 id / Java 代码 均不改动） ----------
# 图标为 Material 风格单色白线/实心矢量，直接生成 Android vector drawable xml
VEC = {}

# takagen99(Box) 仓库原版 vector 图标（原样内嵌，编译时直接写入 res/drawable）
TK_XML = {}
TK_XML['tvx_pre'] = (
'<vector android:height="24dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">\n    <path android:fillColor="@android:color/white" android:pathData="M7,6c0.55,0 1,0.45 1,1v10c0,0.55 -0.45,1 -1,1s-1,-0.45 -1,-1L6,7c0,-0.55 0.45,-1 1,-1zM10.66,12.82l5.77,4.07c0.66,0.47 1.58,-0.01 1.58,-0.82L18.01,7.93c0,-0.81 -0.91,-1.28 -1.58,-0.82l-5.77,4.07c-0.57,0.4 -0.57,1.24 0,1.64z"/>\n</vector>'
)
TK_XML['tvx_next'] = (
'<vector android:height="24dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">\n    <path android:fillColor="@android:color/white" android:pathData="M7.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L7.58,7.11C6.91,6.65 6,7.12 6,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM16,7v10c0,0.55 0.45,1 1,1s1,-0.45 1,-1V7c0,-0.55 -0.45,-1 -1,-1s-1,0.45 -1,1z"/>\n</vector>'
)
TK_XML['tvx_replay'] = (
'<vector android:height="24dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">\n    <path android:fillColor="@android:color/white" android:pathData="M12,5V2.21c0,-0.45 -0.54,-0.67 -0.85,-0.35l-3.8,3.79c-0.2,0.2 -0.2,0.51 0,0.71l3.79,3.79c0.32,0.31 0.86,0.09 0.86,-0.36V7c3.73,0 6.68,3.42 5.86,7.29 -0.47,2.27 -2.31,4.1 -4.57,4.57 -3.57,0.75 -6.75,-1.7 -7.23,-5.01 -0.07,-0.48 -0.49,-0.85 -0.98,-0.85 -0.6,0 -1.08,0.53 -1,1.13 0.62,4.39 4.8,7.64 9.53,6.72 3.12,-0.61 5.63,-3.12 6.24,-6.24C20.84,9.48 16.94,5 12,5z"/>\n</vector>'
)
TK_XML['tvx_subtitle'] = (
'<vector android:height="24dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">\n    <path android:fillColor="@android:color/white" android:pathData="M20,4L4,4c-1.1,0 -2,0.9 -2,2v12c0,1.1 0.9,2 2,2h16c1.1,0 2,-0.9 2,-2L22,6c0,-1.1 -0.9,-2 -2,-2zM4,12h4v2L4,14v-2zM14,18L4,18v-2h10v2zM20,18h-4v-2h4v2zM20,14L10,14v-2h10v2z"/>\n</vector>'
)
TK_XML['tvx_audio'] = (
'<vector android:height="24dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">\n    <path android:fillColor="@android:color/white" android:pathData="M12,5v8.55c-0.94,-0.54 -2.1,-0.75 -3.33,-0.32 -1.34,0.48 -2.37,1.67 -2.61,3.07 -0.46,2.74 1.86,5.08 4.59,4.65 1.96,-0.31 3.35,-2.11 3.35,-4.1V7h2c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2h-2c-1.1,0 -2,0.9 -2,2z"/>\n</vector>'
)
TK_XML['tvx_danmu'] = (
'<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="436dp"\n    android:height="419dp"\n    android:viewportWidth="436"\n    android:viewportHeight="419">\n  <path\n      android:pathData="M322.65,272.14L274.13,272.14L274.13,290.36L328.16,290.36L328.16,318.2L274.13,318.2L274.13,347.96L242.96,347.96L242.96,318.2L188.7,318.2L188.7,290.36L242.96,290.36L242.96,272.14L194.21,272.14L194.21,147.1L216.3,147.1L209.39,129.82L238.16,129.82L245.13,147.1L271.73,147.1L278.7,129.82L307.53,129.82L300.32,147.1L322.88,147.1L322.65,272.14ZM115.05,189.58L152.26,189.58L152.26,164.62L110.25,164.62L110.25,135.09L182.96,135.09L182.96,218.35L143.59,218.35L142.18,244.78L184.66,244.78L177.92,347.02L117.22,347.02L117.22,316.79L148.39,316.79L151.79,273.55L110.25,273.55L115.05,189.58ZM244.89,243.08L244.89,223.16L222.81,223.16L222.81,243.08L244.89,243.08ZM244.89,195.79L244.89,176.11L222.81,176.11L222.81,195.79L244.89,195.79ZM294.06,243.08L294.06,223.16L272.02,223.16L272.02,243.08L294.06,243.08ZM294.06,195.79L294.06,176.11L272.02,176.11L272.02,195.79L294.06,195.79Z"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"/>\n  <path\n      android:pathData="M20.27,79.27Q0.5,99.04 0.5,127L0.5,351Q0.5,378.96 20.27,398.73Q40.04,418.5 68,418.5L368,418.5Q395.96,418.5 415.73,398.73Q435.5,378.96 435.5,351L435.5,127Q435.5,99.04 415.73,79.27Q395.96,59.5 368,59.5L68,59.5Q40.04,59.5 20.27,79.27ZM35.5,351L35.5,127Q35.5,113.54 45.02,104.02Q54.54,94.5 68,94.5L368,94.5Q381.46,94.5 390.98,104.02Q400.5,113.54 400.5,127L400.5,351Q400.5,364.46 390.98,373.98Q381.46,383.5 368,383.5L68,383.5Q54.54,383.5 45.02,373.98Q35.5,364.46 35.5,351Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FCFCFC"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/>\n  <path\n      android:pathData="M208.26,55.63L128.98,0.62L109.02,29.38L188.31,84.39Q201.24,93.36 216.98,93.4Q232.71,93.44 245.69,84.53L325.91,29.42L306.09,0.57L225.87,55.68Q221.89,58.41 217.06,58.4Q212.23,58.39 208.26,55.63Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/>\n</vector>'
)
TK_XML['tvx_scale'] = (
'<vector android:height="24dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">\n    <path android:fillColor="@android:color/white" android:pathData="M18,12c-0.55,0 -1,0.45 -1,1v2h-2c-0.55,0 -1,0.45 -1,1s0.45,1 1,1h3c0.55,0 1,-0.45 1,-1v-3c0,-0.55 -0.45,-1 -1,-1zM7,9h2c0.55,0 1,-0.45 1,-1s-0.45,-1 -1,-1L6,7c-0.55,0 -1,0.45 -1,1v3c0,0.55 0.45,1 1,1s1,-0.45 1,-1L7,9zM21,3L3,3c-1.1,0 -2,0.9 -2,2v14c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2zM20,19.01L4,19.01c-0.55,0 -1,-0.45 -1,-1L3,5.99c0,-0.55 0.45,-1 1,-1h16c0.55,0 1,0.45 1,1v12.02c0,0.55 -0.45,1 -1,1z"/>\n</vector>'
)
TK_XML['tvx_speed'] = (
'<vector android:height="24dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">\n    <path android:fillColor="@android:color/white" android:pathData="M5.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L5.58,7.11C4.91,6.65 4,7.12 4,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM13,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63l-5.77,-4.07c-0.67,-0.47 -1.58,0 -1.58,0.81z"/>\n</vector>'
)
TK_XML['tvx_screen'] = (
'<vector android:height="24dp"\n    android:tint="#FFFFFF"\n    android:viewportHeight="24"\n    android:viewportWidth="24"\n    android:width="24dp"\n    xmlns:android="http://schemas.android.com/apk/res/android">\n    <path\n        android:fillColor="@android:color/white"\n        android:pathData="M21,3L3,3c-1.11,0 -2,0.89 -2,2v12c0,1.1 0.89,2 2,2h5v2h8v-2h5c1.1,0 1.99,-0.9 1.99,-2L23,5c0,-1.11 -0.9,-2 -2,-2zM21,17L3,17L3,5h18v12zM16,11l-7,4L9,7z" />\n</vector>'
)

def _vec(name, w, paths, stroke=False, sw=1.8):
    VEC[name] = (w, paths, stroke, sw)

# 静态文字按钮 —— 文字清空后只显示图标
_vec('tvx_pre',    24, ["M6,6h2v12H6V6z", "M9.5,12l8.5,-6v12l-8.5,-6z"])
_vec('tvx_next',   24, ["M6,18l8.5,-6L6,6v12z", "M16,6v12h2V6h-2z"])
_vec('tvx_replay', 24, ["M12,5V1L7,6l5,5V7c3.31,0 6,2.69 6,6s-2.69,6 -6,6c-1.54,0 -2.94,-0.58 -4.01,-1.54l-1.42,1.42C8.27,18.99 10.03,20 12,20c4.42,0 8,-3.58 8,-8s-3.58,-8 -8,-8z"])
_vec('tvx_refresh',24, ["M17.65,6.35C16.2,4.9 14.21,4 12,4c-4.42,0 -7.99,3.58 -7.99,8s3.57,8 7.99,8c3.73,0 6.84,-2.55 7.73,-6h-2.08c-0.82,2.33 -3.04,4 -5.65,4 -3.31,0 -6,-2.69 -6,-6s2.69,-6 6,-6c1.66,0 3.14,0.69 4.22,1.78L13,11h7V4l-2.35,2.35z"])
_vec('tvx_reset',  24, ["M12,5c-1.93,0 -3.68,0.79 -4.95,2.05l-2.09,-2.09v5.99h5.99l-2.1,-2.1C9.85,7.53 10.86,7.1 12,7.1 14.65,7.1 16.9,9.35 16.9,12s-2.25,4.9 -4.9,4.9c-1.14,0 -2.15,-0.43 -2.96,-1.11l-1.42,1.42C9.02,18.42 10.42,19 12,19c3.87,0 7,-3.13 7,-7c0,-3.87 -3.13,-7 -7,-7z", "M14,12c0,-1.1 -0.9,-2 -2,-2s-2,0.9 -2,2 0.9,2 2,2 2,-0.9 2,-2z"])
_vec('tvx_cast',   24, ["M1,18v3h3c0,-1.66 -1.34,-3 -3,-3z", "M1,14v2c2.76,0 5,2.24 5,5h2c0,-3.87 -3.13,-7 -7,-7z", "M1,10v2c4.97,0 9,4.03 9,9h2c0,-6.08 -4.93,-11 -11,-11z", "M21,3L3,3c-1.1,0 -2,0.9 -2,2v3h2L3,5h18v14h-7v2h7c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2z"])
_vec('tvx_subtitle',24, ["M20,4L4,4c-1.1,0 -2,0.9 -2,2v12c0,1.1 0.9,2 2,2h16c1.1,0 2,-0.9 2,-2L22,6c0,-1.1 -0.9,-2 -2,-2zM4,12h4v2L4,14v-2zM14,18L4,18v-2h10v2zM20,18h-4v-2h4v2zM20,14L10,14v-2h10v2z"])
_vec('tvx_audio',  24, ["M12,3v10.55c-0.59,-0.34 -1.27,-0.55 -2,-0.55 -2.21,0 -4,1.79 -4,4s1.79,4 4,4 4,-1.79 4,-4L14,7h4L18,3h-6z"])
VEC['tvx_video'] = (26, ["M3.4,6.4h10.4c0.7,0 1.1,0.4 1.1,1.1v9c0,0.7 -0.4,1.1 -1.1,1.1h-10.4c-0.7,0 -1.1,-0.4 -1.1,-1.1v-9c0,-0.7 0.4,-1.1 1.1,-1.1z", "M15.3,10.6l4.8,-2.9v8.6l-4.8,-2.9"], True, 1.6)
_vec('tvx_danmu',  24, ["M20,2L4,2c-1.1,0 -1.99,0.9 -1.99,2L2,22l4,-4h14c1.1,0 2,-0.9 2,-2L22,4c0,-1.1 -0.9,-2 -2,-2z"])
_vec('tvx_screen', 24, ["M21,2L3,2c-1.1,0 -2,0.9 -2,2v12c0,1.1 0.9,2 2,2h4v2h10v-2h4c1.1,0 2,-0.9 2,-2L23,4c0,-1.1 -0.9,-2 -2,-2zM3,16L21,16L21,4L3,4v12z"])
# 动态文字按钮 —— 文字保留（代码会刷新），左侧配小图标
VEC['tvx_player'] = (18, ["M3.6,4.6h16.8c0.7,0 1.1,0.4 1.1,1.1v12.6c0,0.7 -0.4,1.1 -1.1,1.1h-16.8c-0.7,0 -1.1,-0.4 -1.1,-1.1v-12.6c0,-0.7 0.4,-1.1 1.1,-1.1z", "M8,4.6v15.4", "M16,4.6v15.4"], True, 1.6)
VEC['tvx_decoder'] = (20, ["M6.6,6.6h10.8v10.8h-10.8z", "M9.6,9.6h4.8v4.8h-4.8z", "M9,4v2.4", "M12,4v2.4", "M15,4v2.4", "M9,17.6v2.4", "M12,17.6v2.4", "M15,17.6v2.4", "M4,9h2.4", "M4,12h2.4", "M4,15h2.4", "M17.6,9h2.4", "M17.6,12h2.4", "M17.6,15h2.4"], True, 1.4)
_vec('tvx_scale',  18, ["M19,12h-2v3h-3v2h5L19,12zM3,10h2L5,7h3L8,5L3,5v5zM21,3L3,3c-1.1,0 -2,0.9 -2,2v14c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2zM21,19L3,19L3,5h18v14z"])
_vec('tvx_speed',  18, ["M4,18l8.5,-6L4,6v12zM13,18l8.5,-6L13,6v12z"])
# 横竖屏：竖屏手机 + 横屏手机 + 旋转箭头（线框）
VEC['tvx_orientation'] = (26, ["M6.5,2.8h4c0.6,0 1,0.4 1,1v10.4c0,0.6 -0.4,1 -1,1h-4c-0.6,0 -1,-0.4 -1,-1V3.8c0,-0.6 0.4,-1 1,-1z", "M7.9,4.9h2.2", "M12.6,9h8c0.6,0 1,0.4 1,1v3.6c0,0.6 -0.4,1 -1,1h-8c-0.6,0 -1,-0.4 -1,-1V10c0,-0.6 0.4,-1 1,-1z", "M13.8,10.8h2.6"], True, 2.2)

def _write_vec(name):
    w, paths, stroke, sw = VEC[name]
    head = ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
            '    android:width="%ddp"\n    android:height="%ddp"\n'
            '    android:viewportWidth="24"\n    android:viewportHeight="24">\n') % (w, w)
    body = ''
    for pd in paths:
        if stroke:
            body += '    <path android:strokeColor="#FFFFFFFF" android:strokeWidth="%s" android:fillColor="@android:color/transparent" android:pathData="%s"/>\n' % (sw, pd)
        else:
            body += '    <path android:fillColor="#FFFFFFFF" android:pathData="%s"/>\n' % pd
    return head + body + '</vector>\n'

# 静态文字按钮：清空文字 + 图标
STATIC_MAP = [
    ('play_pre', 'tvx_pre'),
    ('play_next', 'tvx_next'),
    ('play_retry', 'tvx_replay'),
    ('play_refresh', 'tvx_refresh'),
    ('play_time_reset', 'tvx_reset'),
    ('play_cast', 'tvx_cast'),
    ('zimu_select', 'tvx_subtitle'),
    ('audio_track_select', 'tvx_audio'),
    ('video_track_select', 'tvx_video'),
    ('danmu_setting', 'tvx_danmu'),
    ('screen_display', 'tvx_screen'),
]
# 动态文字按钮：文字保留，左侧小图标
DYN_MAP = [
    ('play_player', 'tvx_player'),
    ('play_ijk', 'tvx_decoder'),
    ('play_scale', 'tvx_scale'),
    ('play_speed', 'tvx_speed'),
    ('landscape_portrait', 'tvx_orientation'),
]


def _find_block(xml, view_id):
    """返回 (start, end) —— 包含该 id 的 <TextView ... /> 整块"""
    m = re.search(r'<TextView\b[^>]*?android:id="@\+id/%s"[^>]*?/>' % re.escape(view_id), xml, re.S)
    if not m:
        m = re.search(r'<TextView\b[^>]*?android:id="@\+id/%s".*?/>' % re.escape(view_id), xml, re.S)
    return (m.start(), m.end()) if m else None


def inject_ui_icons():
    res = jpath('app/src/main/res')
    dr = os.path.join(res, 'drawable')
    os.makedirs(dr, exist_ok=True)
    # 1) 生成矢量图标资源
    made = 0
    tk = 0
    for name in VEC:
        f = os.path.join(dr, name + '.xml')
        with open(f, 'w', encoding='utf-8') as fh:
            if name in TK_XML:
                fh.write('<?xml version="1.0" encoding="utf-8"?>\n' + TK_XML[name] + '\n')
                tk += 1
            else:
                fh.write(_write_vec(name))
        made += 1
    print('+ 已生成 %d 个矢量图标 -> res/drawable/tvx_*.xml（其中 %d 个取自 takagen99 原版）' % (made, tk))

    # 2) 改播放面板布局
    lp = os.path.join(res, 'layout', 'player_vod_control_view.xml')
    if not os.path.isfile(lp):
        print('!! 未找到 player_vod_control_view.xml')
        fails.append('ui-layout')
        return
    xml = open(lp, encoding='utf-8').read()
    if 'TVBOX_MOD: UI 图标' in xml:
        print('· 播放面板图标改造已存在，跳过')
        return

    changed = []
    for vid, icon in STATIC_MAP:
        sp = _find_block(xml, vid)
        if not sp:
            print('  !! 未找到控件 @id/%s' % vid)
            continue
        blk = xml[sp[0]:sp[1]]
        # 图标在上、汉字在下：文字保留，字号缩到最小档 ts_10
        blk2 = re.sub(r'android:textSize="@dimen/ts_[0-9]+"', 'android:textSize="@dimen/ts_10"', blk, count=1)
        extra = ('android:drawableTop="@drawable/%s"\n                android:drawablePadding="2dp"\n'
                 '                android:gravity="center"\n                android:textAlignment="center"\n                android:minWidth="76dp"\n                ') % icon
        if 'android:background=' in blk2:
            blk2 = blk2.replace('android:background=', extra + 'android:background=', 1)
        else:
            blk2 = blk2.replace('/>', extra + '/>', 1)
        xml = xml[:sp[0]] + blk2 + xml[sp[1]:]
        changed.append(vid)

    for vid, icon in DYN_MAP:
        sp = _find_block(xml, vid)
        if not sp:
            print('  !! 未找到控件 @id/%s' % vid)
            continue
        blk = xml[sp[0]:sp[1]]
        # 同样是 图标在上、小字在下
        blk = re.sub(r'android:textSize="@dimen/ts_[0-9]+"', 'android:textSize="@dimen/ts_10"', blk, count=1)
        extra = ('android:drawableTop="@drawable/%s"\n                android:drawablePadding="2dp"\n'
                 '                android:gravity="center"\n                android:textAlignment="center"\n                android:minWidth="76dp"\n                ') % icon
        if 'android:background=' in blk:
            blk = blk.replace('android:background=', extra + 'android:background=', 1)
        else:
            blk = blk.replace('/>', extra + '/>', 1)
        xml = xml[:sp[0]] + blk + xml[sp[1]:]
        changed.append(vid)

    # 3) 隐藏多余的「搜弹幕」按钮（控件保留，仅不可见，代码 findView 不受影响）
    sp = _find_block(xml, 'danmu_search_ui')
    if sp:
        blk = xml[sp[0]:sp[1]]
        if 'android:visibility=' in blk:
            blk = re.sub(r'android:visibility="[^"]*"', 'android:visibility="gone"', blk, count=1)
        else:
            blk = blk.replace('android:text=', 'android:visibility="gone"\n                android:text=', 1)
        xml = xml[:sp[0]] + blk + xml[sp[1]:]
        changed.append('danmu_search_ui=gone')

    # 4) 加注释锚点（便于重复执行判断）
    xml = xml.replace('<?xml version="1.0" encoding="utf-8"?>',
                      '<?xml version="1.0" encoding="utf-8"?>\n<!-- TVBOX_MOD: UI 图标（按钮文字已替换为矢量图标，控件 id 未改动） -->', 1)
    open(lp, 'w', encoding='utf-8').write(xml)
    print('+ 播放面板按钮已图标化: %s' % ', '.join(changed))
    print('  说明：控件 id 与 Java 监听完全未改动；全部按钮为「图标在上 + 最小汉字在下」(ts_10)，播放器/解码/比例/倍速/横竖屏 的文字由代码动态刷新，不影响显示')


def main():
    print('=== TVBoxOS 定制增强 v7 ===')
    print('源码:', os.path.abspath(SRC))
    print('订阅:', DEF_URL or '(未传)')
    print('名称:', APP_NAME)
    if DEF_URL:
        inject_sub()
    else:
        print('· 未传订阅地址，跳过内置订阅注入')
    inject_name()
    # inject_netspeed_always()  ← v5 取消：恢复原版「仅调出菜单时显示速度」
    inject_dns_default()
    # inject_title_tags()  ← v6 取消：标题只保留「片名 + 第几集」
    inject_icon()
    inject_ui_icons()
    print('=== 汇总：%s ===' % ('全部成功' if not fails else '失败项 ' + ','.join(fails)))
    if fails:
        sys.exit(1)


if __name__ == '__main__':
    main()
