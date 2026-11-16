#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tvbox_ext.py — 统一小图标版（图标 14dp，按钮只加图标不换结构）

用法（与 workflow 现有调用一致）:
    python3 tvbox_ext.py <源码目录> [订阅地址] [APP名称]

做的事：
  1. 铺入 takagen99 的 14 个图标，尺寸统一改成 14dp（原图 24dp）
  2. 给播放控制栏的 17 个文字按钮加「图标在上」的 drawableTop，间距 0
  3. 返回箭头 / 锁图标换成 takagen 的（ImageView 尺寸不变）

尺寸算清楚了：
  原按钮 = 单行文字，高约 25dp
  加 24dp 图标 + 2dp 间距 → 51dp（约 2.0~2.3 倍，这就是上次菜单被撑坏的原因）
  改成 14dp 图标 + 0 间距 → 39dp 左右，只高一点点，宽度完全不变（不会横向溢出）

不做的：不改 Java、不加订阅/DNS/名称、不碰播放内核、不换布局文件。
"""
import os, re, sys, base64, zlib, json

SRC = sys.argv[1] if len(sys.argv) > 1 else '.'
DEF_URL = sys.argv[2] if len(sys.argv) > 2 else ''
APP_NAME = sys.argv[3] if len(sys.argv) > 3 else ''

ICON_SIZE = '14dp'
TK_BUNDLE = "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"

BTN_ICON = {
    'play_pre':            'v_prev',
    'play_next':           'v_next',
    'play_retry':          'v_replay',
    'play_refresh':        'v_replay',
    'play_scale':          'v_aspect',
    'play_speed':          'v_ffwd',
    'play_player':         'v_type',
    'play_time_start':     'vod_skip',
    'play_time_end':       'vod_skip',
    'play_time_reset':     'v_replay',
    'zimu_select':         'v_subtitle',
    'audio_track_select':  'v_audio',
    'video_track_select':  'v_audio',
    'danmu_setting':       'v_danmu',
    'danmu_search_ui':     'v_danmu',
    'landscape_portrait':  'v_aspect',
    'screen_display':      'ic_clock',
}
IMG_SRC = {'tv_back': 'v_back', 'tv_lock': 'tk_unlock'}

fails = []


def jpath(*p):
    return os.path.join(SRC, *p)


def read(p):
    return open(p, encoding='utf-8').read()


def shrink(xml):
    """把 vector 的 width/height 统一改成 ICON_SIZE"""
    xml = re.sub(r'android:width="[^"]*"', 'android:width="%s"' % ICON_SIZE, xml)
    xml = re.sub(r'android:height="[^"]*"', 'android:height="%s"' % ICON_SIZE, xml)
    return xml


def main():
    print('=== 统一小图标版（图标 %s）===' % ICON_SIZE)
    print('源码:', os.path.abspath(SRC))
    files = json.loads(zlib.decompress(base64.b64decode(TK_BUNDLE)).decode('utf-8'))

    ddir = jpath('app/src/main/res/drawable')
    os.makedirs(ddir, exist_ok=True)
    for path, meta in files.items():
        name = path.split('/')[-1]
        if name == 'icon_unlock.xml':
            name = 'tk_unlock.xml'
        c = meta['c']
        try:
            raw = c.encode('latin-1') if isinstance(c, str) else c
        except UnicodeEncodeError:
            raw = c.encode('utf-8')
        txt = raw.decode('utf-8', 'ignore')
        out = shrink(txt).encode('utf-8') if txt.lstrip().startswith(('<?xml', '<vector')) else raw
        open(os.path.join(ddir, name), 'wb').write(out)
        print('  + drawable/' + name)

    p = jpath('app/src/main/res/layout/player_vod_control_view.xml')
    if not os.path.isfile(p):
        print('!! 找不到 player_vod_control_view.xml')
        sys.exit(1)
    s = read(p)
    before = len(s)
    hit, miss = 0, []

    for vid, icon in BTN_ICON.items():
        pat = re.compile(r'(<TextView[^>]*?android:id="@\+id/%s"[^>]*?)(/?)>' % re.escape(vid), re.S)
        m = pat.search(s)
        if not m:
            miss.append(vid)
            continue
        if 'android:drawableTop' in m.group(0):
            continue
        s = s[:m.start()] + m.group(1) + '\n        android:drawableTop="@drawable/%s"\n        android:drawablePadding="0dp"' % icon + ' />' + s[m.end():]
        hit += 1

    for vid, icon in IMG_SRC.items():
        pat = re.compile(r'(android:id="@\+id/%s"[^>]*?android:src="@drawable/)(\w+)"' % re.escape(vid), re.S)
        s2, n = pat.subn(lambda mm: mm.group(1) + icon + '"', s, count=1)
        if n:
            s = s2; hit += 1
        else:
            pat2 = re.compile(r'(android:src="@drawable/)(\w+)("(?:[^>]*?)android:id="@\+id/%s")' % re.escape(vid), re.S)
            s2, n2 = pat2.subn(lambda mm: mm.group(1) + icon + mm.group(3), s, count=1)
            if n2:
                s = s2; hit += 1
            else:
                miss.append(vid)

    open(p, 'w', encoding='utf-8').write(s)
    print('  + 图标已加到 %d 处（%d 个按钮）' % (hit, hit))
    if miss:
        print('  · 未匹配（保留原样）: ' + ', '.join(miss))

    print('-' * 50)
    if fails:
        print('!! 失败项: ' + ', '.join(fails))
        sys.exit(1)
    print('=== 完成：Java 零改动，布局只加图标属性 ===')


if __name__ == '__main__':
    main()
