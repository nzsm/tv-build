#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TVBox 底部菜单：只改图标 + 图标与汉字的对齐

用法：python3 tvbox_ext.py <源码目录> <默认订阅地址> <APP名称>

只做三件事：
  1. 换图标（takagen 那套，统一 26dp、视觉尺寸归一）
  2. 汉字统一 10dp 细体，和图标左右居中
  3. 每个按钮图标位等高，所以图标与图标、汉字与汉字各自对齐

不动：播放内核、按钮增删逻辑、进度条、底板。Java 只改 VodController 控制条两处。
"""
import os, sys, re, json, zlib, base64
import xml.etree.ElementTree as ET

SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
DEF_URL = sys.argv[2] if len(sys.argv) > 2 else ''
APP_NAME = sys.argv[3] if len(sys.argv) > 3 else '影道舱定制版'
VER = 'VER-20261117-E'


# ---------- 图标素材（数据） ----------
TK_BUNDLE = "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"
ICON_SIZE = '26dp'
BTN_ICON = {
    'play_ijk': 'tk_space',
    'play_pre':            'v_prev',
    'play_next':           'v_next',
    'play_retry':          'v_replay_play',
    'play_refresh':        'v_replay',
    'play_scale':          'v_aspect',
    'play_speed':          'v_ffwd',
    'play_player':         'v_type',
    'play_time_reset':     'play_skip',
    'zimu_select':         'v_subtitle',
    'audio_track_select':  'v_audio',
    'danmu_setting':       'v_danmu',
    'landscape_portrait':  'htov',
    'screen_display':      'ic_clock',
    'play_cast':           'v_cast',
}
IMG_SRC = {'tv_back': 'v_back', 'tv_lock': 'tk_unlock'}
HTVO_B64 = ('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')
SPACE_B64 = 'iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAAJElEQVR42u3BMQEAAADCoPVP7WkJoAAAAAAAAAAAAAAAAAAAbjh8AAFmzvMFAAAAAElFTkSuQmCC'
ICON_FIX = {
    'v_prev': (1.494, -0.037, 0.000),   # scale, tx, ty
    'v_next': (1.500, 0.000, 0.000),   # scale, tx, ty
    'v_replay': (0.930, -0.047, 0.581),   # scale, tx, ty
    'v_aspect': (0.818, 0.000, 0.000),   # scale, tx, ty
    'v_ffwd': (1.071, -0.428, 0.000),   # scale, tx, ty
    'v_type': (0.818, 0.000, 0.000),   # scale, tx, ty
    'v_cast': (0.818, 0.000, 0.000),   # scale, tx, ty
    'v_subtitle': (0.900, 0.000, 0.000),   # scale, tx, ty
    'v_audio': (1.000, 0.000, 0.000),   # scale, tx, ty
    'v_danmu': (0.750, 0.000, 0.351),   # scale, tx, ty
    'ic_clock': (0.857, -0.214, 0.428),   # scale, tx, ty
    'v_back': (0.957, 0.383, 0.000),   # scale, tx, ty
    'tk_unlock': (0.857, 0.000, 0.428),   # scale, tx, ty
    'play_skip': (0.763, 0.000, 0.000),   # scale, tx, ty
    'v_replay_play': (0.930, -0.047, 0.581),   # scale, tx, ty
}

# ---------- 工具 ----------
def jpath(*p):
    return os.path.join(SRC, *p)

def write(p, t):
    open(p, 'w', encoding='utf-8').write(t)

def read(p):
    return open(p, encoding='utf-8').read()

def shrink(xml):
    """把 vector 的 width/height 统一改成 ICON_SIZE"""
    xml = re.sub(r'android:width="[^"]*"', 'android:width="%s"' % ICON_SIZE, xml)
    xml = re.sub(r'android:height="[^"]*"', 'android:height="%s"' % ICON_SIZE, xml)
    return xml

def make_replay_icon():
    # 重播图标 = 完整圆环（描边画）+ 中间播放三角
    p = os.path.join(SRC, 'app/src/main/res/drawable/v_replay_play.xml')
    if os.path.exists(p):
        return
    s = ('<vector xmlns:android="http://schemas.android.com/apk/res/android"' + chr(10)
         + '    android:width="24dp" android:height="24dp"' + chr(10)
         + '    android:viewportWidth="24" android:viewportHeight="24"' + chr(10)
         + '    android:tint="#FFFFFF">' + chr(10)
         + '    <path android:strokeColor="@android:color/white" android:strokeWidth="2.2"'
         + ' android:fillColor="@android:color/transparent"'
         + ' android:pathData="M12,5 A7,7 0 1 1 11.99,5"/>' + chr(10)
         + '    <path android:fillColor="@android:color/white" android:pathData="M9.85,8.4 L16.25,12.0 L9.85,15.6 Z"/>' + chr(10)
         + '</vector>')
    write(p, s)
    print('  + 重播图标已生成：完整圆环 + 居中播放三角')

def make_extra_icons():
    # 1) 横竖屏：takagen 原图 htov（54px@3x = 18dp）
    d = os.path.join(SRC, 'app/src/main/res/drawable-xxhdpi')
    if not os.path.isdir(d):
        os.makedirs(d)
    p = os.path.join(d, 'htov.png')
    if not os.path.exists(p):
        import base64
        write_bytes(p, base64.b64decode(HTVO_B64))
        print('  + 横竖屏图标已铺：htov.png（takagen 原图）')
    # 2) 投屏：自绘 cast 图标
    p2 = os.path.join(SRC, 'app/src/main/res/drawable/v_cast.xml')
    if not os.path.exists(p2):
        s = ('<vector xmlns:android="http://schemas.android.com/apk/res/android"' + chr(10)
             + '    android:width="24dp" android:height="24dp"' + chr(10)
             + '    android:viewportWidth="24" android:viewportHeight="24"' + chr(10)
             + '    android:tint="#FFFFFF">' + chr(10)
             + '    <path android:fillColor="@android:color/white" android:pathData="M1,18v3h3c0,-1.66 -1.34,-3 -3,-3zM1,14v2c2.76,0 5,2.24 5,5h2c0,-3.87 -3.13,-7 -7,-7zM1,10v2c4.97,0 9,4.03 9,9h2c0,-6.08 -4.93,-11 -11,-11zM21,3L3,3c-1.1,0 -2,0.9 -2,2v3h2L3,5h18v14h-7v2h7c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2z"/>' + chr(10)
             + '</vector>')
        write(p2, s)
        print('  + 投屏图标已生成：v_cast.xml')

def write_bytes(p, data):
    open(p, 'wb').write(data)

def normalize_icons():
    # 把每个图标的实际图形统一成 18/24 的视觉尺寸，解决大小不一
    for name, (sc, tx, ty) in ICON_FIX.items():
        p = jpath('app/src/main/res/drawable/%s.xml' % name)
        if not os.path.isfile(p):
            continue
        t = read(p)
        if '<group' in t:
            continue
        vw = re.search(r'android:viewportWidth="([^"]+)"', t)
        vh = re.search(r'android:viewportHeight="([^"]+)"', t)
        W = float(vw.group(1)) if vw else 24.0
        H = float(vh.group(1)) if vh else 24.0
        k = max(W, H) / 24.0
        px = round(W / 2.0, 3)
        py = round(H / 2.0, 3)
        sc = sc * 1.222   # 目标 22/24：图标内容 ≈ 23.8dp，不小于两个汉字宽
        g = ('<group android:pivotX="%s" android:pivotY="%s"' % (px, py) + chr(10)
             + '        android:scaleX="%s" android:scaleY="%s"' % (round(sc, 3), round(sc, 3)) + chr(10)
             + '        android:translateX="%s" android:translateY="%s">' % (round(tx * k * 1.222, 3), round((ty - 1.5) * k * 1.222, 3)))
        t = t.replace('<path', g + chr(10) + '        <path', 1)
        idx = t.rfind('</vector>')
        t = t[:idx] + '</group>' + chr(10) + t[idx:]
        write(p, t)
    print('  + 图标视觉尺寸已统一（%d 个）' % len(ICON_FIX))

def add_space_icon():
    # 「硬解」没有图标，用一个透明占位图占住图标位置，使文字与其他按钮齐平
    p = jpath('app/src/main/res/drawable-xxhdpi/tk_space.png')
    d = os.path.dirname(p)
    if not os.path.isdir(d):
        os.makedirs(d)
    open(p, 'wb').write(base64.b64decode(SPACE_B64))
    print('  + 已生成透明占位图 tk_space.png')

def stamp_replay_icon():
    # 最后统一重播图标：圆环与三角都占满画幅，与其他图标视觉等大
    p = os.path.join(SRC, 'app/src/main/res/drawable/v_replay_play.xml')
    s = ('<vector xmlns:android="http://schemas.android.com/apk/res/android"' + chr(10)
         + '    android:width="26dp" android:height="26dp"' + chr(10)
         + '    android:viewportWidth="24" android:viewportHeight="24"' + chr(10)
         + '    android:tint="#FFFFFF">' + chr(10)
         + '    <path android:strokeColor="@android:color/white" android:strokeWidth="2.6"'
         + ' android:fillColor="@android:color/transparent"'
         + ' android:pathData="M12,2.2 A9.8,9.8 0 1 1 11.99,2.2"/>' + chr(10)
         + '    <path android:fillColor="@android:color/white" android:pathData="M9.0,8.6 L16.2,12.0 L9.0,15.4 Z"/>' + chr(10)
         + '</vector>')
    write(p, s)
    print('  + 重播图标已统一（外径19.6 与上集下集等高）')

# ======================= 布局：只动图标与文字排版 =======================
LAY = 'app/src/main/res/layout/player_vod_control_view.xml'
A = '{http://schemas.android.com/apk/res/android}'
NS = 'http://schemas.android.com/apk/res/android'

RENAME = {'play_pre': '上集', 'play_next': '下集', 'landscape_portrait': '旋屏'}
PAD_LR, PAD_TB, ICON_H, TXT = '6dp', '10dp', '26dp', '10dp'

def _pm(root):
    return {c: p for p in root.iter() for c in p}

def _find(root, rid):
    for e in root.iter():
        if e.get(A + 'id') == '@+id/' + rid:
            return e

def _set(e, **kw):
    m = {'w': 'layout_width', 'h': 'layout_height', 'gravity': 'gravity',
         'lg': 'layout_gravity', 'vis': 'visibility'}
    for k, v in kw.items():
        e.set(A + m[k], v)

def _btn(e, icon):
    """按钮统一：图标位 26dp、字 10dp 细体、图标与汉字左右居中、上下留白一致"""
    _set(e, w='wrap_content', h='wrap_content', gravity='top|center_horizontal')
    e.set(A + 'textSize', TXT)
    e.set(A + 'fontFamily', 'sans-serif-light')
    e.set(A + 'includeFontPadding', 'false')
    e.set(A + 'singleLine', 'true')
    e.set(A + 'textColor', '@android:color/white')
    e.set(A + 'drawablePadding', '0dp')
    e.set(A + 'paddingLeft', PAD_LR)
    e.set(A + 'paddingTop', PAD_TB)
    e.set(A + 'paddingRight', PAD_LR)
    e.set(A + 'paddingBottom', PAD_TB)
    if icon:
        e.set(A + 'drawableTop', '@drawable/' + icon)

def write_space_xml():
    '''透明占位：26dp 矢量，正好等于图标格高度（用 png 会因密度换算错位）'''
    p = jpath('app/src/main/res/drawable/tk_space.xml')
    s = ('<vector xmlns:android="http://schemas.android.com/apk/res/android"' + chr(10)
         + '    android:width="%s" android:height="%s"' % (ICON_SIZE, ICON_SIZE) + chr(10)
         + '    android:viewportWidth="26" android:viewportHeight="26">' + chr(10)
         + '    <path android:fillColor="#00000000" android:pathData="M0,0 L26,0 L26,26 L0,26 Z" />' + chr(10)
         + '</vector>')
    write(p, s)
    print('  + 透明占位图 tk_space.xml（严格 26dp）')




def stack_timepair():
    """片头/片尾：上格 26dp 放时间（当图标用），下格 10dp 放汉字 —— 与别的按钮同构"""
    path = jpath(LAY)
    tree = ET.parse(path)
    root = tree.getroot()
    pm = _pm(root)
    for tid, sid, txt in (('play_time_start', 'tk_slot_start', '片头'),
                          ('play_time_end', 'tk_slot_end', '片尾')):
        node = _find(root, tid)
        if node is None or node.tag != 'TextView':
            continue
        par = pm[node]
        idx = list(par).index(node)
        box = ET.Element('LinearLayout')
        box.set(A + 'orientation', 'vertical')
        box.set(A + 'gravity', 'center_horizontal')
        _set(box, w='wrap_content', h='wrap_content')
        box.set(A + 'paddingLeft', PAD_LR)
        box.set(A + 'paddingTop', PAD_TB)
        box.set(A + 'paddingRight', PAD_LR)
        box.set(A + 'paddingBottom', PAD_TB)
        slot = ET.SubElement(box, 'TextView')
        slot.set(A + 'id', '@+id/' + sid)
        slot.set(A + 'layout_height', ICON_H)
        slot.set(A + 'gravity', 'center')
        slot.set(A + 'textSize', '15dp')
        slot.set(A + 'fontFamily', 'sans-serif-light')
        slot.set(A + 'includeFontPadding', 'false')
        slot.set(A + 'singleLine', 'true')
        slot.set(A + 'textColor', '@android:color/white')
        slot.set(A + 'text', '00:00')
        _set(slot, w='wrap_content')
        par.remove(node)
        for k in ('paddingLeft', 'paddingTop', 'paddingRight', 'paddingBottom',
                  'minHeight', 'lineSpacingExtra', 'drawableTop', 'drawablePadding'):
            node.attrib.pop(A + k, None)
        _set(node, w='wrap_content', h='wrap_content', gravity='top|center_horizontal')
        node.set(A + 'textSize', TXT)
        node.set(A + 'singleLine', 'true')
        node.set(A + 'text', txt)
        box.append(node)
        par.insert(idx, box)
    tree.write(path, encoding='utf-8', xml_declaration=True)
    print('  + 片头/片尾改为两行：上格 26dp 时间（当图标对齐）、下格 10dp 汉字')


PURGE = ('    private void purgeSearchViews(android.view.View v) {' + chr(10)
         + '        if (!(v instanceof android.view.ViewGroup)) return;' + chr(10)
         + '        android.view.ViewGroup g = (android.view.ViewGroup) v;' + chr(10)
         + '        for (int i = g.getChildCount() - 1; i >= 0; i--) {' + chr(10)
         + '            android.view.View c = g.getChildAt(i);' + chr(10)
         + '            if (c instanceof android.widget.TextView) {' + chr(10)
         + '                CharSequence cs = ((android.widget.TextView) c).getText();' + chr(10)
         + '                String str = cs == null ? "" : cs.toString();' + chr(10)
         + '                if (str.contains("搜") || str.contains("视轨")) { g.removeView(c); continue; }' + chr(10)
         + '            }' + chr(10)
         + '            purgeSearchViews(c);' + chr(10)
         + '        }' + chr(10)
         + '    }' + chr(10) + chr(10))

HELPER = ('    private CharSequence buildTimeLabel(String time, String label) {' + chr(10)
          + '        int sid = "片头".equals(label) ? R.id.tk_slot_start : R.id.tk_slot_end;' + chr(10)
          + '        android.widget.TextView slot = findViewById(sid);' + chr(10)
          + '        if (slot != null) slot.setText(time);' + chr(10)
          + '        return label;' + chr(10)
          + '    }' + chr(10) + chr(10))


def patch_java():
    ph = jpath('app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java')
    if not os.path.isfile(ph):
        print('  !! 找不到 VodController.java')
        sys.exit(1)
    t = read(ph)

    # ① 时间交给上格，汉字留在下格
    a1 = 'mPlayerTimeStartBtn.setText(start == 0 ? "片头" : stringForTime(start * 1000));'
    b1 = 'mPlayerTimeStartBtn.setText(buildTimeLabel(start == 0 ? "00:00" : stringForTime(start * 1000), "片头"));'
    a2 = 'mPlayerTimeSkipBtn.setText(end == 0 ? "片尾" : stringForTime(end * 1000));'
    b2 = 'mPlayerTimeSkipBtn.setText(buildTimeLabel(end == 0 ? "00:00" : stringForTime(end * 1000), "片尾"));'
    assert a1 in t and a2 in t, '片头片尾 setText 锚点没找到'
    t = t.replace(a1, b1, 1).replace(a2, b2, 1)

    # ② 插两个方法
    anchor = '    private String getPlayerShortName(int playerType) {'
    assert anchor in t, 'getPlayerShortName 锚点没找到'
    t = t.replace(anchor, HELPER + PURGE + anchor, 1)

    # ③ 每次刷新搜弹幕按钮时，顺手把带"搜/视轨"字样的控件从界面上摘掉
    a3 = ('    public void updateDanmuSearchUiBtn() {' + chr(10)
          + '        if (mDanmuSearchUiBtn == null) return;')
    assert a3 in t, 'updateDanmuSearchUiBtn 锚点没找到'
    t = t.replace(a3, a3 + chr(10) + '        purgeSearchViews(mBottomRoot);', 1)

    # ④ 配置晚到时再补两次（1.5 秒 / 5 秒）
    a4 = '        updateDanmuSearchUiBtn();'
    assert a4 in t, '调用点没找到'
    t = t.replace(a4, a4 + chr(10)
                  + '        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() { public void run() { purgeSearchViews(mBottomRoot); } }, 1500);' + chr(10)
                  + '        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() { public void run() { purgeSearchViews(mBottomRoot); } }, 5000);', 1)

    write(ph, t)
    print('  + Java 补丁 2 项：片头片尾时间分格、搜弹幕/视轨物理摘除')


def style_layout():
    ET.register_namespace('android', NS)
    path = jpath(LAY)
    tree = ET.parse(path)
    root = tree.getroot()
    pm = _pm(root)

    group = _find(root, 'play_btn_group')
    if group is None:
        print('!! 找不到 play_btn_group')
        sys.exit(1)

    # ① 整排居中：滚动容器撑满 + 组内居中（不拆底座结构）
    hsv = pm.get(group)
    if hsv is not None and hsv.tag == 'HorizontalScrollView':
        _set(hsv, w='match_parent')
        hsv.set(A + 'fillViewport', 'true')
        hsv.set(A + 'scrollbars', 'none')
        print('  + 滚动容器撑满视口，整排才有"居中"的基准')
    _set(group, w='match_parent', gravity='center')

    # ② 上集放到下集左边（只是换个顺序）
    pre, nxt = _find(root, 'play_pre'), _find(root, 'play_next')
    if pre is not None and nxt is not None and list(group).index(pre) > list(group).index(nxt):
        j = list(group).index(nxt)
        group.remove(pre)
        group.insert(j, pre)
        print('  + 上集移到下集左边')

    # ③ 视轨、搜弹幕：空占位（0dp + gone，纯布局，不动代码）
    for rid in ('video_track_select', 'danmu_search_ui'):
        e = _find(root, rid)
        if e is not None:
            _set(e, w='0dp', h='0dp', vis='gone')
    print('  + 视轨、搜弹幕压成 0dp 并隐藏')

    # ④ 文字（只是字）
    for rid, txt in RENAME.items():
        e = _find(root, rid)
        if e is not None:
            e.set(A + 'text', txt)

    # ④ 每个按钮：图标 + 统一的字
    n = 0
    for e in list(group):
        if e.tag != 'TextView':
            continue
        rid = (e.get(A + 'id') or '').replace('@+id/', '')
        _btn(e, BTN_ICON.get(rid))
        n += 1
    print('  + 按钮 %d 个：图标位 %s、汉字 %s、左右居中' % (n, ICON_H, TXT))


    tree.write(path, encoding='utf-8', xml_declaration=True)


# ======================= 入口 =======================
def main():
    print('*** 脚本版本 %s ***' % VER)
    print('=== 只做图标 + 图标与汉字对齐（不碰其它） ===')
    print('源码:', SRC)

    ddir = jpath('app/src/main/res/drawable')
    os.makedirs(ddir, exist_ok=True)
    files = json.loads(zlib.decompress(base64.b64decode(TK_BUNDLE)).decode('utf-8'))
    cnt = 0
    for path, meta in files.items():
        name = path.split('/')[-1]
        if name.endswith('.png'):
            continue
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
        cnt += 1
    print('  + 图标铺入 %d 个' % cnt)

    make_replay_icon()
    make_extra_icons()
    write_space_xml()
    normalize_icons()

    n = 0
    for f in sorted(os.listdir(ddir)):
        if not (f.startswith('v_') and f.endswith('.xml')):
            continue
        fp = os.path.join(ddir, f)
        t = open(fp, encoding='utf-8').read()
        t2 = re.sub(r'android:width="[^"]*"', 'android:width="%s"' % ICON_SIZE, t, count=1)
        t2 = re.sub(r'android:height="[^"]*"', 'android:height="%s"' % ICON_SIZE, t2, count=1)
        if t2 != t:
            open(fp, 'w', encoding='utf-8').write(t2)
            n += 1
    print('  + 图标本体尺寸钉到 %s（%d 个）' % (ICON_SIZE, n))

    style_layout()
    stack_timepair()
    patch_java()
    print('-' * 46)
    print('=== 完成 ===')


if __name__ == '__main__':
    main()
