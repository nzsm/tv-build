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
TK_BUNDLE = "eNrsvVmP60p3KPZXOsfIE3s358n44uviIIoUKZGiZnzAgUSRFMVJEkVS0kWAGyBI7CAvAYKLIMhDYuQhDwlykZc4tpE/Ew/XT/cvZBXV3bv3cM7eZ3/b9nftsw+OmkPVqjXVqrVWDfzXPzTrrA4r8pz+eChP56dLnv3whw//+ocz/P5wDi/nHx4ffgjwzW/+Fbx7aMJTlZTFf/bbH+gn6rc/PIRFUG6TIoYH9Tl6J/32h3/1R78tfnMKq7I+BWEFNw/w7zf/ybt3D+d1uo7DQpYf/vrP//Lv/+x/+Pd/+n/9h7/6k7/+y3/7cN6Fefjw9//1f/t3/+N/+Xd/8Wfw4l7iP/zVnz68e/cCIyiz8vRQrPMQWgOEu1q//eGP/kCT6B4j/IbsCvxs6R8lCldQ1V9QReyqKOwvqCJ0VWT5F1ThuyoS9QuqcF0VQfgFVbbrU/pKkKTSHC19VO9DQWXra1mfH/7uv//f/uZP/t3/92/+i7/9k//ur//yf/+7v/oLENTf/9n/BIL6Kfl0Nz9S3b9Xrt9vfw7Te7Ve714S13q5/ppa+N9rY/fbL1d7xvGFK7+wNaarxrJf29pztRfZfW01VsP/vWrJ/farW6O7ajT6hUjSPK7GCL+Qky+0fZaTWL+gy39Wo/7m3/3F3/yff/5Go7ZJHhavSlz9SDMAmWby/Ddk9+qnyjEclGO4L5eTcDnpbbnfVOdrFr6UaZJtWP64K0/JrSzO6+zHw6mMwbhVyvoEVe9gO9DJOcxfaq2L7alMtn+Yry/zZHvedUhvD78hcaEvVUqKbXgOT3lSrM/hqMiuUDtaZ1X4DdW107pdb7LwA1Txvz9+Kb59LkG+EPbjBwDekP6m3a9C5AXgGxz++H1rYFheefmmkW+hsT6tzzAkAXyWx+r2iyEo4W7dJCUW6Ck8hOvz18GAyq/S/Ui4vyE7LfoJdYIx9JwEvyrTP4wyvXD3n58qkW+9qh/+c3DMXlmwKS8/BsDZU5ll4enHTXk+l/mPm/h7+XPVbn0IH6BCUf3hM9JQYnc+H/6QJKsAfIt19fT84ikoc3J9SDG65POzTmeeCYpP620SFuf3PHlhw7qIM8wWGTD59G1YbFU8kkCBV43rhhbyfFoX1WF9wkA/UzGA5+Hpte69zidj/6f1qvP6dP5stff+yQPZSabjzx/9rEzO5eE/WoEw4veVyO/K2RrUu/hxm6yzMv6xKbffjathFgZncGt+R8a+7+hvKAYDGJVBXYUY4PlUgxH76PUBG7A3r9+ajTsfPjS84IOdCqDsFQwWZF1hnnbuDNlUP7IvrPygYlVmyfbhA5m9l8QHAcYHdV/E8WKa3tqpnyW3G3P+BdH7e0bPb88vvvff/t9/+Tf/zf/89//mT//6z/+Pv/lf/+2//3//n7/9X/6rzuF+LlOBvUrDV9AtHpawBcjzN+ILPt/r2x0w5R9LZZ7f/6Pz+GcM3dcQDo+fjcxHRm2bYj8GBopXTyYr19hGfbecTIk5+DuZtjstH7t7HS9fyDg3lx+rQ1J8XDg6lbkWAmEh5j318etz+f4lK3zy+pA05XkB73jqP/3su+XLu04GH3J2dy6bp0MRv2fiJileeZjMlNG4pQZGXCL4N/SnO30awxX+H5lIRUv4q1HhcCJ0T/VM92ZjblEzW1W4nGfsPCSZ/mzk6M0yDVGFFG1vXmxtOsidJTlPzUnc010lQ+vBYDJR1FlCmYpDz4Y+6k93drY9THu9fqIrIjSsq7ve1tdQuTPnqJ1q06aPSmXM8cf+kRuODBSuMs+W08WCJqOwusin06S/IG3pvFj203O4DLhLQ/ZHFbnkiduWixeKClh7O/ixGMUx6+VlYMADoE43PR2I073n96bnqD5CE1SNkkzD97iQg5Ty5do0FBNYFM/7Y38HnIAbRQVoFHq+1jWUImS0tlYeUAv3AHYHoAbo+VpFsaormqnsqGm6wvcYlxj1ELrcrxHqaQiAt8Jg4sTPeIIAYrR8uVZ3sdcic9WzmGl33zUeo+HrNWotkJqTUOLgjhgG3SKjfLmOl3oFiCrrbYYRu9O/RNq/IF4kcZZa6WIsTXqHqdGGK0d3miHlr7fWKFv4ke/DRTpKS35LTurdNUDWOudUmmqE/Og3/ukwpuogJVfzdNKypFmbt6ANqcylWqTXh9lge1nlq0EdexPKyBWaak8OIe2EqXGKWmK61WRrLPD8iN8qXB/pZCb6Myi+cFkx0MeSOvd8oGOWKdbSWKKdkl7Q2l/k7K297XiyvvEupeh5cVMkZXQpJ4SlpiyvUaNL/6LNAugq2uK6D32Z5QykuJ6vM7mmOrcd2Zdt6iTU29kykk7nuVKp4cXggNrGXxyysXvjF7uIlc/SBdn0bGv0+T7I1UG6fZQJgZtvcmkoyrvVIDwvyiiS6U3tcWpw6XOIKsiRbxOrATc8kpGCeuNF27+R8SVGE13p59XeWV49eSIPbtaWIUp5bB5mktqnqVW8iKicsFlHcpDcE3eXxhF3qA/WZBye2YV6ldoCeD6lMnZer/iTOQQlWMoWsQ/GTtTS3ipoNF1drGb0aFoGF2QliF9NLrNDL+f3VNZMN/7cOw/jDdpVJom2V1+eDe2Wlw6R2FK2clTZJOGq4kY5SF3FYTSXlsNpu6cPS8H07DhwxoR9TS/URC/Iua56rje9TRe5U61BTpPKVIVVvWnJRjxZGk2gUPfN2GfMCJ39SNqZ5dryFIwjAhwvtZ5Xa6RfUHtdjG79sx0ewzS8TQPr2FOWaqvOKFCV1HMKSuUEJTCWw342Z8XW6HipanwgOjsqE86Cvzfaq5uqqO0teycroqfj/kU4xmw+VwLNQdtM3sdp7FFDpK5j06cz/pT7bHXpy/vVtKcPVqmkLCyXvSXufj+aBNvgKjmtFVPz+XmPsgps5A1dDpN+c9VvN35LjRbywNX4zSxrp/GcaMhs0k6W9SDcTSslV60ZBOp8cm9vikYrYja2TlfKidfUjlKOikVFukFX9vooc2BTRD0ckBPqECvtCFifQMFt5GquO49Ylb3oPUZ0MqVXZoFZp8HVTpo1ZYS2iuvax2zdr0K+RBpSHKZMnIt0XEfxUBg2w1qlN94cHRSDC92mPYIMmn4m6mo7ahPNpg3CM7HsHBO0rhkR6V5UebJwkVWds/QWj9OssOt5g24I+fxqrYiGu0KoRePh0ZyM3Iz16YN2dmtE256AFqiQ9kLkZVHfa5UjWlx9itpf9CHWJzOmU76oUncxSPhZOkd7yg/1oU6OmrkOOn/uCbtb7WwYDzBKN3OfWYWDUX5NV9ts5MWc7iYLPTJE2w8HaJ7wo3h9mcy7frkX/OVtQgtDssmSgjeWVdnO4rDPoil/IPyR5njKPMzbhlmmnW7velbBx0GqjUn62laqPkxGrVHtuTpkanYh1EAvdRvmO8nx8iGCQRKsa4/PiyQ6aJOqateUFzsaq07a1NyLgRm3jmeeZ87ycFjGIMPtTvWFJiIaojooI7a26A14Esr8Ah5Baefurn9htxuAq6yP3G7lak6nY7vDCRsGM6wF48zqvKIq7RpZ7n65j9Yx5UEfpZPDvufwjtIivzqum9mEJLUZT4UVsTwv0FJRR5chN5D23JkXF7dN0xsnKFzkN6bV9dXeQ7mJaNoKVzZvUdT4uAjiVDdttIqn2/7FrtiaWayPNx1RpJXJE8q8GS3w2Ogfp9u8n7CHUSEKvLxTl4qp9rmjGd1O1jWr6iTuL/Xdld1PR3GLR6CYH9fVRWqO48hYh9cTMoGcq966SEZj+bTzWqO0ZuAkrcadTnnReM4sRy7JRteZPzggRhl5e2mV+oErbQ2BuCpolvT189YZH2GgNpAqH8/H1YHLhOVo0lsde6anKnGgLSyL8vStfEBeYJTm9Gg4W2+D2/Cb8yrc2NaEuQV+Tkxla2P16QF1CLJooie7Wo55ZjYwtSG51uY0kfWsA1UI82nubna3Pnd1k5PP6gnqlaV3MpzJOMb9Lt3bN5W3a2aApjtJnjTUxD9CPz3Em70pTAzVmOTByiK8rWlbY3Yz7++0kS0t9DBkdOUFx8hLwF0YxsaK8BRrdpuWLb+16n2cbPK4HabWsdAV0EHtcFmZ9Vq9TXPAZ0fXJrbF3m7uLJm9iYbJOgYjsD+ObYO3d7PrVB4mA8OGssrS2GJczOtEhvc756wNBEYfTyNOHF4SNKvHsZFu90ql+QqUY64e7awG02G/7bfbFI8zjd0mDiB6m/A9arcei3vbjsXyHOg7fSGKorNJzjHqb/YXmRL1HBRumKxi5ypFzX7IK7Q9CjbnVtiT5K53uY0Tu/KWupyEXu5vbeLop30mRxPFidTSU9Y6sm6JTq1jpYLxM2dT2ldbMthQlTC4Duqtxrm8xp3j4CJVA49Mi0l61ppzHZ3aFaf1x47HyuLl2sYVqKSrrsJcVifjCqkXxzOWxGJoi/JRnPK9UBqpA2NytVNl2bPUyYTarAJ3bybu5HCq+iWMA+rpUJFRyzPRamQuc/ZYb5Ksl2snaUcujwc6k2+sL1t1cQYz5Q4FEWxNVk2u4HJMWodkJW2zSIlRom3rIojNIWOicamZ+rmazE2kCP3ST6184W8OLdEeR0EdTUwYcKezVaJ7SeX56LZrCdnYi9Kxsem2jEsy5IaarmTENhPV8QhFs8Ux2A28PCR8ebBTBwteJmx1nri7euldqs10GTuMVKyj3Y0SnMGUleWxds2Cvry70xf62IdIOc0h7SR12mNGuGsz7IHblF/OPsh9xxHzU3Nbci7YC11ecFWAZkMLrMJ0FY944OsqtMNi6iUpYftWuNjE5Jyv/KtzLXz2kC2jw2Ic+G6PEF1lgHy3OJPizS3npJS15mh2XNUsutm3eZoWvfnpsjfjJblfb3rtOLdW6mpFHY+k7YKEtvohKgzkXI8jbS1qS6NnlEptQf8ZLW6rW2P0qNPlNEZtvlMCfZXMvTwYFagRhyerCcOTu2Out2ZmxySMVYBH1WzjQXtifbtoxymfMP4+2U+5g3GOtC24QCPGTlSAsTWJ7KTQTc2QxkrXenKxcDfJttUG1IiQg/k6bJrjSGB6ztYiZ0d3OToKBNd3hfl5OXc30C/SjdDMbc86WiIaI08+jsgbtRgzYnMqJG2a3OQpJ6SGvyskN+v7pLIX6mqnC7dleJkrbszG6mZ2WSqT9IQWkbSM9SLbRjAukA4MqlsrLAcpt62PocosWtUaxv1KWwzEIOm3DqpF4dKqTrk2h3S2k7XR9Ab+Gj3cbiLO4OrN6oa49IrCdlgtdEIf3nRlS9Kg/8s5Y4uZww45kRW563BW+OMT4QoSofq3gWLHbKtxmd/bnPRCW7gtuLTrWRVu2eOQYiKLKFZpLpD8xA7OSasmAFeM6Xa+MRPmpFv1qIrQTWXKZrWxb6NoMMp8fxGuAqWebw4uMp9xmt4O+nAcPOO08ub5JgQ7fgKbT7eRWdXjVr2tKiS3a66vpmNh7OmsO3fReLearZtmxsoHabN19qt2diVoVBrphBtyaCvEpzO7AieSJQ1THY+t66pzZiHOICxjvrIyQtXGJ3RuN0tN8k1+eFbt/akPvtR+Xo5qNbiJV/pAGCcr5Ji2rzcQSymWTmghcuupkeVnXwK0wc5uV7NrMqquEmP4LIypgsIsuGZDgG0qOvgu4ZuSq+mLOx935Gich9tBuHciZlNpY1ve5DcT+Md6E5ZPG02688NeShqf8c1xYlsbfhxMa/12CuhlaweGoN5UJ5fJ89k8ipKDfcCLX5i3UW8fQWe8rNkAlT1ZsUrw72KkjDLnzgs0pFfEihcuBLcmryPZY/fWyTauM28TA1xG3deJWuVewgkXSavMvge+5C49Ct7WroabeujDuD8ALyqOd6JO+PEewuXSE4lqP3FvzcEk2jribeFca9PthmxQxGBdMje0N49veh94QPCituoBYQaEQCuKv01r/mKaoj6Pk2VAgs/dOE0/Cq8hQmEit4mbZnzRpGBC9dUKem1MSaTWBxfM2LYQ5/eDnmj1yFXGlcLEbMFH1lFKySQEJybtT63xCry+USu41tBgL3lxatfkWKLFqVBtUjWucZuVgrbrMTfHeQM0vvpoAON2z2qpSJZKG9mxv47c3R71l4dBFDE4bqd0Z2ZJ8c6RiIlsLq0sX1l2aw/BN7+gHg89tdngvERpnjZ6by/TjVxYK8rsx/vKG2iH3U0ylmY0CPJqoWgIAqnxhVW9q3Sd+8W+qY/HSw6+EY/Ltfp1fOjXbZ9cX/W4iZSZYpFXRTyxotDQGx+chd54v7fNjWp2cLVcNc/WQQV/Jjc3p2UWDW8K+B95clHHCjdc9nuuC3gOZ/4yko9olyAhLqlzX371Czfw4NoesqkHrHTU60WfU9zFRci8uVtbP63qpW31mCuDPLOxbMTtRMIwlUG9UVi19Vqk0tNypS+dwuWESB7tl2PNcKpd5SR93A9Gnrmn8hQYrubc5sjNQH9sPY0WvVus9C7Dpa27EaB4XkyWDYRE4C8LqGSrArpIRk6ccWXyM2XfZK4391cwRhoza8FdzfxSu8RG283GJOpv0zNRGy7aJhfifCVCZM9IkDdiLrp3KHhlmrEb1Q/IYMQF0UxU18Qgsar13iCKdFC6HBIVmxR3+7a/LKNTwMRzRWgEDc13aAz1kZ4thmNtEPuGNBnaPX3R02LRGOqZTaNte018LiSBt/a6cTdbyjuOONwHjYPlr27gc6290U5Eze7Im6Fx6WvZpUeT65KIew0Sw8293eYUULv37U6g3WFaFMOdNtAdu+1742IsTdpGZshjTMa7UhXDBnRVW1fuYcuOBVUgGQSNKlPoI42w9AxvlxlkFLqJUa0TYz7XO1pX1rYBjrdKNe1Ttbiy0DYiFaRM7MHebaxj3lMIgQUdnumzYG7yGU0QpVYb6+tiAkbIU06zA2nXycxjFxIEGgv/Wl374CdEwXivyQn4S6OA1Z2wMmde1GpzX4wwjb1lSR4Cav9Mo5/MZxAvmqN0dpn3JHAlYZA2N5dF32kKFvN1z625CPOVCRejXQmRT8dXJfHmk3wF/rSNxL0w7l3Che5Y2/OiL2maNWTlFmzaVLX4Yc6YXn9Bth6aJlf9xl4Xh+lytot6rF+NIZ4LzOX1tK7dUu37w1vCLSVlYDmycduqpX0iQWcHO/Bf+vyWGuf6csMR5uWyqBfigZY9XfJdk9FYYMmgoJhNq4ASy0o79GzTdpreyT9CW65KJYuM4SKimNPAjnjkn/sNt4x79qFiU00ZnEStXcdz5K/CNZOm7UkbqU7iZvlznW3bEJOfrPPiNy23LQ1uF3Si/OiW6CRYS+hXV8SvINaOKHPmBhH4iaB97q2XZv2eubqs9LF0YDWSOjInjdDaybIaBwv9sHPs4ZEEnZcUFTMDIRhUpoE29ONhO6PQIUJZLxqxURPf0Ho3d8nzQr/ua1comVYBh3PQTpebKRoUThPF2solrzaxkN0Q/JjTjSfFBnxzp51x0NWFxlxIYbRrrgdJj6ToijgN9FJtoi1L36QJ+DDoMGZiDmlXaRQuSr2kb8TmrKv70hW3g+ZcomULceJgXgThUrs6LhkbJ/fmSsz8eK7jwSJZkcPr3YdS8DDmcsu2n5oR6fmlbJKEJsQttHmSRK1r00Bo6DHxOB+VSCKRPOZXBdenrb1haj7HhGS9aQjHg8FxaOaO4yj8qEfm6OS2LtESlYkyhSMJid3KoE9gIKfD0rC0K3LJG3Mc3fqku5n30Dae6OOt4zvYv4CQ1FH1C9M0Bz+QYu0mydIqIqc9J0IiMvaLJK1TczLckXR8FJhYgX6P0LrN6GNZ3fEcBhWjTyRavm611lobF28xSe3O10TohqCXn9jptBiZuGzYW5Dy+Ka3aHiMZxnHu0vTJira8CYIMe1+QVxCTjUsslwl9ehmEX2S2XChd449mg/YXaikUeNeCuC7Uu0NMoAx2nB81r3R0016k4ZkQLbLWGWWwbQiFX1TufRZaT2l2s0ZKZfbnqOIljhbrpOJ5JIE2y5bleGd1Tkao+UxkivNc7RKmwvBnKd6EuJ69jZaeRPCda/shZMUxtS356sQtWgvr66BCf7fVhrRRCVWMAxgb64UpRr06nImgLcj0t7JjAf+uiaJFq6vFLtNXHMqg9jw1ESNNyT7jSByUoD2jupZq5UN4zbhUCcfbM7YMQQSIl90TgL2dqA3GLbb8gBbMfu9LM89H2ATe2tZKQZis21c8wBbBOuyPXszgC3uuQDDTvzDatVfmqBDzLGDHcwFIgfYwyRgxB11h33FsDXT7WX13PPusLlAMRT2sIprAWDf5vUQ8O7dYQPeE0edWquttjRdwDvDsK1qIJBHgE0nAX1bzU53vGmMNwxjGQMSnwPsibV0lBzdzmFciwBb9s9DwHuFYU8w3hMnmR+2VVHpGzKfeBbwNA3dbcj2KBReRmu5LGUQTltcluDbKUmT3CIIYliyIlgUWed4MC1kDXX9TrNmlw2Hbqaxtndx3vmgXcdcCf1OP43wmBSVVqD0xtzGg86nRcjxRsXYdWLobzq5pBaBQajOcZgfPc+uCYhpl0gZ7ImpovBqn5RuMyiAHGKY19LS7GIVDgpojE9caAT2tJctlCZGC5PZmLv39uHocgR0qAY1xxKCvetNvZ3Ww86nbaEr0YrQAxvKlQlXa57JQT83BOUiTLNt1Ui3Oe4SpWIsoW8hRgmint1H9u4Uo015irWGHBrklmS3FRst3IuDrFir3QAJEfShdY+W0jxQuQGnGEdVRKfbbUySobyIXDZjyc4Y2nsWjRqJHdfxNupZRZyjul2V8YgbSA6Ml4tmwd5ocUtSNzRHKsRJ2skdshtOm1/8LY/bM45IqZMGjViSEmmalInbVg4kPUY5xGtEezsTMpqVi4LwV7/i/ivuv+L+K+6/4g64z8EdXCASjSbNJFBltDgA7rfOz+PQBbVWAnQ5lL1nDr7Y9mJU4vUAEV4PwMrHychbI9VTC4RsA+cCLtW02PpLtMbz/i7KYtRvTxNm5eCqFTrEJgD1rijANHjpfS1EH68NUKQ1BcMwprWPBqahOHhdw6J/8VftAIELjtBMUg2kRczB4WEoypHVqqoST2BUWvZ4cpp7aozXTbRWAC6cysr5ZKSY4CYOAoSqpe4gzQBe0FZ8Xz8hqXOEIvXsrtKOZ62ao1jr1kJcpGm+VT20xgscoo6My2lCrLDgUAA8eD8WWgUqkYGXNCxwTmdIrtNb2pFRIBPIcPFCiEUhgz4M7usxshavx4iAKRzoTYoO4FBf8PoJZ9Oz2GmOjBiv0bgzZUABGY4CCoAGSxUcBt2J+5gplIWUIzBlfCfDOLt8ipmitGoCTEFIW/YwGYF6X6fxRmZjTIYaoBjIkPD6kzCirRTI0PGCkwVCG3QmgSmx/48j25gfmtoQz+OuDz0nY6eR76/s2hwVS/BKJxwKlYW308eD1Lq0WjXds/ViUkKQwSyGB2J+sUYrmdeocjgnFeooFIK3n3PH8dwt9zFgMZxq8mB5dIYJeFzbRJ/l0QKvEaBImk8PXCysJiMqGW2VMRAJRXqJNtmkro764w1TOkV2KDTC5VbpQRCMut7ovrbN4h2ec0N2WIzt8dKJ9aLX5aRJXvUDed0s5SbdZ4czyAT7aOteHjVBaKAwkdpDxu8Hk8JfHJnD8MwWiXiwl91sJcQHmrXdTWvlqJ6CMyfkwUUqj2Pb2jIZdxtbm0AHPcYCXdhb0thBtflCsjfWQQUeTCgjzYrtKg4Hi5mO0AihcGfeyrOteKO2tsytW2tOo2u+f51u6Vl2PAydHV6HoxwVbe5LueXd0DI90jw3JMM+SW5XZshS2eBg9FAHb6J64cY5QCC0tgNWiOeLvPHn8lQeyPSJsAfXngcdUsN8nwm9RoGOu9sGhHORcmHL+PuM5wbluPG79UN6m/Wp22DuoDwpenzZS1/XROTiaL9v1qaJcLxJldOJOwB+qwItrg5cIywsK7JIxcvPJqOYIDUXjdZxJ++lSNK3Q8pH5q1Zi9swhhCNQjFWYaNU9MO8XCtotlsyE/dWDKcNqTCXaoisXjtgoQdDe0prj0q8EOvIGIQUMEtiNjRnaS6wUsAGyNQNtZvzR8Pr2cwtiEW99LjNo3AmKzpxY6Wd4rvO2bvryLrNe8l1CTfGUhnVXMJscmk1qLNiUgSzbT709lOcb4Wmj70wkUftKkYwTNxcPAfvqV4y01Xjcpfndmc6vVYaxLrTDmLuQkuVcyWm22HBDUQnUUYlXmfVInd6lE0KIVlpRaCTHy7K4koy681utLOXcifzXBHlhVacsO2xK79wNeLmXtFhZOyjIlNKvVK7GMWK1EW6w7GXofLzFU9lgie40CGX+hj3KTCve9VMe+d8gNAqHjC3CXuaCKeIdP394cIc6GXfG9CdAExlrSxOzT7ulZUrrIixZd0Yqh3qA7XFRGHd7um9y9zc6AB3Y45PRHleuCQdDYh8KSy2e6X9mF/ruIoOBV9W6WI7Xs5NT4unOD8LfLAcM6EWC7NEyhw1E1fZZvzZ8E/1qCDZjKuoSn7W/3C34cZQZ30s6LxJNd/ymN5YjT3oFF3fdAYFmrvXFtOheWnqcGFE1uR0qic6KnvWXSfUiVreeo6n9s2xehZU53bjbaqdbRLT48ybrnf2INeHhdjvtQjsg5H1jNWJD6i9s1HDrbfcXCZUVqXR9ORn15ns+Fa92V/ytnRh1Mq5IaWm3JTFeZDzxFMJc5SPtOB0uZwXjbVpj2bOHx2NV+NKmyvDdsMNN3Ft6zaOBzeSiVajpWb12Fk5sEKrLpLETnbtNjZVzxR1FuJHsEIrs9fTWW0RXSuD03LfzmnTnxEzeZiYhi2AogV6nSzwHKBo+1frNF0APsTZMFXWnxzY0/IwjOT++xxvmy/OKuij4s/86ViZ2W1MaVNFbjfL7aJnbVJJFZtDc/GUwCZy3V1XNOkttKNLEvqiP5R7NTgjk6O6idnWLQe6rmfQoJxdanSzr5uDsgzrITHf9lb6opcefHdttFbbkVMMbqvjjergtx6S8Hy7cdCM5OomhMfqngcyNhnwc0aBNvE2w2nR8RYGdduymWSu0FFaTNjE3RnB+FJpXG/V4dHLdhWd3ZThjWY5U6n1m78LFoOwfwAcuADJZ23ZX6p4fnFbKxWjeHjMYsGuhFaYjXfrE1cfx3uTGIi7idEOvfFAxXNOil1uhqWD6TszYNlgfNjrVq/RqKSfhZxLn7XSxPOQToUzC5Ox0tKsZCswavjrYH6sewc96h/bhl0ZsZVhHVgqGTfMBTW2G2J+g5CfKoXjDA1X1ES3cEGmMjOlB8rSFeRUnH/ISQVG/ehcDKVyfKqNnaGpod5Dk0rFc36nGqWRWj3zVQvMOje9jAqNcT8abK/Rye954wp8ytVaWRFOjucpm3aqpdZskJi7q3JY8JUYsCgKDKFHy1URLSKy0G4ihfq6bs4UOyZ7C39FyMd7LgP68zomYuIS+Q7AHa+TFVEZz/OfCM33saFYas/rs0q27xULdmOO1Dpqcf9WhykVTy1vEhgMsrba6oznG8i9jm1SriUj5aaTqPH6ownfbudXOz4VEpijdXyIhqatOZPP5V7Wo4upV0LQ9TPrWjFrsCcveZdhKWZTjzJawGcfb9ba6pi+toly7bpSblO3a9Pjs+0c+tNLm/RmaC00x+vavCp5wi2t1zbdHaefT9N73x5L8418ftMmUU49duB1bR4WyqopXtvUoM1UmaQRtNkbjfn1LKO013yqXnEHZwqutU0pk9KfrcZb9SVP1eqD0SDvjTwcI0xFJdPmC096yfMq10lSj/epCHCNkXbwej1q8Qq3jLmqXfI2hrtP6wm9WhmvcIf2yHaNUSfPpWCmx+n8ff4YqfsrtdsDLAz3surRWVq8wnVSqZ4uZbWDGw/G4/HKfoVrmK7N9ZsJ1r+QH6XKfD55n5f2b1fiIlJ7zPs6MclNjxJf4bal1HLhHa5YDUYhv3Vf4bqW64yzqouV5txwv6vFNzpmx1TrMxfcj7TNNBzVizh5zgX2S96/Ti6XZWeTelXCHYBosTn1sc852p9GB9s84L5Qq2lzqgkb99UuJ2/zo+Ewq8ZO16aecNAm8dqm6FG0KlywMminFFyw/mv+sV9Ks+uE4suuzfyQcKfe2zbZ9cGejro2Ebc/1fnitc0+7w754uxjOkMOosBasOqXNrUTovjr7hqB/dfGu9vzOggYF9kdi9x+wyr5LoyahmKjuYv9A0YLlFWr1dpW5eXaq+vwrsslku4McdaZxc526O6Cr+PJmzhsqtIAD9HjWRwxgVpoZCEcRmJNCiu87q3Ewd0rjEWIdhjEEJk3lGMf094LB+myQmdvVXrD6WzZlwsIukieOE5qsSFyD9sVHOR0PDQOECOyMbB/qXVg9jjUMa/2hDhKykw9o/HB23qLJcuniJcInqgn9akgQwi+VBi+WqvWQmTS9/KBskGglR6MdBb4IMGAI+pNcyraFDBTBRxvyhDHL/oHiIVs1MWrfRYBThAjFgI/EuroukQTpD2TWcdBmHXxVRcDux7wFVydUXRMxVokDyleJxlDQNnZq8vxHrN1sdcQ9QtMi3WFWFYE+x6oLfKRnSsO1nXjEIY4DnRQD4elUaBCpLdQa/eUiwIvQbzpoLqEGC/COYuLMH2ur3bEpTjmfuaFlGPkhGeWln1MHNXVt2KNQvMAx/E/I8NpfidO8xQex49qcKRIENWhgDhTj1U+nnT2/7gADe3qL5/ZFqNee9oLfE3UEcTvE2QfwYHtY33s2NbVvxO3wnFuHZ1S8ciTVgzIjZ7Z1uW+u/i/Y5uMegWOnX9OX7r6VowoFAbYDywGZxfEITzLtF7qN7A1+jrjxWlXf/7Mtl914led+FUnftWJf4E6QTmezvVqf59cptxNH0tR2CNEh1ac0oQAqzhxLWHQAV6zu7e29NRwRqxZD8q2YTYO0siJPHB7+oBbUWPpVCjkuVwhY9l3ePc6o+bR3o8HK2I+8t3MWbbkdCytRz3itt0hl59TGWWbk7Y0j1zFWsQZgg1wjx0+YhYUs0l8vC57PBz01XwEzo81ss9XUvXcdsZbowE3br2pL1U/2aaUkVGkGi6XmCnXsDbQT6KLHxGc7pgi0HDZRfVt6E0GquHlvEA47u680Ku9w/IRdWsPe0Lf6a69a8nr0mlHshWm7W430hfIJOxkJM0hCp3rarxLrTxoLhAA9w6WqY36i1sbRXG/3ZazS6NNIV4kuOjiGJwtm0Q9G6iWRbiJFU4vrcZQw3gL+F6jfFNMys1s55o3Y2sSO7IXRNcicRM3mxiUpKXIvZKH4bXa+fZhTu2phNs3vWCDZMVYZh0OdG5VdErHQRuQzaQ20owdQPgzGPcvRFUu53uEWraKI7q0lpsFa1MLffUae9NoVdjE6ugOxwnlXZ3LjttfnOZ4iFbURpe0ilutpbnmaPEFQmZhGV/VM14FttvGox4EUIQ0QgKzk5RK6S1JbdEnVok7Gh+mutO4xPEicZEYX7W00M79gtPtQzOrVuNNrBq8NrwRWiM517NyctfE5GxqZm03Rpn0dBW1atsfsdfrkln7S8/YhJOtWVjWjCAcbtDysnHRpMM4s0mfQycka6p9tc9HaY7XS271FdHYsSh6DBqhkpXMRCs2HJ/khDDOA6cvZu1OmAlD093PEjspR4fVHOxe4fcP7HB5k+WTrFD7dCytDGOZmFNVv6idjvIjb7XV53gPxXw1MFw2PJPOnke07riMN9odJxS9LJWRvvFnwDB3qckJa9iHHl6xdDUNjWuKMc7f+F6+upJ2AjZlNs61o0ss+BkV5a6b1fptxfARGYlkaXI5xGKeb6wBgOUO/f3KuM62rns9LNPxNCqG05iJzeMYfHNbDgdpGuaLPID2PNm0d57MrS3XDkGfVr3aOl49JI239mleKtdc2eNcyDAtN5FO7q5jdIkOjmmjsio6vZJmC8onFHoWCdqePGikPMqise4v5bpw/An0JXbOJRfLc9pIi27ZdSFP0TlOkK4GwK5E3Yy4AWDWiPlAO4gjxVmS55t0UTYGSTGyslEEg9G42cArwFxqoJgmTvyM+nJYJ+7GiQdNUu534jLNFykrybbhjsE2+GAb8qsCFlhdxlNlr5TabUi5QyYYrD03L0iCdptrqlVueeDNkb/bkxsOzRUxzikYULhIZu29Nz6p0WU8di/6xktY9kT30E2TtrUXnZFvzbu9hLqheaA3wiGpBE6Mp1v94p7X8VkN0Gwv9zRL6jcSuY7TaTVVYjUenA1PG7GX8WyVUqZgOeNgujr1eyWNNOkkBMy59c1QNS/DsqdrrZtualmteEqMA+ir8nkZD40UQBO9hTaTnKl8as24j3LHXw91FLiicdKUkzdVo8SM84KZng1O29lLRK6JYqLu9CuwOKdgOOLc63Axv82Dq9dGg4lE+nZi02enyZ75Ysx9MmNszowtgO+th9MO/lHlT56uLsaB15yD426LZasXFsn3KJ5eKvou0LdJ36tRPyZHtL8Y8bTFqttD/6xfHOYc5/s1GlwItciXoDDpaanMrek4qC9KyXhKSxYQ9rrhWr8khBRKhQkoLKxzvpCoTdybTsKDkSb8MfMN5DGWhYR2jSRxmy03xbAIkG0S1mJehm0POe3FTYt0J/qjTEtiCeWKskqQhrep+LO1TFlDN7QiLjheVRPs+LFIFSeLZjf/GopHs5EJVb0pqK8RxFnf5NPLaOkm2/MYTLRSFSyT69p4tUe91VBQxlbBKxSLEr5qPf0ap9UF01IdMy/Wzrq4U6iG2nOHE+ORNLEzqysaVPmwfxlTbpX1N+n06nhWPB2NONWcb73lLSVH/ULttfPWjvonUbeTQb1QBsF4Mo+iObpJNIw755HvKc5JQbyx1NMJcrjIKDfI9FJp4FtEyGRSLwd9OYyQBH2vPnr7LF5vQ9Vo9xLyse5qJK1yKNChD7Cjm5QsTkPdKisa47c1hfRMlcK6LNpknKr+bYoKjaDUtidPZWsPvCbtw6JXxiw6xqk8H1pebIwW83iSyMm8XSEXEZE7s1fFacBbxCovGmIsL8/StJOl0XACZzD+JA2Xei/24/V0gxwxSs9j46Q6Y2JI+P3TKGXJJTkb8lvDVGb65RQqu4RwR/FifC2vV0qJg9iUwRcdsYR3XS6HjGpffOrkJMsmOZPSnKz3OiKux3EeySpVV2l/w3LCQUFyOxYcTw0aQsiEgxhPVoOwr/QbAWX6tl3F8tY1F/5CHlK5KwjZkh+aUbzlwMcMG5dj/HTBs/LMJUmCGY5XgbG0iWhc8CqVw3h+6odqGsADraSwLjQnz8oySRSacncjLwQxDOeL8RnBmLiPWs2fgj0eSRm7JhfewV44cUFtsC2SmqnV658iqhBOvA34GawMPlfYjtqI1K+SEGTkZpDuyG0w61sbreyHnU26ZWurhzeKFgszt7ljP7czfqowhkSNoivP9ZxUG0uHyLJ6h2l+9T1rhO0kLXg6u3SFEZU1mTsREje2h5dkrtQqKqjTaGHTPUnZWTLrTZBbzPUC3GXrSs4r5lKT/JoqqrTxp4lbn5xW5lB/qDq7TJpHpp9WoIOWJdVCv6X4qtiymC/1BuSS1gt+Qe2AvgFRsKBXzW1RSGafclrDmKZWoVntNbTqNDo1wta+nzmwyZfORB+bYG8MhCYx5QZiZFfHa91sBX9GTIbardzwE2o0hRYaf5EehVHiyEtqG8dz74aUk8r1Xs5qGCIbeRdk89NUa+/nO8TgcHfzYpKWTOPnZzpq8LNm5vvu67kZ5gZPjm2QavvXl7MiBjJ+JveA4tczJXYV3uMB4Utll9PnZ3sKENAovcqunnM/j0EF993THQhQ2lrxnp9pntrqoK7EzELS8zkOEDTh+UGlQVxmPj9TkI33Sdj0NN23r2dAgDOET5pACVXtXp41eE7dHft+NEAv531s8LkTIlJsVei9PJMxArJiW0GqvZxBATQo4HcYlR1PX55RqIJBFzWZ77kv51e0aNmxph1Z/sszT5XgmSrPLFO6n4OBn1eYkAqZZxuQuz87UfBMo6ZpcY1fzswwLniuG8Kbtt55z8/cMSDgev51YaH2WZ4wxqHfdxkv+6TWLsby/mqE4lbDp8kgPetNUr/2clX98IyaJPgxyMog/bnDfpr72WQv597swiTenfHZTNz28OagpHNS4Kd/cD+19ePTcpokbPFJz/33td/UfXk7fzn2ifu4/uuBUPdGv8dBaYf1effpGXFRkmXqz54z9WkdDElbn9dQxaHpR6lPszOa69M0uFM088hQqvREs/D3gX+khSdJxH9Zv3soPEAJ+JEfZbjFf2lWpeUnEf4+MNQTK8AFfsPQ+ILl1fsF8/KEZu4X3XPqSZJwLUZ4lJ5kDO6JYh/FJ1a24SnHP/JPsqgyFPzlcKNPPDzqSnGP3BMv2LT4JAA+KqBJifBI5B5oDtp45DCenCpieNwDC+ApFv4AGd0jhsHvGUalmSde7m4BNeGRoZ9kDl+LNL6WgDb2icOXDN8VkYAtTwK+pKRHQESmMQiR6a4xc55YEXOu46NDA+P68ozt0/yMdgDJjqH8DODxffwzw7d9/LP67Q/3o/zu+vvJ8UxJUBY/1sVXav/3O77qQ03+8N1Hfeujs6q+qoP9dBf6bBf8B+4M0qO0e0eDVj0KAfX4DgQrPMAvwz2+4x/e8fDri4+gzNwDlNgxuAz9JIDYn1goghXsHVuBlsEtXLMNY4NiB1CGfqQA0CP1JOM/TENTUBceP8CTR+gRj8yOZoJ7OebxHS4HfxjoBY9dUQziAT+GhxjCO+bmdLoIDXQ/NAUAAOwN92Ba/BRU9UHtt8i8x+H2ep5k87mz17oTZDcnLI4irKp/EjWkWepn9PCzbz9WNZqlvqhrXZlO2T5Qtc8pjQBWDkucUUUR+vc7fPkAlyxYGekB3oIl4Z4kWeWhl4Nt6NQHrjkwnTwYyAceLBID5lTmcBEZNAtsywMvP7EgYDBKD68trN4r8OdU/g+i7t/dkHwF5gxoNhgxCWybykBzTIcQaDGYVmwcseVnJUDxkQHKZJVjnmTpkYUy8Jx+ouRHjn0S6AeGx+rPCk8iHgmg87BQtTOXHLa0QPXDm6a+MxE01XU+AM2CKabEJw6GIg7Y+EADNTBOQNOUDDeAAXBfglEFimFuYzQ5KEaBLBhMFoxFNAXoCo9ANceosgDD1iNQDUOHJOGxBzjDCA8y/STKmCeSpMocyAbkC2KSu7EIhgcJBrI3WH1ngkExAHVgvCqCPOhHln6QgGoaIw2EylgkjzyFh14ZxmXuUaDxsAjYQWFReBLEB0nG0pCAPFmV4K34CGTIoKwyFjbUokErYbiHa+ANp4KYJSjDPvEPwDOBfxRlDIbtxkMBuMyoLLaVjxzwVX7gOFwG9IHiHl6xde4KDYjxjAq/kvDIsxgKJ2AEBBi72QeexggAXQKUAc7KjyJwEBCD8fcRYyo/CMBlGM4prJBADWgbRgZ4wGApivAcrvHvo4A7jwpvwcfhma6uhEdtaFBiHt6g850FBF0fGsQiUemOHtyrQSV43OX5zp/CnkxXhqdV6D0gPECHEh5Ap8AtAhJ5CXcZgCPSnV6L2CERORAGaDJ2jETg3QMWYMctVsXWXcTkQ/+Fa9BbEKAA49QrMt+732HaOsjgRIEDQ3OYNmAyjf0mCd9QNNwI2BsDXLCjBEaDw2LhcSn5mTzMGqbTZKzPYEKAWInBBILgcStcRzmIGPdutiNSwAfsYcsqCJhImgIecrgVVnh4g9j3tpedjZRxz1bBXIAEoSNx0gMHPoCEu8rdXoIa3s0ILgT95m5gcM/h8DgNXYR/wHYIzENnlMATxt0Umytawu4rJ3V1BOCS1LmWFIU7BC4mPEI/xt41h3kkY7Y9vEHrOxMMbT1DZjp+Y6Mhd6YVJEGBdeABPWA4oCdis8HKamd0wculur6NCQS/HP/BwQKISb5TLWAjTGH1pWGY4NkHzD1cDfdQbMOw8aSwHVGlztvHpWEcwbjImG5GfHiD3XemG1QUSwfQBfsBsQDfCRQkLXZ9GGsoOIYiJuqRhv5Lq2BZZBwKgUsvYNOJMWaw9cWjOx5Y8TDYje+gAjS2eA88j4MmIJjmHt40+EtI+clg4X7W/7quwn+pkfIviAk+r/oQqO0YG4fHtvwoNVLnWDOqgHsndpbxxQMWbPXcYUG9n3/f4SfdBU35oCvYmeoCwjsMKsAFuohAgngBW0N8IVX4Ev4+SPef7g30uIeuDP4LNwCCfUaNx8EKA5h9lTJ8+hWR73Vicnce87ssqc7f/0D4Dsofv78jN+sgjU9lXWy/4lDrnz3/+5OvIX16tvVPHooNVm2bHL71DO9PiHoRzockBRk08QFCr5TAm9EJf4yg+xAHZvT7b4b88Pk68WndJOcrlM3C6PzJ10k+y8BfcIj6Zxn4DUz8lJH3J5jkTw8Jf696X9D6l8+d/Krz/3x0/kWmX9b4+4de/oXo/Clsk2L767j/beM+DPi0hId9IXsHIf+j8ND9wrBL4+Qtk3W3OC/3UuCrht8qTQ7fJBLqA5F8mqfqPgLzhXzX/UMx/xSMf9YdrD0/kbx55CBu4APqkaUgvHmA+PWRxan0Bw54y+LEuMpwEO5DaPfActhl5qGg/HoNFXB6lHoC9wi8c/bxHTjs3MM7GoJoERwwgX6ibeyZ4SyB/dLe7SUU+F2Q5/BMA8AD1x9QYHA8+oDTrnf8IcbprrgAX3UIsjhoBI8PqGLe30h3/PmHdwxOIjMMTrO8YyFCpPFriBuyd9iXhPDKftPkdyFBYnDuF3ORz0AEDJ1JmO/vKFuWqUcJz1B0Vy8lAC2oAIp/L/V6Yb8B9FX9oSmzOg9/zSA/9wKumzfjupQRJeN8GJ4yo7v4GQeG8hOeocLZWZzOxNkPlsMBJyfj2Jlmu7krCJQluYvGeRxk4yBExXkEHIvSEs6Lgd5w92ic4x9wRA1RDoXzCV10z4tdmEvzXXgvco9yF4xjhO65BhGCdpCzyNyzUg84Dga8cRKY6zKeODTicX5PxhksjCoAw/1NwJllAWcA3lP6vdOiPM4n4Twzo+J0k/jYJU8ehC69xnR5JgGYJjwyAk6147SliPOCAo/LAJNwqlHsykhd7oGScSFe7oJ0+TmViZkn8jh4v+dyWFHlOJy8wuwUceqclXBOQqIfoCODICX2iQL+dtlUicG5H9ylafycBoxAZN1jQQUuyt1TPB+DTR6eMwUnVHgURfhVuwQfztAKuACD07qY7TijybOYoq4szqyCcQHJchJWGgFTw92T491UJ1zTDE4sMXT3nMN4gny74irGHywYiIzDaVwQNUs9JyteuPud5QYWhO0S65wqicA2nCzGyR2c5OtyyNIDTvcwOL0t4e6BBfPI3zP8OMvE4QQwiytwAs5j87wq8XhGGVtJGs/EMOIjvJXEBwmz7FHCqqjKOFWKs4wgKbgGbuD5GQaXwTPJWAvwhI4A16DY8oN4nzLgu1zzK87fJVvTeX4/Pn/X6PlbePh7bT9WYZj+GrF8+Dng7xR+VCEwers+Xd2fjEO+T7TwyYeJv9n1/52Cqu8b+vxDBTA/2xOg6Trf/P5/xPCzH/z6CsruX2375Ftuv/BriK+C+UdC6uu+Wfi9sSrKU44j/2/l1QvW/1BokR9+w+4b9PwZ1u/Pl1A/9Hc7eAChbDC9L1z8hrzJb6rkFn66LOfFW3//+UHmsx9XfXXcPyz4wWdRv4X7nar8M2T+7xHnz+vD79V3fn+hM0LzP/v13Tup1SEMtz/ukuL8H+vHd7/9y6H0PXdFfru/x3z+i6M/8e3VDzJlP2V7xO/9sd5/ofz5yQ+03vUeeHT68gT0l/R+Oul9xy7+ifk8Af7dt7vh3dd85/unv8f9/IF0lvq2D6sLX/xu+Fc39vbj8O/l+KKEn5b/zHd+sVZ1n0P+Wcv2XsI/nn5/ZPz5cfKNoP/ZyvmZqp8U9H0OzA6j8/hF5PKbVOeHXxk+fKbcw8/pxMv3jL/XKPcPlv3lPpxQeXViuK9I+352husnl6d/PtXLPLIPSH6UH6gH6pHutkIwbx/gBSL02wfspwXYzwntbvU/Svx/EAHh96+kPL2l5YOUFfX87+O14B/7cs2Pa/BugvOvM43fONMogWQDPPPD46VA9CPe8IL/0g2ze/f5N1W3KQaU4JHescFzARpPH+GE/uM7unn3PB3G8w/dU3iGa76jb474KOMtC59Wqj4saQuP4ufxwrA70O/RqN4CsqGJmwM6zdrsI/vZfQ/cp/sepM/te2Af+Z/Y9oC3RMhPFG1z979vUX33givgwuLNQ/IrN15IxO92tPCeD8/Y0w1eq8i8UPjumURM98czWp/0g3qblL92g2/sBswj3+DF9ViOMtdJi8ObbjppingqFCfq4ZoFFehW1VN4ed27bqcVjVeZwqUAOvdEiZ3YhEem2wfWLTHH8wdcN++BJ3poPP+DQYFdxSl83MzLJfdEz8Qd86WdM13X/ESxvzTp2fyIU+K/QEfW9bl0ktOpPH0unfWLNl79vAb9giHv91WDhG7fBe7sWPxyZwVkrCuM9P5aFB8pW7hPjT6xuCQrP+Kfh/sluCMMHmCfODrD02WP+Cfo4HUgOmjPVxhWdW8KP37oDJUo2t2WAprJxCcGFAr/YgB3JKSH+2VXAR5QdFdJ+LLmbNdFXv+TTJVzrPAzU+UcLX/ZZwIQXzRkAOhrp8pZptt/wuC115zNiFy3UfXDOzyzJ9jdAgrhozsWz3u+FPzwhhPBNtgM3uMkfHzXFaQl6Un84PoZ9nOpj+7uONEyh6cWP7yjATptM6C37Ms1nkmWuyXjEh78OmRf7ji+W2d+LyiCzry/wVg8F2Mp8Yln399R3bLzrhxmmiS9uXnl4Mp5Wa8vyU+8ZNM8g2dOP7oTwHbipdAUVuuP7lioLgM/OqI/vGPw7ifeprlu+fLrHdNtosWTy9CCBMCE1ztRxBPbmPkUbkHspn0/vMNr56EFPHMtv97xzxuyoCH+BbPXuzf0rRzckgRFObx/1365Y/D6CZvBbKI/vvuwZHf3CobGGyDkl5c03o5Ev1T86O7Dkt0dgAF9oITXNp7vntsXsTvy8d2HJV+wud++tPF899z+veJHdx+WvGPzhZnsD52SDwtNrl2YHTZhMdpuv34/DYWn5kUZfj0Y9fEOEop7oLp1dqKN/7I83b1hQdNl4eFegZVB7VmPo7pd4Hhly4Mg3S9s9uXKY4EqUML7ew60ALrNS81u6dUzzOcbHvzJ7gqafi5wR+e56h3LZ6C8jHfCQVP4wn7++4xQ9+4NZSvntYFX+PcLvPEF4POdRPCyBsbjOTxA4UUMmCT8t6MIX3isRL+scHhgwda8rFJhoGHqDTzqhYH3K8zC5yvouZzwUpeF/iFLL1BZiX0mqbuyXy6eMbq/vqP6UpF/A/KZws/o0D3stJMitMoEh/05DOSnnyr3Mmqw/Je0UcX/fZ02/jRK6vqAVwfX5/Mv0FkJ20S8/oe1aRhVZOwVYIMIJhz3UOwDdOMDdiHwFkaPoWi8gxxvagIVprsVOXDDeQzeNEl319wDNvN4ARDwG6InhsdrigAYh225gJe84P1PYE66LWW4eclj8E47GW9743AmQezW/0gYMN5X1u0ABPfmLcb/iAL6Bebi6wX0M15SFLW/Lnr+Rg+ax6v18EkfcsZj5xZiIUrEEXIXLHUmWeg8V+7u6oLqd1XAn6DVbvWbgKMrDj9guj8y2+CNbV00LXXRPoyB2POlcT28Rq3byPQ1Bb8Wpezdm4Lvui2JuKSInX8M6uUvNPNln7sA3flVm75Nm8Rfrk3iqzYJr9ok3LVJ+FptgoL3YzV+LkM1E38iPVa9TXR9WT9+3Vv5OygIPjjnMzk/mnoUP5vzq37+5BSQPfci+w9eVB9Al74C+lcIPltff5X7t8odn7wAggJHqOunovxAdTvk8YpfGjuacMtluK8/vsO74QPsWnUJO1wSX0JR+dlsyDZepoyzvJIqdV4R7ta4EXxeR9fWV8jzFDa/yvMbDf3jZ9Po1Ody6NVH2XnhUfxsah46M4VTAuDBvgz9z8MHPOyG887mdwm010sJd2+cUcNDxfN2oHsvp18Sbu+LPvsJL24CL2KwD/er50EJLxP/suqcwl+Nwe+W959BmELf5cV16sJ3+X+hy+NLfNfx+ewd+4Q3w4tdehfbaubh+YIHY4/NCJ3h1/cyXd6ry/B3Z8xQ+Eyc7goDE2D8Z3E4Tz0I+MwOFh/MweO3IrYrnb/42B0u8a47fYXDgwWHNQP/dBvxsbrgWQkBHwuBM7gPONHLYntFdTpHic/53tdktNTRJkvvr4W7O0ph54Vnuw6Cd4N0Jg7HjA/cE/aHBO4Bb/ABUybiPR10ZwoF+gGHcvjkAOwedYeT4V8VnzwEYWZ39gDe4oJPygMmf1mRq3pzTs7Zr/7MN6oyQz1yNvfIfXbCk/l0wlP43IQncz9y7jMTnvgokR3XMHjCk2ve3f0dWsK3EtzuaKp5nhaVdu9wAVz4/oDrtj5yr6W+qApnCM2/XQ2+5QDAXzgZ9eXDCX9/z9r8YGL8VVGkTzVFelEVvmF2nYz5Z5Wh8a6/TmvuVx/MlH86VY7T0NBi98PvQF3oe6RE09k7sGm2/CjevrjOAy+M/sL25X+CjUgvK/a6RZofZ5A+u4D/dSP2pxmnT9c8v1119TMrnt8We1kf9YbA+1IBeFDWZ/J52TPm5+uic9Dw78XX3mmdh3bX1HeYCnyGcDh8Ve13eLr6w6rnssyqn6/cFfm4S9/3NBHJljyV5XkGDAKS4d+Hpe4s/fFFbvn6HOwgKD/h9Xw/fLboq/A+LPt+5RzON65PdwZ+2o/fo3Uu///2rmbJbeMIv4qinHcDYAl6pfIhWSmK96CyStwkF1WxQBK7RBYEWAC4P1Xrg98gT5Cf8sGX3HL0+0R+jOCPAElMz3QPBiCXO/LBNjUNgjPdX//3LPPzc9L1EUvkEe/Ge7+auUzrnENQj7dI34i1rm7C2xKDSfiw5j8/q8JPf87khkVff4EbzFgLQuE4jhoFZxnHZlWFiM6CcvVVuMQv/sxsRgCXX+TVkIj1iXNT7PDmmVdMw2EcgHnu8g33UxITmluC5B8cDw0MAc3CiW68YHevTZAsBOcObe1KvjO59DZaDIHfWX+5vfvdeHEW0tVMXZTrIkiKHRplRcHbr2mgiRuMT6DdPZoBmvKPpeTDhwqSNsWJQMwQLu5LbwMVs19ph7GuUi3JZ65tkcu8m/EOTArY8T5yCpnH8VXFj0S6XX58KqZziV+zmjPBWzz1veltaQgVJWTwWtf3vWXWEtYE/IYhnDXBlI8t22AQiy9TVl5N5x/DGYqOvDML5yGD4li0KfHcmYX379h9NevaZxH5+4eUFrPuEbeuKrY/460ttRGSozNbMl1+dXeVrRatxHo2LNpRwTalvCepMh0KSZLHnH8moc/ltTsv9iaeX3BC/j8+AAqwHgaBoWjPowHDpn1mdKipAAy322A4lzhEThRkMuTGTjZORgDZ4OkUDhvviFDH9I2BJEVjOBfHi0abJ9i8ICNpGzRlI2o+w1+0XBInKVhJwUsqZjbZlMZPJXqOsvWYte/gRk0MeRNCLRTZFowyYFFW+D5+uhhJiJ2E6OxB7ESWPYm+adxrQRQI1cfJMt6HTJlDSZnannSzaWkoskO8QNoMGdi9+CdCAdu3/dJwGEDhkohl5Ce7nhV14USStsgZ2RaRoG0Ovm2FhqbRDg6J9LioRevIxZYsBjM3ZZiFFziJe+HO0+3LYSdyl66TkKjfszIPs9sy9l/No/ZDJwtDkh79feA/cvz4pr2zmWmovpACZ7y/kox6Wh1GPXnQhgqt2b0HPQezJQW8LQO1vi1o7y3WqTxiqSB4mMpr6K+yo39p0UNCRHD3dgEdpXuNZh31wTejh+CbQEc0Pq5zuPhMa6E2IlK6FZIgqsQ1Q66ivO/WZt2EwdbB5bluYD8RKd6GKStI8u7O6OF8CQSfZ7aQaFd/nhep+vqoJXQoAM9wgDCzbMaBm5SRnXynWL6UBFIrMDQErj4SajHgKcie24L1jAQ6RMGKpkX10W8fPzakhnT78+GRMCUP2ITRtoZpLMeVUORMMyCRAXMDDstUrJCSIp4SR2a50aP69eX4qZhK6i1czVAKGIoHaZsOczHajrftJeMZxlvDePX0Kv/3oaKaJOc9xom70Lx32Lx3wGzH8AQ2kVCu5nI892buIRdeEgsn2Zn2oyydLI9OTf1kgw+Os4hSttaNuT2HFLIqY5PHE7KCRNU2Xkw5mpDp9l5pprpyjCpm0uVjPDjS5WPC8jHwnA63hkwXjx1s8RiKm3QF2UhW8vZdRobicV1FpqvIDrGKTN4koZWSES0S0G/WBWS6gEwXkD2PArISWxRUkUEfb/SxC4oDijBpl73YovVA6FZpdYB8sMxnvI7i2D3PQ+LH7p/EGVKgyAD8ImQtxDiCHiB0qGQcKZp2kYkQ4kwFQkRUYRebwn7rQYsaxIFxiF3TlM2Bhi2oC5fkslEpmMyEfS5O2wH22nG8LeZlYHt0t2y6MVAmKEnOFzLYKxnwpVY41lq3dCZNw4CjH2i7vZaou9ROCouNmjggb8bla/4+/4+SqEb7ShwvnIgojCKc5gnj2WwpKYNP+I7BTe1ui79w4TysTwkVris3fpxvqYT/fblwblxC3q0QCW9KKhOvFcVQMhcwNLpUwru68KyNLuQT9zJTIo6mzZFgpY2Mq2re8E7qTxm8wuQRP5zeIrwUyGyhxmGozQJSvSAyPSAoXkOQNHmMTQRNwlolSRiMZ57jhzfZXDbmrZ6cESos3oXW8GQQYs8MTcarAGKbLX/RC5r1+eR6+4t0oy7yXSGx6ZDIpkMSm4K175pP98Sn2FJ+QIcSYU9RjY5ICUJCWFzdBxe0kYvZqnP0VwtMHdsAuKaX2skC7MOYN7hvi43lORjTjkJnPN6LF1agcKsZUbltFgYtf4bFn39LZbIzrH6mtb/+FTxbH+AMhtkMMccbQ7i2wRhwDQfHlLc4XwTa8Du2e72D1dHtVjHToMUa4HcKsVbNTpnDGS4CWlVc8vbW8ZfzbMqwcfoGi2y59bu1wQrhbSJS253DWxFmfjEgV2x4kMpN10BXf5MGO6Vgt3mEGvA6ArzGJvNArxlHZ1de+Cl3w7FzocFrGUQPyjQoLpRiEOOGaqghGpJ/TAyqiwLpouA5JmAOB8kLpvCC65C5PuWRP/jeTZCeaHa25e+HllLvHUCEzjHhckL2GoijU7r9KwHqsuEfSlnT0tUSqepWaepeZQ8OuVA6l3qreFDQ60OgwcYRyNls2Uy2ZBZbOoONzV6TM9fUVidhrvqwhvPsP/shmZPuqdXIfmYTqlHpY37qGEwbw26Vgqyx4oqgs9mSeJmBTZxixs8tozLEnAgTI0HMq2YUOGJshGLlhSVywjL5YBXqS5wHls4Bd1p7V4go0w2M3HsvmPFdwG9/c3JCA9Bzkf9hCfwPC+F/DL68PjlZv/U0XJzeeMl8NTlN7ibhw2kYT0+rG/1Sprpxk9ORt1j67qj8VOTQrqnz66k6qKolR/KaVegUr1FJB71pd9pBz358qVuEPiG/r4WhBs1hvMS5gjKeXHFcnRZmK2Qh3DVZ5W8S3ZRVaipulOx4r89qVapOmDLT8XBY/mQA3PyAbiY97NuRUTqr4Tp9gQ/OwsubUmIniE9iN/Ku9cyGbmc2KHWkhBWImxolCKMFfx4A/rIfYqggfoyZAIMrRzk3epEuYbthK4kRPp0oMqKipiOTmex5b96eGa8+fTxG8cJ4vhIKfcwZv3aISl10j6GtrQFtDWhrAIYr6zlYAxAyaWtAWwNoa+AYxUqNFXAIV7mYtqyKN+2+pzZOV1Ek751YxrgLPEKViaP0ZyLCgpKK1niNDFwdoRcCzPyVjA7jkqXSV+nssK1p0C482uZW1iuMXPcWmVuNy6WHPxOVIHIkI3s71h2sfH/vRQlV1tYQrPqOMdCIS+IFVJISU/i3YDAImtU9MnjHpykzyczxQEXpWDkiaF1+mJUiZhzPFfb5ajHBP2qcrxc+8Pvr69ht7MeB4gfJdQiz6opj0tTYYV20TBROVycvIGK4T12NMea/q4zY0TTLdKIbDDq+6AG2zsECkjj/ARMninMvqOxw2Vz5JfVXviSAI1P/BdTdV1d2l2VZbBKB98MlAutRuVSsIgg2AX4lr9CXTQFBQ1GwyqX5zOzmzTi1cTDcU2OfXDHkIXLvmu9BKMMSEoLFWEJK8amgC7OGBNrmrguoKe3p8FNYTejwatreBCkgfsiev+bC9fFvRvxgcr6Dz2S3zXLA5t+24q92PCbNZ/xe+EKOCkMq4c/TUSe760akIxPepvFFEd8G0A41bsjiRqeCz+Lmy8UNWmybTG23Qgy7Z8TYGK/UG2QEZUeIRgyNGM8PMY7DVChksF+5j9d3bWjB14LfrYvx5+Wmg4FgvIryfXgfEGnx7rg406vepCmuxfFa2TTPCtqur++r3ogEAW9AxJkGa+NE2qYZSEOb1Ru0nVjGYkEHtRPTJpEVhQLnIhpuk35xHHMvSPA4VCXCEMuBFJoqCCuD0w/GqWWLVwpi03zi5t05FoKI0YGkzEKI3CR61BaCthCOzDUYtNKfg371Z+Rmsti7czB1fB1H1KJ/HHHEnJv3anT3DBpOanZN0RGF1iZ3vr3a5NYmt0KT2xy+ffPiLO6imEzrXa13jyN/V9RGtlO8z8paTx6XLogKQv0q3kpQyeK20qZvJb+8StlWIpVRO4VElxqGYvr631++/vJP3HKyehKrqIGYkDFNUtJ7lDAGvb/dav31wvXXmu4To0lguD/Vx+pZOEcZo1///Z9ff/7p679+JFikQC8j1SQdKDcy1zPLtJhqM1NHdvdnK9ZyiNLOzas2+ZcZsxHA98czJ1isxrGbJIhb0Ym3MFKAQHKbEWRcMEDTs+EATc4EBDQ1AAk8epkr0bCwQLWkeesJveEsaHgF/BFy7Bl4ey+Oa0n02E3hQ0QuqowbWTvO/jirmRdq80CbB9o82GMOpxDC3vK+8TRy3Yw74iLhrKVfS7+W/v1IvzcdT4urjDsM3O3OCyjGBeBld33jmJZZ1TLbjBaDnUjqImGm0Xe61bKY/J39URGJzhtZIzd1dEnKbLf1XkaZDez+BcNqIxhWC8GwWgmG1WdAuvrdlZmVjWu59UocW/+zr2D03kRwLXLKxC7O2FPShvxG25AYsRu0ErvBkTYXYbkP7DDCPkA+mWSY5ZibfhNJQziRJCvlwikRRyLjgzYyfjySVqEIflIMT0qF3MOXUSG5ltAMyNylpIjahrZ+j8P6PUQzNgs4jPYiYugu4PU9vM3ljBt5wTIrpjdLj8766UfxNB84GUZJ5HjSxfb2cxJrHaE9tAgtUXyUFhX7dwLuP/Q4MIuIGhueJyFqrBjvexoh5PovWGMuNxZI3nGzdKLsmvYwTDq84oZ88zdpaCbmPnehLhFoEfa97jsWIJnhTcs4kLu7uZBroykZN2iov6oGHLhpHvkk3l9//ul///h733N4KReMs4ZTZ5f7hvducJrcRe70ceq7UXYn7/pa36u7z+Wn2AnWiz9F3uwvO9f6CmSu1cjtLiQNN+t+6nvLd3PPn6VoixlEn62/CuvqbphguXyb3G1c7jpaOtOU5q9eMv+Yi3KMEOPiIbHru9PEnV0m7uIyfpfvgDvj1KiVdOsR3+KvVjJ2/eBht2lk44G3CaEyuCt5WwllAvpvSUhrIpHWJCCtefAAKig1hj7GXm2dVRrPEmfZwZXWovXc9uh1Jx37zTBWHtPC84L6fijeHn77uw+Rs3CrT17/8MP/Ad4yWnY="


TK_DEAD_IDS = [
    "tv_speed_top", "tv_play_speed_top", "tv_spin_top", "tv_system_time",
    "top_container_hide", "tv_top_line1_hide", "tv_title_top_hide", "tv_speed_top_hide",
    "tv_play_speed_top_hide", "tv_MPBS_top_hide", "tv_spin_top_hide",
    "play_time_step", "lv_portrait",
]


def _tk_strip_block(xml, vid):
    """按 id 把整个控件块（含子节点）从 layout 里删掉"""
    key = 'android:id="@+id/%s"' % vid
    i = xml.find(key)
    if i < 0:
        return xml, False
    start = xml.rfind("<", 0, i)
    m = re.match(r"<([\w.:]+)", xml[start:])
    if not m:
        return xml, False
    tag = m.group(1)
    gt = xml.find(">", i)
    if gt < 0:
        return xml, False
    if xml[gt - 1] == "/":
        return xml[:start] + xml[gt + 1:], True
    depth = 0
    pos = start
    pat = re.compile(r"<%s\b|</%s>" % (re.escape(tag), re.escape(tag)))
    while pos < len(xml):
        mm = pat.search(xml, pos)
        if not mm:
            return xml, False
        if mm.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return xml[:start] + xml[mm.end():], True
        else:
            depth += 1
        pos = mm.end()
    return xml, False


TK_PLACEHOLDERS = [
    ("TextView", "danmu_search_ui"),
    ("TextView", "video_track_select"),
    ("TextView", "play_refresh"),
    ("TextView", "play_label"),
    ("TextView", "play_time_start_end_text"),
    ("TextView", "tv_info_name1"),
    ("TextView", "net_play_speed"),
    ("LinearLayout", "tv_screen_display"),
    ("ImageView", "tv_back"),
    ("FrameLayout", "play_speed_3_container"),
    ("com.google.android.exoplayer2.ui.SubtitleView", "exo_subtitle_view"),
    ("com.github.tvbox.osc.subtitle.widget.SimpleSubtitleView", "lyric_view"),
    ("com.owen.tvrecyclerview.widget.TvRecyclerView", "mGridParseView"),
]

CAST_BTN = '        <TextView\n            android:id="@+id/play_cast"\n            android:layout_width="@dimen/vs_60"\n            android:layout_height="@dimen/vs_60"\n            android:layout_marginStart="@dimen/vs_6"\n            android:layout_marginLeft="@dimen/vs_6"\n            android:layout_marginEnd="@dimen/vs_6"\n            android:layout_marginRight="@dimen/vs_6"\n            android:background="@drawable/button_dialog_vod"\n            android:drawableTop="@drawable/tvx_cast"\n            android:focusable="true"\n            android:gravity="center"\n            android:text=""\n            android:textColor="@android:color/white"\n            android:textSize="0sp" />\n'




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
    files = glob.glob(os.path.join(res, "layout", "*.xml")) + glob.glob(os.path.join(res, "drawable*", "*.xml")) + glob.glob(os.path.join(res, "anim", "*.xml")) + glob.glob(os.path.join(res, "values*", "*.xml"))
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

    pf = os.path.join(src, "app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java")
    if os.path.exists(pf):
        t = open(pf, encoding="utf-8", errors="ignore").read()
        n0 = t
        t = t.replace('mController.mLandscapePortraitBtn.setText("竖屏");', ';')
        t = t.replace('mController.mLandscapePortraitBtn.setText("横屏");', ';')
        if t != n0:
            open(pf, "w", encoding="utf-8").write(t)
            print("+ PlayFragment 横竖屏文字调用已改掉（他 layout 用图标表达）")

    # 删掉他布局里「界面有、代码根本不驱动」的块
    removed = []
    for vid in TK_DEAD_IDS:
        lay2, ok = _tk_strip_block(lay2, vid)
        if ok:
            removed.append(vid)
    print("+ 已删掉 %d 个无驱动控件块：%s" % (len(removed), ", ".join(removed)))

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
        ("backBtn = findViewById(R.id.tv_back);", "backBtn = findViewById(R.id.tvBackButton);"),
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
             ("TextView mNextBtn;", "LinearLayout mNextBtn;"),
             ("TextView mPlayerRetry;", "LinearLayout mPlayerRetry;"),
             ("public TextView mLandscapePortraitBtn;", "public LinearLayout mLandscapePortraitBtn;"),
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

    # 横竖屏按钮在他 layout 里只有图标没有文字控件：去掉文字切换调用，避免类型不匹配
    js = js.replace('if (showButton) mLandscapePortraitBtn.setText(isPortrait ? "横屏" : "竖屏");',
                    'if (showButton) { }')
    js = js.replace('mLandscapePortraitBtn.setText("竖屏");', ';')
    js = js.replace('mLandscapePortraitBtn.setText("横屏");', ';')
    js = re.sub(r"\n\s*mScreenDisplay\.setTextColor\([^;]*\);", "", js)
    print("+ 倍速/比例/播放器文字改到他 layout 里的小徽标")

    # 片头/片尾：他的 layout 里就是显示时间（00:00），不要汉字
    js = js.replace('mPlayerTimeStartBtn.setText(start == 0 ? "片头" : stringForTime(start * 1000));',
                    'mPlayerTimeStartBtn.setText(stringForTime(start * 1000));')
    js = js.replace('mPlayerTimeSkipBtn.setText(end == 0 ? "片尾" : stringForTime(end * 1000));',
                    'mPlayerTimeSkipBtn.setText(stringForTime(end * 1000));')
    # 右上码率：数字与单位分开（他的 tv_MPBS_top 专门放单位），避免出现 "7Kb/sMbps"
    tk_speed_java = ('{ String _tkRaw = speedBps; '
                     'String _tkNum = _tkRaw.replaceAll("[^0-9.]+", ""); '
                     'String _tkUnit = _tkRaw.replaceAll("[0-9.]+", ""); '
                     'mPlayLoadNetSpeed.setText(_tkNum); '
                     'TextView _tkMbTop = (TextView) findViewById(R.id.tv_MPBS_top); '
                     'if (_tkMbTop != null && _tkUnit.length() > 0) _tkMbTop.setText(_tkUnit); }')
    js = js.replace('mPlayLoadNetSpeed.setText(speed);', tk_speed_java)
    print("+ 片头/片尾改为显示时间，码率数字与单位已分离")

    open(vc, "w", encoding="utf-8").write(js)
    _tk_autofill(res)
    print("--- 移植完成：布局=他的，资源=他的，代码只改绑定与类型 ---")


def tk_patch_crash():
    """崩溃取证：异常堆栈写文件 + Toast 显示一行定位（只为定位这次闪退，定位后可撤）"""
    ap = os.path.join(SRC, "app/src/main/java/com/github/tvbox/osc/base/App.java")
    if not os.path.exists(ap):
        print("  !! 未找到 App.java，崩溃取证未注入")
        return
    t = open(ap, encoding="utf-8", errors="ignore").read()
    if "TKBOX_CRASH" in t:
        print("· 崩溃取证已存在，跳过")
        return
    anchor = "super.onCreate();"
    if anchor not in t:
        print("  !! 未找到 onCreate 锚点，崩溃取证未注入")
        return
    handler = r'''

        try {
            final Thread.UncaughtExceptionHandler tkDefHandler = Thread.getDefaultUncaughtExceptionHandler();
            Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
                @Override
                public void uncaughtException(Thread t, Throwable e) {
                    String tkFull = "";
                    try {
                        java.io.StringWriter tkSw = new java.io.StringWriter();
                        e.printStackTrace(new java.io.PrintWriter(tkSw));
                        tkFull = tkSw.toString();
                        android.util.Log.e("TKBOX_CRASH", tkFull);
                        try {
                            java.io.File tkDir = getExternalFilesDir(null);
                            if (tkDir != null) {
                                java.io.FileOutputStream tkFo = new java.io.FileOutputStream(new java.io.File(tkDir, "crash.txt"));
                                tkFo.write(tkFull.getBytes("UTF-8"));
                                tkFo.flush();
                                tkFo.close();
                            }
                        } catch (Throwable ignored2) { }
                        String tkShow = e.getClass().getName() + " | " + e.getMessage();
                        int tkI = tkFull.indexOf("at com.github.tvbox");
                        if (tkI > 0) {
                            String tkTail = tkFull.substring(tkI, Math.min(tkFull.length(), tkI + 160)).replace("\n", "  ");
                            tkShow = tkShow + " || " + tkTail;
                        }
                        final String tkFinal = tkShow;
                        new android.os.Handler(android.os.Looper.getMainLooper()).post(new Runnable() {
                            @Override
                            public void run() {
                                android.widget.Toast.makeText(App.this, tkFinal, android.widget.Toast.LENGTH_LONG).show();
                            }
                        });
                        Thread.sleep(4000);
                    } catch (Throwable ignored) { }
                    if (tkDefHandler != null) tkDefHandler.uncaughtException(t, e);
                }
            });
        } catch (Throwable ignored) { }
'''
    t = t.replace(anchor, anchor + handler, 1)
    open(ap, "w", encoding="utf-8").write(t)
    print("+ 崩溃取证已注入（崩溃时弹英文 Toast + 写 crash.txt）")


def main():
    print("=== TVBoxOS 定制增强 v37（takagen99 整份移植 / 内置订阅保留） ===")
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
    tk_patch_crash()
    print("=== 汇总：全部成功 ===")


if __name__ == "__main__":
    main()
