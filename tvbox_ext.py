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

ICON_SIZE = '26dp'
TK_BUNDLE = "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"

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

fails = []


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




def _block_span(text, idx):
    """从 idx 处的开标签开始，返回 (start, end) 覆盖整个标签块"""
    open_end = text.find('>', idx) + 1
    tag = re.match(r'<(\w+)', text[idx:]).group(1)
    depth, pos = 1, open_end
    while depth > 0:
        m = re.search(r'<(/?)(%s)\b' % tag, text[pos:])
        if not m:
            return (idx, open_end)
        if m.group(1) == '/':
            depth -= 1
            if depth == 0:
                return (idx, pos + m.end() + 1)
        else:
            depth += 1
        pos += m.end()
    return (idx, open_end)


def tweak_bar(s, sp='10sp'):
    """字缩小 + 整排居中"""
    j = s.find('@+id/play_btn_group"')
    if j < 0:
        print('  !! 找不到 play_btn_group')
        return s
    st = s.rfind('<', 0, j)
    a, b = _block_span(s, st)

    # 1) 组内文字统一缩小
    seg = s[a:b]
    n1 = seg.count('android:textSize="@dimen/ts_19"')
    seg = seg.replace('android:textSize="@dimen/ts_19"', 'android:textSize="%s"' % sp)
    # 去掉字体自带上下留白，图标与文字贴紧
    # 左右间距加宽（10dp → 14dp）
    seg = seg.replace('android:padding="@dimen/vs_10"',
                      'android:paddingLeft="14dp"' + chr(10)
                      + '            android:paddingRight="14dp"' + chr(10)
                      + '            android:paddingTop="10dp"' + chr(10)
                      + '            android:paddingBottom="10dp"')
    seg = seg.replace('android:textColor="@android:color/white"', 'android:textColor="@android:color/white"' + chr(10) + '                android:includeFontPadding="false"')
    # 去掉灰色底板
    seg = seg.replace('android:background="@drawable/button_dialog_main"', 'android:background="@null"')
    # 左右间隙加宽（10dp → 14dp），上下保持 10dp
    seg = seg.replace('android:padding="@dimen/vs_10"',
                      'android:paddingTop="@dimen/vs_10"' + chr(10) + '                android:paddingBottom="@dimen/vs_10"' + chr(10) + '                android:paddingLeft="14dp"' + chr(10) + '                android:paddingRight="14dp"')
    # 汉字横向拉宽一点，视觉更扁
    seg = seg.replace('android:textColor="@android:color/white"',
                      'android:textColor="@android:color/white"' + chr(10)
                      + '                ' + chr(10)
                      + '                android:textStyle="normal"' + chr(10)
                      + '                android:fontFamily="sans-serif-light"')
    s = s[:a] + seg + s[b:]
    print('  + 组内字号缩小：%d 处 → %s' % (n1, sp))

    # 2) 外层 HorizontalScrollView 开启 fillViewport（否则无法居中）
    hs = s.rfind('<HorizontalScrollView', 0, s.find('@+id/play_btn_group"'))
    if hs > 0:
        hs_end = s.find('>', hs)
        blk = s[hs:hs_end]
        if 'fillViewport="false"' in blk:
            s = s[:hs] + blk.replace('fillViewport="false"', 'fillViewport="true"') + s[hs_end:]
            print('  + HorizontalScrollView 已开启 fillViewport')

    # 3) 按钮组撑满父宽 + 内部居中（ScrollView 里 layout_gravity 不生效）
    j = s.find('@+id/play_btn_group"')
    st = s.rfind('<', 0, j)
    e = s.find('>', j)
    blk = s[st:e]
    blk = blk.replace('android:layout_width="wrap_content"',
                      'android:layout_width="match_parent"')
    if 'android:gravity=' not in blk:
        blk = blk.replace('<LinearLayout',
                          '<LinearLayout' + chr(10) + '                android:gravity="center"')
    if 'layout_gravity' not in blk:
        blk = blk + chr(10) + '                android:layout_gravity="center_horizontal"'
    s = s[:st] + blk + s[e:]
    print('  + 按钮组已撑满父宽并内部居中')
    return s



def hide_dead_buttons(s):
    # 压成 0dp 隐藏：搜弹幕、视轨（点了没实际作用或重复的按钮）
    for vid, why in (('danmu_search_ui', '搜弹幕'), ('video_track_select', '视轨')):
        j = s.find('@+id/%s"' % vid)
        if j < 0:
            print('  · 布局里没有 %s，跳过' % vid)
            continue
        st = s.rfind('<', 0, j)
        e = s.find('>', j)
        blk = s[st:e].rstrip()
        closed = blk.endswith('/')
        if closed:
            blk = blk[:-1].rstrip()
        for k in ('android:layout_width', 'android:layout_height'):
            if k in blk:
                blk = re.sub(r'%s="[^"]*"' % k, '%s="0dp"' % k, blk, count=1)
            else:
                blk = blk + (chr(10) + '        %s="0dp"' % k)
        if 'android:visibility' in blk:
            blk = re.sub(r'android:visibility="[^"]*"', 'android:visibility="gone"', blk, count=1)
        else:
            blk = blk + (chr(10) + '        android:visibility="gone"')
        s = s[:st] + blk + (' />' if closed else '>') + s[e + 1:]
        print('  + 「%s」已压成 0dp 隐藏' % why)
    return s

def merge_danmu_buttons():
    # 把「搜弹幕」合并进「弹幕」按钮：长按弹幕 = 搜弹幕；独立按钮彻底隐藏
    # 做法：按两个锚点整段替换，不解析括号，不会破坏代码结构
    p = jpath('app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java')
    if not os.path.isfile(p):
        print('  !! 找不到 VodController.java')
        fails.append('VodController')
        return
    s = read(p)
    A = '        setOnTvLongClickListener(mDanmuSettingBtn, new OnLongClickListener() {'
    B = '        mLandscapePortraitBtn.setOnClickListener('
    i = s.find(A)
    j = s.find(B, i) if i >= 0 else -1
    if i < 0 or j < i:
        print('  · Java 补丁锚点未命中，跳过（不影响其它改动）')
        return
    nb = chr(10).join([
        A,
        '            @Override',
        '            public boolean onLongClick(View view) {',
        '                FastClickCheckUtil.check(view);',
        '                listener.searchDanmuUi(false);',
        '                hideBottom();',
        '                return true;',
        '            }',
        '        });',
        '        mDanmuSearchUiBtn.setVisibility(View.GONE);',
        '',
    ])
    s = s[:i] + nb + s[j:]
    write(p, s)
    print('  + 长按「弹幕」= 搜弹幕；独立「搜弹幕」按钮已清除')


def unify_danmu_search():
    # 把「搜弹幕」统一到 APP 自带的搜索框（不再依赖影视源实现）
    p = jpath('app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java')
    if not os.path.isfile(p):
        print('  !! 找不到 PlayFragment.java')
        fails.append('PlayFragment')
        return
    s = read(p)
    A = '            public void searchDanmuUi(boolean longClick) {'
    B = '            public void playNext(boolean rmProgress) {'
    i = s.find(A)
    j = s.find(B, i) if i >= 0 else -1
    if i < 0 or j < i:
        print('  · 弹幕搜索统一锚点未命中，跳过')
        return
    nb = chr(10).join([
        A,
        '                SearchDanmuDialog d = new SearchDanmuDialog(requireContext());',
        '                d.setDanmuLoader(new SearchDanmuDialog.DanmuLoader() {',
        '                    @Override',
        '                    public void loadDanmu(String danmu) {',
        '                        if (!isAdded()) return;',
        '                        checkDanmu(danmu);',
        '                    }',
        '                });',
        '                VodInfo.VodSeries series = mVodInfo == null ? null : getCurrentSeries(mVodInfo.playFlag, mVodInfo.playIndex);',
        '                d.setEpisode(series == null ? "" : series.name);',
        '                d.setSearchWord(mVodInfo == null ? "" : mVodInfo.name);',
        '                d.show();',
        '            }',
        '',
        '',
    ])
    s = s[:i] + nb + s[j:]
    write(p, s)
    print('  + 长按「弹幕」现在打开 APP 自带的搜索框（与设置里的「搜索」同一个）')

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


HTVO_B64 = ('iVBORw0KGgoAAAANSUhEUgAAADYAAAA2CAYAAACMRWrdAAAEuklEQVR42u1aTUhjVxQ+994XfXk6WpXk'
           'JWszg5ofuipxIaWx6mKwuOhQaNUwzlAps3BRXBS6sYKbVFdCuzISdDEMpepGEAN2Y6A7f4LUH9DaaohhIHm0Jnn3vttFfTZjO07+pskM74O7SLg57335zjn33HsugAEDBgwYMPBqYIwBAGBsbOzdtra2GgAAQsi/5iGEAADAbrfjhYWFLxKJxL6qqpeU0gxjTL1tUEozqqpeJhKJ/fn5+cdWqxW/dmKCIAAAwNzc3MjBwcG6xWLBN8khhAAhBLIs42g0usJLxNbW1jObzXYrOaEQEgghIIQA5/z6O/1zMpl87nA4utfX15/29fV9EovFNEIIMMYAYwyMMZiamvJ3dHT0M8aylNL00dHRT5xzLc9nY4fD8QEhpMbj8XwcCAQ+Hxoa+r5kZXRXehmmp6c/YoypnHO+s7Pzo/6P6sqJoginp6c/M8bUVCp11tnZeScfu7lzOjs77yiKEmOMqclk8reSFUMIAeccCCHg9/vv+Xy+7sbGRgtCCGGMiaZpzOl0fogxFlRV/dPlcg2sra096+npeRCPxzUAAEmSkNlsfgdjLBwfH0cikYgCAC+o/zLocyKRiHJ8fBxxuVwD9fX1cslKYYyhoaEBhcPhb/OJgWw2+wfnnEej0RVJkgAAoLm5GSUSiX1dUT3pFJqodnd3lzjnnDGmlqSYHh+BQOAzn8/3JaU0LQiCqGkavRkDCCGsaRolhNQAAMzOzn6VyWTgv5TRNK1gYsX85lbfbmlpQalU6owxpiqKEhseHm51Op21LpdL9Hg8otPprF1cXHySq9bDhw/v5sZYU1PTC4oV+05lUUyPLZvNViNJUgvGWNjc3JwLhUJHN+een5//yjnXTCaTNDIyci8YDB6YTCaglFZkfRUKUA8DAGSz2TQh5NpFBUEASimIomhGCGG/3+8IhUJHJpMJVFXNK+tVlFgOQcQYu/Z5fRBCyPj4+Hu5pCoJoVQDuqtNTEw8jcViGsa44qQAAMpWc+mkypa5qoUYQqhqSJWVWD4VxBtJrOq2U4Wme1Sp/F3OrKjHzOHhYcbtdksIIaQoCtUX7mrmKOSTFFRVhWg0mqnmmCqqpOKcgyiKUFdXhwotRhVF4ZUoq4RXZTqr1YonJyc/7e7uHmloaLBfVfF5+2BXV5d7b28vU8w25bURs9vtOBwOr7S3t98v9gEmkwlVnSvOzMw8aW9vv08pTetnFFdK5h1gl5eXrOqI9ff3f61pGk2n08ne3t67kUhE0eOu0D3d/12V3Or4ZrO5uZgzijdmgb46tHk7K49qKnCNWtEgZhAziBnEDGKFEiv3Al1sU6KsxDjnvNQFOnen87e54poSvBw1XW4jwuv11t98wUII1dbWwsnJSURv/BViT5/j9Xrr9cZfKpU6K7q6X15e/mZwcPA7SZJaNjY2fi+ktapjYGDgweHhoZrJZGB1dXV2dHR0oRh7CCHc2tr6viAIIsZYWFpamihaMVmW8fb29g+lNMLdbreox4fFYsF6G6jU5rosy6UFvSzLeH5+/vHFxcUv+V5fyB1Op7MW4J/bBTabDQeDwUeF2NOvQ8Tj8b1gMPioZFIGDBgwYOBtwV+WdcgT60j7TwAAAABJRU5ErkJggg==')


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

def label_time_buttons(s):
    # 片头/片尾：上面时间、下面汉字（两行显示）
    for vid, label in (('play_time_start', '片头'), ('play_time_end', '片尾')):
        i = s.find('@+id/%s"' % vid)
        if i < 0:
            print('  · 没有 %s，跳过' % vid)
            continue
        st = s.rfind('<', 0, i)
        en = s.find('>', i)
        blk = s[st:en+1]
        blk = blk.replace('android:singleLine="true"', 'android:singleLine="false"')
        blk = re.sub(r'android:text="[^"]*"', 'android:text="%s"' % label, blk, count=1)
        blk = re.sub(r'android:textSize="[^"]*"', 'android:textSize="13sp"', blk, count=1)
        nl = chr(10) + '                '
        # 上下留白不对称：整体下移 2dp，配合行距 2dp，让时间中心落在图标中心、汉字中心落在文字中心
        blk = re.sub(r'android:padding(?:Top|Bottom|Left|Right)?="[^"]*"', '', blk)
        blk = blk.replace('<TextView',
                          '<TextView' + nl + 'android:paddingTop="13dp"' + nl
                          + 'android:paddingBottom="0dp"' + nl
                          + 'android:paddingLeft="14dp"' + nl
                          + 'android:paddingRight="14dp"')
        if 'lineSpacingExtra' not in blk:
            blk = blk.replace('android:singleLine="false"',
                              'android:singleLine="false"' + nl + 'android:lineSpacingExtra="7dp"')
        if 'minHeight' not in blk:
            blk = blk.replace('android:layout_height="wrap_content"',
                              'android:layout_height="wrap_content"' + nl + 'android:minHeight="58dp"')
        if 'fontFamily' not in blk:
            blk = blk.replace('android:textScaleX', 'android:fontFamily="sans-serif-light"' + chr(10) + '                android:textScaleX')
        # 垂直居中，让时间与图标齐、汉字与汉字齐
        if 'android:layout_gravity' not in blk:
            blk = blk.replace('<TextView', '<TextView' + chr(10) + '                android:layout_gravity="center_vertical"')
        if 'android:gravity=' not in blk:
            blk = blk.replace('<TextView', '<TextView' + chr(10) + '                android:gravity="top|center_horizontal"')
        s = s[:st] + blk + s[en:]
        print('  + %s 改为两行：时间 + 「%s」' % (vid, label))
    return s


def patch_time_text():
    p = jpath('app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java')
    if not os.path.isfile(p):
        print('  !! 找不到 VodController.java')
        fails.append('VodController')
        return
    s = read(p)
    pairs = [
        ('mPlayerTimeStartBtn.setText(start == 0 ? "片头" : stringForTime(start * 1000));',
         'mPlayerTimeStartBtn.setText((start == 0 ? "00:00" : stringForTime(start * 1000)) + "\\n片头");'),
        ('mPlayerTimeSkipBtn.setText(end == 0 ? "片尾" : stringForTime(end * 1000));',
         'mPlayerTimeSkipBtn.setText((end == 0 ? "00:00" : stringForTime(end * 1000)) + "\\n片尾");'),
    ]
    n = 0
    for a, b in pairs:
        if a in s:
            s = s.replace(a, b, 1)
            n += 1
    if n:
        write(p, s)
        print('  + 片头/片尾文字已改：时间在上、汉字在下')


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

def shorten_player_names():
    # 播放器按钮文字太长（IJK播放器），统一去掉「播放器」三字
    p = jpath('app/src/main/java/com/github/tvbox/osc/util/PlayerHelper.java')
    if not os.path.isfile(p):
        fails.append('PlayerHelper.java')
        return
    t = read(p)
    for a, b in (('"IJK播放器"', '"IJK"'), ('"EXO播放器"', '"EXO"'),
                 ('"MX播放器"', '"MX"'), ('"Reex播放器"', '"Reex"'),
                 ('"Kodi播放器"', '"Kodi"'), ('"VLC播放器"', '"VLC"')):
        t = t.replace(a, b)
    t = t.replace('return "EXO播放器";', 'return "EXO";')
    write(p, t)
    print('  + 播放器按钮文字已缩短（IJK / EXO / MX / Reex / Kodi / VLC）')

def rename_labels(s):
    # 上一集→上级、下一集→下级、横竖屏→旋屏
    for a, b in (('android:text="上一集"', 'android:text="上集"'),
                 ('android:text="下一集"', 'android:text="下集"'),
                 ('android:text="横竖屏"', 'android:text="旋屏"')):
        n = s.count(a)
        s = s.replace(a, b)
        print('  + 按钮文字 %s -> %s（%d 处）' % (a.split('"')[1], b.split('"')[1], n))
    return s

def add_space_icon():
    # 「硬解」没有图标，用一个透明占位图占住图标位置，使文字与其他按钮齐平
    p = jpath('app/src/main/res/drawable-xxhdpi/tk_space.png')
    d = os.path.dirname(p)
    if not os.path.isdir(d):
        os.makedirs(d)
    open(p, 'wb').write(base64.b64decode(SPACE_B64))
    print('  + 已生成透明占位图 tk_space.png')


def swap_progress_up(s):
    # 把进度条那一行（含 seekBar）挪到按钮组上方
    i = s.find('@+id/bottom_container')
    if i < 0:
        print('  · 没有 bottom_container，跳过')
        return s
    st = s.rfind('<', 0, i)
    blocks = []
    depth = 0
    cur = None
    for m in re.finditer(r'<(/?)(\w+)([^>]*?)(/?)>', s[st:]):
        close, tag, attrs, selfc = m.group(1), m.group(2), m.group(3), m.group(4)
        if close:
            depth -= 1
            if depth == 1 and cur is not None:
                blocks.append((cur, m.end() + st))
                cur = None
            if depth == 0:
                break
        else:
            if depth == 1:
                cur = m.start() + st
            if not selfc:
                depth += 1
    if len(blocks) < 2:
        print('  · 容器子元素不足，跳过')
        return s
    idx = None
    for k, (a, b) in enumerate(blocks):
        if 'seekBar' in s[a:b]:
            idx = k
            break
    if idx is None:
        print('  · 没找到进度条行，跳过')
        return s
    if idx == 0:
        print('  · 进度条已在最上方')
        return s
    a, b = blocks[idx]
    bar = s[a:b]
    body = s[:a] + s[b:]
    # 去掉块间多余空行
    body = re.sub(r'(\n\s*){3,}', chr(10) + chr(10), body)
    pos = body.find('@+id/play_btn_group')
    head = body.rfind('<', 0, pos)
    # 插到按钮组所在的 HorizontalScrollView 之前
    hs = body.rfind('<HorizontalScrollView', 0, head)
    body = body[:hs] + bar + chr(10) + chr(10) + body[hs:]
    # 按钮组在下方了：原来的下边距改成上边距
    body = body.replace('android:layout_marginBottom="@dimen/vs_10"\n            android:fillViewport',
                        'android:layout_marginTop="@dimen/vs_10"\n            android:fillViewport')
    print('  + 进度条已移到按钮组上方')
    return body


def tighten_seek(s):
    # 时间与进度条拉近：缩小 seekbar 两端为滑块预留的偏移
    s = s.replace('android:thumbOffset="8dp"', 'android:thumbOffset="1dp"')
    s = s.replace('android:thumbOffset="@dimen/vs_8"', 'android:thumbOffset="3dp"')
    print('  + 进度条与左右时间已拉近')
    return s


def align_seek_row(s):
    # 进度条一行：左右时间与进度条垂直居中对齐
    i = s.find('@+id/seekBar')
    if i < 0:
        print('  · 没找到 seekBar，跳过')
        return s
    st = s.rfind('<LinearLayout', 0, i)
    en = s.find('>', st)
    blk = s[st:en]
    if 'android:gravity' not in blk:
        blk = blk.replace('<LinearLayout', '<LinearLayout' + chr(10) + '                android:gravity="center_vertical"', 1)
        s = s[:st] + blk + s[en:]
    for vid in ('curr_time', 'seekBar', 'total_time'):
        j = s.find('@+id/%s"' % vid)
        if j < 0:
            continue
        a = s.rfind('<', 0, j)
        b = s.find('>', j)
        t = s[a:b]
        if 'layout_gravity' not in t:
            ins = b - 1 if s[b - 1] == '/' else b
            s = s[:ins] + chr(10) + '                android:layout_gravity="center_vertical" ' + s[ins:]
    print('  + 进度条行已垂直居中（时间与进度条同轴）')
    return s


def unflatten_text(s):
    # 汉字恢复四方四正：去掉 textScaleX 横向拉伸
    n = s.count('android:textScaleX="1.15"')
    s = s.replace('android:textScaleX="1.15"', '')
    n2 = s.count('android:textScaleX="1.15"')
    print('  + 汉字已取消横向拉伸（%d 处）' % n)
    return s


def match_ref_gaps(s):
    # 按 takagen 实机观感：进度条更细、时间更贴进度条
    s = s.replace('android:maxHeight="@dimen/vs_6"', 'android:maxHeight="4dp"')
    s = s.replace('android:minHeight="@dimen/vs_6"', 'android:minHeight="4dp"')
    s = s.replace('android:thumbOffset="8dp"', 'android:thumbOffset="1dp"')
    print('  + 进度条已调细、时间已贴近进度条')
    return s


def narrow_seek(s):
    # 进度条整行左右内缩，别顶到屏幕边（时间与条的相对距离不变）
    j = s.find('@+id/seekBar"')
    if j < 0:
        print('  · 没找到 seekBar，跳过')
        return s
    a = s.rfind('<LinearLayout', 0, j)
    b = s.find('>', a)
    blk = s[a:b]
    if 'android:paddingLeft' not in blk and 'android:paddingStart' not in blk:
        ins = b - 1 if s[b - 1] == '/' else b
        add = (chr(10) + '                android:paddingLeft="24dp"'
               + chr(10) + '                android:paddingRight="24dp" ')
        s = s[:ins] + add + s[ins:]
        print('  + 进度条整行左右各内缩 24dp')
    return s


MPV_JAVA = '''package com.github.tvbox.osc.player.thirdparty;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.util.Log;

import com.github.tvbox.osc.base.App;

public class MpvPlayer {
    public static final String TAG = "ThirdParty.mpv";

    private static final String PACKAGE_NAME = "is.xyz.mpv";
    private static final String PLAYBACK_ACTIVITY = "is.xyz.mpv.MainActivity";

    private static class MpvPackageInfo {
        final String packageName;
        final String activityName;

        MpvPackageInfo(String packageName, String activityName) {
            this.packageName = packageName;
            this.activityName = activityName;
        }
    }

    private static final MpvPackageInfo[] PACKAGES = {
            new MpvPackageInfo(PACKAGE_NAME, PLAYBACK_ACTIVITY),
    };

    public static MpvPackageInfo getPackageInfo() {
        for (MpvPackageInfo pkg : PACKAGES) {
            try {
                ApplicationInfo info = App.getInstance().getPackageManager().getApplicationInfo(pkg.packageName, 0);
                if (info.enabled)
                    return pkg;
                else
                    Log.v(TAG, "mpv package `" + pkg.packageName + "` is disabled.");
            } catch (PackageManager.NameNotFoundException ex) {
                Log.v(TAG, "mpv package `" + pkg.packageName + "` does not exist.");
            }
        }
        return null;
    }

    public static boolean run(Activity activity, String url, String title, String subtitle, long progress) {
        MpvPackageInfo packageInfo = getPackageInfo();
        if (packageInfo == null)
            return false;

        Intent intent = new Intent(Intent.ACTION_VIEW);
        intent.setPackage(packageInfo.packageName);
        intent.setDataAndTypeAndNormalize(Uri.parse(url), "video/*");
        intent.putExtra("title", title);

        if (subtitle != null && !subtitle.isEmpty()) {
            intent.putExtra("subs", subtitle);
        }

        if (progress > 0) {
            intent.putExtra("position", progress);
        }

        try {
            activity.startActivity(intent);
            return true;
        } catch (ActivityNotFoundException ex) {
            Log.e(TAG, "Can't run mpv", ex);
            return false;
        }
    }
}
'''

def add_mpv_player():
    # 播放器菜单里加一项 mpv（装了 mpv-android 才出现）
    d = jpath('app/src/main/java/com/github/tvbox/osc/player/thirdparty')
    if not os.path.isdir(d):
        print('  !! 找不到 thirdparty 目录')
        fails.append('MpvPlayer')
        return
    write(os.path.join(d, 'MpvPlayer.java'), MPV_JAVA)
    ph = jpath('app/src/main/java/com/github/tvbox/osc/util/PlayerHelper.java')
    if not os.path.isfile(ph):
        print('  !! 找不到 PlayerHelper.java')
        fails.append('PlayerHelper')
        return
    t = read(ph)
    if 'MpvPlayer' in t:
        print('  · mpv 已存在，跳过')
        return
    if 'import com.github.tvbox.osc.player.thirdparty.MXPlayer;' in t:
        t = t.replace('import com.github.tvbox.osc.player.thirdparty.MXPlayer;',
                      'import com.github.tvbox.osc.player.thirdparty.MpvPlayer;' + chr(10)
                      + 'import com.github.tvbox.osc.player.thirdparty.MXPlayer;', 1)
    m = re.search(r'playersInfo\.put\(14, "[^"]*"\);', t)
    if m:
        t = t[:m.end()] + chr(10) + '            playersInfo.put(15, "mpv");' + t[m.end():]
    m = re.search(r'playersExist\.put\(14, [^\n]*\);', t)
    if m:
        t = t[:m.end()] + chr(10) + '            playersExist.put(15, MpvPlayer.getPackageInfo() != null);' + t[m.end():]
    m = re.search(r'(case 14: \{[\s\S]*?break;[\s\S]*?\})', t)
    if m:
        add = (chr(10) + '            case 15: {' + chr(10)
               + '                callResult = MpvPlayer.run(activity, url, title, subtitle, progress);' + chr(10)
               + '                break;' + chr(10) + '            }')
        t = t[:m.end(1)] + add + t[m.end(1):]
    write(ph, t)
    print('  + 播放器菜单已加 mpv 选项')


def unstick_bar(s):
    # 去掉横向滚动，底部栏固定不能左右滑
    m = re.search(r'<HorizontalScrollView[^>]*>', s)
    if m:
        margin = re.search(r'android:layout_marginTop="([^"]*)"', m.group(0))
        s = s[:m.start()] + s[m.end():]
        s = s.replace('</HorizontalScrollView>', '', 1)
        if margin:
            j = s.find('@+id/play_btn_group"')
            a = s.rfind('<', 0, j)
            b = s.find('>', a)
            if 'layout_marginTop' not in s[a:b]:
                ins = b - 1 if s[b - 1] == '/' else b
                s = s[:ins] + chr(10) + '                android:layout_marginTop="%s" ' % margin.group(1) + s[ins:]
        print('  + 已去掉横向滚动段落子，底部栏固定')
    return s


def center_pair(s):
    # 图标与汉字左右居中对齐 + 左右间隙收到半个图标宽
    s = s.replace('android:paddingLeft="14dp"', 'android:paddingLeft="6dp"')
    s = s.replace('android:paddingRight="14dp"', 'android:paddingRight="6dp"')
    # 汉字尺寸用 dp 而不是 sp：sp 会随电视「系统字号」放大（实测被放大 2 倍）
    s = re.sub(r'android:textSize="10sp"', 'android:textSize="10dp"', s)
    s = re.sub(r'\s*android:layout_marginEnd="@dimen/vs_5"', '', s)
    s = re.sub(r'\s*android:layout_marginRight="@dimen/vs_5"', '', s)
    # 按钮内文字水平居中（图标与汉字同一条中线）
    j = s.find('@+id/play_btn_group"')
    if j < 0:
        print('  · 找不到按钮组，跳过居中')
        return s
    st = s.rfind('<', 0, j)
    a, b = _block_span(s, st)
    seg = s[a:b]
    cnt = [0]
    def fix(m):
        tag = m.group(0)
        if 'android:gravity=' in tag:
            return tag
        cnt[0] += 1
        if tag.rstrip().endswith('/>'):
            return tag.rstrip()[:-2].rstrip() + chr(10) + '                android:gravity="center_horizontal" />'
        return tag[:-1] + chr(10) + '                android:gravity="center_horizontal">'
    seg = re.sub(r'<TextView[^>]*>', fix, seg)
    s = s[:a] + seg + s[b:]
    print('  + 按钮内文字已水平居中（%d 个），字宽改 dp 不再随系统放大' % cnt[0])
    return s


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


def patch_java():
    # 弹幕搜索 / 视轨：Java 运行时会把它们重新设成 VISIBLE，必须在这里断掉
    f = os.path.join(SRC, 'app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java')
    if not os.path.exists(f):
        print('  · 找不到 VodController.java')
        return
    s = read(f)
    hits = 0
    a = 'mDanmuSearchUiBtn.setVisibility(hasDanmuSearchUi ? VISIBLE : GONE);'
    if a in s:
        s = s.replace(a, 'mDanmuSearchUiBtn.setVisibility(GONE);')
        hits += 1
    b = 'mVideoTrackBtn.setVisibility((playerType == 1 || playerType == 2) ? VISIBLE : GONE);'
    if b in s:
        s = s.replace(b, 'mVideoTrackBtn.setVisibility(GONE);')
        hits += 1
    # 旋屏按钮：电视上按设备类型被隐藏，这里强制常显，并把文字固定成「旋屏」
    c = 'if (showButton) mLandscapePortraitBtn.setText(isPortrait ? "横屏" : "竖屏");'
    if c in s:
        s = s.replace(c, 'if (showButton) mLandscapePortraitBtn.setText("旋屏");')
        hits += 1
    d = 'mLandscapePortraitBtn.setText("竖屏");'
    if d in s:
        s = s.replace(d, 'mLandscapePortraitBtn.setText("旋屏");')
        hits += 1
    e = 'mLandscapePortraitBtn.setText("横屏");'
    if e in s:
        s = s.replace(e, 'mLandscapePortraitBtn.setText("旋屏");')
        hits += 1
    f2 = 'showButton = width > 0 && height > 0 && (width <= height || shortVideo) && ScreenUtils.getSqrt(mActivity) < 10.0;'
    if f2 in s:
        s = s.replace(f2, 'showButton = true;')
        hits += 1
    # 片头片尾：00:00 与汉字拆成两种字号（13dp / 10dp）
    g1 = 'mPlayerTimeStartBtn.setText((start == 0 ? "00:00" : stringForTime(start * 1000)) + "\\n片头");'
    g2 = 'mPlayerTimeSkipBtn.setText((end == 0 ? "00:00" : stringForTime(end * 1000)) + "\\n片尾");'
    if g1 in s and g2 in s:
        s = s.replace(g1, 'mPlayerTimeStartBtn.setText(buildTimeLabel(start == 0 ? "00:00" : stringForTime(start * 1000), "片头"));')
        s = s.replace(g2, 'mPlayerTimeSkipBtn.setText(buildTimeLabel(end == 0 ? "00:00" : stringForTime(end * 1000), "片尾"));')
        helper = ('    private CharSequence buildTimeLabel(String time, String label) {' + chr(10)
                  + '        android.text.SpannableString ss = new android.text.SpannableString(time + "\\n" + label);' + chr(10)
                  + '        ss.setSpan(new android.text.style.AbsoluteSizeSpan(15, true), 0, time.length(), android.text.Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);' + chr(10)
                  + '        ss.setSpan(new android.text.style.AbsoluteSizeSpan(10, true), time.length() + 1, ss.length(), android.text.Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);' + chr(10)
                  + '        return ss;' + chr(10)
                  + '    }' + chr(10) + chr(10))
        anchor = '    private String getPlayerShortName(int playerType) {'
        if anchor in s:
            s = s.replace(anchor, helper + anchor, 1)
        hits += 1
    write(f, s)
    print('  + Java 补丁已打（%d 处）：弹幕搜索/视轨锁死 GONE、旋屏常显改字、片头片尾分字号' % hits)


def swap_order(s):
    # 上集挪到最左（原版是 下集 在前）
    jn = s.find('@+id/play_next"')
    jp = s.find('@+id/play_pre"')
    if jn < 0 or jp < 0 or jp < jn:
        print('  · 上集/下集 顺序已正确')
        return s
    an = s.rfind('<', 0, jn); bn = s.find('/>', jn) + 2
    ap = s.rfind('<', 0, jp); bp = s.find('/>', jp) + 2
    blk_n = s[an:bn]
    blk_p = s[ap:bp]
    s = s[:an] + blk_p + chr(10) + '            ' + blk_n + s[bp:]
    print('  + 已把「上集」挪到「下集」左边')
    return s


def unify_timepair(s):
    # 片头片尾：汉字与其它按钮统一 10sp，两行高度重排
    for key in ('play_time_start', 'play_time_end'):
        j = s.find('@+id/%s"' % key)
        if j < 0:
            continue
        a = s.rfind('<', 0, j); b = s.find('/>', j)
        blk = s[a:b]
        blk = re.sub(r'android:textSize="[^"]*"', 'android:textSize="10dp"', blk)
        blk = re.sub(r'android:paddingTop="[^"]*"', 'android:paddingTop="19dp"', blk)
        blk = re.sub(r'android:lineSpacingExtra="[^"]*"', 'android:lineSpacingExtra="1dp"', blk)
        blk = re.sub(r'android:minHeight="[^"]*"', 'android:minHeight="50dp"', blk)
        s = s[:a] + blk + s[b:]
    print('  + 片头片尾汉字已统一 10dp（00:00 由 Java 单独放大）')
    return s


def main():
    print('=== 图标版（图标 %s、字缩小、整排居中）===' % ICON_SIZE)
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

    s = tweak_bar(s)
    make_replay_icon()
    make_extra_icons()
    patch_time_text()
    shorten_player_names()
    add_space_icon()
    normalize_icons()
    s = label_time_buttons(s)
    s = hide_dead_buttons(s)
    s = rename_labels(s)
    s = swap_progress_up(s)
    s = align_seek_row(s)
    s = tighten_seek(s)
    s = unflatten_text(s)
    s = match_ref_gaps(s)
    s = narrow_seek(s)
    s = unstick_bar(s)
    s = center_pair(s)
    s = swap_order(s)
    s = unify_timepair(s)
    add_mpv_player()
    stamp_replay_icon()
    patch_java()
    open(p, 'w', encoding='utf-8').write(s)
    print('  + 图标已加到 %d 处（%d 个按钮）' % (hit, hit))
    if miss:
        print('  · 未匹配（保留原样）: ' + ', '.join(miss))

    print('-' * 50)
    if fails:
        print('!! 失败项: ' + ', '.join(fails))
        sys.exit(1)
    print('=== 完成 ===')


if __name__ == '__main__':
    main()
