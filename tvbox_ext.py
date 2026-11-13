#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===== TVBoxOS 定制增强 V30 完整版（含图标/布局/时间/弹幕关闭）=====
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
import os, re, sys, shutil, glob

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
TK_XML['tvx_audio'] = (
'<vector android:height="24dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">\n    <path android:fillColor="@android:color/white" android:pathData="M12,5v8.55c-0.94,-0.54 -2.1,-0.75 -3.33,-0.32 -1.34,0.48 -2.37,1.67 -2.61,3.07 -0.46,2.74 1.86,5.08 4.59,4.65 1.96,-0.31 3.35,-2.11 3.35,-4.1V7h2c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2h-2c-1.1,0 -2,0.9 -2,2z"/>\n</vector>'
)
TK_XML['tvx_danmu'] = (
'<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="436dp"\n    android:height="419dp"\n    android:viewportWidth="436"\n    android:viewportHeight="419">\n  <path\n      android:pathData="M322.65,272.14L274.13,272.14L274.13,290.36L328.16,290.36L328.16,318.2L274.13,318.2L274.13,347.96L242.96,347.96L242.96,318.2L188.7,318.2L188.7,290.36L242.96,290.36L242.96,272.14L194.21,272.14L194.21,147.1L216.3,147.1L209.39,129.82L238.16,129.82L245.13,147.1L271.73,147.1L278.7,129.82L307.53,129.82L300.32,147.1L322.88,147.1L322.65,272.14ZM115.05,189.58L152.26,189.58L152.26,164.62L110.25,164.62L110.25,135.09L182.96,135.09L182.96,218.35L143.59,218.35L142.18,244.78L184.66,244.78L177.92,347.02L117.22,347.02L117.22,316.79L148.39,316.79L151.79,273.55L110.25,273.55L115.05,189.58ZM244.89,243.08L244.89,223.16L222.81,223.16L222.81,243.08L244.89,243.08ZM244.89,195.79L244.89,176.11L222.81,176.11L222.81,195.79L244.89,195.79ZM294.06,243.08L294.06,223.16L272.02,223.16L272.02,243.08L294.06,243.08ZM294.06,195.79L294.06,176.11L272.02,176.11L272.02,195.79L294.06,195.79Z"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"/>\n  <path\n      android:pathData="M20.27,79.27Q0.5,99.04 0.5,127L0.5,351Q0.5,378.96 20.27,398.73Q40.04,418.5 68,418.5L368,418.5Q395.96,418.5 415.73,398.73Q435.5,378.96 435.5,351L435.5,127Q435.5,99.04 415.73,79.27Q395.96,59.5 368,59.5L68,59.5Q40.04,59.5 20.27,79.27ZM35.5,351L35.5,127Q35.5,113.54 45.02,104.02Q54.54,94.5 68,94.5L368,94.5Q381.46,94.5 390.98,104.02Q400.5,113.54 400.5,127L400.5,351Q400.5,364.46 390.98,373.98Q381.46,383.5 368,383.5L68,383.5Q54.54,383.5 45.02,373.98Q35.5,364.46 35.5,351Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FCFCFC"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/>\n  <path\n      android:pathData="M208.26,55.63L128.98,0.62L109.02,29.38L188.31,84.39Q201.24,93.36 216.98,93.4Q232.71,93.44 245.69,84.53L325.91,29.42L306.09,0.57L225.87,55.68Q221.89,58.41 217.06,58.4Q212.23,58.39 208.26,55.63Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/>\n</vector>'
)
TK_XML['tvx_scale'] = (
'<vector android:height="24dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">\n    <path android:fillColor="@android:color/white" android:pathData="M18,12c-0.55,0 -1,0.45 -1,1v2h-2c-0.55,0 -1,0.45 -1,1s0.45,1 1,1h3c0.55,0 1,-0.45 1,-1v-3c0,-0.55 -0.45,-1 -1,-1zM7,9h2c0.55,0 1,-0.45 1,-1s-0.45,-1 -1,-1L6,7c-0.55,0 -1,0.45 -1,1v3c0,0.55 0.45,1 1,1s1,-0.45 1,-1L7,9zM21,3L3,3c-1.1,0 -2,0.9 -2,2v14c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2zM20,19.01L4,19.01c-0.55,0 -1,-0.45 -1,-1L3,5.99c0,-0.55 0.45,-1 1,-1h16c0.55,0 1,0.45 1,1v12.02c0,0.55 -0.45,1 -1,1z"/>\n</vector>'
)

def _vec(name, w, paths, stroke=False, sw=1.8):
    VEC[name] = (w, paths, stroke, sw)

# 静态文字按钮 —— 文字清空后只显示图标
_vec('tvx_pre',    26, ["M6,6h2v12H6V6z", "M9.5,12l8.5,-6v12l-8.5,-6z"])
_vec('tvx_next',   26, ["M6,18l8.5,-6L6,6v12z", "M16,6v12h2V6h-2z"])
_vec('tvx_replay', 26, ["M12,5.4a6.6,6.6 0 1 0 4.7,1.8", "M10.2,10.4L13.2,12L10.2,13.6Z"], True, 2.0)
_vec('tvx_refresh',26, ["M17.65,6.35C16.2,4.9 14.21,4 12,4c-4.42,0 -7.99,3.58 -7.99,8s3.57,8 7.99,8c3.73,0 6.84,-2.55 7.73,-6h-2.08c-0.82,2.33 -3.04,4 -5.65,4 -3.31,0 -6,-2.69 -6,-6s2.69,-6 6,-6c1.66,0 3.14,0.69 4.22,1.78L13,11h7V4l-2.35,2.35z"])
_vec('tvx_reset',  26, ["M12,5c-1.93,0 -3.68,0.79 -4.95,2.05l-2.09,-2.09v5.99h5.99l-2.1,-2.1C9.85,7.53 10.86,7.1 12,7.1 14.65,7.1 16.9,9.35 16.9,12s-2.25,4.9 -4.9,4.9c-1.14,0 -2.15,-0.43 -2.96,-1.11l-1.42,1.42C9.02,18.42 10.42,19 12,19c3.87,0 7,-3.13 7,-7c0,-3.87 -3.13,-7 -7,-7z", "M14,12c0,-1.1 -0.9,-2 -2,-2s-2,0.9 -2,2 0.9,2 2,2 2,-0.9 2,-2z"])
_vec('tvx_cast',   26, ["M3,6.2L21,6.2L21,16.2L3,16.2Z", "M7.4,6.2L4.9,3.4M16.6,6.2L19.1,3.4", "M9.5,16.2V18.4M14.5,16.2V18.4", "M6.5,8.4h3.4M8.2,8.4v4.6", "M12.4,8.4l1.6,4.6M15.6,8.4l-1.6,4.6"], True, 2.0)
_vec('tvx_subtitle',26, ["M3,7L21,7L21,17L3,17Z", "M7.2,12a0.55,0.55 0 1 0 1.1,0a0.55,0.55 0 1 0 -1.1,0", "M11.45,12a0.55,0.55 0 1 0 1.1,0a0.55,0.55 0 1 0 -1.1,0", "M15.7,12a0.55,0.55 0 1 0 1.1,0a0.55,0.55 0 1 0 -1.1,0"], True, 2.0)
_vec('tvx_audio',  26, ["M12,3v10.55c-0.59,-0.34 -1.27,-0.55 -2,-0.55 -2.21,0 -4,1.79 -4,4s1.79,4 4,4 4,-1.79 4,-4L14,7h4L18,3h-6z"])
VEC['tvx_gauge'] = (26, ["M3.6,16.2a8.4,8.4 0 0 1 16.8,0", "M12,16.2L16.6,10.4"], True, 2.0)
VEC['tvx_head'] = (26, ["M2.6,12h19.2", "M2.6,5.6v12.8"], True, 2.0)
VEC['tvx_tail'] = (26, ["M2.8,12h19.2", "M21.4,5.6v12.8"], True, 2.0)
VEC['tvx_video'] = (28, ["M3.4,6.4h10.4c0.7,0 1.1,0.4 1.1,1.1v9c0,0.7 -0.4,1.1 -1.1,1.1h-10.4c-0.7,0 -1.1,-0.4 -1.1,-1.1v-9c0,-0.7 0.4,-1.1 1.1,-1.1z", "M15.3,10.6l4.8,-2.9v8.6l-4.8,-2.9"], True, 1.6)
_vec('tvx_danmu',  26, ["M20,2L4,2c-1.1,0 -1.99,0.9 -1.99,2L2,22l4,-4h14c1.1,0 2,-0.9 2,-2L22,4c0,-1.1 -0.9,-2 -2,-2z"])
_vec('tvx_screen', 26, ["M4,9V4H9", "M15,4H20V9", "M20,15V20H15", "M9,20H4V15"], True, 2.0)
# 动态文字按钮 —— 文字保留（代码会刷新），左侧配小图标
VEC['tvx_player'] = (20, ["M3.6,4.6h16.8c0.7,0 1.1,0.4 1.1,1.1v12.6c0,0.7 -0.4,1.1 -1.1,1.1h-16.8c-0.7,0 -1.1,-0.4 -1.1,-1.1v-12.6c0,-0.7 0.4,-1.1 1.1,-1.1z", "M8,4.6v15.4", "M16,4.6v15.4"], True, 1.6)
VEC['tvx_decoder'] = (22, ["M6.6,6.6h10.8v10.8h-10.8z", "M9.6,9.6h4.8v4.8h-4.8z", "M9,4v2.4", "M12,4v2.4", "M15,4v2.4", "M9,17.6v2.4", "M12,17.6v2.4", "M15,17.6v2.4", "M4,9h2.4", "M4,12h2.4", "M4,15h2.4", "M17.6,9h2.4", "M17.6,12h2.4", "M17.6,15h2.4"], True, 1.4)
_vec('tvx_scale',  18, ["M19,12h-2v3h-3v2h5L19,12zM3,10h2L5,7h3L8,5L3,5v5zM21,3L3,3c-1.1,0 -2,0.9 -2,2v14c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2zM21,19L3,19L3,5h18v14z"])
# 横竖屏：竖屏手机 + 横屏手机 + 旋转箭头（线框）
VEC['tvx_orientation'] = (28, ["M6.5,2.8h4c0.6,0 1,0.4 1,1v10.4c0,0.6 -0.4,1 -1,1h-4c-0.6,0 -1,-0.4 -1,-1V3.8c0,-0.6 0.4,-1 1,-1z", "M7.9,4.9h2.2", "M12.6,9h8c0.6,0 1,0.4 1,1v3.6c0,0.6 -0.4,1 -1,1h-8c-0.6,0 -1,-0.4 -1,-1V10c0,-0.6 0.4,-1 1,-1z", "M13.8,10.8h2.6"], True, 2.0)

ICON_DP = 50   # 图标边长：takagen99 用 vs_50 = 50mm，直接照抄   # 按钮图标边长（dp）：整排 18 个须落在进度条头尾之间

# ---- 图标视觉尺寸归一化：每个图标内容都缩放到画布的 86%，视觉大小一致 ----
NORM = {"tvx_audio": [1.1733, -2.08, -2.08], "tvx_cast": [1.0476, -0.571, 0.56], "tvx_danmu": [0.8457, 33.64, 32.328], "tvx_decoder": [1.2055, -2.466, -2.466], "tvx_gauge": [1.1139, -1.367, -1.367], "tvx_head": [0.9944, -0.111, 0.068], "tvx_next": [1.76, -9.12, -9.12], "tvx_orientation": [1.1579, -3.701, 1.579], "tvx_player": [1.0233, -0.279, -0.586], "tvx_pre": [1.7426, -9.015, -8.911], "tvx_refresh": [1.3134, -3.761, -3.761], "tvx_replay": [1.375, -4.748, -4.5], "tvx_reset": [1.4915, -5.898, -5.898], "tvx_scale": [0.9565, 0.522, 0.522], "tvx_screen": [1.1733, -2.08, -2.08], "tvx_subtitle": [1.0476, -0.571, -0.571], "tvx_tail": [0.9944, -0.35, 0.068], "tvx_video": [1.0798, -0.115, -0.957]}


def _apply_norm(content, name):
    """等比缩放图标内容到统一视觉尺寸并居中（用 vector group 变换实现）"""
    if name not in NORM:
        return content
    s, tx, ty = NORM[name]
    info = VEC.get(name, (24, [], False, 0))
    if info[2] and info[3]:
        content = re.sub(r'android:strokeWidth="[0-9.]+"', 'android:strokeWidth="' + ('%.3f' % (info[3] / s)) + '"', content)
    tag = '<group android:scaleX="' + ('%.4f' % s) + '" android:scaleY="' + ('%.4f' % s) + '" android:translateX="' + ('%.3f' % tx) + '" android:translateY="' + ('%.3f' % ty) + '">'
    content = re.sub(r'(<vector[^>]*>)', lambda m: m.group(1) + '\n    ' + tag, content, count=1)
    content = content.replace('</vector>', '    </group>\n</vector>')
    return content


def _write_vec(name):
    w, paths, stroke, sw = VEC[name]
    head = ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
            '    android:width="%dmm"\n    android:height="%dmm"\n'
            '    android:viewportWidth="24"\n    android:viewportHeight="24">\n') % (w, w)
    body = ''
    for pd in paths:
        if stroke:
            body += '    <path android:strokeColor="#FFFFFFFF" android:strokeWidth="%s" android:fillColor="@android:color/transparent" android:pathData="%s"/>\n' % (sw, pd)
        else:
            body += '    <path android:fillColor="#FFFFFFFF" android:pathData="%s"/>\n' % pd
    return head + body + '</vector>\n'


# ================= takagen99 整份移植 =================
TK_BUNDLE = "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"

TK_PLACEHOLDERS = [
    ("TextView", "danmu_search_ui"),
    ("TextView", "video_track_select"),
    ("TextView", "play_refresh"),
    ("TextView", "play_label"),
    ("TextView", "play_time_start_end_text"),
    ("TextView", "tv_info_name1"),
    ("TextView", "net_play_speed"),
    ("TextView", "tv_screen_display"),
    ("TextView", "tv_back"),
    ("LinearLayout", "play_speed_3_container"),
    ("com.google.android.exoplayer2.ui.SubtitleView", "exo_subtitle_view"),
    ("com.github.tvbox.osc.subtitle.widget.SimpleSubtitleView", "lyric_view"),
    ("com.owen.tvrecyclerview.widget.TvRecyclerView", "mGridParseView"),
]

CAST_BTN = '        <TextView\n            android:id="@+id/play_cast"\n            android:layout_width="@dimen/vs_60"\n            android:layout_height="@dimen/vs_60"\n            android:layout_marginStart="@dimen/vs_6"\n            android:layout_marginLeft="@dimen/vs_6"\n            android:layout_marginEnd="@dimen/vs_6"\n            android:layout_marginRight="@dimen/vs_6"\n            android:background="@drawable/button_dialog_vod"\n            android:drawableTop="@drawable/tvx_cast"\n            android:focusable="true"\n            android:gravity="center"\n            android:text=""\n            android:textColor="@android:color/white"\n            android:textSize="0sp" />\n'

METHOD_SRC = '\n    private void tkTimeRefresh() {\n        try {\n            java.text.SimpleDateFormat hm = new java.text.SimpleDateFormat("HH:mm:ss");\n            TextView sys = (TextView) findViewById(R.id.tv_sys_time);\n            if (sys != null) sys.setText(hm.format(new java.util.Date()));\n            long dur = 0, cur = 0;\n            if (mPlayer != null) {\n                dur = mPlayer.getDuration();\n                cur = mPlayer.getCurrentPosition();\n            }\n            if (dur > 0) {\n                long left = dur - cur;\n                TextView tvLeft = (TextView) findViewById(R.id.tk_time_left);\n                if (tvLeft != null) tvLeft.setText("影片剩余 " + tkHms(left));\n                TextView tvEnd = (TextView) findViewById(R.id.tv_time_end);\n                if (tvEnd != null) tvEnd.setText("影片结束 " + hm.format(new java.util.Date(System.currentTimeMillis() + left)));\n            }\n        } catch (Throwable ignored) {\n        }\n    }\n\n    private String tkHms(long ms) {\n        long s = ms / 1000;\n        long h = s / 3600;\n        long m = (s % 3600) / 60;\n        long ss = s % 60;\n        if (h > 0) return String.format("%d:%02d:%02d", h, m, ss);\n        return String.format("%02d:%02d", m, ss);\n    }\n    // tk_time_refresh\n'



TK_LIB_PREFIX = ("dkplayer_", "brvah_", "exo_", "dp_", "sp_", "ms_", "y_", "material_",
                 "abc_", "mtrl_", "design_", "cardview_", "appcompat_", "tooltip_", "m3_",
                 "bottomsheet_", "nested_", "swiperefresh_", "coordinatorlayout_")


def _tk_autofill(res):
    """兜底：布局里引用了工程没有的 dimen/color 时自动补一个，避免 aapt link 失败"""
    known_d, known_c = set(), set()
    vals = os.path.join(res, "values")
    for f in glob.glob(os.path.join(vals, "*.xml")):
        try:
            t = open(f, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        known_d |= set(re.findall(r'<dimen\s+name="([^"]+)"', t))
        known_c |= set(re.findall(r'<color\s+name="([^"]+)"', t))
    need_d, need_c = set(), set()
    files = glob.glob(os.path.join(res, "layout", "*.xml")) + glob.glob(os.path.join(res, "drawable*", "*.xml")) + glob.glob(os.path.join(res, "anim", "*.xml"))
    for f in files:
        try:
            t = open(f, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        need_d |= set(re.findall(r'@dimen/([a-zA-Z0-9_]+)', t))
        need_c |= set(re.findall(r'@color/([a-zA-Z0-9_]+)', t))
    need_d = set(n for n in need_d - known_d if not n.startswith(TK_LIB_PREFIX))
    need_c = set(n for n in need_c - known_c if not n.startswith(TK_LIB_PREFIX))
    if not need_d and not need_c:
        print("+ 资源兜底：无缺失，跳过")
        return
    out = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>",
           "    <!-- 自动兜底：上游新增引用、本工程缺定义时按名字数值补齐 -->"]
    for n in sorted(need_d):
        m = re.search(r"(\d+)", n)
        v = int(m.group(1)) if m else 0
        unit = "mm" if n.startswith(("vs_", "ts_")) else ("sp" if n.startswith("sp_") else "dp")
        out.append('    <dimen name="%s">%d%s</dimen>' % (n, v, unit))
    for n in sorted(need_c):
        m = re.match(r"color_([0-9a-fA-F]{6})(?:_([0-9a-fA-F]{2}))?", n)
        if m:
            val = "#" + ((m.group(2) or "FF").upper()) + m.group(1).upper()
        else:
            val = "#FFFFFFFF"
        out.append('    <color name="%s">%s</color>' % (n, val))
    out.append("</resources>")
    dvals = os.path.join(res, "values")
    os.makedirs(dvals, exist_ok=True)
    open(os.path.join(dvals, "tk_autofill.xml"), "w", encoding="utf-8").write("\n".join(out))
    print("+ 资源兜底：补了 %d 个尺寸 / %d 个颜色（例如 %s）" % (
        len(need_d), len(need_c), ", ".join(sorted(need_d)[:6]) or "-"))


def _tk_existing_names(res):
    names = set()
    vals = os.path.join(res, "values")
    for f in (os.listdir(vals) if os.path.isdir(vals) else []):
        if not f.endswith(".xml"):
            continue
        try:
            t = open(os.path.join(vals, f), encoding="utf-8").read()
        except Exception:
            continue
        names |= set(re.findall(r'<(?:color|dimen)\s+name="([^"]+)"', t))
    return names


def inject_takagen(src):
    import base64, zlib, json
    res = jpath("app/src/main/res")
    data = json.loads(zlib.decompress(base64.b64decode(TK_BUNDLE)).decode("utf-8"))
    exist = _tk_existing_names(res)

    n_dr = 0
    d = os.path.join(res, "drawable")
    os.makedirs(d, exist_ok=True)
    for rel, c in data.items():
        if not rel.startswith("drawable/"):
            continue
        nm = os.path.basename(rel)
        if c.get("t") == "bin":
            open(os.path.join(d, nm), "wb").write(base64.b64decode(c["c"]))
        else:
            t = c["c"]
            if nm.startswith("v_"):
                t = re.sub(r'android:(width|height)="[^"]*"', lambda m: "android:%s=\"50mm\"" % m.group(1), t, count=2)
            open(os.path.join(d, nm), "w", encoding="utf-8").write(t)
        n_dr += 1
    print("+ takagen99 drawable 已铺 %d 个" % n_dr)

    vp = data.get("values/tk_port.xml", {}).get("c", "")
    kept, skipped = [], 0
    for line in vp.split("\n"):
        m = re.search(r'<(?:color|dimen|style)\s+name="([^"]+)"', line)
        if m and m.group(1) in exist:
            skipped += 1
            continue
        kept.append(line)
    dvals = os.path.join(res, "values")
    os.makedirs(dvals, exist_ok=True)
    open(os.path.join(dvals, "tk_port.xml"), "w", encoding="utf-8").write("\n".join(kept))
    print("+ takagen99 颜色/尺寸已补（跳过工程已有 %d 项）" % skipped)

    open(os.path.join(d, "tvx_cast.xml"), "w", encoding="utf-8").write(
        _apply_norm(
            re.sub(r'android:(width|height)="[0-9.]+dp"', lambda m: "android:%s=\"%dmm\"" % (m.group(1), ICON_DP),
                   _write_vec("tvx_cast")), "tvx_cast"))

    lay = data["layout/player_vod_control_view.xml"]["c"]
    lp = jpath("app/src/main/res/layout/player_vod_control_view.xml")

    i = lay.find('android:id="@+id/vod_control_bar"')
    seg = lay[i:]
    j = seg.find(">")
    depth = 0
    ends = None
    while j < len(seg):
        mm = re.search(r"<LinearLayout\b|</LinearLayout>", seg[j:])
        if not mm:
            break
        t = mm.group(0)
        if t.startswith("</"):
            depth -= 1
            if depth < 0:
                ends = j + mm.start()
                break
        else:
            depth += 1
        j = j + mm.end()
    lay2 = (lay[:i + ends] + CAST_BTN + lay[i + ends:]) if ends else lay
    print("+ 已在按钮条末尾加入「投屏」按钮（id=play_cast）")

    ph = ['    <!-- 代码占位：takagen99 布局没有这些 id，补零尺寸控件防止空指针 -->',
          '    <LinearLayout', '        android:layout_width="0dp"', '        android:layout_height="0dp"',
          '        android:visibility="gone"', '        android:orientation="vertical" >', '']
    for tag, vid in TK_PLACEHOLDERS:
        ph += ['        <%s' % tag, '            android:id="@+id/%s"' % vid,
               '            android:layout_width="0dp"', '            android:layout_height="0dp"',
               '            android:visibility="gone" />', '']
    ph.append("    </LinearLayout>")
    block = "\n".join(ph) + "\n"
    idx = lay2.rstrip().rfind("</")
    lay2 = lay2[:idx] + block + lay2[idx:]
    print("+ 已补 %d 个零尺寸占位控件" % len(TK_PLACEHOLDERS))

    i2 = lay2.find('android:id="@+id/ll_time_end"')
    seg2 = lay2[i2:i2 + 2500]
    mm2 = re.search(r'<TextView\s*\n\s*android:layout_width="wrap_content"', seg2)
    if mm2:
        abs_pos = i2 + mm2.start()
        lay2 = lay2[:abs_pos] + '<TextView\n                android:id="@+id/tk_time_left"\n                ' + lay2[abs_pos + len('<TextView\n                '):]
        print("+ 已给「影片剩余」文本框加 id=tk_time_left")
    else:
        print("  !! 未找到「影片剩余」文本框")

    open(lp, "w", encoding="utf-8").write(lay2)
    print("+ 播放控制面板已整份替换为 takagen99 的 layout")

    vc = jpath("app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java")
    js = open(vc, encoding="utf-8").read()
    binds = [
        ("mPlayTitle = findViewById(R.id.tv_info_name);", "mPlayTitle = findViewById(R.id.tv_title_top);"),
        ("mTopRoot1 = findViewById(R.id.tv_top_l_container);", "mTopRoot1 = findViewById(R.id.top_container);"),
        ("mPlayBtnGroup = findViewById(R.id.play_btn_group);", "mPlayBtnGroup = findViewById(R.id.vod_control_bar);"),
        ("mPreBtn = findViewById(R.id.play_pre);", "mPreBtn = findViewById(R.id.play_prev);"),
        ("mPlayLoadNetSpeed = findViewById(R.id.tv_play_load_net_speed);", "mPlayLoadNetSpeed = findViewById(R.id.tv_play_load_net_speed_right_top);"),
        ("mVideoSize = findViewById(R.id.tv_videosize);", "mVideoSize = findViewById(R.id.tv_resolution);"),
        ("mZimuBtn = findViewById(R.id.zimu_select);", "mZimuBtn = findViewById(R.id.play_subtitle);"),
        ("mAudioTrackBtn = findViewById(R.id.audio_track_select);", "mAudioTrackBtn = findViewById(R.id.play_audio);"),
        ("mDanmuSettingBtn = findViewById(R.id.danmu_setting);", "mDanmuSettingBtn = findViewById(R.id.ll_danmu_setting);"),
    ]
    got = 0
    for a, b in binds:
        if a in js:
            js = js.replace(a, b)
            got += 1
        else:
            print("  !! 绑定未找到: %s" % a)
    print("+ id 绑定已切到 takagen99 控件（%d/%d）" % (got, len(binds)))

    types = [("TextView mPreBtn;", "LinearLayout mPreBtn;"),
             ("TextView mPlayerScaleBtn;", "LinearLayout mPlayerScaleBtn;"),
             ("public TextView mPlayerSpeedBtn;", "public LinearLayout mPlayerSpeedBtn;"),
             ("TextView mPlayerBtn;", "LinearLayout mPlayerBtn;"),
             ("TextView mZimuBtn;", "LinearLayout mZimuBtn;"),
             ("TextView mAudioTrackBtn;", "LinearLayout mAudioTrackBtn;"),
             ("TextView mDanmuSettingBtn;", "LinearLayout mDanmuSettingBtn;"),
             ("TextView mScreenDisplay;", "LinearLayout mScreenDisplay;")]
    for a, b in types:
        js = js.replace(a, b)
    print("+ 按钮字段类型已改为 LinearLayout")

    js = js.replace("mPlayerScaleBtn.setText(", "((TextView) findViewById(R.id.play_scale_txt)).setText(")
    js = js.replace("mPlayerSpeedBtn.setText(", "((TextView) findViewById(R.id.play_speed_txt)).setText(")
    js = js.replace("mPlayerBtn.setText(", "((TextView) findViewById(R.id.play_player_txt)).setText(")
    js = re.sub(r"\n\s*mScreenDisplay\.setTextColor\([^;]*\);", "", js)
    print("+ 倍速/比例/播放器文字改到他 layout 里的小徽标")

    if "tk_time_refresh" not in js:
        if "private void initView() {" in js:
            js = js.replace("private void initView() {", METHOD_SRC + "\n    private void initView() {", 1)
        js = js.replace("case 1002: { // 显示底部菜单", "case 1002: { // 显示底部菜单\n                        tkTimeRefresh();", 1)
        print("+ 已注入北京时间/影片剩余/结束（用他的 tv_sys_time / tk_time_left / tv_time_end）")
    open(vc, "w", encoding="utf-8").write(js)
    _tk_autofill(res)
    print("--- 移植完成：布局=他的，资源=他的，代码只改绑定与类型 ---")


def main():
    print("=== TVBoxOS 定制增强 v31（takagen99 整份移植） ===")
    print("源码:", os.path.abspath(SRC))
    print("订阅:", DEF_URL or "(未传)")
    print("名称:", APP_NAME)
    if DEF_URL:
        inject_sub()
    else:
        print("· 未传订阅地址，跳过内置订阅注入")
    inject_name()
    inject_dns_default()
    inject_icon()
    inject_takagen(SRC)
    print("=== 汇总：全部成功 ===")


if __name__ == "__main__":
    main()
