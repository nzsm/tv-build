#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TVBox 底部菜单定制 —— 按已经确认的规则一次做到位

图标：takagen 那套，26dp，图形占画布 22/24，视觉等大；重播是完整圆环 + 居中三角。
汉字：10dp 细体、不压扁、单行，和图标左右居中，图标与汉字紧贴。
间距：每个按钮左右 6dp，相邻约半个图标宽。
整排：去掉横向滚动，固定居中。
底板：全部 @null（无底）。
进度条：在按钮上方；条高 4dp、thumb 1dp、左右各收 24dp；时间紧贴条两端、上下居中。
片头/片尾：上格 26dp 放时间（当图标位对齐），下格 10dp 放汉字。
文字：上集 / 下集 / 旋屏；播放器名用 IJK / EXO / MX / Reex / Kodi / VLC。
隐藏：视轨、搜弹幕（布局里压 0dp，运行时再物理摘除）。
不动：播放内核、播放器实现、任何解码逻辑。

用法：python3 tvbox_ext.py <源码目录> <默认订阅地址> <APP名称>
"""
import base64

ICONS = {
    'v_prev': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.826" android:scaleY="1.826"\n        android:translateX="-0.045" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M7,6c0.55,0 1,0.45 1,1v10c0,0.55 -0.45,1 -1,1s-1,-0.45 -1,-1L6,7c0,-0.55 0.45,-1 1,-1zM10.66,12.82l5.77,4.07c0.66,0.47 1.58,-0.01 1.58,-0.82L18.01,7.93c0,-0.81 -0.91,-1.28 -1.58,-0.82l-5.77,4.07c-0.57,0.4 -0.57,1.24 0,1.64z"/></group></vector>',
    'v_next': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.833" android:scaleY="1.833"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M7.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L7.58,7.11C6.91,6.65 6,7.12 6,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM16,7v10c0,0.55 0.45,1 1,1s1,-0.45 1,-1V7c0,-0.55 -0.45,-1 -1,-1s-1,0.45 -1,1z"/></group></vector>',
    'v_replay': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.136" android:scaleY="1.136"\n        android:translateX="-0.057" android:translateY="-1.123"><path android:fillColor="@android:color/white" android:pathData="M12,5V2.21c0,-0.45 -0.54,-0.67 -0.85,-0.35l-3.8,3.79c-0.2,0.2 -0.2,0.51 0,0.71l3.79,3.79c0.32,0.31 0.86,0.09 0.86,-0.36V7c3.73,0 6.68,3.42 5.86,7.29 -0.47,2.27 -2.31,4.1 -4.57,4.57 -3.57,0.75 -6.75,-1.7 -7.23,-5.01 -0.07,-0.48 -0.49,-0.85 -0.98,-0.85 -0.6,0 -1.08,0.53 -1,1.13 0.62,4.39 4.8,7.64 9.53,6.72 3.12,-0.61 5.63,-3.12 6.24,-6.24C20.84,9.48 16.94,5 12,5z"/></group></vector>',
    'v_replay_play': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="24" android:viewportHeight="24"\n    android:tint="#FFFFFF"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.136" android:scaleY="1.136"\n        android:translateX="-0.057" android:translateY="-1.123"><path android:strokeColor="@android:color/white" android:strokeWidth="2.2" android:fillColor="@android:color/transparent" android:pathData="M12,5 A7,7 0 1 1 11.99,5"/><path android:fillColor="@android:color/white" android:pathData="M9.85,8.4 L16.25,12.0 L9.85,15.6 Z"/></group></vector>',
    'v_aspect': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M18,12c-0.55,0 -1,0.45 -1,1v2h-2c-0.55,0 -1,0.45 -1,1s0.45,1 1,1h3c0.55,0 1,-0.45 1,-1v-3c0,-0.55 -0.45,-1 -1,-1zM7,9h2c0.55,0 1,-0.45 1,-1s-0.45,-1 -1,-1L6,7c-0.55,0 -1,0.45 -1,1v3c0,0.55 0.45,1 1,1s1,-0.45 1,-1L7,9zM21,3L3,3c-1.1,0 -2,0.9 -2,2v14c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2zM20,19.01L4,19.01c-0.55,0 -1,-0.45 -1,-1L3,5.99c0,-0.55 0.45,-1 1,-1h16c0.55,0 1,0.45 1,1v12.02c0,0.55 -0.45,1 -1,1z"/></group></vector>',
    'v_ffwd': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.309" android:scaleY="1.309"\n        android:translateX="-0.523" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M5.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L5.58,7.11C4.91,6.65 4,7.12 4,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM13,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63l-5.77,-4.07c-0.67,-0.47 -1.58,0 -1.58,0.81z"/></group></vector>',
    'v_type': '<vector android:height="26dp"\n    android:tint="#FFFFFF"\n    android:viewportHeight="24"\n    android:viewportWidth="24"\n    android:width="26dp"\n    xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M21,3L3,3c-1.11,0 -2,0.89 -2,2v12c0,1.1 0.89,2 2,2h5v2h8v-2h5c1.1,0 1.99,-0.9 1.99,-2L23,5c0,-1.11 -0.9,-2 -2,-2zM21,17L3,17L3,5h18v12zM16,11l-7,4L9,7z" /></group></vector>',
    'v_subtitle': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.1" android:scaleY="1.1"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M20,4L4,4c-1.1,0 -2,0.9 -2,2v12c0,1.1 0.9,2 2,2h16c1.1,0 2,-0.9 2,-2L22,6c0,-1.1 -0.9,-2 -2,-2zM4,12h4v2L4,14v-2zM14,18L4,18v-2h10v2zM20,18h-4v-2h4v2zM20,14L10,14v-2h10v2z"/></group></vector>',
    'v_audio': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.222" android:scaleY="1.222"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M12,5v8.55c-0.94,-0.54 -2.1,-0.75 -3.33,-0.32 -1.34,0.48 -2.37,1.67 -2.61,3.07 -0.46,2.74 1.86,5.08 4.59,4.65 1.96,-0.31 3.35,-2.11 3.35,-4.1V7h2c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2h-2c-1.1,0 -2,0.9 -2,2z"/></group></vector>',
    'v_danmu': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp"\n    android:height="26dp"\n    android:viewportWidth="436"\n    android:viewportHeight="419"><group android:pivotX="218.0" android:pivotY="209.5"\n        android:scaleX="0.916" android:scaleY="0.916"\n        android:translateX="0.0" android:translateY="-25.507"><path\n      android:pathData="M322.65,272.14L274.13,272.14L274.13,290.36L328.16,290.36L328.16,318.2L274.13,318.2L274.13,347.96L242.96,347.96L242.96,318.2L188.7,318.2L188.7,290.36L242.96,290.36L242.96,272.14L194.21,272.14L194.21,147.1L216.3,147.1L209.39,129.82L238.16,129.82L245.13,147.1L271.73,147.1L278.7,129.82L307.53,129.82L300.32,147.1L322.88,147.1L322.65,272.14ZM115.05,189.58L152.26,189.58L152.26,164.62L110.25,164.62L110.25,135.09L182.96,135.09L182.96,218.35L143.59,218.35L142.18,244.78L184.66,244.78L177.92,347.02L117.22,347.02L117.22,316.79L148.39,316.79L151.79,273.55L110.25,273.55L115.05,189.58ZM244.89,243.08L244.89,223.16L222.81,223.16L222.81,243.08L244.89,243.08ZM244.89,195.79L244.89,176.11L222.81,176.11L222.81,195.79L244.89,195.79ZM294.06,243.08L294.06,223.16L272.02,223.16L272.02,243.08L294.06,243.08ZM294.06,195.79L294.06,176.11L272.02,176.11L272.02,195.79L294.06,195.79Z"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"/><path\n      android:pathData="M20.27,79.27Q0.5,99.04 0.5,127L0.5,351Q0.5,378.96 20.27,398.73Q40.04,418.5 68,418.5L368,418.5Q395.96,418.5 415.73,398.73Q435.5,378.96 435.5,351L435.5,127Q435.5,99.04 415.73,79.27Q395.96,59.5 368,59.5L68,59.5Q40.04,59.5 20.27,79.27ZM35.5,351L35.5,127Q35.5,113.54 45.02,104.02Q54.54,94.5 68,94.5L368,94.5Q381.46,94.5 390.98,104.02Q400.5,113.54 400.5,127L400.5,351Q400.5,364.46 390.98,373.98Q381.46,383.5 368,383.5L68,383.5Q54.54,383.5 45.02,373.98Q35.5,364.46 35.5,351Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FCFCFC"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/><path\n      android:pathData="M208.26,55.63L128.98,0.62L109.02,29.38L188.31,84.39Q201.24,93.36 216.98,93.4Q232.71,93.44 245.69,84.53L325.91,29.42L306.09,0.57L225.87,55.68Q221.89,58.41 217.06,58.4Q212.23,58.39 208.26,55.63Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/></group></vector>',
    'v_back': '<vector android:autoMirrored="true" android:height="26dp"\n    android:tint="#FFFFFF" android:viewportHeight="24"\n    android:viewportWidth="24" android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.169" android:scaleY="1.169"\n        android:translateX="0.468" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M16.62,2.99c-0.49,-0.49 -1.28,-0.49 -1.77,0L6.54,11.3c-0.39,0.39 -0.39,1.02 0,1.41l8.31,8.31c0.49,0.49 1.28,0.49 1.77,0s0.49,-1.28 0,-1.77L9.38,12l7.25,-7.25c0.48,-0.48 0.48,-1.28 -0.01,-1.76z"/></group></vector>',
    'ic_clock': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.047" android:scaleY="1.047"\n        android:translateX="-0.262" android:translateY="-1.31"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M11,8H13V14H11V8M12,20C8.13,20 5,16.87 5,13S8.13,6 12,6 19,9.13 19,13C19.7,13 20.36,13.13 21,13.35C21,13.23 21,13.12 21,13C21,10.88 20.26,8.93 19.03,7.39L20.45,5.97C20,5.46 19.55,5 19.04,4.56L17.62,6C16.07,4.74 14.12,4 12,4C7.03,4 3,8.03 3,13S7.03,22 12,22C12.59,22 13.16,21.94 13.71,21.83C13.4,21.25 13.18,20.6 13.08,19.91C12.72,19.96 12.37,20 12,20M15,1H9V3H15V1M16.5,16.5V21.5H21.5V16.5H16.5Z"/></group></vector>',
    'play_skip': '<vector android:height="26dp" android:viewportHeight="1000"\n    android:viewportWidth="1000" android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="500.0" android:pivotY="500.0"\n        android:scaleX="0.932" android:scaleY="0.932"\n        android:translateX="0.0" android:translateY="-76.375"><path android:fillColor="#FFFFFFFF" android:pathData="M10,499.5c0,301.7 0.3,319.9 4.5,316.5C24,808.3 345.7,501.9 345.7,500.3c0,-0.8 -75.3,-73.4 -167.7,-161.1L10,179.6L10,499.5z"/><path android:fillColor="#FFFFFFFF" android:pathData="M414.1,498.9c0,203.1 1.1,319.9 2.6,319.4c2.6,-0.8 335.5,-316.2 335.5,-318c0,-0.5 -234,-223.5 -328.1,-312.5l-10,-9.3L414.1,498.9z"/><path android:fillColor="#FFFFFFFF" android:pathData="M820.9,500.5l0,321l84.5,-0L990,821.5L990,500.5l0,-320.9l-84.5,-0l-84.5,-0L820.9,500.5z"/></group></vector>',
    'tk_unlock': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp"\n    android:height="26dp"\n    android:tint="#FFFFFF"\n    android:viewportWidth="24"\n    android:viewportHeight="24"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.047" android:scaleY="1.047"\n        android:translateX="0.0" android:translateY="-1.31"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M18,8h-1L17,6c0,-2.76 -2.24,-5 -5,-5S7,3.24 7,6h2c0,-1.66 1.34,-3 3,-3s3,1.34 3,3v2L6,8c-1.1,0 -2,0.9 -2,2v10c0,1.1 0.9,2 2,2h12c1.1,0 2,-0.9 2,-2L20,10c0,-1.1 -0.9,-2 -2,-2zM18,20L6,20L6,10h12v10zM12,17c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2z" /></group></vector>',
    'v_cast': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="24" android:viewportHeight="24"\n    android:tint="#FFFFFF"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M1,18v3h3c0,-1.66 -1.34,-3 -3,-3zM1,14v2c2.76,0 5,2.24 5,5h2c0,-3.87 -3.13,-7 -7,-7zM1,10v2c4.97,0 9,4.03 9,9h2c0,-6.08 -4.93,-11 -11,-11zM21,3L3,3c-1.1,0 -2,0.9 -2,2v3h2L3,5h18v14h-7v2h7c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2z"/></group></vector>',
    'tk_space': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="26" android:viewportHeight="26"><path android:fillColor="#00000000" android:pathData="M0,0 L26,0 L26,26 L0,26 Z" /></vector>',
}

HTVO_B64 = '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'

import os
import re
import sys
import xml.etree.ElementTree as ET

SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
DEF_URL = sys.argv[2] if len(sys.argv) > 2 else ''
APP_NAME = sys.argv[3] if len(sys.argv) > 3 else '影道仓定制版'

VER = 'VER-20261117-G'
LAYOUT = 'app/src/main/res/layout/player_vod_control_view.xml'
VOD = 'app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java'
PLAYER_HELPER = 'app/src/main/java/com/github/tvbox/osc/util/PlayerHelper.java'

A = '{http://schemas.android.com/apk/res/android}'
NS = 'http://schemas.android.com/apk/res/android'

ICON_SIZE = '26dp'      # 图标位高度
TEXT_SIZE = '10dp'      # 汉字
PAD_LR = '6dp'          # 每个按钮左右内边距 → 相邻 12dp ≈ 半个图标
PAD_TB = '10dp'
SEEK_INSET = '24dp'     # 进度条整行左右各收

RENAME = {'play_pre': '上集', 'play_next': '下集', 'landscape_portrait': '旋屏'}

BTN_ICON = {
    'play_pre': 'v_prev',
    'play_next': 'v_next',
    'play_retry': 'v_replay_play',
    'play_refresh': 'v_replay',
    'play_scale': 'v_aspect',
    'play_speed': 'v_ffwd',
    'play_player': 'v_type',
    'play_ijk': 'tk_space',
    'play_time_reset': 'play_skip',
    'play_cast': 'v_cast',
    'zimu_select': 'v_subtitle',
    'audio_track_select': 'v_audio',
    'danmu_setting': 'v_danmu',
    'landscape_portrait': 'htov',
    'screen_display': 'ic_clock',
}


def log(msg):
    print('  + ' + msg)


def jp(*parts):
    return os.path.join(SRC, *parts)


def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write_text(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


# ---------------------------------------------------------------- 图标
def write_icons():
    ddir = jp('app/src/main/res/drawable')
    os.makedirs(ddir, exist_ok=True)
    for name, xml in ICONS.items():
        write_text(os.path.join(ddir, name + '.xml'), xml)
    dpi = jp('app/src/main/res/drawable-xxhdpi')
    os.makedirs(dpi, exist_ok=True)
    with open(os.path.join(dpi, 'htov.png'), 'wb') as f:
        f.write(base64.b64decode(HTVO_B64))
    log('图标写入 %d 个（自包含，不引用任何外部资源）' % (len(ICONS) + 1))


# ---------------------------------------------------------------- 布局
def find_id(root, rid):
    for e in root.iter():
        if e.get(A + 'id') == '@+id/' + rid:
            return e


def parents(root):
    return {c: p for p in root.iter() for c in p}


def style_button(e, icon):
    e.set(A + 'layout_width', 'wrap_content')
    e.set(A + 'layout_height', 'wrap_content')
    e.set(A + 'gravity', 'top|center_horizontal')
    e.set(A + 'textSize', TEXT_SIZE)
    e.set(A + 'fontFamily', 'sans-serif-light')
    e.set(A + 'includeFontPadding', 'false')
    e.set(A + 'singleLine', 'true')
    e.set(A + 'textColor', '@android:color/white')
    e.set(A + 'background', '@null')
    e.set(A + 'drawablePadding', '0dp')
    e.set(A + 'paddingLeft', PAD_LR)
    e.set(A + 'paddingTop', PAD_TB)
    e.set(A + 'paddingRight', PAD_LR)
    e.set(A + 'paddingBottom', PAD_TB)
    if icon:
        e.set(A + 'drawableTop', '@drawable/' + icon)


def apply_layout():
    ET.register_namespace('android', NS)
    path = jp(LAYOUT)
    tree = ET.parse(path)
    root = tree.getroot()
    pm = parents(root)

    bottom = find_id(root, 'bottom_container')
    group = find_id(root, 'play_btn_group')
    if bottom is None or group is None:
        sys.exit('布局结构不符：缺少 bottom_container / play_btn_group')

    # ① 去掉横向滚动：整排固定，不许左右滑
    hsv = pm.get(group)
    if hsv is not None and hsv.tag == 'HorizontalScrollView':
        par = pm[hsv]
        idx = list(par).index(hsv)
        margin_top = hsv.get(A + 'layout_marginTop')
        par.remove(hsv)
        if margin_top:
            group.set(A + 'layout_marginTop', margin_top)
        par.insert(idx, group)
        pm = parents(root)
        log('去掉横向滚动容器，按钮整排固定')
    group.set(A + 'layout_width', 'match_parent')
    group.set(A + 'gravity', 'center')

    # ② 进度条一行挪到按钮组上方
    seek_row = pm.get(find_id(root, 'curr_time'))
    block_parse = find_id(root, 'parse_root')
    for e in (seek_row, group, block_parse):
        if e is not None and e in list(bottom):
            bottom.remove(e)
    pos = 0
    for e in (seek_row, group, block_parse):
        if e is not None:
            bottom.insert(pos, e)
            pos += 1
    log('底部顺序：进度条 → 按钮组 → 解析行')

    # ③ 上集放到下集左边
    pre, nxt = find_id(root, 'play_pre'), find_id(root, 'play_next')
    if pre is not None and nxt is not None:
        i, j = list(group).index(pre), list(group).index(nxt)
        if i > j:
            group.remove(pre)
            group.insert(j, pre)
            log('上集已在下集左边')

    # ④ 按钮文字
    for rid, text in RENAME.items():
        e = find_id(root, rid)
        if e is not None:
            e.set(A + 'text', text)

    # ⑤ 空按钮：视轨 / 搜弹幕 压 0dp 隐藏；片头尾小标签隐藏
    for rid in ('video_track_select', 'danmu_search_ui', 'play_time_start_end_text', 'play_label'):
        e = find_id(root, rid)
        if e is not None:
            e.set(A + 'layout_width', '0dp')
            e.set(A + 'layout_height', '0dp')
            e.set(A + 'visibility', 'gone')

    # ⑥ 逐按钮：图标 + 统一汉字 + 去底
    styled = 0
    for e in list(group):
        if e.tag != 'TextView':
            continue
        rid = (e.get(A + 'id') or '').replace('@+id/', '')
        if rid in ('video_track_select', 'danmu_search_ui', 'play_time_start_end_text', 'play_label'):
            continue
        style_button(e, BTN_ICON.get(rid))
        styled += 1
    log('按钮统一样式 %d 个（图标 %s、汉字 %s、无底、左右居中）' % (styled, ICON_SIZE, TEXT_SIZE))

    # ⑦ 进度条行：上下居中、左右各收 24dp、时间紧贴条两端
    if seek_row is not None:
        seek_row.set(A + 'gravity', 'center_vertical')
        seek_row.set(A + 'paddingLeft', SEEK_INSET)
        seek_row.set(A + 'paddingRight', SEEK_INSET)
        for c in list(seek_row):
            c.set(A + 'layout_gravity', 'center_vertical')
            if c.tag == 'SeekBar':
                c.set(A + 'layout_width', '0dp')
                c.set(A + 'layout_weight', '1')
                c.set(A + 'maxHeight', '4dp')
                c.set(A + 'thumbOffset', '1dp')
            else:
                c.set(A + 'layout_width', 'wrap_content')
                c.set(A + 'layout_weight', '0')
                c.set(A + 'gravity', 'center_vertical')
                c.set(A + 'textSize', TEXT_SIZE)
                c.set(A + 'includeFontPadding', 'false')
        # 时间与条两端各 3dp、进度条下方到按钮排 -3dp、底板去掉、旋屏常显
        ct = find_id(root, 'curr_time'); tt = find_id(root, 'total_time')
        if ct is not None: ct.set(A + 'layout_marginEnd', '3dp')
        if tt is not None: tt.set(A + 'layout_marginStart', '3dp')
        seek_row.set(A + 'layout_marginBottom', '7dp')
        bottom.set(A + 'background', '@null')
        lp = find_id(root, 'landscape_portrait')
        if lp is not None: lp.set(A + 'visibility', 'visible')
        log('间距：时间↔条 3dp、条↔按钮排 7dp（原 10dp -3dp）；底板去掉；旋屏常显')

    # ⑧ 片头 / 片尾：上格 26dp 时间（当图标位）+ 下格 10dp 汉字
    for rid, slot_id, text in (('play_time_start', 'tk_slot_start', '片头'),
                               ('play_time_end', 'tk_slot_end', '片尾')):
        node = find_id(root, rid)
        if node is None or node.tag != 'TextView':
            continue
        par = pm[node]
        idx = list(par).index(node)
        box = ET.Element('LinearLayout')
        box.set(A + 'orientation', 'vertical')
        box.set(A + 'gravity', 'center_horizontal')
        box.set(A + 'layout_width', 'wrap_content')
        box.set(A + 'layout_height', 'wrap_content')
        box.set(A + 'paddingLeft', PAD_LR)
        box.set(A + 'paddingTop', PAD_TB)
        box.set(A + 'paddingRight', PAD_LR)
        box.set(A + 'paddingBottom', PAD_TB)
        slot = ET.SubElement(box, 'TextView')
        slot.set(A + 'id', '@+id/' + slot_id)
        slot.set(A + 'layout_width', 'wrap_content')
        slot.set(A + 'layout_height', ICON_SIZE)
        slot.set(A + 'gravity', 'center')
        slot.set(A + 'textSize', '15dp')
        slot.set(A + 'fontFamily', 'sans-serif-light')
        slot.set(A + 'includeFontPadding', 'false')
        slot.set(A + 'singleLine', 'true')
        slot.set(A + 'textColor', '@android:color/white')
        slot.set(A + 'text', '00:00')
        par.remove(node)
        for k in ('paddingLeft', 'paddingTop', 'paddingRight', 'paddingBottom',
                  'minHeight', 'lineSpacingExtra', 'drawableTop', 'drawablePadding'):
            node.attrib.pop(A + k, None)
        node.set(A + 'layout_width', 'wrap_content')
        node.set(A + 'layout_height', 'wrap_content')
        node.set(A + 'gravity', 'top|center_horizontal')
        node.set(A + 'textSize', TEXT_SIZE)
        node.set(A + 'singleLine', 'true')
        node.set(A + 'text', text)
        box.append(node)
        par.insert(idx, box)
    log('片头/片尾：上格 %s 时间 + 下格 %s 汉字（结构对齐）' % (ICON_SIZE, TEXT_SIZE))

    tree.write(path, encoding='utf-8', xml_declaration=True)


# ---------------------------------------------------------------- Java
TIME_PATCH = [
    ('mPlayerTimeStartBtn.setText(start == 0 ? "片头" : stringForTime(start * 1000));',
     'mPlayerTimeStartBtn.setText(buildTimeLabel(start == 0 ? "00:00" : stringForTime(start * 1000), "片头"));'),
    ('mPlayerTimeSkipBtn.setText(end == 0 ? "片尾" : stringForTime(end * 1000));',
     'mPlayerTimeSkipBtn.setText(buildTimeLabel(end == 0 ? "00:00" : stringForTime(end * 1000), "片尾"));'),
]

HELPERS = '''    private CharSequence buildTimeLabel(String time, String label) {
        int sid = "片头".equals(label) ? R.id.tk_slot_start : R.id.tk_slot_end;
        android.widget.TextView slot = findViewById(sid);
        if (slot != null) slot.setText(time);
        return label;
    }

    private void purgeSearchViews(android.view.View v) {
        if (!(v instanceof android.view.ViewGroup)) return;
        android.view.ViewGroup g = (android.view.ViewGroup) v;
        for (int i = g.getChildCount() - 1; i >= 0; i--) {
            android.view.View c = g.getChildAt(i);
            if (c instanceof android.widget.TextView) {
                CharSequence cs = ((android.widget.TextView) c).getText();
                String s = cs == null ? "" : cs.toString();
                if (s.contains("搜") || s.contains("视轨")) {
                    g.removeView(c);
                    continue;
                }
            }
            purgeSearchViews(c);
        }
    }

'''

PURGE_CALL = '''        purgeSearchViews(mBottomRoot);
        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() {
            public void run() { purgeSearchViews(mBottomRoot); }
        }, 1500);
        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() {
            public void run() { purgeSearchViews(mBottomRoot); }
        }, 5000);
'''

SHORT_NAMES = [('"EXO播放器"', '"EXO"'), ('"IJK播放器"', '"IJK"'), ('"MX播放器"', '"MX"'),
               ('"Reex播放器"', '"Reex"'), ('"Kodi播放器"', '"Kodi"'), ('"VLC播放器"', '"VLC"')]


def apply_java():
    t = read_text(jp(VOD))

    for old, new in TIME_PATCH:
        if old not in t:
            sys.exit('锚点丢失：' + old)
        t = t.replace(old, new, 1)

    anchor = '    private String getPlayerShortName(int playerType) {'
    if anchor not in t:
        sys.exit('锚点丢失：getPlayerShortName')
    t = t.replace(anchor, HELPERS + anchor, 1)

    # 片头/片尾：① 原来在"半段外"是静默 return，看着像没反应 → 给提示
    #            ② 外包一层容器后点击命中区只剩下面那行小字 → 整块可点

    a1 = ('                    if (current > duration / 2) return;\n'
          '                    mPlayerConfig.put("st",current/1000);')
    b1 = ('                    mPlayerConfig.put("st",current/1000);\n'
          '                    Toast.makeText(getContext(), "片头已设为 " + stringForTime(current), Toast.LENGTH_SHORT).show();')
    if a1 not in t:
        sys.exit('锚点丢失：片头点击')
    t = t.replace(a1, b1, 1)

    a2 = ('                    if (current < duration / 2) return;\n'
          '                    mPlayerConfig.put("et", (duration - current)/1000);')
    b2 = ('                    mPlayerConfig.put("et", (duration - current)/1000);\n'
          '                    Toast.makeText(getContext(), "片尾已设为 距结束 " + stringForTime(duration - current), Toast.LENGTH_SHORT).show();')
    if a2 not in t:
        sys.exit('锚点丢失：片尾点击')
    t = t.replace(a2, b2, 1)

    a3 = '        mPlayerTimeResetBtn = findViewById(R.id.play_time_reset);'
    b3 = ('        mPlayerTimeResetBtn = findViewById(R.id.play_time_reset);\n'
          '        // 片头/片尾整块可点：外包容器后命中区只剩下面那行小字\n'
          '        for (final TextView b : new TextView[]{mPlayerTimeStartBtn, mPlayerTimeSkipBtn}) {\n'
          '            View wrap = (View) b.getParent();\n'
          '            if (wrap != null) {\n'
          '                wrap.setFocusable(true);\n'
          '                wrap.setClickable(true);\n'
          '                wrap.setOnClickListener(new OnClickListener() {\n'
          '                    @Override\n'
          '                    public void onClick(View v) { b.performClick(); }\n'
          '                });\n'
          '                wrap.setOnLongClickListener(new OnLongClickListener() {\n'
          '                    @Override\n'
          '                    public boolean onLongClick(View v) { b.performLongClick(); return true; }\n'
          '                });\n'
          '                b.setFocusable(false);\n'
          '            }\n'
          '        }')
    if a3 not in t:
        sys.exit('锚点丢失：findViewById 段')
    t = t.replace(a3, b3, 1)
    log('片头/片尾：点击提示 + 整块可点')

    # 旋屏：Java 里 showButton=false 时会被再藏一次
    a4 = '        mLandscapePortraitBtn.setVisibility(showButton ? VISIBLE : GONE);'
    b4 = '        mLandscapePortraitBtn.setVisibility(VISIBLE);'
    if a4 not in t:
        sys.exit('锚点丢失：旋屏可见性')
    t = t.replace(a4, b4, 1)
    log('旋屏按钮：不再被 showButton 条件隐藏')

    # 「推送」这个字样会出现在播放页的线路菜单里（push_agent 伪源），改名成“直链”
    for fname, old, new in (
        ('api/ApiConfig.java', 'sourceBean.setName("推送");', 'sourceBean.setName("直链");'),
        ('viewmodel/SourceViewModel.java', 'video.type = "推送";', 'video.type = "直链";'),
        ('viewmodel/SourceViewModel.java', 'urlInfo.flag = "推送";', 'urlInfo.flag = "直链";'),
    ):
        fp = os.path.join(SRC, 'app/src/main/java/com/github/tvbox/osc', fname)
        if not os.path.exists(fp):
            sys.exit('缺失文件 ' + fname)
        txt = open(fp, encoding='utf-8').read()
        if old not in txt:
            sys.exit('锚点丢失：' + old)
        txt = txt.replace(old, new, 1)
        open(fp, 'w', encoding='utf-8').write(txt)
    log('推送字样：改为“直链”（播放页线路菜单不再出现“推送”）')

    # 投屏按钮：底座用 SDK>=30 才显示，很多电视是 SDK 28/29，按钮直接被藏了
    gate = ('        if (Build.VERSION.SDK_INT < 30) {' + '\n'
            + '            mCastBtn.setVisibility(GONE);' + '\n'
            + '        } else {' + '\n'
            + '            mCastBtn.setVisibility(VISIBLE);' + '\n'
            + '        }')
    if gate in t:
        t = t.replace(gate, '        mCastBtn.setVisibility(VISIBLE);', 1)
        # 横竖屏切换复位处还有一次同样的门槛判定，一起放行
        n2 = t.count('mCastBtn.setVisibility(Build.VERSION.SDK_INT < 30 ? GONE : VISIBLE);')
        t = t.replace('mCastBtn.setVisibility(Build.VERSION.SDK_INT < 30 ? GONE : VISIBLE);',
                      'mCastBtn.setVisibility(VISIBLE);')
        log('投屏按钮：去掉 %d 处系统版本门槛，任何电视都显示' % (n2 + 1))
    else:
        sys.exit('锚点丢失：投屏按钮的系统版本判定')

    head = ('    public void updateDanmuSearchUiBtn() {' + '\n'
            + '        if (mDanmuSearchUiBtn == null) return;')
    if head not in t:
        sys.exit('锚点丢失：updateDanmuSearchUiBtn')
    t = t.replace(head, head + '\n' + PURGE_CALL, 1)
    write_text(jp(VOD), t)
    log('VodController：片头时间入上格、搜弹幕/视轨物理摘除（+1.5s/5s 复扫）')

    p = jp(PLAYER_HELPER)
    if os.path.isfile(p):
        h = read_text(p)
        for old, new in SHORT_NAMES:
            h = h.replace(old, new)
        write_text(p, h)
        log('播放器名称缩短：IJK / EXO / MX / Reex / Kodi / VLC')


# ---------------------------------------------------------------- 自检
def self_check():
    res = jp('app/src/main/res')
    colors = set()
    for f in os.listdir(os.path.join(res, 'values')):
        if f.endswith('.xml'):
            t = read_text(os.path.join(res, 'values', f))
            colors |= set(re.findall(r'<color\s+name="([^"]+)"', t))
    bad = []
    for sub in ('layout', 'drawable'):
        d = os.path.join(res, sub)
        for f in os.listdir(d):
            if not f.endswith('.xml'):
                continue
            t = read_text(os.path.join(d, f))
            for ref in re.findall(r'@color/([A-Za-z0-9_]+)', t):
                if ref not in colors:
                    bad.append('%s/%s -> @color/%s' % (sub, f, ref))
    need = list(ICONS.keys()) + ['htov']
    have = set()
    for sub in ('drawable', 'drawable-xxhdpi'):
        d = os.path.join(res, sub)
        if os.path.isdir(d):
            have |= {f.split('.')[0] for f in os.listdir(d)}
    miss = [n for n in need if n not in have]
    if bad or miss:
        print('  !! 自检失败：颜色缺失 %d 处，图标缺失 %s' % (len(bad), miss))
        for b in bad[:8]:
            print('     ' + b)
        sys.exit(1)
    log('自检通过：@color 全部存在，图标 %d 个齐全' % len(need))


# ---------------------------------------------------------------- 入口
def main():
    print('*** 脚本版本 %s ***' % VER)
    print('=== 底部菜单：图标 %s / 汉字 %s / 结构对齐 / 不动内核 ===' % (ICON_SIZE, TEXT_SIZE))
    print('源码：', SRC)
    write_icons()
    apply_layout()
    apply_java()
    self_check()
    print('-' * 46)
    print('=== 完成 ===')


if __name__ == '__main__':
    main()
