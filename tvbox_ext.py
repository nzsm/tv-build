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

import glob
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
    for rel, inset, minw in (('values', SEEK_INSET, '78dp'), ('values-port', '2dp', '52dp')):
        d = os.path.join(SRC, 'app/src/main/res', rel)
        os.makedirs(d, exist_ok=True)
        xml = ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
               + '    <dimen name="tk_seek_inset">' + inset + '</dimen>\n'
               + '    <dimen name="tk_time_minw">' + minw + '</dimen>\n'
               + '    <dimen name="tk_time_ts">' + ('12dp' if rel == 'values' else '10dp') + '</dimen>\n'
               + '</resources>\n')
        open(os.path.join(d, 'tk_dimens.xml'), 'w', encoding='utf-8').write(xml)
    log('进度条收边：横屏 %s / 竖屏 2dp；时间框 78dp / 52dp' % SEEK_INSET)

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
                c.set(A + 'maxHeight', '2dp')
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
            ct.set(A + 'textSize', '@dimen/tk_time_ts')
            ct.set(A + 'textColor', '@android:color/white')
            ct.set(A + 'minWidth', '@dimen/tk_time_minw')
            ct.set(A + 'gravity', 'center_vertical|right')
        if tt is not None:
            tt.set(A + 'layout_marginStart', '3dp')
            tt.set(A + 'textSize', '@dimen/tk_time_ts')
            tt.set(A + 'textColor', '#B3FFFFFF')
            tt.set(A + 'minWidth', '@dimen/tk_time_minw')
            tt.set(A + 'gravity', 'center_vertical|left')
        seek_row.set(A + 'layout_marginBottom', '5dp')
        bottom.set(A + 'background', '@null')
        sub = find_id(root, 'subtitle_view')
        if sub is not None:
            sub.set(A + 'layout_marginBottom', '104dp')
            log('字幕：底部抬高 104dp，不再压住按钮')
        lp = find_id(root, 'landscape_portrait')
        if lp is not None: lp.set(A + 'visibility', 'gone')
        log('间距：时间↔条 3dp、条↔按钮排 5dp；底板去掉；旋屏按画面自动显示')

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
        slot.set(A + 'paddingTop', '8dp')
        slot.set(A + 'textSize', '12dp')
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

    # 轨道再细一档：3dp -> 2dp
    seek_drawable = jp('app/src/main/res/drawable/shape_player_control_vod_seek.xml')
    if os.path.isfile(seek_drawable):
        sd = read_text(seek_drawable).replace('android:height="3dp"', 'android:height="2dp"')
        write_text(seek_drawable, sd)
        log('进度条轨道：3dp -> 2dp')


# ---------------------------------------------------------------- Java
TIME_PATCH = [
    ('mPlayerTimeStartBtn.setText(start == 0 ? "片头" : stringForTime(start * 1000));',
     'mPlayerTimeStartBtn.setText(buildTimeLabel(start == 0 ? "00:00" : stringForTime(start * 1000), "片头"));'),
    ('mPlayerTimeSkipBtn.setText(end == 0 ? "片尾" : stringForTime(end * 1000));',
     'mPlayerTimeSkipBtn.setText(buildTimeLabel(end == 0 ? "00:00" : stringForTime(end * 1000), "片尾"));'),

    ('mCurrentTime.setText(stringForTime(safeTimeMs(newPosition)));',
     'mCurrentTime.setText(formatHMS(safeTimeMs(newPosition)));'),
    ('mCurrentTime.setText(stringForTime(position));',
     'mCurrentTime.setText(formatHMS(position));'),
    ('mTotalTime.setText(stringForTime(duration));',
     'mTotalTime.setText(formatHMS(duration));'),
    ('Toast.makeText(getContext(), "已移除视频广告 "+M3u8.currentAdCount+" 条", Toast.LENGTH_SHORT).show();',
     '// 静默：不再弹出广告过滤条数提示'),
]

HELPERS = '''
    private String formatHMS(long timeMs) {
        if (timeMs < 0) timeMs = 0;
        long total = timeMs / 1000;
        long h = total / 3600;
        long m = (total % 3600) / 60;
        long sec = total % 60;
        return String.format("%02d:%02d:%02d", h, m, sec);
    }

    private CharSequence buildTimeLabel(String time, String label) {
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


BUILTIN_ADS = ['mimg.0c1q0l.cn', 'www.googletagmanager.com', 'www.google-analytics.com', 'mc.usihnbcq.cn', 'mg.g1mm3d.cn', 'mscs.svaeuzh.cn', 'cnzz.hhttm.top', 'tp.vinuxhome.com', 'cnzz.mmstat.com', 'www.baihuillq.com', 's23.cnzz.com', 'z3.cnzz.com', 'c.cnzz.com', 'stj.v1vo.top', 'z12.cnzz.com', 'img.mosflower.cn', 'tips.gamevvip.com', 'ehwe.yhdtns.com', 'xdn.cqqc3.com', 'www.jixunkyy.cn', 'sp.chemacid.cn', 'hm.baidu.com', 's9.cnzz.com', 'z6.cnzz.com', 'um.cavuc.com', 'mav.mavuz.com', 'wofwk.aoidf3.com', 'z5.cnzz.com', 'xc.hubeijieshikj.cn', 'tj.tianwenhu.com', 'xg.gars57.cn', 'k.jinxiuzhilv.com', 'cdn.bootcss.com', 'ppl.xunzhuo123.com', 'xomk.jiangjunmh.top', 'img.xunzhuo123.com', 'z1.cnzz.com', 's13.cnzz.com', 'xg.huataisangao.cn', 'z7.cnzz.com', 'z2.cnzz.com', 's96.cnzz.com', 'q11.cnzz.com', 'thy.dacedsfa.cn', 'xg.whsbpw.cn', 's19.cnzz.com', 'z8.cnzz.com', 's4.cnzz.com', 'f5w.as12df.top', 'ae01.alicdn.com', 'www.92424.cn', 'k.wudejia.com', 'vivovip.mmszxc.top', 'qiu.xixiqiu.com', 'cdnjs.hnfenxun.com', 'cms.qdwght.com', 'iqiyi.hbuioo.com', 'vip.ffzyad.com', 'wan.51img1.com', 'https://lf1-cdn-tos.bytegoofy.com/obj/tos-cn-i-dy/455ccf9e8ae744378118e4bd289288dd']

BUILTIN_BLK = [{'name': '暴风', 'hosts': ['bfzy', 'bfbfvip', 'bfengbf'], 'regex': ['#EXTINF.*?\\s+.*?adjump.*?\\.ts']}, {'name': '量子', 'hosts': ['vip.lz', 'hd.lz', '.cdnlz'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:7\\.166667,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXTINF.*?\\s+.*?08646.*?\\.ts', '#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF.*?6\\.667,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXTINF.*?\\s+.*?48234.*?\\.ts', '#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF.*?7\\.067,[\\s\\S]*?#EXT-X-DISCONTINUITY', '17.19', '19.63']}, {'name': '非凡', 'hosts': ['vip.ffzy', 'hd.ffzy', 'super.ffzy', 'cachem3u8.2s0'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:6\\.400000,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:6\\.666667,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXTINF.*?\\s+.*?1171(057).*?\\.ts', '#EXTINF.*?\\s+.*?6d7b(077).*?\\.ts', '#EXTINF.*?\\s+.*?6718a(403).*?\\.ts', '17.99', '14.45']}, {'name': '索尼', 'hosts': ['suonizy'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:1\\.000000,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXTINF.*?\\s+.*?p1ayer.*?\\.ts', '#EXTINF.*?\\s+.*?\\/video\\/original.*?\\.ts']}, {'name': '快看', 'hosts': ['kuaikan'], 'regex': ['#EXT-X-KEY:METHOD=NONE\\r*\\n*#EXTINF:5,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXT-X-KEY:METHOD=NONE\\r*\\n*#EXTINF:2\\.4,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXT-X-KEY:METHOD=NONE\\r*\\n*#EXTINF:1\\.467,[\\s\\S]*?#EXT-X-DISCONTINUITY']}, {'name': 'leshiyun', 'hosts': ['leshiyuncdn'], 'regex': ['15.92']}, {'name': '看影网', 'hosts': ['fentvoss'], 'regex': ['38.68', '38.12', '38.80', '30.08', '44.00', '36.80', '40.68', '29.08', '29.28', '24.88']}, {'name': '1080zyk', 'hosts': ['high24-playback', 'high20-playback', 'yzzy.play', 'yzzy-dy'], 'regex': ['16.63', '17.66']}, {'name': 'ikun', 'hosts': ['bfikuncdn'], 'regex': ['#EXTINF.*?\\s+.*?XR8pDxQk.*?\\.ts', '#EXTINF.*?\\s+.*?p5XQill8.*?\\.ts']}, {'name': '黑木耳hmr', 'hosts': ['hmrvideo'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:3\\.366667,[\\s\\S]*?#EXT-X-DISCONTINUITY']}, {'name': 'ryplay', 'hosts': ['cdn.ryplay'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:6\\.633333,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:8\\.333333,[\\s\\S].*?\\.ts', '#EXTINF:2\\.933333,[\\s\\S].*?\\.ts']}, {'name': '555DM', 'hosts': ['cqxfjz'], 'regex': ['10.56']}, {'name': '海外看', 'hosts': ['haiwaikan'], 'regex': ['10.0099', '10.3333', '16.0599', '8.1748', '10.85']}, {'name': '磁力广告', 'hosts': ['magnet'], 'regex': ['更多', '社 區', 'x u u', '最 新', '更 新', '社 区', '有趣', '有 趣', '英皇体育', '全中文AV在线', '澳门皇冠赌场', '哥哥快来', '美女荷官', '裸聊', '新片首发', 'UUE29']}, {'name': '通用-广告片段过滤', 'hosts': ['*'], 'regex': ['#EXTINF:\\s*([0-4]\\.\\d+|5\\.0),.*?(ad|promo|preroll|midroll|postroll)', '#EXT-X-DISCONTINUITY[^#]*#EXTINF[^#]*adjump', '.*popads\\.net.*', '.*doubleclick\\.net.*']}, {'name': '通用-广告域名拦截', 'hosts': ['*'], 'regex': ['.*googlesyndication\\.com.*', '.*propellerads\\.com.*', '.*adnxs\\.com.*', '.*ae01\\.alicdn\\.com.*']}]

BUILTIN_PAGE_KW = ['doubleclick.net', 'googlesyndication.com', 'googletagmanager.com', 'cnzz.com', 'um.cavuc.com', 'ae01.alicdn.com', 'tips.gamevvip.com', 'popads.net', 'propellerads.com', 'adnxs.com', 'adsafeprotected.com', 'cms.qdwght.com', 'api.htpan.net', 'ppl.xunzhuo123.com', 'qiu.xixiqiu.com']

BUILTIN_PAGE_RE = ['.*\\.cnzz\\..*', '.*popads\\.net.*', '.*googlesyndication.*', '.*doubleclick\\.net.*', '.*propellerads\\.com.*']

BUILTIN_PAGE_SEL = ["iframe[src*='ads']", "iframe[src*='pop']", 'div.ad', 'div.ads', 'div.adbox', 'div.ad-wrap', "div[class*='advert']", "div[class*='banner']", "div[class*='popup']", "div[class*='modal-ad']", "div[class*='cnzz']", "div[id*='cnzz']", "div[class*='floating']", "div[class*='float-ads']", "img[src*='ae01.alicdn']", "img[src*='tips.gamevvip']", "script[src*='cnzz']", "script[src*='googletag']", "script[src*='doubleclick']"]

BUILTIN_STREAM_RE = ['#EXTINF[^\\n]*?[/._-](?:promo|preroll|midroll|postroll|advert|popup_ad|adbreak|adpod)[/._-]', '#EXTINF:\\s*([0-4]\\.\\d+|5\\.0),.*?(ad|promo|popup|preroll)', '#EXT-X-DISCONTINUITY[^#]*#EXTINF[^#]*adjump', '#EXT-X-DISCONTINUITY[^#]*#EXTINF[^#]*p1ayer', '#EXT-X-DISCONTINUITY[^#]*#EXTINF[^#]*08646.*?\\.ts', '#EXT-X-DISCONTINUITY[^#]*#EXTINF[^#]*1171.*?\\.ts']

BUILTIN_HEADER_HOSTS = ['doubleclick.net', 'googletagmanager.com', 'googlesyndication.com', 'cnzz.com', 'um.cavuc.com', 'ae01.alicdn.com', 'tips.gamevvip.com', 'popads.net', 'propellerads.com', 'adnxs.com', 'adsafeprotected.com']


def emit_builtin():
    """把仓库里的去广告规则固化成 BuiltinAdRules.java（不依赖订阅）"""
    esc = lambda v: v.replace('\\', '\\\\').replace('"', '\\"')

    def lit(items):
        return 'list(' + ', '.join('"%s"' % esc(i) for i in items) + ')'

    lines = [
        'package com.github.tvbox.osc.util;',
        '',
        'import java.util.ArrayList;',
        '',
        'public class BuiltinAdRules {',
        '',
        '    private static ArrayList<String> list(String... items) {',
        '        ArrayList<String> out = new ArrayList<>();',
        '        for (String s : items) out.add(s);',
        '        return out;',
        '    }',
        '',
        '    public static void apply() {',
    ]
    for a in BUILTIN_ADS:
        lines.append('        AdBlocker.addAdHost("%s");' % esc(a))
    for b in BUILTIN_BLK:
        adsRe = [r for r in b['regex'] if ('#EXTINF' in r or '#EXT-X-DISCONTINUITY' in r)]
        plain = [r for r in b['regex'] if r not in adsRe]
        for host in b['hosts']:
            if adsRe:
                lines.append('        VideoParseRuler.addHostRegex("%s", %s);' % (esc(host), lit(adsRe)))
            if plain:
                lines.append('        VideoParseRuler.addHostRule("%s", %s);' % (esc(host), lit(plain)))
    for r in BUILTIN_STREAM_RE:
        lines.append('        M3u8.addGlobalRegex("%s");' % esc(r))
    for k in BUILTIN_PAGE_KW:
        lines.append('        AdBlocker.addUrlKeyword("%s");' % esc(k))
    for k in BUILTIN_HEADER_HOSTS:
        lines.append('        AdBlocker.addUrlKeyword("%s");' % esc(k))
    for r in BUILTIN_PAGE_RE:
        lines.append('        AdBlocker.addUrlRegex("%s");' % esc(r))
    for sel in BUILTIN_PAGE_SEL:
        lines.append('        AdBlocker.addPageSelector("%s");' % esc(sel))
    lines += ['    }', '}', '']
    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/BuiltinAdRules.java'), chr(10).join(lines))


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
    a4 = '        mLandscapePortraitBtn.setVisibility(showButton ? VISIBLE : GONE);'  # 保持上游自动判定
    b4 = a4  # 不再强改可见性：电视隐藏、竖屏视频/短视频才显示
    if a4 not in t:
        sys.exit('锚点丢失：旋屏可见性')
    t = t.replace(a4, b4, 1)
    log('旋屏按钮：保持上游自动判定（电视/横屏视频不显示）')

    # 旋屏按钮文字别被横/竖屏状态改写，固定“旋屏”；硬解按钮常显
    for o1, n1 in (
        ('mLandscapePortraitBtn.setText("竖屏");', 'mLandscapePortraitBtn.setText("旋屏");'),
        ('mLandscapePortraitBtn.setText("横屏");', 'mLandscapePortraitBtn.setText("旋屏");'),
        ('mPlayerIJKBtn.setVisibility(playerType == 1 ? VISIBLE : GONE);',
         'mPlayerIJKBtn.setVisibility(playerType == 1 && getResources().getConfiguration().orientation != Configuration.ORIENTATION_PORTRAIT ? VISIBLE : GONE);'),
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

    # ===== 安全 DNS：国内 2 家 + 国外 2 家；去广告默认开启 =====
    og = jp('app/src/main/java/com/github/tvbox/osc/util/OkGoHelper.java')
    if os.path.isfile(og):
        h = read_text(og)
        old_dns = ('    private static final String dnsConfigJson = "["\n'
                   + '            + "{\\\"name\\\": \\\"腾讯\\\", \\\"url\\\": \\\"https://doh.pub/dns-query\\\"}, "\n')
        i0 = h.find('    private static final String dnsConfigJson = ')
        i1 = h.find(';', h.find('";', i0)) + 1
        if i0 == -1 or i1 <= i0:
            sys.exit('锚点丢失：dnsConfigJson')
        new_dns = ('    private static final String dnsConfigJson = "["' + chr(10)
                   + '            + "{\\\"name\\\": \\\"腾讯\\\", \\\"url\\\": \\\"https://doh.pub/dns-query\\\"}, "' + chr(10)
                   + '            + "{\\\"name\\\": \\\"阿里\\\", \\\"url\\\": \\\"https://dns.alidns.com/dns-query\\\"}, "' + chr(10)
                   + '            + "{\\\"name\\\": \\\"Cloudflare\\\", \\\"url\\\": \\\"https://1.1.1.1/dns-query\\\", \\\"ips\\\": [\\\"1.1.1.1\\\", \\\"1.0.0.1\\\"]}, "' + chr(10)
                   + '            + "{\\\"name\\\": \\\"Google\\\", \\\"url\\\": \\\"https://dns.google/dns-query\\\", \\\"ips\\\": [\\\"8.8.8.8\\\", \\\"8.8.4.4\\\"]}"' + chr(10)
                   + '            + "]";')
        h = h[:i0] + new_dns + h[i1:]
        write_text(og, h)

    for rel, cnt in (('ui/fragment/ModelSettingFragment.java', 2), ('ui/fragment/PlayFragment.java', 1)):
        fp = os.path.join(SRC, 'app/src/main/java/com/github/tvbox/osc', rel)
        if not os.path.isfile(fp):
            sys.exit('缺失文件 ' + rel)
        txt = read_text(fp)
        txt = txt.replace('Hawk.get(HawkConfig.M3U8_PURIFY, false)', 'Hawk.get(HawkConfig.M3U8_PURIFY, true)')
        write_text(fp, txt)
    log('DNS：腾讯/阿里 + Cloudflare/Google；去广告（M3u8 净化）默认开启')


    # ===== 吸收 tvbox-server 的去广告 / DNS 规则 =====
    ac = jp('app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java')
    h = read_text(ac)

    # (1) 内置广告域名：55 条 → 118 条（来自 tvbox-server/tvbox.json 的 ads 字段）
    i0 = h.find('\\"ads\\":[')
    i1 = h.find(']}', i0)
    assert i0 > 0 and i1 > i0, '锚点丢失：ads 字面量'
    ADS_LIT = r'''\"doubleclick.net\",\"googleads.g.doubleclick.net\",\"googlesyndication.com\",\"imasdk.googleapis.com\",\"securepubads.g.doubleclick.net\",\"2mdn.net\",\"moatads.com\",\"adsafeprotected.com\",\"adnxs.com\",\"pagead2.googlesyndication.com\",\"static.doubleclick.net\",\"tpc.googlesyndication.com\"'''
    h = h[:i0] + r'\"ads\":[' + ADS_LIT + ']}' + h[i1 + 2:]
    # 订阅 ads 不再合并（统计类噪声大，只用公网视频广告规则）
    h = h.replace('        if(infoJson.has("ads")){', '        if(false && infoJson.has("ads")){', 1)


    # (3) 订阅 doh（全是境外节点、且会把选择重置成"关闭"）→ 内置列表优先，不改动用户所选
    old_doh = ('        if (infoJson.has("doh")) {' + chr(10) +
               '            String doh_json = infoJson.getAsJsonArray("doh").toString();' + chr(10) +
               '            if(!Hawk.get(HawkConfig.DOH_JSON, "").equals(doh_json)){' + chr(10) +
               '                Hawk.put(HawkConfig.DOH_URL, 0);' + chr(10) +
               '                Hawk.put(HawkConfig.DOH_JSON,doh_json);' + chr(10) +
               '            }' + chr(10) +
               '        }else {' + chr(10) +
               '            Hawk.put(HawkConfig.DOH_JSON,"");' + chr(10) +
               '        }')
    new_doh = ('        // 安全DNS以内置列表为准（腾讯/阿里 + Cloudflare/Google）；订阅 doh 不再覆盖、' + chr(10) +
               '        // 也不再把它重置成"关闭"' + chr(10) +
               '        if (!infoJson.has("doh")) {' + chr(10) +
               '            Hawk.put(HawkConfig.DOH_JSON,"");' + chr(10) +
               '        }')
    assert old_doh in h, '锚点丢失：doh 分支原文'
    h = h.replace(old_doh, new_doh, 1)

    write_text(ac, h)

    # (5) AdBlocker 增强：URL 关键字/正则、页面元素移除脚本
    ab_java = r"""package com.github.tvbox.osc.util;

import android.webkit.WebResourceResponse;

import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;

public class AdBlocker {

    // 广告域名（内置 + 订阅）
    private static final List<String> AD_HOSTS = new ArrayList<>();
    // 公网清单更新的视频广告域名（后缀匹配）
    private static final Set<String> REMOTE_HOSTS = new HashSet<>();
    // 网页 URL 关键字
    private static final List<String> URL_KEYWORDS = new ArrayList<>();
    // 网页 URL 正则
    private static final List<Pattern> URL_REGEX = new ArrayList<>();
    // 播放页要摘掉的元素选择器
    private static final List<String> PAGE_SELECTORS = new ArrayList<>();

    public static void clear() {
        AD_HOSTS.clear();
        REMOTE_HOSTS.clear();
        URL_KEYWORDS.clear();
        URL_REGEX.clear();
        PAGE_SELECTORS.clear();
    }

    public static boolean isEmpty() {
        return AD_HOSTS.isEmpty() && REMOTE_HOSTS.isEmpty();
    }

    public static void addAdHost(String host) {
        if (host != null && !AD_HOSTS.contains(host)) AD_HOSTS.add(host);
    }

    public static boolean hasHost(String host) {
        return AD_HOSTS.contains(host);
    }

    public static void addUrlKeyword(String keyword) {
        if (keyword == null) return;
        String k = keyword.trim().toLowerCase();
        if (k.length() > 2 && !URL_KEYWORDS.contains(k)) URL_KEYWORDS.add(k);
    }

    public static void addUrlRegex(String regex) {
        if (regex == null) return;
        for (Pattern p : URL_REGEX) {
            if (p.pattern().equals(regex)) return;
        }
        try {
            URL_REGEX.add(Pattern.compile(regex));
        } catch (Throwable ignored) {
        }
    }

    public static void addPageSelector(String selector) {
        if (selector != null && selector.length() > 2 && !PAGE_SELECTORS.contains(selector)) PAGE_SELECTORS.add(selector);
    }

    public static void addRemoteHost(String host) {
        if (host == null) return;
        String h = host.trim().toLowerCase();
        if (h.length() > 3 && !REMOTE_HOSTS.contains(h)) REMOTE_HOSTS.add(h);
    }

    public static void clearRemote() {
        REMOTE_HOSTS.clear();
    }

    public static int remoteCount() {
        return REMOTE_HOSTS.size();
    }

    public static boolean hasRemoteHost(String host) {
        return host != null && REMOTE_HOSTS.contains(host.trim().toLowerCase());
    }

    private static String hostOf(String url) {
        String host = url;
        int scheme = host.indexOf("://");
        if (scheme > 0) host = host.substring(scheme + 3);
        int slash = host.indexOf('/');
        if (slash >= 0) host = host.substring(0, slash);
        int question = host.indexOf('?');
        if (question >= 0) host = host.substring(0, question);
        int colon = host.indexOf(':');
        if (colon >= 0) host = host.substring(0, colon);
        int at = host.indexOf('@');
        if (at >= 0) host = host.substring(at + 1);
        return host.toLowerCase();
    }

    private static boolean hitRemote(String url) {
        if (REMOTE_HOSTS.isEmpty()) return false;
        String host = hostOf(url);
        while (true) {
            if (REMOTE_HOSTS.contains(host)) return true;
            int dot = host.indexOf('.');
            if (dot < 0) return false;
            host = host.substring(dot + 1);
        }
    }

    public static boolean isAd(String url) {
        if (url == null) return false;
        String lower = url.toLowerCase();
        for (String adHost : AD_HOSTS) {
            if (lower.contains(adHost)) return true;
        }
        for (String keyword : URL_KEYWORDS) {
            if (lower.contains(keyword)) return true;
        }
        for (Pattern pattern : URL_REGEX) {
            try {
                if (pattern.matcher(lower).find()) return true;
            } catch (Throwable ignored) {
            }
        }
        return hitRemote(url);
    }

    // 播放页（WebView 解析类源）加载完后摘除广告元素
    public static String removeElementScript() {
        if (PAGE_SELECTORS.isEmpty()) return "";
        StringBuilder sb = new StringBuilder();
        sb.append("(function(){try{var list=[");
        for (int i = 0; i < PAGE_SELECTORS.size(); i++) {
            if (i > 0) sb.append(",");
            sb.append('"').append(PAGE_SELECTORS.get(i).replace("\\", "\\\\").replace("\"", "\\\"")).append('"');
        }
        sb.append("];for(var i=0;i<list.length;i++){try{var els=document.querySelectorAll(list[i]);for(var j=0;j<els.length;j++){var el=els[j];if(el&&el.parentNode)el.parentNode.removeChild(el);}}catch(e){}}");
        sb.append("}catch(e){}})();");
        return sb.toString();
    }

    public static WebResourceResponse createEmptyResource() {
        return new WebResourceResponse("text/plain", "utf-8", new ByteArrayInputStream("".getBytes()));
    }

}
"""
    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/AdBlocker.java'), ab_java)

    log('去广告/ DNS：内置视频广告域名 + 内置 DoH（不读订阅自定义字段）')


    # ===== 打开设置页自动更新广告规则（源自 tvbox-server 的 ads 字段） =====
    ar = r"""package com.github.tvbox.osc.util;

import android.app.Activity;
import android.content.Context;
import android.widget.Toast;

import com.orhanobut.hawk.Hawk;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.LinkedHashSet;
import java.util.Set;

public class AdRuleUpdater {

    // 公共广告规则源（DNS 级域名清单，官方维护）
    public static final String[] RULES_URLS = {
            "https://anti-ad.net/domains.txt"
    };
    private static final long MIN_INTERVAL = 86400000L;
    private static final String KEY_TIME = "ad_rules_update_time";
    private static final String CACHE_FILE = "ad_rules_cache.txt";
    private static final int MAX_HOSTS = 20000;
    private static volatile boolean running = false;
    private static volatile boolean cacheLoaded = false;

    public static void loadCache(Context context) {
        if (cacheLoaded || context == null) return;
        cacheLoaded = true;
        BufferedReader br = null;
        try {
            File file = new File(context.getCacheDir(), CACHE_FILE);
            if (!file.exists()) return;
            br = new BufferedReader(new InputStreamReader(new FileInputStream(file), "UTF-8"));
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.length() > 3) AdBlocker.addRemoteHost(line);
            }
        } catch (Throwable t) {
            t.printStackTrace();
        } finally {
            try {
                if (br != null) br.close();
            } catch (Throwable ignored) {
            }
        }
    }

    public static void clearCache(Context context) {
        AdBlocker.clearRemote();
        try {
            File file = new File(context.getCacheDir(), CACHE_FILE);
            if (file.exists()) file.delete();
        } catch (Throwable t) {
            t.printStackTrace();
        }
    }

    public static void autoUpdate(final Activity activity) {
        if (activity == null) return;
        loadCache(activity);
        if (running) return;
        long last = Hawk.get(KEY_TIME, 0L);
        if (System.currentTimeMillis() - last < MIN_INTERVAL) return;
        running = true;
        new Thread(new Runnable() {
            @Override
            public void run() {
                int added = 0;
                boolean ok = false;
                Set<String> hosts = new LinkedHashSet<>();
                try {
                    for (String rulesUrl : RULES_URLS) {
                        String content = fetch(rulesUrl);
                        if (content != null) parse(content, hosts);
                        if (hosts.size() > MAX_HOSTS) break;
                    }
                    if (hosts.size() > 0) {
                        ok = true;
                        writeCache(activity, hosts);
                        for (String host : hosts) {
                            if (!AdBlocker.hasRemoteHost(host)) {
                                AdBlocker.addRemoteHost(host);
                                added++;
                            }
                        }
                        Hawk.put(KEY_TIME, System.currentTimeMillis());
                    }
                } catch (Throwable t) {
                    t.printStackTrace();
                }
                final int n = added;
                final boolean success = ok;
                if (activity.isFinishing()) {
                    running = false;
                    return;
                }
                activity.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        running = false;
                        if (success) {
                            Toast.makeText(activity, n > 0 ? "视频广告规则已更新，新增 " + n + " 条，共 " + AdBlocker.remoteCount() + " 条" : "视频广告规则已是最新，共 " + AdBlocker.remoteCount() + " 条", Toast.LENGTH_SHORT).show();
                        } else {
                            Toast.makeText(activity, "视频广告规则更新失败，沿用已有规则", Toast.LENGTH_SHORT).show();
                        }
                    }
                });
            }
        }).start();
    }

    private static String fetch(String url) {
        HttpURLConnection conn = null;
        BufferedReader br = null;
        try {
            conn = (HttpURLConnection) new URL(url).openConnection();
            conn.setConnectTimeout(10000);
            conn.setReadTimeout(15000);
            conn.setRequestProperty("User-Agent", "Mozilla/5.0 TVBox");
            InputStream in = conn.getInputStream();
            br = new BufferedReader(new InputStreamReader(in, "UTF-8"));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) {
                sb.append(line).append('\n');
            }
            return sb.toString();
        } catch (Throwable t) {
            return null;
        } finally {
            try {
                if (br != null) br.close();
            } catch (Throwable ignored) {
            }
            try {
                if (conn != null) conn.disconnect();
            } catch (Throwable ignored) {
            }
        }
    }

    // 视频贴片/播放器广告的主机名特征（只认独立广告子域，避免误伤）
    private static final String[] VIDEO_AD_EXACT = {
            "ad", "ads", "adv", "adx", "ima", "imasdk", "vast", "vmap",
            "pubads", "gampad", "scte", "adcdn", "adunit"
    };
    private static final String[] VIDEO_AD_PREFIX = {
            "advert", "adserver", "adservice", "adstream", "preroll", "midroll",
            "postroll", "doubleclick", "googlesyndication", "moatads",
            "adsafeprotected", "adnxs", "adform", "spotx", "teads", "inmobi",
            "applovin", "unityads", "vungle", "chartboost", "ironsource",
            "mintegral", "pangolin"
    };

    private static boolean isVideoAdHost(String host) {
        String[] labels = host.split("\\.");
        for (int i = 0; i < labels.length - 1; i++) {
            String label = labels[i];
            for (String token : VIDEO_AD_EXACT) {
                if (label.equals(token)) return true;
            }
            for (String token : VIDEO_AD_PREFIX) {
                if (label.startsWith(token)) return true;
            }
        }
        return false;
    }

    private static void parse(String content, Set<String> out) {
        String[] lines = content.split("\n");
        for (String raw : lines) {
            if (out.size() > MAX_HOSTS) return;
            String line = raw.trim();
            if (line.length() < 4) continue;
            if (line.startsWith("#") || line.startsWith("!") || line.startsWith("[") || line.startsWith("@@")) continue;
            if (line.startsWith("||")) {
                int end = line.indexOf('^');
                String host = end > 2 ? line.substring(2, end) : "";
                if (isHostLike(host) && isVideoAdHost(host)) out.add(host.toLowerCase());
                continue;
            }
            if (line.indexOf(' ') >= 0 || line.indexOf('/') >= 0 || line.indexOf('*') >= 0 || line.indexOf("##") >= 0) continue;
            if (isHostLike(line) && isVideoAdHost(line)) out.add(line.toLowerCase());
        }
    }

    private static boolean isHostLike(String host) {
        if (host == null || host.length() < 4 || host.length() > 100) return false;
        if (host.indexOf('.') < 0) return false;
        for (int i = 0; i < host.length(); i++) {
            char c = host.charAt(i);
            boolean ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '.' || c == '-' || c == '_';
            if (!ok) return false;
        }
        return true;
    }

    private static void writeCache(Context context, Set<String> hosts) {
        FileOutputStream fos = null;
        try {
            File file = new File(context.getCacheDir(), CACHE_FILE);
            fos = new FileOutputStream(file);
            StringBuilder sb = new StringBuilder();
            for (String host : hosts) sb.append(host).append('\n');
            fos.write(sb.toString().getBytes("UTF-8"));
            fos.flush();
        } catch (Throwable t) {
            t.printStackTrace();
        } finally {
            try {
                if (fos != null) fos.close();
            } catch (Throwable ignored) {
            }
        }
    }
}
"""
    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/AdRuleUpdater.java'), ar)

    msf = jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/ModelSettingFragment.java')
    mh = read_text(msf)
    a4 = 'import com.github.tvbox.osc.util.DanmuHelper;'
    assert a4 in mh, '锚点丢失：Fragment import'
    mh = mh.replace(a4, 'import com.github.tvbox.osc.util.AdRuleUpdater;' + chr(10) + a4, 1)
    a5 = '        tvm3u8AdText.setText(Hawk.get(HawkConfig.M3U8_PURIFY, true) ? "开启" : "关闭");'
    assert a5 in mh, '锚点丢失：去广告文本初始化'
    inject = ('        AdRuleUpdater.autoUpdate(mActivity);' + chr(10) +
              '        findViewById(R.id.m3u8Ad).setOnLongClickListener(new View.OnLongClickListener() {' + chr(10) +
              '            @Override' + chr(10) +
              '            public boolean onLongClick(View v) {' + chr(10) +
              '                AdRuleUpdater.clearCache(mActivity);' + chr(10) +
              '                Toast.makeText(mActivity, "已清除网络广告规则，仅保留内置规则", Toast.LENGTH_SHORT).show();' + chr(10) +
              '                return true;' + chr(10) +
              '            }' + chr(10) +
              '        });')
    mh = mh.replace(a5, a5 + chr(10) + inject, 1)
    write_text(msf, mh)
    log('设置页打开：后台拉取 tvbox-server 的 ads 并合并（1 小时节流）')

    # 启动即加载本地缓存的网络广告规则（不必等到进设置页）
    acx = jp('app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java')
    ax = read_text(acx)
    if 'AdRuleUpdater' not in ax:
        ax = ax.replace('import com.github.tvbox.osc.util.AdBlocker;',
                        'import com.github.tvbox.osc.util.AdBlocker;' + chr(10) + 'import com.github.tvbox.osc.util.AdRuleUpdater;', 1)
        ax = ax.replace('        if(AdBlocker.isEmpty()){',
                        '        AdRuleUpdater.loadCache(App.getInstance());' + chr(10) + '        if(AdBlocker.isEmpty()){', 1)
        write_text(acx, ax)

    # 补几个视频贴片广告常见 CDN 特征（M3u8 分片识别用）
    m3 = jp('app/src/main/java/com/github/tvbox/osc/util/M3u8.java')
    m3s = read_text(m3)
    anchor_kw = '"advertising", "2mdn.net", "moatads", "scorecardresearch", "quantserve"'
    if anchor_kw in m3s:
        m3s = m3s.replace(anchor_kw,
                          anchor_kw + chr(10) + '        , "imasdk", "pubads", "gampad", "adcdn", "preroll", "scte", "vast"', 1)
        write_text(m3, m3s)

    # M3u8：支持全局插片广告正则（来自内置规则）
    m3f = jp('app/src/main/java/com/github/tvbox/osc/util/M3u8.java')
    m3t = read_text(m3f)
    if 'GLOBAL_AD_REGEX' not in m3t:
        anchor_g = '    private static final int MAX_FRAME_RATE_AD_BLOCK_SIZE = 12;'
        assert anchor_g in m3t, '锚点丢失：M3u8 常量'
        m3t = m3t.replace(anchor_g, anchor_g + chr(10) +
            '    private static final java.util.List<String> GLOBAL_AD_REGEX = new java.util.ArrayList<>();' + chr(10) + chr(10) +
            '    public static void addGlobalRegex(String regex) {' + chr(10) +
            '        if (regex != null && regex.length() > 0 && !GLOBAL_AD_REGEX.contains(regex)) GLOBAL_AD_REGEX.add(regex);' + chr(10) +
            '    }', 1)
    old_ret = ('        return list;' + chr(10) + '    }' + chr(10) + chr(10) + '    private static String clean(String line, List<String> ads) {')
    assert old_ret in m3t, '锚点丢失：getRegex 返回'
    m3t = m3t.replace(old_ret,
        '        List<String> merged = new ArrayList<>(list);' + chr(10) +
        '        merged.addAll(GLOBAL_AD_REGEX);' + chr(10) +
        '        return merged;' + chr(10) + '    }' + chr(10) + chr(10) +
        '    private static String clean(String line, List<String> ads) {', 1)
    write_text(m3f, m3t)

    # ApiConfig：启动即套用内置规则（订阅刷新后也保持）
    ac2 = jp('app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java')
    h2 = read_text(ac2)
    a6 = '    private void loadDefaultConfig() {'
    assert a6 in h2, '锚点丢失：loadDefaultConfig'
    if 'BuiltinAdRules' not in h2:
        h2 = h2.replace('import com.github.tvbox.osc.util.AdBlocker;',
                        'import com.github.tvbox.osc.util.AdBlocker;' + chr(10) + 'import com.github.tvbox.osc.util.BuiltinAdRules;', 1)
        h2 = h2.replace(a6, a6 + chr(10) + '        BuiltinAdRules.apply();', 1)
        h2 = h2.replace('            VideoParseRuler.clearRule();',
                        '            VideoParseRuler.clearRule();' + chr(10) + '            BuiltinAdRules.apply();', 1)
        write_text(ac2, h2)

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

    ph = jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java')
    if os.path.isfile(ph):
        pt = read_text(ph)
        if 'removeElementScript' not in pt:
            a_p = '    public void onPageFinished(WebView view, String url) {'
            if a_p in pt:
                pt = pt.replace(a_p, a_p + chr(10) +
                    '        try {' + chr(10) +
                    '            String adScript = com.github.tvbox.osc.util.AdBlocker.removeElementScript();' + chr(10) +
                    '            if (adScript.length() > 0) view.evaluateJavascript(adScript, null);' + chr(10) +
                    '        } catch (Throwable ignored) {' + chr(10) +
                    '        }', 1)
                write_text(ph, pt)

    emit_builtin()
    lint_java_literals()

    # 防再犯：括号配平检查（曾出现 formatHMS(position))); 多一个右括号）
    vc = read_text(jp('app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java'))
    for line in vc.split(chr(10)):
        if '));' in line and 'setText(' in line and line.count(')') > line.count('('):
            sys.exit('括号不配平：' + line.strip())

    # 防再犯：跨包调用必须带 import
    acx = read_text(jp('app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java'))
    if 'BuiltinAdRules.apply()' in acx and 'import com.github.tvbox.osc.util.BuiltinAdRules;' not in acx:
        sys.exit('ApiConfig 缺少 BuiltinAdRules 的 import')
    log('内置规则固化：广告域名/源级正则/网页规则/插片正则全部编译进包')


# ---------------------------------------------------------------- 自检

def lint_java_literals():
    """防再犯：多字符 char 字面量（如 '##'）会导致 javac unclosed character literal"""
    import re as _re
    bad = []
    for f in glob.glob(jp('app/src/main/java/com/github/tvbox/osc/**/*.java'), recursive=True):
        txt = read_text(f)
        for i, line in enumerate(txt.split(chr(10)), 1):
            for m in _re.finditer(r"indexOf\\('([^'\\\\]{2,})'\\)", line):
                bad.append('%s:%d %s' % (os.path.basename(f), i, m.group(0)))
    if bad:
        sys.exit('多字符 char 字面量（编译必炸）：' + '; '.join(bad[:5]))
    log('字面量检查通过：无多字符 char')


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
