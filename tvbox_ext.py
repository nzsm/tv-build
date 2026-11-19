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
import re

ICONS = {'htov': '<layer-list xmlns:android="http://schemas.android.com/apk/res/android"><item android:width="23dp" android:height="23dp" android:gravity="center"><bitmap android:src="@drawable/htov_png" android:gravity="fill"/></item></layer-list>', 'v_prev': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="11.950" android:pivotY="10.575" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.050" android:translateY="1.425"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.826" android:scaleY="1.826"\n        android:translateX="-0.045" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M7,6c0.55,0 1,0.45 1,1v10c0,0.55 -0.45,1 -1,1s-1,-0.45 -1,-1L6,7c0,-0.55 0.45,-1 1,-1zM10.66,12.82l5.77,4.07c0.66,0.47 1.58,-0.01 1.58,-0.82L18.01,7.93c0,-0.81 -0.91,-1.28 -1.58,-0.82l-5.77,4.07c-0.57,0.4 -0.57,1.24 0,1.64z"/></group></group></vector>', 'v_next': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.833" android:scaleY="1.833"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M7.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L7.58,7.11C6.91,6.65 6,7.12 6,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM16,7v10c0,0.55 0.45,1 1,1s1,-0.45 1,-1V7c0,-0.55 -0.45,-1 -1,-1s-1,0.45 -1,1z"/></group></group></vector>', 'v_replay': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="11.975" android:pivotY="10.575" android:scaleX="0.9929" android:scaleY="0.9929" android:translateX="0.025" android:translateY="1.425"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.136" android:scaleY="1.136"\n        android:translateX="-0.057" android:translateY="-1.123"><path android:fillColor="@android:color/white" android:pathData="M12,5V2.21c0,-0.45 -0.54,-0.67 -0.85,-0.35l-3.8,3.79c-0.2,0.2 -0.2,0.51 0,0.71l3.79,3.79c0.32,0.31 0.86,0.09 0.86,-0.36V7c3.73,0 6.68,3.42 5.86,7.29 -0.47,2.27 -2.31,4.1 -4.57,4.57 -3.57,0.75 -6.75,-1.7 -7.23,-5.01 -0.07,-0.48 -0.49,-0.85 -0.98,-0.85 -0.6,0 -1.08,0.53 -1,1.13 0.62,4.39 4.8,7.64 9.53,6.72 3.12,-0.61 5.63,-3.12 6.24,-6.24C20.84,9.48 16.94,5 12,5z"/></group></group></vector>', 'v_replay_play': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="24" android:viewportHeight="24"\n    android:tint="#FFFFFF"><group android:pivotX="11.925" android:pivotY="10.875" android:scaleX="1.1382" android:scaleY="1.1382" android:translateX="0.075" android:translateY="1.125"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.136" android:scaleY="1.136"\n        android:translateX="-0.057" android:translateY="-1.123"><path android:strokeColor="@android:color/white" android:strokeWidth="2.2" android:fillColor="@android:color/transparent" android:pathData="M12,5 A7,7 0 1 1 11.99,5"/><path android:fillColor="@android:color/white" android:pathData="M9.85,8.4 L16.25,12.0 L9.85,15.6 Z"/></group></group></vector>', 'v_aspect': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M18,12c-0.55,0 -1,0.45 -1,1v2h-2c-0.55,0 -1,0.45 -1,1s0.45,1 1,1h3c0.55,0 1,-0.45 1,-1v-3c0,-0.55 -0.45,-1 -1,-1zM7,9h2c0.55,0 1,-0.45 1,-1s-0.45,-1 -1,-1L6,7c-0.55,0 -1,0.45 -1,1v3c0,0.55 0.45,1 1,1s1,-0.45 1,-1L7,9zM21,3L3,3c-1.1,0 -2,0.9 -2,2v14c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2zM20,19.01L4,19.01c-0.55,0 -1,-0.45 -1,-1L3,5.99c0,-0.55 0.45,-1 1,-1h16c0.55,0 1,0.45 1,1v12.02c0,0.55 -0.45,1 -1,1z"/></group></group></vector>', 'v_ffwd': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.309" android:scaleY="1.309"\n        android:translateX="-0.523" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M5.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L5.58,7.11C4.91,6.65 4,7.12 4,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM13,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63l-5.77,-4.07c-0.67,-0.47 -1.58,0 -1.58,0.81z"/></group></group></vector>', 'v_type': '<vector android:height="26dp"\n    android:tint="#FFFFFF"\n    android:viewportHeight="24"\n    android:viewportWidth="24"\n    android:width="26dp"\n    xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M21,3L3,3c-1.11,0 -2,0.89 -2,2v12c0,1.1 0.89,2 2,2h5v2h8v-2h5c1.1,0 1.99,-0.9 1.99,-2L23,5c0,-1.11 -0.9,-2 -2,-2zM21,17L3,17L3,5h18v12zM16,11l-7,4L9,7z" /></group></group></vector>', 'v_subtitle': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.1" android:scaleY="1.1"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M20,4L4,4c-1.1,0 -2,0.9 -2,2v12c0,1.1 0.9,2 2,2h16c1.1,0 2,-0.9 2,-2L22,6c0,-1.1 -0.9,-2 -2,-2zM4,12h4v2L4,14v-2zM14,18L4,18v-2h10v2zM20,18h-4v-2h4v2zM20,14L10,14v-2h10v2z"/></group></group></vector>', 'v_audio': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9906" android:scaleY="0.9906" android:translateX="0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.222" android:scaleY="1.222"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M12,5v8.55c-0.94,-0.54 -2.1,-0.75 -3.33,-0.32 -1.34,0.48 -2.37,1.67 -2.61,3.07 -0.46,2.74 1.86,5.08 4.59,4.65 1.96,-0.31 3.35,-2.11 3.35,-4.1V7h2c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2h-2c-1.1,0 -2,0.9 -2,2z"/></group></group></vector>', 'v_danmu': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp"\n    android:height="26dp"\n    android:viewportWidth="436"\n    android:viewportHeight="419"><group android:pivotX="218.000" android:pivotY="185.058" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="24.442"><group android:pivotX="218.0" android:pivotY="209.5"\n        android:scaleX="0.916" android:scaleY="0.916"\n        android:translateX="0.0" android:translateY="-25.507"><path\n      android:pathData="M322.65,272.14L274.13,272.14L274.13,290.36L328.16,290.36L328.16,318.2L274.13,318.2L274.13,347.96L242.96,347.96L242.96,318.2L188.7,318.2L188.7,290.36L242.96,290.36L242.96,272.14L194.21,272.14L194.21,147.1L216.3,147.1L209.39,129.82L238.16,129.82L245.13,147.1L271.73,147.1L278.7,129.82L307.53,129.82L300.32,147.1L322.88,147.1L322.65,272.14ZM115.05,189.58L152.26,189.58L152.26,164.62L110.25,164.62L110.25,135.09L182.96,135.09L182.96,218.35L143.59,218.35L142.18,244.78L184.66,244.78L177.92,347.02L117.22,347.02L117.22,316.79L148.39,316.79L151.79,273.55L110.25,273.55L115.05,189.58ZM244.89,243.08L244.89,223.16L222.81,223.16L222.81,243.08L244.89,243.08ZM244.89,195.79L244.89,176.11L222.81,176.11L222.81,195.79L244.89,195.79ZM294.06,243.08L294.06,223.16L272.02,223.16L272.02,243.08L294.06,243.08ZM294.06,195.79L294.06,176.11L272.02,176.11L272.02,195.79L294.06,195.79Z"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"/><path\n      android:pathData="M20.27,79.27Q0.5,99.04 0.5,127L0.5,351Q0.5,378.96 20.27,398.73Q40.04,418.5 68,418.5L368,418.5Q395.96,418.5 415.73,398.73Q435.5,378.96 435.5,351L435.5,127Q435.5,99.04 415.73,79.27Q395.96,59.5 368,59.5L68,59.5Q40.04,59.5 20.27,79.27ZM35.5,351L35.5,127Q35.5,113.54 45.02,104.02Q54.54,94.5 68,94.5L368,94.5Q381.46,94.5 390.98,104.02Q400.5,113.54 400.5,127L400.5,351Q400.5,364.46 390.98,373.98Q381.46,383.5 368,383.5L68,383.5Q54.54,383.5 45.02,373.98Q35.5,364.46 35.5,351Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FCFCFC"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/><path\n      android:pathData="M208.26,55.63L128.98,0.62L109.02,29.38L188.31,84.39Q201.24,93.36 216.98,93.4Q232.71,93.44 245.69,84.53L325.91,29.42L306.09,0.57L225.87,55.68Q221.89,58.41 217.06,58.4Q212.23,58.39 208.26,55.63Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/></group></group></vector>', 'v_back': '<vector android:autoMirrored="true" android:height="26dp"\n    android:tint="#FFFFFF" android:viewportHeight="24"\n    android:viewportWidth="24" android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.575" android:scaleX="0.9929" android:scaleY="0.9929" android:translateX="0.000" android:translateY="1.425"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.169" android:scaleY="1.169"\n        android:translateX="0.468" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M16.62,2.99c-0.49,-0.49 -1.28,-0.49 -1.77,0L6.54,11.3c-0.39,0.39 -0.39,1.02 0,1.41l8.31,8.31c0.49,0.49 1.28,0.49 1.77,0s0.49,-1.28 0,-1.77L9.38,12l7.25,-7.25c0.48,-0.48 0.48,-1.28 -0.01,-1.76z"/></group></group></vector>', 'ic_clock': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9906" android:scaleY="0.9906" android:translateX="-0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.047" android:scaleY="1.047"\n        android:translateX="-0.262" android:translateY="-1.31"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M11,8H13V14H11V8M12,20C8.13,20 5,16.87 5,13S8.13,6 12,6 19,9.13 19,13C19.7,13 20.36,13.13 21,13.35C21,13.23 21,13.12 21,13C21,10.88 20.26,8.93 19.03,7.39L20.45,5.97C20,5.46 19.55,5 19.04,4.56L17.62,6C16.07,4.74 14.12,4 12,4C7.03,4 3,8.03 3,13S7.03,22 12,22C12.59,22 13.16,21.94 13.71,21.83C13.4,21.25 13.18,20.6 13.08,19.91C12.72,19.96 12.37,20 12,20M15,1H9V3H15V1M16.5,16.5V21.5H21.5V16.5H16.5Z"/></group></group></vector>', 'play_skip': '<vector android:height="26dp" android:viewportHeight="1000"\n    android:viewportWidth="1000" android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="500.000" android:pivotY="423.958" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="76.042"><group android:pivotX="500.0" android:pivotY="500.0"\n        android:scaleX="0.932" android:scaleY="0.932"\n        android:translateX="0.0" android:translateY="-76.375"><path android:fillColor="#FFFFFFFF" android:pathData="M10,499.5c0,301.7 0.3,319.9 4.5,316.5C24,808.3 345.7,501.9 345.7,500.3c0,-0.8 -75.3,-73.4 -167.7,-161.1L10,179.6L10,499.5z"/><path android:fillColor="#FFFFFFFF" android:pathData="M414.1,498.9c0,203.1 1.1,319.9 2.6,319.4c2.6,-0.8 335.5,-316.2 335.5,-318c0,-0.5 -234,-223.5 -328.1,-312.5l-10,-9.3L414.1,498.9z"/><path android:fillColor="#FFFFFFFF" android:pathData="M820.9,500.5l0,321l84.5,-0L990,821.5L990,500.5l0,-320.9l-84.5,-0l-84.5,-0L820.9,500.5z"/></group></group></vector>', 'tk_unlock': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp"\n    android:height="26dp"\n    android:tint="#FFFFFF"\n    android:viewportWidth="24"\n    android:viewportHeight="24"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9906" android:scaleY="0.9906" android:translateX="-0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.047" android:scaleY="1.047"\n        android:translateX="0.0" android:translateY="-1.31"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M18,8h-1L17,6c0,-2.76 -2.24,-5 -5,-5S7,3.24 7,6h2c0,-1.66 1.34,-3 3,-3s3,1.34 3,3v2L6,8c-1.1,0 -2,0.9 -2,2v10c0,1.1 0.9,2 2,2h12c1.1,0 2,-0.9 2,-2L20,10c0,-1.1 -0.9,-2 -2,-2zM18,20L6,20L6,10h12v10zM12,17c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2z" /></group></group></vector>', 'v_cast': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="24" android:viewportHeight="24"\n    android:tint="#FFFFFF"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M1,18v3h3c0,-1.66 -1.34,-3 -3,-3zM1,14v2c2.76,0 5,2.24 5,5h2c0,-3.87 -3.13,-7 -7,-7zM1,10v2c4.97,0 9,4.03 9,9h2c0,-6.08 -4.93,-11 -11,-11zM21,3L3,3c-1.1,0 -2,0.9 -2,2v3h2L3,5h18v14h-7v2h7c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2z"/></group></group></vector>', 'tk_space': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="26" android:viewportHeight="26"><path android:fillColor="#00000000" android:pathData="M0,0 L26,0 L26,26 L0,26 Z" /></vector>'}

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

ICON_SIZE = '23dp'      # 图标位高度（26 → 23，整体缩 3dp）
TEXT_SIZE = '8dp'       # 汉字（10 → 8）
PAD_LR = '6dp'          # 每个按钮左右内边距 → 相邻 12dp ≈ 半个图标
PAD_TB = '10dp'
SEEK_INSET = '16dp'     # 进度条整行左右各收

RENAME = {'play_pre': '上集', 'play_next': '下集', 'landscape_portrait': '旋屏',
          'play_player': 'EXO'}

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
        xml = re.sub(r'android:(width|height)="[0-9.]+dp"',
                     'android:\\1="' + ICON_SIZE + '"', xml)
        write_text(os.path.join(ddir, name + '.xml'), xml)
    dpi = jp('app/src/main/res/drawable-xxhdpi')
    os.makedirs(dpi, exist_ok=True)
    with open(os.path.join(dpi, 'htov_png.png'), 'wb') as f:
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

    # ① 拆掉上游那层横向滚动，把按钮组提到 bottom_container 里
    hsv_old = pm.get(group)
    if hsv_old is not None and hsv_old.tag == 'HorizontalScrollView':
        par = pm[hsv_old]
        idx = list(par).index(hsv_old)
        margin_top = hsv_old.get(A + 'layout_marginTop')
        par.remove(hsv_old)
        if margin_top:
            group.set(A + 'layout_marginTop', margin_top)
        par.insert(idx, group)
        pm = parents(root)

    # ② 竖屏放不下时可左右滑动：外层横向滚动，撑满时按钮仍居中
    par = pm[group]
    idx = list(par).index(group)
    margin_bottom = group.get(A + 'layout_marginBottom')
    par.remove(group)
    hsv = ET.Element('HorizontalScrollView')
    hsv.set(A + 'layout_width', 'match_parent')
    hsv.set(A + 'layout_height', 'wrap_content')
    hsv.set(A + 'fillViewport', 'true')
    hsv.set(A + 'scrollbarAlwaysDrawHorizontalTrack', 'false')
    hsv.set(A + 'scrollbars', 'none')
    hsv.set(A + 'overScrollMode', 'never')
    hsv.set(A + 'focusable', 'false')
    hsv.set(A + 'descendantFocusability', 'afterDescendants')
    hsv.append(group)
    par.insert(idx, hsv)
    if margin_bottom:
        hsv.set(A + 'layout_marginBottom', margin_bottom)
        group.attrib.pop(A + 'layout_marginBottom', None)
    group.set(A + 'layout_width', 'wrap_content')
    group.set(A + 'gravity', 'center')
    pm = parents(root)
    log('按钮组外层加横向滚动（竖屏可左右滑，横屏撑满居中）')

    # ③ 顺序：进度条行 → 滚动按钮组 → 解析行
    seek_row = pm.get(find_id(root, 'curr_time'))
    block_parse = find_id(root, 'parse_root')
    for e in (seek_row, hsv, block_parse):
        if e is not None and e in list(bottom):
            bottom.remove(e)
    pos = 0
    for e in (seek_row, hsv, block_parse):
        if e is not None:
            bottom.insert(pos, e)
            pos += 1
    log('底部顺序：进度条 → 滚动按钮组 → 解析行')

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

    # ⓪ 进度条收边 / 时间框宽度：竖屏单独覆盖（条尽量长、贴两边）
    for rel, inset, minw in (('values', SEEK_INSET, '60dp'), ('values-port', '6dp', '34dp')):
        d = os.path.join(SRC, 'app/src/main/res', rel)
        os.makedirs(d, exist_ok=True)
        xml = ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
               + '    <dimen name="tk_seek_inset">' + inset + '</dimen>\n'
               + '    <dimen name="tk_time_minw">' + minw + '</dimen>\n'
               + '</resources>\n')
        open(os.path.join(d, 'tk_dimens.xml'), 'w', encoding='utf-8').write(xml)
    log('进度条收边：横屏 %s / 竖屏 6dp；时间框 60dp / 34dp' % SEEK_INSET)

    # ⑦ 进度条行：上下居中、左右各收 24dp、时间紧贴条两端
    if seek_row is not None:
        seek_row.set(A + 'gravity', 'center_vertical')
        seek_row.set(A + 'paddingLeft', '@dimen/tk_seek_inset')
        seek_row.set(A + 'paddingRight', '@dimen/tk_seek_inset')
        for c in list(seek_row):
            c.set(A + 'layout_gravity', 'center_vertical')
            if c.tag == 'SeekBar':
                c.set(A + 'layout_width', '0dp')
                c.set(A + 'layout_weight', '1')
                c.set(A + 'maxHeight', '4dp')
                c.set(A + 'thumbOffset', '0dp')
            else:
                c.set(A + 'layout_width', 'wrap_content')
                c.set(A + 'layout_weight', '0')
                c.set(A + 'gravity', 'center_vertical')
                c.set(A + 'textSize', '9dp')
                c.set(A + 'includeFontPadding', 'false')
        # 时间与条两端各 3dp、进度条下方到按钮排 -3dp、底板去掉、旋屏常显
        ct = find_id(root, 'curr_time'); tt = find_id(root, 'total_time')
        if ct is not None:
            ct.set(A + 'layout_marginEnd', '3dp')
            ct.set(A + 'textSize', '10dp')
            ct.set(A + 'textColor', '@android:color/white')
            ct.set(A + 'minWidth', '@dimen/tk_time_minw')
            ct.set(A + 'gravity', 'center_vertical|right')
        if tt is not None:
            tt.set(A + 'layout_marginStart', '3dp')
            tt.set(A + 'textSize', '10dp')
            tt.set(A + 'textColor', '#B3FFFFFF')
            tt.set(A + 'minWidth', '@dimen/tk_time_minw')
            tt.set(A + 'gravity', 'center_vertical|left')
        seek_row.set(A + 'layout_marginBottom', '7dp')
        bottom.set(A + 'background', '@null')
        sub = find_id(root, 'subtitle_view')
        if sub is not None:
            sub.set(A + 'layout_marginBottom', '104dp')
            log('字幕：底部抬高 104dp，不再压住按钮')
        lp = find_id(root, 'landscape_portrait')
        if lp is not None: lp.set(A + 'visibility', 'visible')
        log('间距：时间↔条 6dp、条↔按钮排 7dp；底板去掉；旋屏常显')

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
        slot.set(A + 'gravity', 'top|center_horizontal')
        slot.set(A + 'paddingTop', '3dp')
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
        android.widget.TextView slot = null;
        android.view.View btn = "片头".equals(label) ? mPlayerTimeStartBtn : mPlayerTimeSkipBtn;
        android.view.ViewParent p = (btn == null) ? null : btn.getParent();
        if (p instanceof android.view.ViewGroup) {
            slot = ((android.view.ViewGroup) p).findViewById(sid);
        }
        if (slot == null) slot = findViewById(sid);
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
               ('"Reex播放器"', '"Reex"'), ('"Kodi播放器"', '"Kodi"'), ('"VLC播放器"', '"VLC"'), ('"附近TVBox"', '"TVBox"')]


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

    # 旋屏按钮文字别被横/竖屏状态改写，固定“旋屏”；硬解按钮常显
    for o1, n1 in (
        ('mLandscapePortraitBtn.setText("竖屏");', 'mLandscapePortraitBtn.setText("旋屏");'),
        ('mLandscapePortraitBtn.setText("横屏");', 'mLandscapePortraitBtn.setText("旋屏");'),
        ('mPlayerIJKBtn.setVisibility(playerType == 1 ? VISIBLE : GONE);',
         'mPlayerIJKBtn.setVisibility(getResources().getConfiguration().orientation == Configuration.ORIENTATION_PORTRAIT ? GONE : VISIBLE);'),
    ):
        if o1 not in t:
            sys.exit('锚点丢失：' + o1)
        t = t.replace(o1, n1)
    pf = jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java')
    if os.path.isfile(pf):
        h = read_text(pf)
        h = h.replace('mController.mLandscapePortraitBtn.setText("竖屏");',
                      'mController.mLandscapePortraitBtn.setText("旋屏");')
        write_text(pf, h)
    log('旋屏文字固定为“旋屏”、硬解常显')

    # 竖屏别再偷偷把进度条两端时间藏掉
    for o6, n6 in (
        ('if (mCurrentTime != null) mCurrentTime.setVisibility(isPortrait ? GONE : VISIBLE);',
         'if (mCurrentTime != null) mCurrentTime.setVisibility(VISIBLE);'),
        ('if (mTotalTime != null) mTotalTime.setVisibility(isPortrait ? GONE : VISIBLE);',
         'if (mTotalTime != null) mTotalTime.setVisibility(VISIBLE);'),
    ):
        if o6 not in t:
            sys.exit('锚点丢失：' + o6)
        t = t.replace(o6, n6, 1)

    # 竖屏分支里片头/片尾/重置也被藏掉了 —— 全部保留可点（用硬解那行做锚，避免误伤直播分支）
    NL = chr(10)
    pblock = ("            mPlayerIJKBtn.setVisibility(GONE);" + NL
              + "            mPlayerTimeStartEndText.setVisibility(GONE);" + NL
              + "            mPlayerTimeStartBtn.setVisibility(GONE);" + NL
              + "            mPlayerTimeSkipBtn.setVisibility(GONE);" + NL
              + "            mPlayerTimeResetBtn.setVisibility(GONE);" + NL)
    nblock = ("            mPlayerIJKBtn.setVisibility(GONE);" + NL
              + "            mPlayerTimeStartEndText.setVisibility(GONE);" + NL
              + "            mPlayerTimeStartBtn.setVisibility(VISIBLE);" + NL
              + "            mPlayerTimeSkipBtn.setVisibility(VISIBLE);" + NL
              + "            mPlayerTimeResetBtn.setVisibility(VISIBLE);" + NL)
    if pblock not in t:
        sys.exit('锚点丢失：竖屏分支片头片尾块')
    t = t.replace(pblock, nblock, 1)
    log('竖屏：进度条两端时间、片头/片尾/重置 全部保留')

    o5 = '        if (showButton) mLandscapePortraitBtn.setText(isPortrait ? "横屏" : "竖屏");'
    n5 = '        mLandscapePortraitBtn.setText("旋屏");'
    if o5 not in t:
        sys.exit('锚点丢失：旋屏文字（showButton 处）')
    t = t.replace(o5, n5, 1)

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
