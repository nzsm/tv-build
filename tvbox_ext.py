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

HTVO_XML = ('<vector xmlns:android="http://schemas.android.com/apk/res/android"'
            ' android:width="23dp" android:height="23dp"'
            ' android:viewportWidth="24" android:viewportHeight="24">'
            # 旋屏（屏显）图标原来是满幅绘制（0-24 全占），实测比同排图标大一圈，
            # 整体缩到 88%：画布里留出呼吸位，视觉大小和其它图标齐平。
            '<group android:pivotX="12.0" android:pivotY="12.0"'
            ' android:scaleX="0.88" android:scaleY="0.88">'
            '<path android:pathData="M16.48 2.52c3.27 1.55 5.61 4.72 5.97 8.48h1.5C23.44 4.84 18.29 0 12 0l-.66.03 3.81 3.81 1.33-1.32z" android:fillColor="#FFFFFF" android:strokeColor="#FFFFFF" android:strokeWidth="0.6" android:strokeLineJoin="round"/>'
            '<path android:pathData="M10.23 1.75c-.59-.59-1.54-.59-2.12 0L1.75 8.11c-.59.59-.59 1.54 0 2.12l12.02 12.02c.59.59 1.54.59 2.12 0l6.36-6.36c.59-.59.59-1.54 0-2.12L10.23 1.75m4.6 19.44L2.81 9.17l6.36-6.36 12.02 12.02-6.36 6.36z" android:fillColor="#FFFFFF" android:strokeColor="#FFFFFF" android:strokeWidth="0.6" android:strokeLineJoin="round"/>'
            '<path android:pathData="M7.52 22.25C4.25 19.94 1.91 16.76 1.55 13H.05C.56 19.16 5.71 24 12 24l.66-.03-3.81-3.81-1.33 1.32z" android:fillColor="#FFFFFF" android:strokeColor="#FFFFFF" android:strokeWidth="0.6" android:strokeLineJoin="round"/>'
            '</group></vector>')

ICONS = {'htov': HTVO_XML, 'v_prev': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="11.950" android:pivotY="10.575" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.050" android:translateY="1.425"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.826" android:scaleY="1.826"\n        android:translateX="-0.045" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M7,6c0.55,0 1,0.45 1,1v10c0,0.55 -0.45,1 -1,1s-1,-0.45 -1,-1L6,7c0,-0.55 0.45,-1 1,-1zM10.66,12.82l5.77,4.07c0.66,0.47 1.58,-0.01 1.58,-0.82L18.01,7.93c0,-0.81 -0.91,-1.28 -1.58,-0.82l-5.77,4.07c-0.57,0.4 -0.57,1.24 0,1.64z"/></group></group></vector>', 'v_next': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.833" android:scaleY="1.833"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M7.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L7.58,7.11C6.91,6.65 6,7.12 6,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM16,7v10c0,0.55 0.45,1 1,1s1,-0.45 1,-1V7c0,-0.55 -0.45,-1 -1,-1s-1,0.45 -1,1z"/></group></group></vector>', 'v_replay': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="11.975" android:pivotY="10.575" android:scaleX="0.9929" android:scaleY="0.9929" android:translateX="0.025" android:translateY="1.425"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.136" android:scaleY="1.136"\n        android:translateX="-0.057" android:translateY="-1.123"><path android:fillColor="@android:color/white" android:pathData="M12,5V2.21c0,-0.45 -0.54,-0.67 -0.85,-0.35l-3.8,3.79c-0.2,0.2 -0.2,0.51 0,0.71l3.79,3.79c0.32,0.31 0.86,0.09 0.86,-0.36V7c3.73,0 6.68,3.42 5.86,7.29 -0.47,2.27 -2.31,4.1 -4.57,4.57 -3.57,0.75 -6.75,-1.7 -7.23,-5.01 -0.07,-0.48 -0.49,-0.85 -0.98,-0.85 -0.6,0 -1.08,0.53 -1,1.13 0.62,4.39 4.8,7.64 9.53,6.72 3.12,-0.61 5.63,-3.12 6.24,-6.24C20.84,9.48 16.94,5 12,5z"/></group></group></vector>', 'v_replay_play': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="24" android:viewportHeight="24"\n    android:tint="#FFFFFF"><group android:pivotX="11.925" android:pivotY="10.875" android:scaleX="1.1382" android:scaleY="1.1382" android:translateX="0.075" android:translateY="1.125"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.136" android:scaleY="1.136"\n        android:translateX="-0.057" android:translateY="-1.123"><path android:strokeColor="@android:color/white" android:strokeWidth="2.2" android:fillColor="@android:color/transparent" android:pathData="M12,5 A7,7 0 1 1 11.99,5"/><path android:fillColor="@android:color/white" android:pathData="M9.85,8.4 L16.25,12.0 L9.85,15.6 Z"/></group></group></vector>', 'v_aspect': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M18,12c-0.55,0 -1,0.45 -1,1v2h-2c-0.55,0 -1,0.45 -1,1s0.45,1 1,1h3c0.55,0 1,-0.45 1,-1v-3c0,-0.55 -0.45,-1 -1,-1zM7,9h2c0.55,0 1,-0.45 1,-1s-0.45,-1 -1,-1L6,7c-0.55,0 -1,0.45 -1,1v3c0,0.55 0.45,1 1,1s1,-0.45 1,-1L7,9zM21,3L3,3c-1.1,0 -2,0.9 -2,2v14c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2zM20,19.01L4,19.01c-0.55,0 -1,-0.45 -1,-1L3,5.99c0,-0.55 0.45,-1 1,-1h16c0.55,0 1,0.45 1,1v12.02c0,0.55 -0.45,1 -1,1z"/></group></group></vector>', 'v_ffwd': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.309" android:scaleY="1.309"\n        android:translateX="-0.523" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M5.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L5.58,7.11C4.91,6.65 4,7.12 4,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM13,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63l-5.77,-4.07c-0.67,-0.47 -1.58,0 -1.58,0.81z"/></group></group></vector>', 'v_type': '<vector android:height="26dp"\n    android:tint="#FFFFFF"\n    android:viewportHeight="24"\n    android:viewportWidth="24"\n    android:width="26dp"\n    xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M21,3L3,3c-1.11,0 -2,0.89 -2,2v12c0,1.1 0.89,2 2,2h5v2h8v-2h5c1.1,0 1.99,-0.9 1.99,-2L23,5c0,-1.11 -0.9,-2 -2,-2zM21,17L3,17L3,5h18v12zM16,11l-7,4L9,7z" /></group></group></vector>', 'v_subtitle': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.1" android:scaleY="1.1"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M20,4L4,4c-1.1,0 -2,0.9 -2,2v12c0,1.1 0.9,2 2,2h16c1.1,0 2,-0.9 2,-2L22,6c0,-1.1 -0.9,-2 -2,-2zM4,12h4v2L4,14v-2zM14,18L4,18v-2h10v2zM20,18h-4v-2h4v2zM20,14L10,14v-2h10v2z"/></group></group></vector>', 'v_audio': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9906" android:scaleY="0.9906" android:translateX="0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.222" android:scaleY="1.222"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M12,5v8.55c-0.94,-0.54 -2.1,-0.75 -3.33,-0.32 -1.34,0.48 -2.37,1.67 -2.61,3.07 -0.46,2.74 1.86,5.08 4.59,4.65 1.96,-0.31 3.35,-2.11 3.35,-4.1V7h2c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2h-2c-1.1,0 -2,0.9 -2,2z"/></group></group></vector>', 'v_danmu': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp"\n    android:height="26dp"\n    android:viewportWidth="436"\n    android:viewportHeight="419"><group android:pivotX="218.000" android:pivotY="185.058" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="24.442"><group android:pivotX="218.0" android:pivotY="209.5"\n        android:scaleX="0.916" android:scaleY="0.916"\n        android:translateX="0.0" android:translateY="-25.507"><path\n      android:pathData="M322.65,272.14L274.13,272.14L274.13,290.36L328.16,290.36L328.16,318.2L274.13,318.2L274.13,347.96L242.96,347.96L242.96,318.2L188.7,318.2L188.7,290.36L242.96,290.36L242.96,272.14L194.21,272.14L194.21,147.1L216.3,147.1L209.39,129.82L238.16,129.82L245.13,147.1L271.73,147.1L278.7,129.82L307.53,129.82L300.32,147.1L322.88,147.1L322.65,272.14ZM115.05,189.58L152.26,189.58L152.26,164.62L110.25,164.62L110.25,135.09L182.96,135.09L182.96,218.35L143.59,218.35L142.18,244.78L184.66,244.78L177.92,347.02L117.22,347.02L117.22,316.79L148.39,316.79L151.79,273.55L110.25,273.55L115.05,189.58ZM244.89,243.08L244.89,223.16L222.81,223.16L222.81,243.08L244.89,243.08ZM244.89,195.79L244.89,176.11L222.81,176.11L222.81,195.79L244.89,195.79ZM294.06,243.08L294.06,223.16L272.02,223.16L272.02,243.08L294.06,243.08ZM294.06,195.79L294.06,176.11L272.02,176.11L272.02,195.79L294.06,195.79Z"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"/><path\n      android:pathData="M20.27,79.27Q0.5,99.04 0.5,127L0.5,351Q0.5,378.96 20.27,398.73Q40.04,418.5 68,418.5L368,418.5Q395.96,418.5 415.73,398.73Q435.5,378.96 435.5,351L435.5,127Q435.5,99.04 415.73,79.27Q395.96,59.5 368,59.5L68,59.5Q40.04,59.5 20.27,79.27ZM35.5,351L35.5,127Q35.5,113.54 45.02,104.02Q54.54,94.5 68,94.5L368,94.5Q381.46,94.5 390.98,104.02Q400.5,113.54 400.5,127L400.5,351Q400.5,364.46 390.98,373.98Q381.46,383.5 368,383.5L68,383.5Q54.54,383.5 45.02,373.98Q35.5,364.46 35.5,351Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FCFCFC"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/><path\n      android:pathData="M208.26,55.63L128.98,0.62L109.02,29.38L188.31,84.39Q201.24,93.36 216.98,93.4Q232.71,93.44 245.69,84.53L325.91,29.42L306.09,0.57L225.87,55.68Q221.89,58.41 217.06,58.4Q212.23,58.39 208.26,55.63Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/></group></group></vector>', 'v_back': '<vector android:autoMirrored="true" android:height="26dp"\n    android:tint="#FFFFFF" android:viewportHeight="24"\n    android:viewportWidth="24" android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.575" android:scaleX="0.9929" android:scaleY="0.9929" android:translateX="0.000" android:translateY="1.425"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.169" android:scaleY="1.169"\n        android:translateX="0.468" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M16.62,2.99c-0.49,-0.49 -1.28,-0.49 -1.77,0L6.54,11.3c-0.39,0.39 -0.39,1.02 0,1.41l8.31,8.31c0.49,0.49 1.28,0.49 1.77,0s0.49,-1.28 0,-1.77L9.38,12l7.25,-7.25c0.48,-0.48 0.48,-1.28 -0.01,-1.76z"/></group></group></vector>', 'ic_clock': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9906" android:scaleY="0.9906" android:translateX="-0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.047" android:scaleY="1.047"\n        android:translateX="-0.262" android:translateY="-1.31"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M11,8H13V14H11V8M12,20C8.13,20 5,16.87 5,13S8.13,6 12,6 19,9.13 19,13C19.7,13 20.36,13.13 21,13.35C21,13.23 21,13.12 21,13C21,10.88 20.26,8.93 19.03,7.39L20.45,5.97C20,5.46 19.55,5 19.04,4.56L17.62,6C16.07,4.74 14.12,4 12,4C7.03,4 3,8.03 3,13S7.03,22 12,22C12.59,22 13.16,21.94 13.71,21.83C13.4,21.25 13.18,20.6 13.08,19.91C12.72,19.96 12.37,20 12,20M15,1H9V3H15V1M16.5,16.5V21.5H21.5V16.5H16.5Z"/></group></group></vector>', 'play_skip': '<vector android:height="26dp" android:viewportHeight="1000"\n    android:viewportWidth="1000" android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="500.000" android:pivotY="423.958" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="76.042"><group android:pivotX="500.0" android:pivotY="500.0"\n        android:scaleX="0.932" android:scaleY="0.932"\n        android:translateX="0.0" android:translateY="-76.375"><path android:fillColor="#FFFFFFFF" android:pathData="M10,499.5c0,301.7 0.3,319.9 4.5,316.5C24,808.3 345.7,501.9 345.7,500.3c0,-0.8 -75.3,-73.4 -167.7,-161.1L10,179.6L10,499.5z"/><path android:fillColor="#FFFFFFFF" android:pathData="M414.1,498.9c0,203.1 1.1,319.9 2.6,319.4c2.6,-0.8 335.5,-316.2 335.5,-318c0,-0.5 -234,-223.5 -328.1,-312.5l-10,-9.3L414.1,498.9z"/><path android:fillColor="#FFFFFFFF" android:pathData="M820.9,500.5l0,321l84.5,-0L990,821.5L990,500.5l0,-320.9l-84.5,-0l-84.5,-0L820.9,500.5z"/></group></group></vector>', 'tk_unlock': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp"\n    android:height="26dp"\n    android:tint="#FFFFFF"\n    android:viewportWidth="24"\n    android:viewportHeight="24"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9906" android:scaleY="0.9906" android:translateX="-0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.047" android:scaleY="1.047"\n        android:translateX="0.0" android:translateY="-1.31"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M18,8h-1L17,6c0,-2.76 -2.24,-5 -5,-5S7,3.24 7,6h2c0,-1.66 1.34,-3 3,-3s3,1.34 3,3v2L6,8c-1.1,0 -2,0.9 -2,2v10c0,1.1 0.9,2 2,2h12c1.1,0 2,-0.9 2,-2L20,10c0,-1.1 -0.9,-2 -2,-2zM18,20L6,20L6,10h12v10zM12,17c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2z" /></group></group></vector>', 'v_cast': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="24" android:viewportHeight="24"\n    android:tint="#FFFFFF"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M1,18v3h3c0,-1.66 -1.34,-3 -3,-3zM1,14v2c2.76,0 5,2.24 5,5h2c0,-3.87 -3.13,-7 -7,-7zM1,10v2c4.97,0 9,4.03 9,9h2c0,-6.08 -4.93,-11 -11,-11zM21,3L3,3c-1.1,0 -2,0.9 -2,2v3h2L3,5h18v14h-7v2h7c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2z"/></group></group></vector>', 'tk_space': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="26" android:viewportHeight="26"><path android:fillColor="#00000000" android:pathData="M0,0 L26,0 L26,26 L0,26 Z" /></vector>'}


import glob
import os
import re
import sys
import time
import traceback
import xml.etree.ElementTree as ET

SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
DEF_URL = sys.argv[2] if len(sys.argv) > 2 else ''
APP_NAME = (sys.argv[3] if len(sys.argv) > 3 else '').strip() or 'NZ'

VER = 'VER-20261124-U64'

# ============ 可裁剪开关 ============
# 2026-11-23 拆分：把"只提速、不改播放结果"和"改播放行为"分开，不再一把全关。
#   FEAT_FAST_START   3.5 秒还没拉到 m3u8 清单就直接起播（治"播放页加载慢"）
#   FEAT_PURIFY_CACHE 同一地址净化过就直接走代理（治"切软解/硬解/换播放器慢"）
#   FEAT_SEQ_GUARD    切集后旧的超时回调作废（正确性，正常播放时无感）
#   FEAT_PROXY_WATCHDOG 净化代理 12 秒没画面回落原地址（会打断，先关）
#   FEAT_AD_REPLAY    广告段播完重解析（去广告已关，用不上）
FEAT_FAST_START = False
FEAT_PURIFY_CACHE = False
FEAT_SEQ_GUARD = False
FEAT_PROXY_WATCHDOG = False
FEAT_AD_REPLAY = False

# ============ 改动清单开关（2026-11-23）============
# 这里每一项对应一处"我在上游基础上做的改动"，True=生效，False=不生效（等于回到 q215613905 原样）。
# 底座三项没有开关，因为别的改动都挂在它们生成的结构上：apply_layout / apply_fast_start(空壳) / self_check。
# 01 底栏图标替换：底座，无开关（关掉会缺 drawable，资源编译直接失败）
OPT_BTN_TEXT = True           # 02 按钮文字：上集/下集/旋屏/EXO；播放器名缩短；线路名"直链"；投屏去门槛；摘除搜弹幕/视轨
OPT_SINGLE_LAYOUT = True      # 03 删掉第二份播放控制布局，只留 player_vod_control_view
OPT_APP_NAME = True           # 04 应用名改成 NZ
OPT_APP_ICON = True           # 桌面启动图标换成 NZ（M2 + 橙红渐变）
OPT_TOPBAR_TRANSPARENT = True # 05 顶部四块半透明底板去掉（只留白字）
OPT_TEXT_STROKE = True        # 06 描边撤销（True=保持无描边原样，False=不做处理，结果一样）
OPT_STATIC_UI = True          # 07 尺寸静态化（手机竖屏/横屏/电视三套 dimen，不再起播后跳变）
OPT_SLOT_ALIGN = True         # 08 片头/片尾 00:00 两行右侧对齐
OPT_BTN_WHITELIST = True      # 09 底栏按钮白名单（只留 20 个我方按钮）
OPT_SPACING = True            # 行距/贴边：顶部两行 6dp、进度条→按钮 16dp、按钮行贴边 10dp
OPT_BTN_GUARD = False         # 10 底栏层级守卫（已按要求撤回）
OPT_PAUSE_KEEP = False        # 11 暂停保活 + 底栏直接置可见 + 清遗留消息（已按要求撤回上游）
OPT_GRADIENT_BG = False       # 12 顶部/底部渐变背板（已按要求撤回，改用 OPT_SCRIM_BG 整块半透明）
OPT_SCRIM_BG = True           # 12b 顶部/底部整块半透明底板（不渐变）
OPT_SCREEN_ON = True          # 12c 屏显默认开：右上角网速/播放时间/系统时间默认显示
OPT_DOWNLOAD = True           # 13 下载按钮 + 选集弹窗 + 串行队列
OPT_SEARCH_BOOST = True       # 14 搜索增强（新源并入/每批 10 源）
OPT_DANMU_ALPHA = True        # 15 弹幕透明度下限 10% → 0%
OPT_DANMU_DOUBLE = True       # 16 弹幕按钮双击=关闭，单击=设置
OPT_AD_SWITCH = True          # 17 去广告开关真正生效（关闭时零规则加载）
OPT_DNS_DEFAULT = True        # 18 DNS 默认值改成腾讯 DoH
OPT_TOP_TIME_FIX = False      # 19 右上角时间/网速显隐（已回上游，本项关闭）
OPT_MERGE_SOURCE_ADS = True   # 21 合并源里的 ads 名单进过滤表（= 上游行为）
OPT_PUSH_BTN = False          # 20 播放页「投屏」保持上游原样（汉字「投屏」+ DLNA 设备列表，不改「推送」）
OPT_RENDER_FIX = True         # 22 画面比例：修「填充」档拿 MeasureSpec 原值 + 补回像素宽高比（治拉扁）
LAYOUT = 'app/src/main/res/layout/player_vod_control_view.xml'
VOD = 'app/src/main/java/com/github/tvbox/osc/player/controller/VodController.java'
PLAYER_HELPER = 'app/src/main/java/com/github/tvbox/osc/util/PlayerHelper.java'

A = '{http://schemas.android.com/apk/res/android}'
NS = 'http://schemas.android.com/apk/res/android'

ICON_SIZE = '23dp'      # 图标位高度（26 → 23，整体缩 3dp）
TEXT_SIZE = '8dp'       # 汉字（10 → 8）
PAD_LR = '6dp'          # 每个按钮左右内边距 → 相邻 12dp ≈ 半个图标
PAD_TB = '10dp'
SEEK_INSET = '12dp'     # 进度条整行左右各收

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


TK_DL_DIALOG = r"""    // 底栏「下载」：复用 TkDownloadPicker 选集框（详情页「下载」按钮同一套）
    public void tkShowDownloadDialog() {
        try {
            com.github.tvbox.osc.util.TkDownloadPicker.show(requireContext(), mVodInfo);
        } catch (Throwable ignored) {
        }
    }
"""


TK_URL_MEMO_JAVA = r'''package com.github.tvbox.osc.util;

import com.github.tvbox.osc.bean.VodInfo;
import com.orhanobut.hawk.Hawk;

import java.security.MessageDigest;
import java.util.List;

/**
 * 记住每一集的真实播放地址。
 * 播放页每次拿到真正的 m3u8/mp4（直链，或网页源嗅探出来的那条）就存一笔，
 * 之后在详情页选下载时直接拿来用，不必为了下这一集专门去播放一遍。
 */
public class TkUrlMemo {

    private static final String TAG = "tkum_";

    private static String md5(String s) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] b = md.digest(s.getBytes("UTF-8"));
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < b.length; i++) {
                sb.append(String.format("%02x", b[i]));
            }
            return sb.toString();
        } catch (Throwable t) {
            return String.valueOf(s.hashCode());
        }
    }

    private static String epName(VodInfo v, int idx) {
        try {
            List<VodInfo.VodSeries> eps = v.seriesMap == null ? null : v.seriesMap.get(v.playFlag);
            if (eps != null && idx >= 0 && idx < eps.size() && eps.get(idx) != null) {
                return eps.get(idx).name == null ? "" : eps.get(idx).name;
            }
        } catch (Throwable ignored) {
        }
        return "";
    }

    private static String key(VodInfo v, int idx) {
        if (v == null) return null;
        return TAG + md5(v.id + "|" + v.playFlag + "|" + epName(v, idx));
    }

    /** 播放页拿到地址时调用：按当前集写一笔。 */
    public static void remember(VodInfo v, String url) {
        try {
            if (v == null || url == null || url.length() < 10) return;
            if (!url.startsWith("http")) return;
            if (url.contains("127.0.0.1") || url.contains("localhost")) return;
            String k = key(v, v.playIndex);
            if (k != null) Hawk.put(k, url);
        } catch (Throwable ignored) {
        }
    }

    /** 详情页按集号取。 */
    public static String get(VodInfo v, int idx) {
        try {
            String k = key(v, idx);
            if (k == null) return "";
            String r = Hawk.get(k, "");
            return r == null ? "" : r;
        } catch (Throwable t) {
            return "";
        }
    }
}
'''

TK_DL_PICKER_JAVA = r'''package com.github.tvbox.osc.util;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.text.TextUtils;
import android.widget.Toast;

import com.github.tvbox.osc.bean.VodInfo;

import java.util.List;

/**
 * 选集下载框：播放页底栏「下载」和详情页「下载」按钮共用。
 * 直链直接可下；网页源只要之前播放过一集（TkUrlMemo 记下了真实地址）也能下。
 */
public class TkDownloadPicker {

    public static boolean isDirect(String u) {
        if (TextUtils.isEmpty(u)) return false;
        String s = u.trim().toLowerCase();
        if (!s.startsWith("http")) return false;
        return s.contains(".m3u8") || s.contains(".mp4") || s.contains(".mkv")
                || s.contains(".avi") || s.contains(".flv") || s.contains(".ts")
                || s.contains(".m4v") || s.contains(".mov") || s.contains(".wmv")
                || s.contains(".mp3");
    }

    public static void show(final Context ctx, final VodInfo v) {
        if (ctx == null || v == null) return;
        if (v.seriesMap == null || TextUtils.isEmpty(v.playFlag)) {
            Toast.makeText(ctx, "先选一条线路（等详情加载完）再下载", Toast.LENGTH_SHORT).show();
            return;
        }
        final List<VodInfo.VodSeries> eps;
        try {
            eps = v.seriesMap.get(v.playFlag);
        } catch (Throwable t) {
            return;
        }
        if (eps == null || eps.isEmpty()) {
            Toast.makeText(ctx, "这条线路没有集数", Toast.LENGTH_SHORT).show();
            return;
        }
        final int n = eps.size();
        final boolean[] ok = new boolean[n];
        final String[] real = new String[n];
        final boolean[] sel = new boolean[n];
        final String[] labels = new String[n];
        final String base = TextUtils.isEmpty(v.name) ? "下载" : v.name;
        int cur = v.playIndex;
        if (cur < 0) cur = 0;
        if (cur >= n) cur = n - 1;
        for (int i = 0; i < n; i++) {
            VodInfo.VodSeries vs = eps.get(i);
            String name = (vs == null || TextUtils.isEmpty(vs.name)) ? ("第" + (i + 1) + "集") : vs.name;
            String u = vs == null || vs.url == null ? "" : vs.url.trim();
            if (isDirect(u)) {
                ok[i] = true;
                real[i] = u;
                labels[i] = name;
            } else {
                String memo = TkUrlMemo.get(v, i);
                if (!TextUtils.isEmpty(memo)) {
                    ok[i] = true;
                    real[i] = memo;
                    labels[i] = name + "   （用记住的地址）";
                } else {
                    labels[i] = name + "   （网页源，先点开这集再回来下）";
                }
            }
            sel[i] = ok[i] && i == cur;
        }
        new AlertDialog.Builder(ctx)
                .setTitle(base + "：选要下载的集（可多选）")
                .setMultiChoiceItems(labels, sel, new DialogInterface.OnMultiChoiceClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int which, boolean isChecked) {
                        sel[which] = isChecked;
                    }
                })
                .setPositiveButton("开始下载", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int which) {
                        int added = 0;
                        int skip = 0;
                        for (int i = 0; i < n; i++) {
                            if (!sel[i]) continue;
                            if (!ok[i] || TextUtils.isEmpty(real[i])) {
                                skip++;
                                continue;
                            }
                            VodInfo.VodSeries vs = eps.get(i);
                            String nm = (vs == null || TextUtils.isEmpty(vs.name)) ? ("第" + (i + 1) + "集") : vs.name;
                            TkDownloader.enqueue(ctx, real[i], base + "_" + nm);
                            added++;
                        }
                        if (added > 0) {
                            Toast.makeText(ctx, "已排 " + added + " 个" + (skip > 0 ? "，另有 " + skip + " 个要先进播放页" : ""), Toast.LENGTH_LONG).show();
                        } else {
                            Toast.makeText(ctx, "选中的都下不了：网页源要先点开那一集", Toast.LENGTH_LONG).show();
                        }
                    }
                })
                .setNegativeButton("取消", null)
                .show();
    }
}
'''

TK_DL_CENTER_JAVA = r'''package com.github.tvbox.osc.util;

import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.TextView;

/**
 * 详情页「下载」按钮的状态显示：没任务时是「下载」，一开始下载就变成「下载 3/10」，
 * 有失败的会在后面挂「失败N」。长按按钮弹出下载列表，能看到每集的排队/百分比/完成/失败原因。
 */
public class TkDownloadCenter {

    private static final java.util.WeakHashMap<TextView, Boolean> BOUND =
            new java.util.WeakHashMap<TextView, Boolean>();

    public static void bind(final TextView tv) {
        if (tv == null) return;
        try {
            if (BOUND.containsKey(tv)) return;
            BOUND.put(tv, Boolean.TRUE);
        } catch (Throwable ignored) {
        }
        try {
            tv.setOnLongClickListener(new View.OnLongClickListener() {
                @Override
                public boolean onLongClick(View v) {
                    TkDownloader.showList(v.getContext());
                    return true;
                }
            });
        } catch (Throwable ignored) {
        }
        final Handler h = new Handler(Looper.getMainLooper());
        final Runnable[] r = new Runnable[1];
        r[0] = new Runnable() {
            @Override
            public void run() {
                try {
                    String s = TkDownloader.label();
                    if (!s.contentEquals(tv.getText())) tv.setText(s);
                    h.postDelayed(r[0], 1000);
                } catch (Throwable ignored) {
                }
            }
        };
        h.post(r[0]);
    }
}
'''

TK_DL_JAVA = r"""package com.github.tvbox.osc.util;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.widget.Toast;

import androidx.core.app.NotificationCompat;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.ResponseBody;

/**
 * 极简下载：m3u8 把分片按顺序拼成单个 ts（fMP4 则拼成 mp4），mp4 直链交给系统下载器。
 * 全部在后台线程，任何异常只提示不崩；退出 App 即停止（没有前台服务）。
 */
public class TkDownloader {
    public static volatile String lastUrl = "";
    public static volatile String lastTitle = "";

    private static volatile Thread worker = null;
    private static final java.util.ArrayList<Job> QUEUE = new java.util.ArrayList<Job>();
    private static int okCount = 0;
    private static int failCount = 0;
    private static final String CHANNEL = "tk_download";
    private static final int NOTI_ID = 9527;

    private static final OkHttpClient CLIENT = new OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .followRedirects(true)
            .build();

    public static final int ST_QUEUE = 0;
    public static final int ST_RUN = 1;
    public static final int ST_OK = 2;
    public static final int ST_FAIL = 3;

    static class Job {
        Context app;
        String url;
        String name;
        volatile int status = ST_QUEUE;
        volatile int done = 0;
        volatile int total = 0;
        volatile String msg = "";
    }

    /** 界面上的任务表：详情页「下载」按钮的文字、下载列表都读这里。 */
    public static final java.util.ArrayList<Job> TASKS = new java.util.ArrayList<Job>();
    private static volatile Job CUR = null;

    public static void start(final Context ctx, String urlIn, String title) {
        enqueue(ctx, urlIn, title);
    }

    public static int pending() {
        synchronized (QUEUE) {
            return QUEUE.size();
        }
    }

    /**
     * 把一个下载任务放进队列。多个任务串行执行，不会抢带宽，也不会互相覆盖文件。
     */
    public static void enqueue(final Context ctx, String urlIn, String title) {
        try {
            if (ctx == null) return;
            final Context app = ctx.getApplicationContext();
            String url = urlIn == null ? "" : urlIn.trim();
            if (url.isEmpty()) url = lastUrl;
            if (url.isEmpty()) {
                tip(ctx, "这一集还没拿到地址，先播放一次再下");
                return;
            }
            if (url.contains("127.0.0.1") || url.contains("localhost")) {
                tip(ctx, "当前是本地代理地址，先正常播放再点下载");
                return;
            }
            if (Build.VERSION.SDK_INT >= 23
                    && ctx.checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                    != PackageManager.PERMISSION_GRANTED) {
                if (ctx instanceof Activity) {
                    ((Activity) ctx).requestPermissions(
                            new String[]{android.Manifest.permission.WRITE_EXTERNAL_STORAGE}, 9527);
                    tip(ctx, "先允许存储权限，再点一次下载");
                } else {
                    tip(ctx, "没有存储权限：请在系统设置里给本应用开存储权限，再点一次下载");
                }
                return;
            }
            if (outDir() == null) {
                tip(ctx, "创建下载目录失败");
                return;
            }
            String t = title;
            if (t == null || t.trim().isEmpty()) t = lastTitle;
            Job job = new Job();
            job.app = app;
            job.url = url;
            job.name = safeName(t);
            int left;
            synchronized (QUEUE) {
                QUEUE.add(job);
                left = QUEUE.size() - 1;
            }
            synchronized (TASKS) {
                TASKS.add(job);
                while (TASKS.size() > 40) {
                    Job old = TASKS.get(0);
                    if (old.status == ST_RUN || old.status == ST_QUEUE) break;
                    TASKS.remove(0);
                }
            }
            startWorker();
            tip(ctx, "已加入下载队列：" + job.name + (left > 0 ? ("（前面还有 " + left + " 个）") : ""));
        } catch (Throwable e) {
            e.printStackTrace();
        }
    }

    // 下载期间保持 CPU 醒着：一息屏，几十 MB 的分片流就断在半路
    private static android.os.PowerManager.WakeLock WL = null;

    private static void wlOn(Context ctx) {
        try {
            if (WL != null && WL.isHeld()) return;
            android.os.PowerManager pm = (android.os.PowerManager) ctx.getSystemService(Context.POWER_SERVICE);
            if (pm == null) return;
            WL = pm.newWakeLock(android.os.PowerManager.PARTIAL_WAKE_LOCK, "tkbox:download");
            WL.setReferenceCounted(false);
            WL.acquire(60 * 60 * 1000L);
        } catch (Throwable e) {
            e.printStackTrace();
        }
    }

    private static void wlOff() {
        try {
            if (WL != null && WL.isHeld()) WL.release();
        } catch (Throwable ignored) {
        }
        WL = null;
    }

    private static void startWorker() {
        synchronized (QUEUE) {
            if (worker != null && worker.isAlive()) return;
            worker = new Thread(new Runnable() {
                @Override
                public void run() {
                    loopWorker();
                }
            }, "tk-download");
            okCount = 0;
            failCount = 0;
            worker.start();
        }
    }

    private static void loopWorker() {
        Context lastApp = null;
        while (true) {
            Job job;
            synchronized (QUEUE) {
                if (QUEUE.isEmpty()) {
                    worker = null;
                    break;
                }
                job = QUEUE.remove(0);
            }
            lastApp = job.app;
            CUR = job;
            job.status = ST_RUN;
            wlOn(job.app);
            try {
                File dir = outDir();
                if (dir == null) throw new Exception("创建下载目录失败");
                if (job.url.toLowerCase().contains(".m3u8")) downloadM3u8(job.app, job.url, dir, job.name);
                else downloadMp4(job.app, job.url, dir, job.name);
                okCount++;
            } catch (Throwable e) {
                e.printStackTrace();
                failCount++;
                String msg = e.getMessage();
                done(job.app, job.name, false, msg == null ? "下载失败" : ("下载失败：" + msg));
            } finally {
                wlOff();
            }
        }
        if (lastApp != null && okCount + failCount > 1) {
            tip(lastApp, "这批下完了：成功 " + okCount + " 个，失败 " + failCount + " 个");
        }
    }

    private static File outDir() {
        try {
            File base = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_MOVIES);
            File d = new File(base, "tvbox");
            if (!d.exists() && !d.mkdirs() && !d.exists()) return null;
            return d;
        } catch (Throwable e) {
            e.printStackTrace();
            return null;
        }
    }

    private static String safeName(String raw) {
        String s = raw == null ? "" : raw.trim();
        if (s.isEmpty()) s = "video";
        s = s.replace("\\", " ").replace("/", " ").replace(":", " ")
                .replace("*", " ").replace("?", " ").replace("\"", " ")
                .replace("<", " ").replace(">", " ").replace("|", " ");
        s = s.replaceAll("\\s+", " ").trim();
        if (s.length() > 80) s = s.substring(0, 80).trim();
        if (s.isEmpty()) s = "video";
        return s;
    }

    // ---------------------------------------------------------------- mp4
    private static void downloadMp4(Context ctx, String url, File dir, String name) throws Exception {
        DownloadManager dm = (DownloadManager) ctx.getSystemService(Context.DOWNLOAD_SERVICE);
        if (dm == null) throw new RuntimeException("系统下载服务不可用");
        DownloadManager.Request req = new DownloadManager.Request(Uri.parse(url));
        req.setDestinationInExternalPublicDir(Environment.DIRECTORY_MOVIES, "tvbox/" + name + ".mp4");
        req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
        req.setTitle(name);
        req.allowScanningByMediaScanner();
        try {
            req.addRequestHeader("User-Agent", "okhttp/3.12.11");
        } catch (Throwable ignored) {
        }
        dm.enqueue(req);
        done(ctx, name, true, "已交给系统下载器：Movies/tvbox/" + name + ".mp4");
    }

    // ---------------------------------------------------------------- m3u8
    private static void downloadM3u8(Context ctx, String url, File dir, String name) throws Exception {
        String cur = url;
        String text = getText(cur);
        for (int i = 0; i < 3; i++) {
            if (text == null) throw new RuntimeException("清单读取失败");
            String variant = pickVariant(cur, text);
            if (variant == null) break;
            cur = variant;
            text = getText(cur);
        }
        if (text == null || !text.contains("#EXTINF")) throw new RuntimeException("这不是媒体清单（可能是网页地址）");

        List<String> segs = new ArrayList<>();
        String keyUri = null;
        String ivHex = null;
        boolean hasMap = false;
        String[] lines = text.split("\\r?\\n");
        boolean nextIsSeg = false;
        for (int i = 0; i < lines.length; i++) {
            String line = lines[i].trim();
            if (line.isEmpty()) continue;
            if (line.startsWith("#EXT-X-MAP")) {
                String m = attr(line, "URI");
                if (m != null) {
                    segs.add(resolve(cur, m));
                    hasMap = true;
                }
                continue;
            }
            if (line.startsWith("#EXT-X-KEY")) {
                String method = attr(line, "METHOD");
                if (method != null && method.equalsIgnoreCase("AES-128")) {
                    keyUri = attr(line, "URI");
                    ivHex = attr(line, "IV");
                }
                continue;
            }
            if (line.startsWith("#EXTINF")) {
                nextIsSeg = true;
                continue;
            }
            if (line.startsWith("#")) continue;
            if (nextIsSeg) {
                segs.add(resolve(cur, line));
                nextIsSeg = false;
            }
        }
        if (segs.isEmpty()) throw new RuntimeException("清单里没有分片");

        byte[] key = null;
        if (keyUri != null) key = getBytes(resolve(cur, keyUri));

        File out = new File(dir, name + (hasMap ? ".mp4" : ".ts"));
        if (out.exists()) out.delete();
        FileOutputStream fos = new FileOutputStream(out, true);
        BufferedOutputStream bos = new BufferedOutputStream(fos, 16 * 1024);
        int total = segs.size();
        int doneCount = 0;
        long seq = 0;
        try {
            for (String s : segs) {
                byte[] data = getBytesRetry(s, 3);
                if (key != null && data != null) data = decrypt(data, key, iv(ivHex, seq));
                if (data != null && data.length > 0) bos.write(data);
                doneCount++;
                seq++;
                if (doneCount % 5 == 0 || doneCount == total) progress(ctx, name, doneCount, total);
            }
        } finally {
            try {
                bos.flush();
                bos.close();
            } catch (Throwable ignored) {
            }
        }
        if (out.length() <= 0) throw new RuntimeException("没有下到任何数据（源可能需要特定请求头或已过期）");
        scan(ctx, out);
        done(ctx, name, true, out.getAbsolutePath());
    }

    private static String pickVariant(String base, String text) {
        try {
            String[] lines = text.split("\\r?\\n");
            long bestBand = -1;
            String best = null;
            long band = 0;
            for (String raw : lines) {
                String line = raw.trim();
                if (line.startsWith("#EXT-X-STREAM-INF")) {
                    String b = attr(line, "BANDWIDTH");
                    band = b == null ? 0 : parseLong(b);
                    continue;
                }
                if (line.isEmpty() || line.startsWith("#")) continue;
                if (band >= bestBand) {
                    bestBand = band;
                    best = resolve(base, line);
                }
                band = 0;
            }
            return best;
        } catch (Throwable e) {
            return null;
        }
    }

    private static String resolve(String base, String rel) {
        String r = rel == null ? "" : rel.trim();
        if (r.startsWith("http://") || r.startsWith("https://")) return r;
        try {
            URI b = URI.create(base);
            URI u = b.resolve(r);
            if (u != null) return u.toString();
        } catch (Throwable ignored) {
        }
        try {
            int q = base.indexOf('?');
            String clean = q > 0 ? base.substring(0, q) : base;
            int sl = clean.lastIndexOf('/');
            if (sl > 0) return clean.substring(0, sl + 1) + r;
        } catch (Throwable ignored) {
        }
        return r;
    }

    private static String getText(String url) throws Exception {
        byte[] b = getBytes(url);
        if (b == null) return null;
        return new String(b, "UTF-8");
    }

    private static final String TK_UA = "Mozilla/5.0 (Linux; Android 9; TV) AppleWebKit/537.36 "
            + "(KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36";

    private static String refererOf(String url) {
        try {
            int i = url.indexOf("://");
            if (i < 0) return null;
            int j = url.indexOf('/', i + 3);
            if (j < 0) return null;
            return url.substring(0, j + 1);
        } catch (Throwable t) {
            return null;
        }
    }

    private static byte[] getBytes(String url) throws Exception {
        Request.Builder rb = new Request.Builder().url(url).get();
        rb.header("User-Agent", TK_UA);
        String tkRef = refererOf(url);
        if (tkRef != null) rb.header("Referer", tkRef);
        Request req = rb.build();
        Response resp = CLIENT.newCall(req).execute();
        try {
            ResponseBody body = resp.body();
            if (!resp.isSuccessful() || body == null) throw new RuntimeException("HTTP " + resp.code());
            return body.bytes();
        } finally {
            try {
                resp.close();
            } catch (Throwable ignored) {
            }
        }
    }

    private static byte[] getBytesRetry(String url, int tries) {
        Throwable last = null;
        for (int i = 0; i < tries; i++) {
            try {
                byte[] b = getBytes(url);
                if (b != null && b.length > 0) return b;
                last = new RuntimeException("空响应");
            } catch (Throwable e) {
                last = e;
            }
            try {
                Thread.sleep(400L * (i + 1));
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                return null;
            }
        }
        if (last != null) last.printStackTrace();
        return null;
    }

    private static String attr(String line, String name) {
        try {
            String tag = name + "=";
            int i = line.indexOf(tag);
            if (i < 0) return null;
            int start = i + tag.length();
            if (start >= line.length()) return null;
            char c = line.charAt(start);
            if (c == '"') {
                int end = line.indexOf('"', start + 1);
                if (end > start) return line.substring(start + 1, end);
                return null;
            }
            int end = start;
            while (end < line.length()) {
                char ch = line.charAt(end);
                if (ch == ',' || ch == '"') break;
                end++;
            }
            return line.substring(start, end).trim();
        } catch (Throwable e) {
            return null;
        }
    }

    private static long parseLong(String s) {
        try {
            return Long.parseLong(s.trim());
        } catch (Throwable e) {
            return 0;
        }
    }

    private static byte[] iv(String ivHex, long seq) {
        byte[] out = new byte[16];
        if (ivHex != null && ivHex.length() >= 32) {
            try {
                String h = ivHex.startsWith("0x") || ivHex.startsWith("0X") ? ivHex.substring(2) : ivHex;
                if (h.length() >= 32) {
                    for (int i = 0; i < 16; i++) {
                        out[i] = (byte) Integer.parseInt(h.substring(i * 2, i * 2 + 2), 16);
                    }
                    return out;
                }
            } catch (Throwable ignored) {
            }
        }
        for (int i = 0; i < 8; i++) {
            out[15 - i] = (byte) ((seq >>> (8 * i)) & 0xFF);
        }
        return out;
    }

    private static byte[] decrypt(byte[] data, byte[] key, byte[] iv) throws Exception {
        Cipher c = Cipher.getInstance("AES/CBC/PKCS5Padding");
        c.init(Cipher.DECRYPT_MODE, new SecretKeySpec(key, "AES"), new IvParameterSpec(iv));
        return c.doFinal(data);
    }

    private static void scan(Context ctx, File f) {
        try {
            android.media.MediaScannerConnection.scanFile(ctx, new String[]{f.getAbsolutePath()}, null, null);
        } catch (Throwable ignored) {
        }
    }

    // ---------------------------------------------------------------- 提示
    private static void tip(final Context ctx, final String msg) {
        try {
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    try {
                        Toast.makeText(ctx, msg, Toast.LENGTH_SHORT).show();
                    } catch (Throwable ignored) {
                    }
                }
            });
        } catch (Throwable ignored) {
        }
    }

    private static void progress(Context ctx, String name, int done, int total) {
        try {
            Job j = CUR;
            if (j != null) {
                j.total = total;
                j.done = done;
            }
            NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm == null) return;
            if (Build.VERSION.SDK_INT >= 26) {
                nm.createNotificationChannel(new NotificationChannel(CHANNEL, "下载", NotificationManager.IMPORTANCE_LOW));
            }
            NotificationCompat.Builder b = new NotificationCompat.Builder(ctx, CHANNEL)
                    .setSmallIcon(android.R.drawable.stat_sys_download)
                    .setContentTitle("正在下载 " + name)
                    .setContentText(done + " / " + total + " 段")
                    .setProgress(total, done, false)
                    .setOngoing(true)
                    .setOnlyAlertOnce(true);
            nm.notify(NOTI_ID, b.build());
        } catch (Throwable ignored) {
        }
    }

    private static void done(Context ctx, String name, boolean ok, String extra) {
        try {
            Job j = CUR;
            if (j != null) {
                j.status = ok ? ST_OK : ST_FAIL;
                j.msg = extra == null ? "" : extra;
                if (ok) {
                    j.done = j.total;
                }
            }
            NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm != null) {
                if (Build.VERSION.SDK_INT >= 26) {
                    nm.createNotificationChannel(new NotificationChannel(CHANNEL, "下载", NotificationManager.IMPORTANCE_LOW));
                }
                NotificationCompat.Builder b = new NotificationCompat.Builder(ctx, CHANNEL)
                        .setSmallIcon(ok ? android.R.drawable.stat_sys_download_done : android.R.drawable.stat_notify_error)
                        .setContentTitle((ok ? "下载完成 " : "下载失败 ") + name)
                        .setContentText(extra == null ? "Movies/tvbox" : extra)
                        .setAutoCancel(true);
                nm.notify(NOTI_ID, b.build());
            }
            tip(ctx, (ok ? "下载完成：" : "下载失败：") + name + (extra == null ? "" : ("\n" + extra)));
        } catch (Throwable ignored) {
        }
    }

    /** 详情页「下载」按钮上的文字：没任务→「下载」；有任务→「下载 3/10」，有失败带个标记。 */
    public static String label() {
        synchronized (TASKS) {
            if (TASKS.isEmpty()) return "下载";
            int total = TASKS.size();
            int okc = 0;
            int fail = 0;
            for (Job t : TASKS) {
                if (t.status == ST_OK) okc++;
                else if (t.status == ST_FAIL) fail++;
            }
            String s = "↓" + okc + "/" + total;
            if (fail > 0) s = s + "·" + fail;
            return s;
        }
    }

    /** 下载列表正文：每集一行，排队/下载中百分比/完成/失败原因。 */
    public static String listText() {
        StringBuilder sb = new StringBuilder();
        synchronized (TASKS) {
            if (TASKS.isEmpty()) return "还没有下载任务";
            for (int i = TASKS.size() - 1; i >= 0; i--) {
                Job t = TASKS.get(i);
                sb.append(t.name).append("    ");
                if (t.status == ST_QUEUE) {
                    sb.append("排队中");
                } else if (t.status == ST_RUN) {
                    if (t.total > 0) sb.append("下载中 ").append(t.done * 100 / t.total).append("%");
                    else sb.append("下载中");
                } else if (t.status == ST_OK) {
                    sb.append("完成");
                } else {
                    sb.append("失败");
                    if (t.msg != null && !t.msg.isEmpty()) sb.append("：").append(t.msg);
                }
                sb.append("\n\n");
            }
        }
        return sb.toString();
    }

    public static void showList(Context ctx) {
        try {
            new AlertDialog.Builder(ctx)
                    .setTitle("下载列表")
                    .setMessage(listText())
                    .setPositiveButton("知道了", null)
                    .show();
        } catch (Throwable ignored) {
        }
    }
}
"""


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
ICONS['v_download'] = ('<vector xmlns:android="http://schemas.android.com/apk/res/android"'
    ' android:width="26dp" android:height="26dp"'
    ' android:viewportWidth="24" android:viewportHeight="24" android:tint="#FFFFFF">'
    '<group android:pivotX="12.0" android:pivotY="12.0" android:scaleX="0.9545" android:scaleY="0.9545">'
    '<path android:fillColor="@android:color/white" android:pathData="M9.5,2h5v10h-5z"/>'
    '<path android:fillColor="@android:color/white" android:pathData="M5.5,11h13l-6.5,9.5z"/>'
    '<path android:fillColor="@android:color/white" android:pathData="M3,20.5h18v2.5h-18z"/>'
    '</group></vector>')

# NZ 品牌图标：圆角实心播放三角 + 镂空 NZ（evenOdd 负空间）。
# 只用两种元素——播放三角（视频）与 NZ 两个字母，缩到 48px 仍能认出。
# ---------------------------------------------------------------- 桌面启动图标（NZ）
# 图形用 M2：右指圆角三角被两道平行斜缝切成三块，读作「速度条 / 播放」，单色白。
# 落地方式：Android 8+ 走 adaptive icon（渐变满幅、不受系统白底方框裁切），
# 老设备走各密度 PNG（同时覆盖上游原有的 drawable-*/app_icon.png）。
ICON_M2_PATH = ('M14.82 8.74 L16.32 14.44 L17.91 13.58 L18.6 13.18 L19.02 12.89 L19.31 12.62 L19.45 12.43 L19.52 12.29 L19.57 12.1 L19.57 11.9 L19.52 11.71 L19.45 11.57 L19.31 11.38 L19.14 11.21 L18.83 10.97 L18.23 10.6 Z M10.39 6.33 L13.01 16.25 L15.56 14.86 L13.89 8.47 L13.8 8.18 Z M6.01 4.25 L5.79 4.28 L5.61 4.35 L5.44 4.47 L5.31 4.62 L5.2 4.82 L5.13 5.01 L5.06 5.33 L5.02 5.69 L5.0 6.12 L5.0 17.88 L5.02 18.31 L5.07 18.73 L5.13 18.99 L5.26 19.3 L5.39 19.48 L5.61 19.65 L5.79 19.72 L6.08 19.75 L6.33 19.72 L6.65 19.63 L7.06 19.46 L7.58 19.2 L12.22 16.68 L12.24 16.64 L9.38 5.78 L7.75 4.89 L6.95 4.49 L6.42 4.3 L6.21 4.26 Z')

ICON_B64 = {
    'mdpi': ('iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAIAAADYYG7QAAADtUlEQVR42s3YTWicRRzH8e88SVNJjWJblebQxmDqppisydqDB19ysCIeRNFLQRHBkydBRUVLLdWDL0cLVQvSi1RQiyJ4sNGC5tCa7CraGIOIUVQQ02325Xl2n+eZ8fBk3WefndmMdnWfYQ+7wzzPfnaemfn/WKFeG0YKVOMVf2/V6aDQj5QOChC6+5uucpxUaVDCSZUmBkqHBoWTKg1SOKnStK6hFGh0oJ5q2kC91thv+/9Jg3KcVGkaM5QaDVL0W2noY/J2/IDFOXz/v9Og6Leam6m7uP8gQOlPZo/z+UmU332NBK/mWD2pnVmiNrSNux/jqbfJznRTE4Lrcf4CZdexWjebtxBv24bZ/xzOAJdfdbEaCRWP80XKLqFCin6rX4kg0QYuYeR6RicYm+a9o6z88I81IXgeVY+Q+FWO1Zxr2+4ciwtkcjx9lEcOsH3YVhMoym70gBKaxLY373Ct6bocP31PtYQQ5G7l4DEmb9pAEyrKVYpruLUmJf5dspkYO5432jYyzqZBlr5a/7hpgL0zDAyy7176Nic1gaRcYbWIW0eij6mymRg3PP10zeljbJLv8s2ePTdQq3HzHbz8JrfdSZRtgpByheIF3HrsvNFrIpDFWWwyZXKci4Euu4IdI3xbYOt2Hn6U519ldDfFNbw6UthoIpBFZcCwrjPT/PYLq3+0TNI3jYd4zbUcfoVnDzE4ZKlBmqp9sjIYZmh4F0NbOVeIESc4M0cQNHtumeHJZyw1hpDfXqdMTQgyUy2g8QlKFZYWkyPtNLpqr62aHUx7psifRTXmcMuljI2Tn28OOH2aF1+y1LSFfFMN79AyWX5eYeXHZk/2RhbmAZaXefwJDhyiVLHUoFpKhzlRYDZdeTU7dlKYZ9foes9UjhPv8MJhTn1qOv1Mmnhi3CjfdGjZveTPrr8vrTH3BX7IJ7P/QvP3GroITfSMCgVqHh99wEMP8O779nsqoYkS40aaUBGEnUCT07ge+++jWLI/b7SaaA2ZNaHE9ajVCM2g/Je8cQRJVzQo0a/XhJJqhVq9055fXuLYERYWGld1QYNKhPyoFnoeXr2ls1ptofz+K2+9zmenkHRX05oY6wGeR93X3Hfxa/bdA1Bc5cRxPjyJH8QGdE3TOIf8ANel7qMMf6jNfoznE0rOzOH5rQO6qUE5Qj04gR82IrfQ52KpLcDd1yCFkypNLDGmQ9NIjKnRoES6NKbE2DONNjH2UtOeGHusSSTG3mtiAS0dGt051FNN2znUaw1S/AW/D1vXNvrl4QAAAABJRU5ErkJggg=='),
    'hdpi': ('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'),
    'xhdpi': ('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'),
    'xxhdpi': ('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'),
    'xxxhdpi': ('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'),
}

ICON_BG_XML = ('<vector xmlns:android="http://schemas.android.com/apk/res/android"'
    ' xmlns:aapt="http://schemas.android.com/aapt"'
    ' android:width="108dp" android:height="108dp"'
    ' android:viewportWidth="108" android:viewportHeight="108">'
    '<path android:pathData="M0,0h108v108h-108z">'
    '<aapt:attr name="android:fillColor">'
    '<gradient android:startX="0" android:startY="0" android:endX="108" android:endY="108"'
    ' android:type="linear">'
    '<item android:offset="0" android:color="#FFFF8A00"/>'
    '<item android:offset="0.5" android:color="#FFFF3F63"/>'
    '<item android:offset="1" android:color="#FFFF0F6B"/>'
    '</gradient></aapt:attr></path>'
    '<path android:pathData="M0,0h108v30l-108,52z" android:fillColor="#1AFFFFFF"/>'
    '</vector>')

ICON_FG_XML = ('<vector xmlns:android="http://schemas.android.com/apk/res/android"'
    ' android:width="108dp" android:height="108dp"'
    ' android:viewportWidth="108" android:viewportHeight="108">'
    '<group android:translateX="41.1" android:translateY="42"'
    ' android:scaleX="3.32" android:scaleY="3.32"'
    ' android:pivotX="12.9" android:pivotY="12">'
    '<path android:fillColor="#FFFFFF" android:fillType="evenOdd"'
    ' android:pathData="' + ICON_M2_PATH + '"/>'
    '</group></vector>')

ADAPTIVE_XML = ('<?xml version="1.0" encoding="utf-8"?>\n'
    '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">'
    '<background android:drawable="@drawable/ic_launcher_background"/>'
    '<foreground android:drawable="@drawable/ic_launcher_foreground"/>'
    '</adaptive-icon>')


def apply_app_icon():
    """桌面启动图标换成 NZ（M2 图形 + 橙红渐变）；只动图标资源与清单的一行。"""
    res = jp(SRC, 'app/src/main/res')
    adir = os.path.join(res, 'mipmap-anydpi-v26')
    os.makedirs(adir, exist_ok=True)
    write_text(os.path.join(adir, 'ic_launcher.xml'), ADAPTIVE_XML)
    write_text(os.path.join(adir, 'ic_launcher_round.xml'), ADAPTIVE_XML)
    ddir = os.path.join(res, 'drawable')
    os.makedirs(ddir, exist_ok=True)
    write_text(os.path.join(ddir, 'ic_launcher_background.xml'), ICON_BG_XML)
    write_text(os.path.join(ddir, 'ic_launcher_foreground.xml'), ICON_FG_XML)
    for dens, b in ICON_B64.items():
        p = os.path.join(res, 'mipmap-' + dens)
        os.makedirs(p, exist_ok=True)
        with open(os.path.join(p, 'ic_launcher.png'), 'wb') as f:
            f.write(base64.b64decode(b))
    for dens in ('hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi'):
        p = os.path.join(res, 'drawable-' + dens)
        if os.path.isdir(p) and dens in ICON_B64:
            with open(os.path.join(p, 'app_icon.png'), 'wb') as f:
                f.write(base64.b64decode(ICON_B64[dens]))
    man = jp(SRC, 'app/src/main/AndroidManifest.xml')
    t = read_text(man)
    if '@mipmap/ic_launcher' not in t:
        t2 = t.replace('android:icon="@drawable/app_icon"',
                       'android:icon="@mipmap/ic_launcher" android:roundIcon="@mipmap/ic_launcher_round"')
        if t2 == t:
            t2 = re.sub(r'android:icon="@[^"]*"',
                        'android:icon="@mipmap/ic_launcher" android:roundIcon="@mipmap/ic_launcher_round"',
                        t, count=1)
        write_text(man, t2)
    if '@mipmap/ic_launcher' not in read_text(man):
        raise RuntimeError('桌面图标指向写入失败')
    print('  + 桌面图标：NZ（M2 速度条）+ 橙红渐变，adaptive + %d 档 PNG' % len(ICON_B64))


BTN_ICON['play_download'] = 'v_download'


def write_icons():
    ddir = jp('app/src/main/res/drawable')
    os.makedirs(ddir, exist_ok=True)
    for name, xml in ICONS.items():
        xml = re.sub(r'android:(width|height)="[0-9.]+dp"',
                     'android:\\1="' + ICON_SIZE + '"', xml)
        # 重播：环形箭头中间是空的，视觉重量比同排实心图标轻，实测看着小一号。
        # 内层放大 1.136 → 1.28（约 +12.7%），外接框仍在 23dp 画布内，不会被裁。
        if name == 'v_replay':
            xml = xml.replace('android:scaleX="1.136" android:scaleY="1.136"',
                              'android:scaleX="1.28" android:scaleY="1.28"', 1)
        write_text(os.path.join(ddir, name + '.xml'), xml)
    # 弹幕“已开启”图标：左下角一个小对号，画布/尺寸不变
    base_danmu = ICONS.get('v_danmu', '')
    if base_danmu:
        mark = ('<path android:pathData="M58,292 L74,308 L104,268"'
                ' android:strokeColor="#FFFFFF" android:strokeWidth="18"'
                ' android:fillColor="@android:color/transparent"/>')
        on_xml = base_danmu.replace('</vector>', mark + '</vector>', 1)
        on_xml = re.sub(r'android:(width|height)="[0-9.]+dp"',
                        'android:\\1="' + ICON_SIZE + '"', on_xml)
        write_text(os.path.join(ddir, 'v_danmu_on.xml'), on_xml)
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
    if bottom is not None:
        # 上游 vs_20 = 20mm（≈75dp），竖屏两侧被吃掉 15cm 视野；改为按横/竖屏取值的 dimen
        bottom.set(A + 'paddingLeft', '@dimen/tk_row_pad_lr')
        bottom.set(A + 'paddingRight', '@dimen/tk_row_pad_lr')
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
        # 整排按钮统一按盒子居中对齐，不吃文字基线：
        # 片头/片尾外面套了一层容器（把 00:00 叠在图标位），容器没有文字基线，
        # 与按基线排的普通按钮必然差一截（就是那 11/24px）。关掉基线对齐后，
        # 全排只按一种规则摆，四枚汉字自然与「重置」同一条线，不用任何运行时补偿。
        group.set(A + 'baselineAligned', 'false')
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
    group.set(A + 'clipChildren', 'false')
    group.set(A + 'clipToPadding', 'false')
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

    # ③.5 底栏贴底加固：把 bottom_container 套进一层 match_parent 的垂直锚（gravity=bottom）。
    # 上游只靠 rootView 的 layout_gravity="bottom" 定位；一旦根容器高度/重力被别处改动
    # （旋屏后实机出现过底栏浮在半空），底栏就跟着走。套一层和父等高、自身居底的锚，
    # 底栏与父容器底边强绑定，不再依赖同级重力。
    par = pm.get(bottom)
    if par is not None and par.tag == 'FrameLayout' and par.get(A + 'id') != '@+id/tk_bottom_anchor':
        idx = list(par).index(bottom)
        par.remove(bottom)
        anc = ET.Element('LinearLayout')
        anc.set(A + 'id', '@+id/tk_bottom_anchor')
        anc.set(A + 'layout_width', 'match_parent')
        anc.set(A + 'layout_height', 'match_parent')
        anc.set(A + 'orientation', 'vertical')
        anc.set(A + 'gravity', 'bottom')
        anc.append(bottom)
        bottom.attrib.pop(A + 'layout_gravity', None)
        par.insert(idx, anc)
        pm = parents(root)
        log('底栏贴底加固：bottom_container 套进 match_parent 居底锚')

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
    # 注意：这里写出的 tk_time_ts / tk_row_pad_lr 必须与 apply_static_ui 的最终值保持一致
    #       （14dp / 24dp）。以前写的是 16dp / 35dp，靠 static_ui 后跑覆盖掉才没出事，
    #       一旦 static_ui 因幂等跳过，第二次跑就会把字号和边距悄悄放大。
    for rel, inset, minw, rowpad in (('values', '0dp', '0dp', '24dp'), ('values-port', '0dp', '0dp', '5dp')):
        d = os.path.join(SRC, 'app/src/main/res', rel)
        os.makedirs(d, exist_ok=True)
        xml = ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
               + '    <dimen name="tk_seek_inset">' + inset + '</dimen>\n'
               + '    <dimen name="tk_time_minw">' + minw + '</dimen>\n'
               + '    <dimen name="tk_time_ts">' + ('14dp' if rel == 'values' else '10dp') + '</dimen>\n'
               + '    <dimen name="tk_row_pad_lr">' + rowpad + '</dimen>\n'
               + '    <dimen name="tk_time_gap">' + ('0.5dp' if rel == 'values' else '0.6dp') + '</dimen>\n'
               + '    <dimen name="tk_btn_gap">3dp</dimen>\n'
               + '</resources>\n')
        open(os.path.join(d, 'tk_dimens.xml'), 'w', encoding='utf-8').write(xml)
    log('进度条收边：横屏边 35dp / 竖屏边 5dp；条与时间 横屏0.5dp / 竖屏0.6dp')

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
            ct.set(A + 'layout_marginEnd', '@dimen/tk_time_gap')
            ct.set(A + 'textSize', '@dimen/tk_time_ts')
            ct.set(A + 'textColor', '@android:color/white')
            ct.set(A + 'minWidth', '@dimen/tk_time_minw')
            ct.set(A + 'gravity', 'center_vertical|right')
        if tt is not None:
            tt.set(A + 'layout_marginStart', '@dimen/tk_time_gap')
            tt.set(A + 'textSize', '@dimen/tk_time_ts')
            tt.set(A + 'textColor', '#B3FFFFFF')
            tt.set(A + 'minWidth', '@dimen/tk_time_minw')
            tt.set(A + 'gravity', 'center_vertical|left')
        seek_row.set(A + 'layout_marginBottom', '3dp')
        bottom.set(A + 'background', '@null')
        sub = find_id(root, 'subtitle_view')
        if sub is not None:
            sub.set(A + 'layout_marginBottom', '104dp')
            log('字幕：底部抬高 104dp，不再压住按钮')
        lp = find_id(root, 'landscape_portrait')
        if lp is not None: lp.set(A + 'visibility', 'gone')
        log('间距：时间↔条 3dp、条↔按钮排 5dp；底板去掉；旋屏按画面自动显示')

    # ⑧ 片头 / 片尾：00:00 时间格整个删掉，这两枚汉字直接与「重置」同构，
    #     同一排、同一套对齐规则，别再让额外的容器/叠层把字往下推。
    for rid, text in (('play_time_start', '片头'), ('play_time_end', '片尾')):
        node = find_id(root, rid)
        if node is None or node.tag != 'TextView':
            continue
        # 整个节点属性清空重建：历次补偿（负 margin/容器内偏移/旧图标）全部丢掉，
        # 属性顺序也固定下来，保证连跑两遍的输出完全一致。
        vid = node.get(A + 'id')
        node.attrib.clear()
        if vid is not None:
            node.set(A + 'id', vid)
        node.set(A + 'layout_width', 'wrap_content')
        node.set(A + 'layout_height', 'wrap_content')
        # 与「重置」逐项对齐：左右 6dp、上 4dp、下 0dp、一行 8dp 字、图标位 23dp 透明占位
        node.set(A + 'paddingLeft', PAD_LR)
        node.set(A + 'paddingRight', PAD_LR)
        node.set(A + 'paddingTop', '4dp')
        node.set(A + 'paddingBottom', '0dp')
        node.set(A + 'layout_marginEnd', '@dimen/tk_btn_gap')
        node.set(A + 'gravity', 'top|center_horizontal')
        node.set(A + 'textSize', TEXT_SIZE)
        node.set(A + 'singleLine', 'true')
        node.set(A + 'textColor', '@android:color/white')
        node.set(A + 'text', text)
        node.set(A + 'includeFontPadding', 'false')
        node.set(A + 'drawableTop', '@drawable/tk_space')
        node.set(A + 'drawablePadding', '0dp')
    log('片头/片尾：00:00 时间格已删除，四枚汉字与「重置」逐项同构')

    tree.write(path, encoding='utf-8', xml_declaration=True)

    # 轨道再细一档：3dp -> 2dp
    seek_drawable = jp('app/src/main/res/drawable/shape_player_control_vod_seek.xml')
    if os.path.isfile(seek_drawable):
        sd = read_text(seek_drawable).replace('android:height="3dp"', 'android:height="2dp"')
        write_text(seek_drawable, sd)
        log('进度条轨道：3dp -> 2dp')


# ---------------------------------------------------------------- Java
TIME_PATCH = [
    # tk：00:00 时间格已删除，这两个按钮只显示汉字，不再显示时间
    ('mPlayerTimeStartBtn.setText(start == 0 ? "片头" : stringForTime(start * 1000));',
     'mPlayerTimeStartBtn.setText("片头");'),
    ('mPlayerTimeSkipBtn.setText(end == 0 ? "片尾" : stringForTime(end * 1000));',
     'mPlayerTimeSkipBtn.setText("片尾");'),

    ('Toast.makeText(getContext(), "已移除视频广告 "+M3u8.currentAdCount+" 条", Toast.LENGTH_SHORT).show();',
     '// 静默：不再弹出广告过滤条数提示'),
]

HELPERS = '''
    // 切播放器/切解码后会 replay 重建 player，标签可能被刷回旧值 → 延迟再同步一次
    private void tkRefreshCfgView() {
        try {
            if (myHandle != null) {
                myHandle.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        updatePlayerCfgView();
                    }
                }, 500);
            }
        } catch (Throwable ignored) {
        }
    }

'''


SHORT_NAMES = [('"EXO播放器"', '"EXO"'), ('"IJK播放器"', '"IJK"'), ('"MX播放器"', '"MX"'),
               ('"Reex播放器"', '"Reex"'), ('"Kodi播放器"', '"Kodi"'), ('"VLC播放器"', '"VLC"'), ('"附近TVBox"', '"TVBox"')]


BUILTIN_ADS = ['mimg.0c1q0l.cn', 'mc.usihnbcq.cn', 'mg.g1mm3d.cn', 'mscs.svaeuzh.cn',
    'tp.vinuxhome.com', 'www.baihuillq.com', 'stj.v1vo.top', 'img.mosflower.cn', 'tips.gamevvip.com',
    'ehwe.yhdtns.com', 'xdn.cqqc3.com', 'www.jixunkyy.cn', 'sp.chemacid.cn', 'xg.gars57.cn',
    'k.jinxiuzhilv.com', 'ppl.xunzhuo123.com', 'xomk.jiangjunmh.top', 'img.xunzhuo123.com',
    'xg.huataisangao.cn', 'thy.dacedsfa.cn', 'xg.whsbpw.cn', 'f5w.as12df.top', 'www.92424.cn',
    'k.wudejia.com', 'vivovip.mmszxc.top', 'qiu.xixiqiu.com', 'wofwk.aoidf3.com',
    'xc.hubeijieshikj.cn', 'tj.tianwenhu.com', 'vip.ffzyad.com', 'ae01.alicdn.com']

BUILTIN_BLK = [{'name': '暴风', 'hosts': ['bfzy', 'bfbfvip', 'bfengbf'], 'regex': ['#EXTINF.*?\\s+.*?adjump.*?\\.ts']}, {'name': '量子', 'hosts': ['vip.lz', 'hd.lz', '.cdnlz'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:7\\.166667,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXTINF.*?\\s+.*?08646.*?\\.ts', '#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF.*?6\\.667,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXTINF.*?\\s+.*?48234.*?\\.ts', '#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF.*?7\\.067,[\\s\\S]*?#EXT-X-DISCONTINUITY', '17.19', '19.63']}, {'name': '非凡', 'hosts': ['vip.ffzy', 'hd.ffzy', 'super.ffzy', 'cachem3u8.2s0'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:6\\.400000,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:6\\.666667,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXTINF.*?\\s+.*?1171(057).*?\\.ts', '#EXTINF.*?\\s+.*?6d7b(077).*?\\.ts', '#EXTINF.*?\\s+.*?6718a(403).*?\\.ts', '17.99', '14.45']}, {'name': '索尼', 'hosts': ['suonizy'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:1\\.000000,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXTINF.*?\\s+.*?p1ayer.*?\\.ts', '#EXTINF.*?\\s+.*?\\/video\\/original.*?\\.ts']}, {'name': '快看', 'hosts': ['kuaikan'], 'regex': ['#EXT-X-KEY:METHOD=NONE\\r*\\n*#EXTINF:5,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXT-X-KEY:METHOD=NONE\\r*\\n*#EXTINF:2\\.4,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXT-X-KEY:METHOD=NONE\\r*\\n*#EXTINF:1\\.467,[\\s\\S]*?#EXT-X-DISCONTINUITY']}, {'name': 'leshiyun', 'hosts': ['leshiyuncdn'], 'regex': ['15.92']}, {'name': '看影网', 'hosts': ['fentvoss'], 'regex': ['38.68', '38.12', '38.80', '30.08', '44.00', '36.80', '40.68', '29.08', '29.28', '24.88']}, {'name': '1080zyk', 'hosts': ['high24-playback', 'high20-playback', 'yzzy.play', 'yzzy-dy'], 'regex': ['16.63', '17.66']}, {'name': 'ikun', 'hosts': ['bfikuncdn'], 'regex': ['#EXTINF.*?\\s+.*?XR8pDxQk.*?\\.ts', '#EXTINF.*?\\s+.*?p5XQill8.*?\\.ts']}, {'name': '黑木耳hmr', 'hosts': ['hmrvideo'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:3\\.366667,[\\s\\S]*?#EXT-X-DISCONTINUITY']}, {'name': 'ryplay', 'hosts': ['cdn.ryplay'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:6\\.633333,[\\s\\S]*?#EXT-X-DISCONTINUITY', '#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:8\\.333333,[\\s\\S].*?\\.ts', '#EXTINF:2\\.933333,[\\s\\S].*?\\.ts']}, {'name': '555DM', 'hosts': ['cqxfjz'], 'regex': ['10.56']}, {'name': '海外看', 'hosts': ['haiwaikan'], 'regex': ['10.0099', '10.3333', '16.0599', '8.1748', '10.85']}, {'name': '磁力广告', 'hosts': ['magnet'], 'regex': ['更多', '社 區', 'x u u', '最 新', '更 新', '社 区', '有趣', '有 趣', '英皇体育', '全中文AV在线', '澳门皇冠赌场', '哥哥快来', '美女荷官', '裸聊', '新片首发', 'UUE29']}, {'name': '星星ulivetv', 'hosts': ['aws.ulivetv.net', 'ulivetv'], 'regex': ['#EXT-X-DISCONTINUITY\\r*\\n*#EXTINF:8,[\\s\\S]*?#EXT-X-DISCONTINUITY', '8.1748']}, {'name': '一起看yqk88', 'hosts': ['yqk88'], 'regex': ['#EXT-X-CUE-IN', '18.4', '15.1666', '16.5333']}, {'name': '农民toutiao', 'hosts': ['toutiaovod.com', 'toutiao'], 'regex': ['video/tos/cn']}, {'name': '通用-插片结构', 'hosts': ['*'], 'regex': ['#EXT-X-DISCONTINUITY|#EXTINF:\\s*([0-4]\\.\\d+|5\\.0),\\s*\\n*[^#]', '#EXT-X-CUE-OUT']}]

BUILTIN_PAGE_KW = ['ae01.alicdn.com', 'tips.gamevvip.com']

BUILTIN_PAGE_RE = []

BUILTIN_PAGE_SEL = ["iframe[src*='ads']", "iframe[src*='pop']", "script[src*='cnzz']", "img[src*='ae01.alicdn']"]

BUILTIN_STREAM_RE = [r'#EXT-X-DISCONTINUITY[^#]*#EXTINF[^#]*adjump', r'#EXT-X-DISCONTINUITY[^#]*#EXTINF[^#]*p1ayer', r'#EXTINF:\s*([0-4]\.\d+|5\.0),.*?(\/ad\/|_ad_|preroll|midroll|postroll)']

BUILTIN_HEADER_HOSTS = ['ae01.alicdn.com', 'tips.gamevvip.com']

# 播放页浮层广告文案（娱乐城/博彩/体彩/真人视讯这类，正常影视站不会这么写）
BUILTIN_PAGE_TEXT = ["娱乐城", "博彩", "时时彩", "六合彩", "百家乐", "真人荷官", "体育投注", "滚球",
                     "首存", "注册送", "优惠彩金", "电子游艺", "线上赌场", "AG真人", "沙巴体育",
                     "威尼斯人", "新葡京", "澳门赌场", "老虎机", "棋牌游戏", "彩票代购", "体彩"]



ADRULE_JAVA = r"""package com.github.tvbox.osc.util;

import com.github.catvod.net.OkHttp;
import com.github.tvbox.osc.base.App;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;

/**
 * 去广告规则自动更新（轻量）：
 * 默认从 tvbox-server 的 tvbox.json 里只取 ads + rules 两段，24 小时最多拉一次，
 * 失败/404 静默，直接用本地缓存或内置规则，绝不影响播放。
 */
public class AdRuleUpdater {

    private static final String RULES_URL = "https://raw.githubusercontent.com/nzsm/tvbox-server/main/tvbox.json";
    private static final long INTERVAL = 24L * 60L * 60L * 1000L;
    private static String lastApply = "";

    private static File cacheFile() {
        return new File(App.getInstance().getFilesDir(), "adrules.json");
    }

    /** VideoParseRuler 被 clearRule 之后调用，允许缓存规则重新套一遍 */
    public static void reset() {
        lastApply = "";
    }

    /** 启动/换源时同步套用本地缓存（不联网） */
    public static void loadCache() {
        try {
            if (!AdBlocker.enabled()) return;
            File f = cacheFile();
            if (!f.exists() || f.length() < 20) return;
            apply(FileUtils.read(f.getAbsolutePath()));
        } catch (Throwable ignored) {
        }
    }

    /** 24h 节流后台更新；开关关着就不更新 */
    public static void autoUpdate() {
        try {
            if (!AdBlocker.enabled()) return;
            File f = cacheFile();
            if (f.exists() && System.currentTimeMillis() - f.lastModified() < INTERVAL) return;
            new Thread(new Runnable() {
                @Override
                public void run() {
                    try {
                        String txt = OkHttp.string(RULES_URL, 15000);
                        if (txt == null || txt.length() < 20) return;
                        if (new Gson().fromJson(txt, JsonObject.class) == null) return;
                        File dst = cacheFile();
                        File tmp = new File(dst.getAbsolutePath() + ".tmp");
                        FileOutputStream fos = new FileOutputStream(tmp);
                        fos.write(txt.getBytes("UTF-8"));
                        fos.flush();
                        fos.close();
                        if (dst.exists()) dst.delete();
                        tmp.renameTo(dst);
                        lastApply = "";
                        apply(txt);
                    } catch (Throwable ignored) {
                    }
                }
            }, "tk-adrules").start();
        } catch (Throwable ignored) {
        }
    }

    private static void apply(String txt) {
        try {
            if (txt == null || txt.equals(lastApply)) return;
            JsonObject root = new Gson().fromJson(txt, JsonObject.class);
            if (root == null) return;
            lastApply = txt;
            JsonArray ads = root.getAsJsonArray("ads");
            if (ads != null) {
                for (JsonElement e : ads) {
                    try {
                        String h = e.getAsString();
                        if (h == null || h.length() < 4) continue;
                        if (h.contains("google-analytics") || h.contains("googletagmanager") || h.contains("cnzz")) continue;
                        AdBlocker.addAdHost(h);
                    } catch (Throwable ignored) {
                    }
                }
            }
            JsonArray rules = root.getAsJsonArray("rules");
            if (rules == null) return;
            for (JsonElement e : rules) {
                try {
                    if (!e.isJsonObject()) continue;
                    JsonObject o = e.getAsJsonObject();
                    String name = o.has("name") ? o.get("name").getAsString() : "";
                    if (name.contains("proxy") || name.contains("嗅探") || name.contains("解析")) continue;
                    ArrayList<String> hosts = new ArrayList<>();
                    addStrings(hosts, o.get("hosts"));
                    addStrings(hosts, o.get("host"));
                    ArrayList<String> regex = new ArrayList<>();
                    addStrings(regex, o.get("regex"));
                    ArrayList<String> rule = new ArrayList<>();
                    addStrings(rule, o.get("rule"));
                    for (String h : hosts) {
                        if (!regex.isEmpty()) VideoParseRuler.addHostRegex(h, regex);
                        if (!rule.isEmpty()) VideoParseRuler.addHostRule(h, rule);
                    }
                } catch (Throwable ignored) {
                }
            }
        } catch (Throwable ignored) {
        }
    }

    private static void addStrings(ArrayList<String> out, JsonElement e) {
        if (e == null || e.isJsonNull()) return;
        try {
            if (e.isJsonArray()) {
                for (JsonElement one : e.getAsJsonArray()) {
                    String v = one.getAsString();
                    if (v != null && v.length() > 0 && !out.contains(v)) out.add(v);
                }
            } else {
                String v = e.getAsString();
                if (v != null && v.length() > 0 && !out.contains(v)) out.add(v);
            }
        } catch (Throwable ignored) {
        }
    }
}
"""


def emit_adrules():
    """写 AdRuleUpdater.java + 挂载调用点（启动更新 / 换源套缓存 / 开关打开套缓存）"""
    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/AdRuleUpdater.java'), ADRULE_JAVA)

    ap = jp('app/src/main/java/com/github/tvbox/osc/base/App.java')
    at = read_text(ap)
    anchor_app = '        FileUtils.cleanPlayerCache();'
    assert anchor_app in at, '锚点丢失：App cleanPlayerCache'
    if 'tkWipeOnNewBuild' not in at:
        wipe = (
            '    // tk：换包（versionName 变化）自动清上一版的显示/播放配置，避免残留和新代码打架' + chr(10)
            + '    private void tkWipeOnNewBuild() {' + chr(10)
            + '        try {' + chr(10)
            + '            String now = "";' + chr(10)
            + '            try {' + chr(10)
            + '                now = getPackageManager().getPackageInfo(getPackageName(), 0).versionName;' + chr(10)
            + '            } catch (Throwable ignored) {' + chr(10)
            + '            }' + chr(10)
            + '            if (now == null) now = "";' + chr(10)
            + '            String last = Hawk.get("tkBuildTag", "");' + chr(10)
            + '            if (last != null && last.equals(now)) return;' + chr(10)
            + '            String[] keys = {"doh_url", "doh_json", "m3u8_purify",' + chr(10)
            + '                    "show_preview", "parse_webview", "parse_default", "auto_switch_line",' + chr(10)
            + '                    "subtitle_text_size", "subtitle_time_delay", "subtitle_exo_scale",' + chr(10)
            + '                    "subtitle_exo_position", "danmu_open", "danmu_max_line", "danmu_speed",' + chr(10)
            + '                    "danmu_alpha", "danmu_size_scale", "danmu_random_color", "danmu_api",' + chr(10)
            + '                    "live_show_net_speed", "live_show_resolution", "live_show_time"};' + chr(10)
            + '            for (String k : keys) {' + chr(10)
            + '                try { Hawk.delete(k); } catch (Throwable ignored) {}' + chr(10)
            + '            }' + chr(10)
            + '            Hawk.put("tkBuildTag", now);' + chr(10)
            + '        } catch (Throwable ignored) {' + chr(10)
            + '        }' + chr(10)
            + '    }' + chr(10) + chr(10))
        at = at.replace('    private void initParams() {', wipe + '    private void initParams() {', 1)
        hawk_init = '        Hawk.init(this).build();'
        assert hawk_init in at, '锚点丢失：Hawk.init'
        at = at.replace(hawk_init,
                        hawk_init + chr(10) + '        tkWipeOnNewBuild();', 1)
        at = at.replace(anchor_app,
                        anchor_app + chr(10) + '        com.github.tvbox.osc.util.AdRuleUpdater.autoUpdate();', 1)
        log('换包清零：只清 DNS/去广告/显示/字幕/弹幕，播放器与画面比例设置保留')
    else:
        at = at.replace(anchor_app,
                        anchor_app + chr(10) + '        com.github.tvbox.osc.util.AdRuleUpdater.autoUpdate();', 1)
    write_text(ap, at)

    ac = jp('app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java')
    hc = read_text(ac)
    # 换源套用本地缓存（跟在内置规则后面，同一开关下）
    old1 = '            BuiltinAdRules.apply();'
    assert old1 in hc, '锚点丢失：ApiConfig apply'
    hc = hc.replace(old1, old1 + chr(10) + '            com.github.tvbox.osc.util.AdRuleUpdater.loadCache();', 1)
    hc = hc.replace('            VideoParseRuler.clearRule();',
                    '            VideoParseRuler.clearRule();' + chr(10) + '            com.github.tvbox.osc.util.AdRuleUpdater.reset();', 1)
    hc = hc.replace('if (!infoJson.has("rules")) VideoParseRuler.clearRule();',
                    'if (!infoJson.has("rules")) { VideoParseRuler.clearRule(); com.github.tvbox.osc.util.AdRuleUpdater.reset(); }', 1)
    old2 = '        if (Hawk.get(HawkConfig.M3U8_PURIFY, true)) BuiltinAdRules.apply();'
    assert old2 in hc, '锚点丢失：loadDefaultConfig apply'
    hc = hc.replace(old2,
                    old2 + chr(10) + '        if (Hawk.get(HawkConfig.M3U8_PURIFY, true)) com.github.tvbox.osc.util.AdRuleUpdater.loadCache();', 1)
    write_text(ac, hc)

    mf = jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/ModelSettingFragment.java')
    hf = read_text(mf)
    old3 = '                    com.github.tvbox.osc.util.BuiltinAdRules.apply();'
    assert old3 in hf, '锚点丢失：设置页 apply'
    hf = hf.replace(old3, old3 + chr(10) + '                    com.github.tvbox.osc.util.AdRuleUpdater.loadCache();', 1)
    write_text(mf, hf)

    log('去广告：内置规则 + 本地缓存 + 24h 自动更新（tvbox-server 的 ads/rules）')


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
        # 剔除"0-5 秒短分片一律当广告"这类通杀规则：它会把正片开头/低码率短切片一起删掉，
        # 表现就是广告放完、正片没了、不切换。只有带明确广告特征的才留。
        KEY_AD = ('adjump', 'p1ayer', 'preroll', 'midroll', 'postroll', '/ad/', '_ad_')
        keep = []
        for r in adsRe:
            if '[0-4]' in r and not any(k in r for k in KEY_AD):
                continue
            keep.append(r)
        adsRe = keep
        plain = [r for r in b['regex'] if not ('#EXTINF' in r or '#EXT-X-DISCONTINUITY' in r)]
        for host in b['hosts']:
            if adsRe:
                lines.append('        VideoParseRuler.addHostRegex("%s", %s);' % (esc(host), lit(adsRe)))
            if plain:
                lines.append('        VideoParseRuler.addHostRule("%s", %s);' % (esc(host), lit(plain)))
    for r in BUILTIN_STREAM_RE:
        lines.append('        M3u8.addGlobalRegex("%s");' % esc(r))
    for k in BUILTIN_PAGE_KW:
        lines.append('        AdBlocker.addUrlKeyword("%s");' % esc(k))
    for k in BUILTIN_PAGE_TEXT:
        lines.append('        AdBlocker.addPageTextKeyword("%s");' % esc(k))
    for r in BUILTIN_PAGE_RE:
        lines.append('        AdBlocker.addUrlRegex("%s");' % esc(r))
    for sel in BUILTIN_PAGE_SEL:
        lines.append('        AdBlocker.addPageSelector("%s");' % esc(sel))
    lines += ['    }', '}', '']
    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/BuiltinAdRules.java'), chr(10).join(lines))


TK_ADAPTIVE = """    // 自适应：按屏幕 dp 宽 + 是否电视，调两端时间字号 / 底栏边距 / 按钮间距（图标 23dp 不变）
    private void tkAdaptiveUi() {
        try {
            if (mActivity == null) return;
            android.util.DisplayMetrics dm = mActivity.getResources().getDisplayMetrics();
            float d = dm.density <= 0f ? 1f : dm.density;
            float wDp = dm.widthPixels / d;
            float hDp = dm.heightPixels / d;
            if (wDp <= 0 || hDp <= 0) return;
            boolean portrait = hDp > wDp;
            boolean tv = com.github.tvbox.osc.util.ScreenUtils.isTv(mActivity);
            float ts = 16f, edge = 35f;
            if (portrait) {
                ts = 10f; edge = 5f;
            } else if (tv) {
                ts = Math.max(18f, Math.min(24f, wDp * 0.019f));
                edge = Math.max(48f, Math.min(60f, wDp * 0.052f));
            } else {
                ts = Math.max(14f, Math.min(20f, wDp * 0.0175f));
                edge = Math.max(24f, Math.min(44f, wDp * 0.038f));
            }
            int tsPx = Math.round(ts * d);
            int edgePx = Math.round(edge * d);
            android.widget.TextView c1 = findViewById(R.id.curr_time);
            android.widget.TextView c2 = findViewById(R.id.total_time);
            if (c1 != null) { c1.setTextSize(android.util.TypedValue.COMPLEX_UNIT_PX, tsPx); c1.setIncludeFontPadding(false); }
            if (c2 != null) { c2.setTextSize(android.util.TypedValue.COMPLEX_UNIT_PX, tsPx); c2.setIncludeFontPadding(false); }
            android.view.View bottom = findViewById(R.id.bottom_container);
            if (bottom != null) bottom.setPadding(edgePx, bottom.getPaddingTop(), edgePx, bottom.getPaddingBottom());
            android.view.ViewGroup group = findViewById(R.id.play_btn_group);
            if (group != null) {
                int count = 0;
                int sum = 0;
                for (int i = 0; i < group.getChildCount(); i++) {
                    android.view.View v = group.getChildAt(i);
                    if (v.getVisibility() != android.view.View.VISIBLE) continue;
                    int w = v.getMeasuredWidth();
                    if (w <= 0) {
                        v.measure(android.view.View.MeasureSpec.makeMeasureSpec(0, android.view.View.MeasureSpec.UNSPECIFIED),
                                  android.view.View.MeasureSpec.makeMeasureSpec(0, android.view.View.MeasureSpec.UNSPECIFIED));
                        w = v.getMeasuredWidth();
                    }
                    if (w <= 0) continue;
                    count++;
                    sum += w;
                }
                if (count > 0) {
                    // 固定间距（电视 12dp / 手机 10dp），不再按剩余空间均分放大；太挤才自动压缩
                    int gap = Math.round((tv ? 12f : 10f) * d);
                    int fit = (dm.widthPixels - 2 * edgePx - sum) / count;
                    if (fit < gap) gap = fit;
                    int minGap = Math.round(2f * d);
                    if (gap < minGap) gap = minGap;
                    // 剩余空档左右均分，让按钮整排居中，不偏向左侧
                    int left = dm.widthPixels - 2 * edgePx - sum - count * gap;
                    if (left > 0) group.setPadding(left / 2, group.getPaddingTop(), left / 2, group.getPaddingBottom());
                    for (int i = 0; i < group.getChildCount(); i++) {
                        android.view.View v = group.getChildAt(i);
                        if (v.getVisibility() != android.view.View.VISIBLE) continue;
                        android.view.ViewGroup.LayoutParams lp = v.getLayoutParams();
                        if (lp instanceof android.view.ViewGroup.MarginLayoutParams) {
                            ((android.view.ViewGroup.MarginLayoutParams) lp).rightMargin = gap;
                            v.setLayoutParams(lp);
                        }
                    }
                }
            }
        } catch (Throwable ignored) {
        }
    }

"""


def apply_java():
    NL = chr(10)
    t = read_text(jp(VOD))
    # 幂等：这一套替换（片头尾时间标签、整块可点、旋屏文字）是一次性的，改过就整体跳过，
    # 否则第二次在同一棵树上跑会拿"已经替换后的文本"去找旧锚点，直接 sys.exit。
    if 'mPlayerTimeStartBtn.setText("片头");' in t and 'tkRefreshCfgView' in t and '旋屏");' in t:
        log('  = 按钮文字 / 片头尾 / 旋屏文字已改好，跳过')
        return

    for old, new in TIME_PATCH:
        if new in t:
            continue            # 已经换过：再跑一遍不会把同一处改两次
        if old not in t:
            sys.exit('锚点丢失：' + old)
        t = t.replace(old, new, 1)

    anchor = '    private String getPlayerShortName(int playerType) {'
    if anchor not in t:
        sys.exit('锚点丢失：getPlayerShortName')
    t = t.replace(anchor, HELPERS + anchor, 1)

    # 片头/片尾：① 保留上游"只能前半场设片头 / 后半场设片尾"的限制，设成功才提示
    #            ② 外包一层容器后点击命中区只剩下面那行小字 → 整块可点

    a1 = ('                    if (current > duration / 2) return;\n'
          '                    mPlayerConfig.put("st",current/1000);')
    b1 = ('                    if (current > duration / 2) return;\n'
          '                    mPlayerConfig.put("st",current/1000);')
    t = t.replace(a1, b1, 1)

    a2 = ('                    if (current < duration / 2) return;\n'
          '                    mPlayerConfig.put("et", (duration - current)/1000);')
    b2 = ('                    if (current < duration / 2) return;\n'
          '                    mPlayerConfig.put("et", (duration - current)/1000);')
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
        # DoH 解析失败自动回退系统 DNS（原来只有 tvbox_optimize.py 在做，重复且会被覆盖）
        old_lk = ('                Dns dns = dnsOverHttps != null ? dnsOverHttps : Dns.SYSTEM;' + chr(10) +
                  '                return  dns.lookup(hostname);')
        new_lk = ('                Dns dns = dnsOverHttps != null ? dnsOverHttps : Dns.SYSTEM;' + chr(10) +
                  '                try {' + chr(10) +
                  '                    return dns.lookup(hostname);' + chr(10) +
                  '                } catch (Throwable e) {' + chr(10) +
                  '                    return Dns.SYSTEM.lookup(hostname);' + chr(10) +
                  '                }')
        if 'Dns.SYSTEM.lookup(hostname)' not in h:
            if old_lk not in h:
                sys.exit('锚点丢失：CustomDns.lookup')
            h = h.replace(old_lk, new_lk, 1)
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

    # (1) 默认 ads 字面量保持上游原样（不再裁剪）
    # 订阅 ads 不再合并（统计类噪声大，只用公网视频广告规则）
    if not OPT_MERGE_SOURCE_ADS:
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

import com.orhanobut.hawk.Hawk;

import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

public class AdBlocker {

    // 广告域名（内置 + 订阅）
    private static final List<String> AD_HOSTS = new ArrayList<>();
    // 网页 URL 关键字
    private static final List<String> URL_KEYWORDS = new ArrayList<>();
    // 网页 URL 正则
    private static final List<Pattern> URL_REGEX = new ArrayList<>();
    // 播放页要摘掉的元素选择器
    private static final List<String> PAGE_SELECTORS = new ArrayList<>();
    // 播放页广告浮层文案关键词（娱乐城/博彩/体彩这类，按文字识别后摘掉）
    private static final List<String> PAGE_TEXT_KW = new ArrayList<>();

    public static void clear() {
        AD_HOSTS.clear();
        URL_KEYWORDS.clear();
        URL_REGEX.clear();
        PAGE_SELECTORS.clear();
        PAGE_TEXT_KW.clear();
    }

    public static boolean isEmpty() {
        return AD_HOSTS.isEmpty();
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

    public static void addPageTextKeyword(String keyword) {
        if (keyword == null) return;
        String k = keyword.trim();
        if (k.length() > 1 && !PAGE_TEXT_KW.contains(k)) PAGE_TEXT_KW.add(k);
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

    // 总开关：设置页「去广告」= 开启时才生效，关闭则完全不过滤
    public static boolean enabled() {
        try {
            return Hawk.get(HawkConfig.M3U8_PURIFY, true);
        } catch (Throwable ignored) {
            return true;
        }
    }

    public static boolean isAd(String url) {
        if (!enabled()) return false;
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
        return false;
    }

    // 播放页（WebView 解析类源）加载完后摘除广告元素
    public static String removeElementScript() {
        if (!enabled()) return "";
        if (PAGE_SELECTORS.isEmpty() && PAGE_TEXT_KW.isEmpty()) return "";
        StringBuilder sb = new StringBuilder();
        sb.append("(function(){try{var list=[");
        for (int i = 0; i < PAGE_SELECTORS.size(); i++) {
            if (i > 0) sb.append(",");
            sb.append('"').append(PAGE_SELECTORS.get(i).replace("\\", "\\\\").replace("\"", "\\\"")).append('"');
        }
        sb.append("];for(var i=0;i<list.length;i++){try{var els=document.querySelectorAll(list[i]);for(var j=0;j<els.length;j++){var el=els[j];if(el&&el.parentNode)el.parentNode.removeChild(el);}}catch(e){}}");
        sb.append("}catch(e){}})();");
        String textScript = buildTextKeywordScript();
        return sb.toString() + textScript;
    }

    // 按文字特征摘浮层：娱乐城/博彩/体彩/百家乐这类广告层，正常影视站不会这样写字
    private static String buildTextKeywordScript() {
        if (PAGE_TEXT_KW.isEmpty()) return "";
        StringBuilder sb = new StringBuilder();
        sb.append("(function(){try{var kw=[");
        for (int i = 0; i < PAGE_TEXT_KW.size(); i++) {
            if (i > 0) sb.append(",");
            sb.append('"').append(PAGE_TEXT_KW.get(i).replace("\\", "\\\\").replace("\"", "\\\"")).append('"');
        }
        sb.append("];var all=document.querySelectorAll('body *');");
        sb.append("for(var i=0;i<all.length;i++){var el=all[i];if(!el||!el.parentNode)continue;");
        sb.append("var t=(el.innerText||el.textContent||'').replace(/\\s+/g,'');if(t.length===0||t.length>40)continue;");
        sb.append("for(var j=0;j<kw.length;j++){if(t.indexOf(kw[j])>=0){var st=null;try{st=window.getComputedStyle(el);}catch(e){}");
        sb.append("var fixed=st&&(st.position==='fixed'||st.position==='absolute');");
        sb.append("var small=el.offsetWidth>0&&el.offsetHeight>0&&el.offsetHeight<400;");
        sb.append("if(fixed||small){if(el.parentNode)el.parentNode.removeChild(el);}break;}}}");
        sb.append("}catch(e){}})();");
        return sb.toString();
    }

    public static WebResourceResponse createEmptyResource() {
        return new WebResourceResponse("text/plain", "utf-8", new ByteArrayInputStream("".getBytes()));
    }

}
"""
    assert 'return AD_HOSTS.isEmpty();' in ab_java, 'AdBlocker.isEmpty 缺 return'
    assert 'public static boolean enabled()' in ab_java, 'AdBlocker.enabled 缺失'
    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/AdBlocker.java'), ab_java)

    log('去广告/DNS：内置精简规则（无远程清单）+ 内置 DoH（不读订阅自定义字段）')



    msf = jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/ModelSettingFragment.java')
    mh = read_text(msf)
    a4 = 'import com.github.tvbox.osc.util.DanmuHelper;'
    assert a4 in mh, '锚点丢失：Fragment import'
    a5 = '        tvm3u8AdText.setText(Hawk.get(HawkConfig.M3U8_PURIFY, true) ? "开启" : "关闭");'
    assert a5 in mh, '锚点丢失：去广告文本初始化'
    # 开关点一下立刻生效：开 → 重新套用内置规则并加载缓存；关 → 全部过滤停用
    a6 = ('                tvm3u8AdText.setText(!is_purify ? "开启" : "关闭");')
    assert a6 in mh, '锚点丢失：去广告开关点击'
    a7 = ('                tvm3u8AdText.setText(!is_purify ? "开启" : "关闭");' + chr(10) +
          '                if (!is_purify) {' + chr(10) +
          '                    com.github.tvbox.osc.util.BuiltinAdRules.apply();' + chr(10) +
          '                }')
    mh = mh.replace(a6, a7, 1)
    write_text(msf, mh)
    log('设置页：去广告开关即时生效（无远程清单、无长按清缓存）')



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
        h2 = h2.replace(a6, a6 + chr(10) + '        if (Hawk.get(HawkConfig.M3U8_PURIFY, true)) BuiltinAdRules.apply();', 1)
        h2 = h2.replace('            VideoParseRuler.clearRule();',
                        '            VideoParseRuler.clearRule();' + chr(10) + '            if (Hawk.get(HawkConfig.M3U8_PURIFY, true)) BuiltinAdRules.apply();', 1)
        # 开关关闭时整套 m3u8 规则（内置 + 订阅）都不加载：真关，不是摆设
        wrap_old = ('        if (infoJson.has("rules")) {' + chr(10) +
                    '            VideoParseRuler.clearRule();' + chr(10) +
                    '            if (Hawk.get(HawkConfig.M3U8_PURIFY, true)) BuiltinAdRules.apply();')
        wrap_new = ('        if (Hawk.get(HawkConfig.M3U8_PURIFY, true)) {' + chr(10) +
                    '            if (infoJson.has("rules")) {' + chr(10) +
                    '            VideoParseRuler.clearRule();')
        assert wrap_old in h2, '锚点丢失：rules 块开头'
        h2 = h2.replace(wrap_old, wrap_new, 1)
        close_old = ('            }' + chr(10) + '        }' + chr(10) + chr(10) + '        // 安全DNS以内置列表为准')
        close_new = ('            }' + chr(10) + '        }' + chr(10) +
                     '            if (!infoJson.has("rules")) VideoParseRuler.clearRule();' + chr(10) +                     '            BuiltinAdRules.apply();' + chr(10) + '        }' + chr(10) + chr(10) +
                     '        // 安全DNS以内置列表为准')
        assert close_old in h2, '锚点丢失：rules 块收尾'
        h2 = h2.replace(close_old, close_new, 1)
        write_text(ac2, h2)

    # 线路菜单里的「推送」保持上游原样，不再改名

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
        log('推送按钮：去掉 %d 处系统版本门槛，任何电视都常显' % (n2 + 1))
    else:
        sys.exit('锚点丢失：投屏按钮的系统版本判定')

    head = ('    public void updateDanmuSearchUiBtn() {' + '\n'
            + '        if (mDanmuSearchUiBtn == null) return;')
    # 播放器/解码切换：replay 后控件标签可能被刷回旧值 → 延迟补刷一次
    for o, n in (
        ('listener.setAllowSwitchPlayer(false);',
         'listener.setAllowSwitchPlayer(false);' + NL + '                    tkRefreshCfgView();'),
        ('                    listener.replay(false);' + NL
         + '                    hideBottom();' + NL
         + '                } catch (JSONException e) {',
         '                    listener.replay(false);' + NL
         + '                    tkRefreshCfgView();' + NL
         + '                    hideBottom();' + NL
         + '                } catch (JSONException e) {'),
    ):
        if o not in t:
            sys.exit('锚点丢失：切换后刷新 ' + o[:40])
        t = t.replace(o, n)

    log('播放器/解码切换后延迟补刷标签')

    # 自适应 UI
    if 'tkAdaptiveUi' in t:
        sys.exit('tkAdaptiveUi 已存在，拒绝重复注入')
    t = t.replace('    private String getPlayerShortName(int playerType) {',
                  TK_ADAPTIVE + '    private String getPlayerShortName(int playerType) {', 1)
    a6 = ('    public void setPlayerConfig(JSONObject playerCfg) {' + NL
          + '        this.mPlayerConfig = playerCfg;' + NL
          + '        updatePlayerCfgView();' + NL
          + '    }')
    if a6 not in t:
        sys.exit('锚点丢失：setPlayerConfig')
    t = t.replace(a6, a6[:-1] + '    tkAdaptiveUi();' + NL + '    }', 1)
    a7 = ('        super.onSizeChanged(w, h, oldw, oldh);' + NL
          + '        initLandscapePortraitBtnInfo();' + NL
          + '    }')
    if a7 not in t:
        sys.exit('锚点丢失：onSizeChanged')
    t = t.replace(a7, a7.replace('        initLandscapePortraitBtnInfo();' + NL,
                                 '        initLandscapePortraitBtnInfo();' + NL + '        tkAdaptiveUi();' + NL), 1)
    log('自适应：按屏宽/电视判定调整时间字号、底栏边距、按钮间距')

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
    emit_adrules()
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

def apply_top_width():
    """上游右上容器只占 1/4 屏宽：网速 + 播放时间 + 系统时间三串字排一行必然挤在一起。
    只调整宽度分配（左 2 : 右 3），显隐逻辑完全不动，保持上游 1002/1003 原样。"""
    ET.register_namespace('android', NS)
    path = jp(LAYOUT)
    tree = ET.parse(path)
    root = tree.getroot()
    l = find_id(root, 'tv_top_l_container')
    r = find_id(root, 'tv_top_r_container')
    sd = find_id(root, 'tv_screen_display')
    if l is None or r is None or sd is None:
        sys.exit('顶部宽度锚点丢失')
    if r.get(A + 'layout_weight') == '3':
        log('  = 顶部右栏宽度已是 3，跳过')
        return
    l.set(A + 'layout_weight', '2')
    r.set(A + 'layout_weight', '3')
    # 让时间行占满右栏再靠右对齐，否则 wrap_content 超宽时从左边溢出盖住片名
    sd.set(A + 'layout_width', 'match_parent')
    tree.write(path, encoding='utf-8', xml_declaration=True)
    log('顶部：右栏宽度 1 -> 3（网速与时间不再叠字），左栏 3 -> 2')


def apply_fast_start():
    """净化开着时不再傻等 m3u8 清单：3.5 秒没抓完就直接起播，晚到的净化结果放弃。"""
    log('起播放行：完全回上游（不插入任何字段/方法）')
    return
    p = jp(SRC, VOD)
    src = read_text(p)
    if 'tkTakeOver' in src:
        log('起播放行：补丁已存在，跳过')
        return
    L = chr(10)

    a = '    private JSONObject mPlayerConfig = null;'
    if a not in src:
        sys.exit('起播放行锚点丢失: mPlayerConfig 字段')
    src = src.replace(a, a + L + '    private boolean tkPlayed = false;', 1)

    a = '    public void playM3u8(final String url, final HashMap<String, String> headers) {'
    if a not in src:
        sys.exit('起播放行锚点丢失: playM3u8 方法头')
    helper = (
        '    /** 起播只允许一次：谁先抢到谁播，后到的净化结果直接放弃，避免二次起播 */' + L
        + '    private boolean tkTakeOver() {' + L
        + '        if (tkPlayed) return false;' + L
        + '        tkPlayed = true;' + L
        + '        return true;' + L
        + '    }' + L + L + a)
    src = src.replace(a, helper, 1)

    # 开关关掉时：字段和 tkTakeOver 方法留在树里当锚点（纯新增、无人调用、无副作用），
    # 但下面所有"替换上游行为"的动作全部不做 —— 起播流程一字不动回到上游。
    if not FEAT_FAST_START:
        write_text(p, src)
        log('起播抢占：已关闭（只留空方法作锚点，起播回到上游原逻辑）')
        return

    a = ('        if(url.contains("url=")){' + L
         + '            listener.startPlayUrl(url, headers);' + L
         + '            return;' + L
         + '        }')
    if a not in src:
        sys.exit('起播放行锚点丢失: url= 分支')
    b = ('        if(url.contains("url=")){' + L
         + '            if (tkTakeOver()) listener.startPlayUrl(url, headers);' + L
         + '            return;' + L
         + '        }')
    src = src.replace(a, b, 1)

    a = '        OkGo.getInstance().cancelTag("m3u8-2");'
    if src.count(a) != 1:
        sys.exit('起播放行锚点丢失: cancelTag m3u8-2 不唯一')
    timer = (a + L
        + '        tkPlayed = false;' + L
        + '        try {' + L
        + '            final android.os.Handler tkHandler = new android.os.Handler(android.os.Looper.getMainLooper());' + L
        + '            tkHandler.postDelayed(new Runnable() {' + L
        + '                @Override' + L
        + '                public void run() {' + L
        + '                    if (!tkTakeOver()) return;' + L
        + '                    LOG.i("echo-m3u8起播超时放行: " + url);' + L
        + '                    try { OkGo.getInstance().cancelTag("m3u8-1"); } catch (Throwable ignored) {}' + L
        + '                    try { OkGo.getInstance().cancelTag("m3u8-2"); } catch (Throwable ignored) {}' + L
        + '                    listener.startPlayUrl(url, headers);' + L
        + '                }' + L
        + '            }, 3500);' + L
        + '        } catch (Throwable ignored) {}')
    src = src.replace(a, timer, 1)

    a = ('                        String content = response.body();' + L
         + '                        if (!content.startsWith("#EXTM3U")) {' + L
         + '                            listener.startPlayUrl(url, headers);' + L
         + '                            return;' + L
         + '                        }')
    if a not in src:
        sys.exit('起播放行锚点丢失: onSuccess 非 m3u8 分支')
    b = ('                        String content = response.body();' + L
         + '                        if (!content.startsWith("#EXTM3U")) {' + L
         + '                            if (tkTakeOver()) listener.startPlayUrl(url, headers);' + L
         + '                            return;' + L
         + '                        }')
    src = src.replace(a, b, 1)

    a = ('                        LOG.e("echo-m3u8请求错误1: " + response.getException());' + L
         + '                        listener.startPlayUrl(url, headers);')
    if a not in src:
        sys.exit('起播放行锚点丢失: onError m3u8-1')
    b = ('                        LOG.e("echo-m3u8请求错误1: " + response.getException());' + L
         + '                        if (!tkTakeOver()) return;' + L
         + '                        listener.startPlayUrl(url, headers);')
    src = src.replace(a, b, 1)

    a = ('    private void processM3u8Content(String url, String content, HashMap<String, String> headers) {' + L
         + '        String basePath = getBasePath(url);')
    if src.count('        String basePath = getBasePath(url);') != 1:
        sys.exit('起播放行锚点丢失: processM3u8Content 不唯一')
    b = ('    private void processM3u8Content(String url, String content, HashMap<String, String> headers) {' + L
         + '        if (!tkTakeOver()) { LOG.i("echo-m3u8净化结果晚到，已直接起播，放弃代理"); return; }' + L
         + '        String basePath = getBasePath(url);')
    src = src.replace(a, b, 1)

    a = ('                        LOG.e("echo-重定向 m3u8 请求错误: " + response.getException());' + L
         + '                        listener.startPlayUrl(fallbackUrl, headers);')
    if a not in src:
        sys.exit('起播放行锚点丢失: 重定向 onError')
    b = ('                        LOG.e("echo-重定向 m3u8 请求错误: " + response.getException());' + L
         + '                        if (!tkTakeOver()) return;' + L
         + '                        listener.startPlayUrl(fallbackUrl, headers);')
    src = src.replace(a, b, 1)

    write_text(p, src)
    txt = read_text(p)
    if txt.count('tkTakeOver') != 7:
        sys.exit('起播放行自检失败: tkTakeOver 出现 %d 次（应为 7）' % txt.count('tkTakeOver'))
    if 'private boolean tkPlayed = false;' not in txt:
        sys.exit('起播放行自检失败: 字段没写进去')
    log('起播放行：净化仍在，但 3.5 秒没抓完就直接播（不再等 20 秒）')


def apply_download():
    """底栏加「下载」按钮：点一下弹出选集框，可多选，串行排队下载（m3u8 拼 ts / mp4 走系统下载器）。"""
    L = chr(10)
    ET.register_namespace('android', NS)
    path = jp(LAYOUT)
    tree = ET.parse(path)
    root = tree.getroot()
    # 底栏不再放「下载」按钮：下载入口统一走详情页（U47 定稿）
    dl_old = find_id(root, 'play_download')
    if dl_old is not None:
        parents(root)[dl_old].remove(dl_old)
        tree.write(path, encoding='utf-8', xml_declaration=True)
        log('底栏下载按钮：已移除（下载入口只留详情页）')
    else:
        log('底栏不放下载按钮（入口在详情页）')

    # 下载保活：分片流一息屏就断，必须 WAKE_LOCK 才能扛住整集几十 MB
    mf = jp('app/src/main/AndroidManifest.xml')
    m = read_text(mf)
    if 'android.permission.WAKE_LOCK' not in m:
        fst = 'android:name="android.permission.FOREGROUND_SERVICE"'
        if fst not in m:
            sys.exit('manifest 锚点丢失：FOREGROUND_SERVICE')
        m = re.sub(r'(<uses-permission[^>]*' + re.escape(fst) + r'[^>]*/>)',
                   r'\1' + L + '    <uses-permission android:name="android.permission.WAKE_LOCK" />',
                   m, count=1)
        if 'android.permission.WAKE_LOCK' not in m:
            sys.exit('WAKE_LOCK 权限没写进 manifest')
        write_text(mf, m)

    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/TkDownloader.java'), TK_DL_JAVA)

    pf = jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java')
    txt = read_text(pf)
    if 'TkDownloader.lastUrl' not in txt:
        a = '        final String finalUrl = url;'
        if a not in txt:
            sys.exit('下载锚点丢失：PlayFragment 的 finalUrl')
        b = (a + L
             + '        try {' + L
             + '            com.github.tvbox.osc.util.TkDownloader.lastUrl = finalUrl;' + L
             + '            String tkName = mVodInfo == null ? "" : mVodInfo.name;' + L
             + '            VodInfo.VodSeries tkSeries = mVodInfo == null ? null : getCurrentSeries(mVodInfo.playFlag, mVodInfo.playIndex);' + L
             + '            com.github.tvbox.osc.util.TkDownloader.lastTitle = tkSeries == null ? tkName : (tkName + "_" + tkSeries.name);' + L
             + '        } catch (Throwable ignored) {}')
        txt = txt.replace(a, b, 1)
    if 'mController.tkHost = this;' not in txt:
        a = '        mController = new VodController(requireContext());'
        if a not in txt:
            sys.exit('下载锚点丢失：mController 创建')
        txt = txt.replace(a, a + L + '        mController.tkHost = this;', 1)
    if 'tkShowDownloadDialog()' not in txt:
        a = '    public void playNext(boolean isProgress) {'
        if a not in txt:
            sys.exit('下载锚点丢失：PlayFragment playNext')
        txt = txt.replace(a, TK_DL_DIALOG.strip(L) + L + a, 1)
    write_text(pf, txt)

    vc_path = jp(VOD)
    vc = read_text(vc_path)
    # 底栏没有下载按钮了，只需要留着 tkHost 这个挂点（PlayFragment 会赋值）
    if 'public Object tkHost' not in vc:
        a = '    TextView mCastBtn;'
        if a not in vc:
            sys.exit('下载锚点丢失：mCastBtn 字段')
        vc = vc.replace(a, a + L + '    public Object tkHost = null;', 1)
    # 老版本残留的下载按钮字段/绑定/点击块，一并清掉（否则 R.id.play_download 不存在）
    k = vc.find('        if (mTkDownloadBtn != null) {')
    if k >= 0:
        e = vc.find(L + '        }' + L, k)
        if e > k:
            vc = vc[:k] + vc[e + len(L + '        }' + L):]
    for dead in ('        mTkDownloadBtn = findViewById(R.id.play_download);' + L,
                 '    TextView mTkDownloadBtn;' + L):
        vc = vc.replace(dead, '', 1)
    write_text(vc_path, vc)

    if find_id(ET.parse(jp(LAYOUT)).getroot(), 'play_download') is not None:
        sys.exit('底栏下载按钮没删干净')
    dl = read_text(jp('app/src/main/java/com/github/tvbox/osc/util/TkDownloader.java'))
    for key in ('public static void enqueue', 'loopWorker', 'downloadM3u8', 'downloadMp4', 'AES/CBC',
                'getBytesRetry', 'wlOn', 'wlOff'):
        if key not in dl:
            sys.exit('TkDownloader 生成异常：缺 ' + key)
    pfx = read_text(pf)
    for key in ('TkDownloader.lastUrl', 'mController.tkHost = this;', 'tkShowDownloadDialog()'):
        if key not in pfx:
            sys.exit('PlayFragment 缺 ' + key)
    vcx = read_text(vc_path)
    for key in ('tkHost',):
        if key not in vcx:
            sys.exit('VodController 缺 ' + key)
    log('下载：点按钮弹选集框（可多选）→ 串行排队；m3u8 拼 ts / mp4 走系统下载器，存 Movies/tvbox，退出即停')


def apply_search_boost():
    """搜索结果偏少：源清单不自动增补、每批只 6 个源、单源 15s 超时、searchable=0 的源被排除、带书名号就搜不到。"""
    L = chr(10)
    Q = '"'

    # ① 源池别变窄：searchable=0 的源也照样排队（这类源进源里能看，全局也该能搜）
    p = jp('app/src/main/java/com/github/tvbox/osc/util/SearchHelper.java')
    s = read_text(p)
    a2 = ('            if (!bean.isSearchable()) {' + L +
          '                continue;' + L +
          '            }')
    if 'tk不限 searchable' not in s:
        if a2 in s:
            s = s.replace(a2, '            // tk不限 searchable：不支持搜索的源也排一遍，失败按普通超时处理', 1)
        write_text(p, s)

    # ③ 并发与超时：每批 6 个 -> 10 个；批次推进 3s/2s -> 1s；单源 15s -> 18s
    for rel, pump in (('app/src/main/java/com/github/tvbox/osc/ui/activity/FastSearchActivity.java', True),
                      ('app/src/main/java/com/github/tvbox/osc/ui/activity/SearchActivity.java', False)):
        t = read_text(jp(rel))
        t = t.replace('private static final int SEARCH_THREAD_COUNT = 6;',
                      'private static final int SEARCH_THREAD_COUNT = 10;', 1)
        t = t.replace('private static final int SEARCH_NEXT_BATCH_SECONDS = 3;',
                      'private static final int SEARCH_NEXT_BATCH_SECONDS = 1;', 1)
        t = t.replace('private static final int SEARCH_SITE_TIMEOUT_SECONDS = 15;',
                      'private static final int SEARCH_SITE_TIMEOUT_SECONDS = 18;', 1)
        if pump:
            t = t.replace('private static final int SEARCH_PUMP_SECONDS = 2;',
                          'private static final int SEARCH_PUMP_SECONDS = 1;', 1)
        write_text(jp(rel), t)

    # ④ 关键词归一：《》 引号 空格 先去掉，不然源那边对不上
    clean = ('        if (title != null) {' + L +
             '            // tk关键词归一：去掉书名号和引号，源那边才匹配得上' + L +
             '            title = title.replace("《", "").replace("》", "")' + L +
             '                    .replace("“", "").replace("”", "").replace(String.valueOf((char) 34), "")' + L +
             '                    .trim();' + L +
             '        }')
    pf = jp('app/src/main/java/com/github/tvbox/osc/ui/activity/FastSearchActivity.java')
    t = read_text(pf)
    if 'tk关键词归一' not in t:
        a3 = '        this.searchTitle = title;'
        if a3 not in t:
            sys.exit('搜索增强锚点丢失：FastSearchActivity 的 searchTitle')
        t = t.replace(a3, clean + L + '        this.searchTitle = title;', 1)
        write_text(pf, t)
    ps = jp('app/src/main/java/com/github/tvbox/osc/ui/activity/SearchActivity.java')
    t = read_text(ps)
    if 'tk关键词归一' not in t:
        a4 = '        etSearch.setText(title);'
        if a4 not in t:
            sys.exit('搜索增强锚点丢失：SearchActivity 的 etSearch')
        t = t.replace(a4, clean + L + '        etSearch.setText(title);', 1)
        write_text(ps, t)

    # ⑤ 校验
    h = read_text(jp('app/src/main/java/com/github/tvbox/osc/util/SearchHelper.java'))
    if 'tk不限 searchable' not in h:
        sys.exit('搜索增强没写进 SearchHelper')
    for rel in ('app/src/main/java/com/github/tvbox/osc/ui/activity/FastSearchActivity.java',
                'app/src/main/java/com/github/tvbox/osc/ui/activity/SearchActivity.java'):
        t = read_text(jp(rel))
        for key in ('SEARCH_THREAD_COUNT = 10;', 'SEARCH_NEXT_BATCH_SECONDS = 1;',
                    'SEARCH_SITE_TIMEOUT_SECONDS = 18;', 'tk关键词归一'):
            if key not in t:
                sys.exit('搜索增强缺 ' + key + ' @ ' + rel)
    log('搜索：源池不缩（不限 searchable）+ 每批 10 个源 + 1s 推进 + 单源 18s + 关键词去书名号；勾选不自动补源')


def apply_btn_whitelist():
    """底栏只允许我方按钮存在：运行时被塞进来的（如 Zx推送）第一时间删掉，不再"先显示后消失"。"""
    L = chr(10)
    ok = ['play_label', 'play_pre', 'play_next', 'play_retry', 'play_refresh', 'play_scale',
          'play_speed', 'play_player', 'play_ijk', 'play_time_start_end_text', 'play_time_reset',
          'play_cast', 'play_download', 'zimu_select', 'audio_track_select', 'video_track_select',
          'danmu_setting', 'landscape_portrait', 'screen_display']
    arr = ', '.join('"%s"' % k for k in ok)
    method = L.join([
        '    private static final String[] TK_BTN_OK = {%s};' % arr,
        '',
        '    // 白名单：底栏只留我方按钮；运行时被塞进来的（含 Zx推送 这类）当场删掉',
        '    private void tkPurgeButtons() {',
        '        try {',
        '            android.view.ViewGroup g = findViewById(R.id.play_btn_group);',
        '            if (g == null) return;',
        '            for (int i = g.getChildCount() - 1; i >= 0; i--) {',
        '                android.view.View c = g.getChildAt(i);',
        '                String idn = "";',
        '                try {',
        '                    if (c.getId() != android.view.View.NO_ID) {',
        '                        idn = getResources().getResourceEntryName(c.getId());',
        '                    }',
        '                } catch (Throwable ignored) {',
        '                }',
        '                if (idn.length() > 0) {',
        '                    boolean keep = false;',
        '                    for (String w : TK_BTN_OK) {',
        '                        if (w.equals(idn)) { keep = true; break; }',
        '                    }',
        '                    if (!keep) g.removeView(c);',
        '                    continue;',
        '                }',
        '                g.removeView(c);',
        '            }',
        '        } catch (Throwable ignored) {',
        '        }',
        '    }',
        '    // 延迟再清三次：源常在进页面几百毫秒后才把按钮塞进来',
        '    private void tkPurgeLater() {',
        '        try {',
        '            new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() {',
        '                public void run() { tkPurgeButtons(); tkPurgeTextAll(); }',
        '            }, 600);',
        '            new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() {',
        '                public void run() { tkPurgeButtons(); tkPurgeTextAll(); }',
        '            }, 2000);',
        '            new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() {',
        '                public void run() { tkPurgeButtons(); tkPurgeTextAll(); }',
        '            }, 5000);',
        '        } catch (Throwable ignored) {',
        '        }',
        '    }',
        '    // 纯文字、无图标的“推送”类按钮 = 外来注入；我方推送带 v_cast 图标，不会被误删',
        '    private void tkPurgeTextAll() {',
        '        try {',
        '            android.view.ViewGroup root = findViewById(R.id.bottom_container);',
        '            if (root != null) tkPurgeText(root);',
        '        } catch (Throwable ignored) {',
        '        }',
        '    }',
        '    private void tkPurgeText(android.view.View v) {',
        '        if (!(v instanceof android.view.ViewGroup)) return;',
        '        android.view.ViewGroup g = (android.view.ViewGroup) v;',
        '        for (int i = g.getChildCount() - 1; i >= 0; i--) {',
        '            android.view.View c = g.getChildAt(i);',
        '            if (c instanceof android.widget.TextView) {',
        '                android.widget.TextView tv = (android.widget.TextView) c;',
        '                CharSequence cs = tv.getText();',
        '                String s = cs == null ? "" : cs.toString();',
        '                if (s.contains("推送") || s.indexOf("x推送") >= 0 || s.indexOf("X推送") >= 0) {',
        '                    android.graphics.drawable.Drawable[] ds = tv.getCompoundDrawables();',
        '                    boolean hasIcon = false;',
        '                    for (android.graphics.drawable.Drawable d : ds) { if (d != null) { hasIcon = true; break; } }',
        '                    if (!hasIcon) { g.removeView(c); continue; }',
        '                }',
        '            }',
        '            tkPurgeText(c);',
        '        }',
        '    }'])
    vp = jp(VOD)
    vc = read_text(vp)
    a = '    private JSONObject mPlayerConfig = null;'
    if vc.count(a) != 1:
        sys.exit('白名单锚点丢失：mPlayerConfig')
    TK_HEAL = '''
    // 片头/片尾 两枚汉字：按「重置」的真实底边做像素级对齐。
    // 静态布局已与普通按钮同构（pad4 + 23dp 占位 + 同一行字），这里用测量结果兜一次，
    // 不依赖任何 dp 推算，父容器怎么居中都不会差。
    private void tkAlignSlotText() {
        tkAlignSlotTextPass(0);
    }

    // 片头/片尾 四枚汉字：底边焊到「重置」那条线上，只动汉字，00:00 不动、间隙不管。
    // 片头/片尾外面多一层容器（为了把 00:00 叠在图标位），容器没有文字基线，按钮行却按基线排，
    // 两套规则必然差一截 —— 静态调 padding 只能补一半，所以这里直接量屏幕真实坐标，差多少平移多少。
    // 平移后立刻复核，最多 4 拍，差值为 0 就停：不是轮询，是追布局抖动的自终止校正。
    private void tkAlignSlotTextPass(final int pass) {
        try {
            View base = findViewById(R.id.play_time_reset);
            if (base == null || base.getHeight() <= 0) {
                base = findViewById(R.id.play_retry);
            }
            View start = findViewById(R.id.play_time_start);
            View end = findViewById(R.id.play_time_end);
            if (base == null || base.getHeight() <= 0) return;
            int[] bl = new int[2];
            base.getLocationOnScreen(bl);
            int bBottom = bl[1] + base.getHeight();
            boolean dirty = false;
            for (View v : new View[]{start, end}) {
                if (v == null || v.getHeight() <= 0) continue;
                v.setTranslationY(0f);
                int[] vl = new int[2];
                v.getLocationOnScreen(vl);
                int d = bBottom - (vl[1] + v.getHeight());
                if (d != 0) {
                    v.setTranslationY(d);
                    dirty = true;
                }
            }
            if (dirty && pass < 3) {
                postDelayed(new Runnable() {
                    public void run() {
                        tkAlignSlotTextPass(pass + 1);
                    }
                }, 60);
            }
        } catch (Throwable ignored) {
        }
    }

    // 底栏按钮行的横滑位置：控制栏每次显隐都会让内容宽度变化，
    // HorizontalScrollView 会把 scrollX 夹回去，看着就像按钮自己左右挪了一下。
    private boolean tkAlignWatched = false;

    // 布局一变（旋屏、按场景显隐、控制栏展开收起）就补一次对齐，
    // 保证片头/片尾那四个字永远和普通按钮同一条线，不靠事件猜时机。
    private void tkAlignWatch() {
        try {
            if (tkAlignWatched) return;
            View b = findViewById(R.id.bottom_container);
            if (b == null) return;
            tkAlignWatched = true;
            b.addOnLayoutChangeListener(new View.OnLayoutChangeListener() {
                @Override
                public void onLayoutChange(View v, int l, int t, int r, int bo,
                                           int ol, int ot, int or, int ob) {
                    v.post(new Runnable() {
                        public void run() {
                            tkAlignSlotText();
                        }
                    });
                }
            });
        } catch (Throwable ignored) {
        }
    }

    private int tkScrollX = 0;
    private void tkKeepScroll() {
        try {
            View g = findViewById(R.id.play_btn_group);
            if (g == null || g.getParent() == null) return;
            if (!(g.getParent() instanceof android.widget.HorizontalScrollView)) return;
            final android.widget.HorizontalScrollView h = (android.widget.HorizontalScrollView) g.getParent();
            final int target = tkScrollX;
            // 等这一帧布局完成（显隐刚改完宽高还是旧的），再把横滑位置按回去
            h.post(new Runnable() {
                public void run() {
                    try {
                        if (h.getChildCount() == 0) return;
                        int max = Math.max(0, h.getChildAt(0).getWidth() - h.getWidth());
                        h.scrollTo(Math.min(target, max), 0);
                        tkScrollX = h.getScrollX();
                        tkAlignSlotText();
                    } catch (Throwable ignored) {
                    }
                }
            });
        } catch (Throwable ignored) {
        }
    }

    // 底栏自愈：只在「展开控制栏」这一个时机清一次，不挂常驻轮询。
    // 原先 900ms 一轮是防第三方往按钮行塞东西/把透明度清零，
    // 但这类事只会发生在控制栏展示期间，展开时清一遍就够，没必要一直盯着。
    private void tkSelfHeal() {
        try {
            if (!isAttachedToWindow()) return;
            android.view.ViewGroup b = findViewById(R.id.bottom_container);
            android.view.ViewGroup g = findViewById(R.id.play_btn_group);
            if (b == null || g == null) return;
            if (b.getVisibility() != android.view.View.VISIBLE) return;
            if (g.getVisibility() != android.view.View.VISIBLE) g.setVisibility(android.view.View.VISIBLE);
            if (g.getAlpha() < 0.99f) g.setAlpha(1.0f);
            // 只恢复透明度，绝不改子项可见性：竖屏/按场景本来该隐藏的按钮（片头尾/投屏/字幕…）
            // 一旦被拉出来，按钮行宽度就会跳变，HorizontalScrollView 跟着重排，
            // 实机表现就是"点屏幕中间，图标左右闪一下"。
            for (int i = 0; i < g.getChildCount(); i++) {
                android.view.View c = g.getChildAt(i);
                if (c.getVisibility() == android.view.View.VISIBLE && c.getAlpha() <= 0.05f) {
                    c.setAlpha(1.0f);
                }
            }
            tkKeepScroll();
        } catch (Throwable ignored) {
        }
    }

    private void tkStopHeal() {
    }
'''
    if 'TK_BTN_OK' not in vc:
        vc = vc.replace(a, a + L + method + L + TK_HEAL, 1)
    # 底栏每次弹出都清一遍（源会在显示时把 zx推送 这类塞进按钮行）
    sb = ('    void showBottom() {' + L
          + '        mHandler.removeMessages(1003);' + L
          + '        mHandler.sendEmptyMessage(1002);' + L
          + '        mNextBtn.requestFocus();' + L
          + '    }')
    sb2 = ('    void showBottom() {' + L
           + '        mHandler.removeMessages(1003);' + L
           + '        mHandler.sendEmptyMessage(1002);' + L
           + '        mNextBtn.requestFocus();' + L
           + '        tkPurgeButtons();' + L
           + '        tkPurgeTextAll();' + L
           + '        tkPurgeLater();' + L
           + '        tkKeepScroll();' + L
           + '        tkAlignSlotText();' + L
           + '        tkSelfHeal();' + L
           + '    }')
    if sb2 not in vc:
        if sb not in vc:
            sys.exit('白名单锚点丢失：showBottom')
        vc = vc.replace(sb, sb2, 1)

    old = ('    private void tkAdaptiveUi() {' + L +
           '        // tk：尺寸已全部静态化到 dimen（按屏宽/方向自动生效），不再运行时重排' + L +
           '    }')
    new = L.join(['    private void tkAdaptiveUi() {',
                  '        // tk：尺寸已全部静态化到 dimen（按屏宽/方向自动生效），不再运行时重排',
                  '        tkPurgeButtons();',
                  '        tkSelfHeal();',
                  '        tkKeepScroll();',
                  '        tkAlignWatch();',
                  '    }'])
    if old in vc:
        vc = vc.replace(old, new, 1)
    elif 'tkPurgeButtons();' not in vc:
        sys.exit('tkAdaptiveUi 锚点丢失')
    # 自愈链的生命周期：View 一脱离窗口就移除回调，绝不在后台留一条 900ms 的循环
    od = '        mHandler.removeCallbacks(myRunnable2);'
    if 'tkStopHeal();' not in vc:
        if od not in vc:
            sys.exit('自愈清理锚点丢失：onDetachedFromWindow')
        vc = vc.replace(od, od + L + '        tkStopHeal();', 1)
    write_text(vp, vc)
    vcx = read_text(vp)
    if 'tkAlignSlotTextPass' not in vcx or 'tkKeepScroll' not in vcx:
        sys.exit('片头尾像素对齐 / 横滑保持 没写入')
    if 'TK_BTN_OK' not in vcx or 'tkPurgeButtons();' not in vcx or 'tkSelfHeal();' not in vcx:
        sys.exit('白名单没写入')
    log('底栏白名单：只保留 %d 个我方按钮，运行时塞进来的（Zx推送等）当场删除' % len(ok))


def apply_btn_guard():
    """底栏任何层级被塞入非法节点 → 当场移除（层级监听，赶在绘制前），彻底杜绝 Zx推送 之类闪现。"""
    L = chr(10)
    ids = ['bottom_container', 'curr_time', 'seekBar', 'total_time', 'play_btn_group', 'play_label',
           'play_pre', 'play_next', 'play_retry', 'play_refresh', 'play_scale', 'play_speed', 'play_player',
           'play_ijk', 'play_time_start_end_text', 'play_time_start',
           'play_time_end', 'play_time_reset', 'play_cast', 'play_download', 'zimu_select',
           'audio_track_select', 'video_track_select', 'danmu_setting', 'danmu_search_ui',
           'landscape_portrait', 'screen_display', 'parse_root', 'mGridParseView']
    arr = ', '.join('"%s"' % k for k in ids)
    body = []
    A_ = body.append
    A_('    private static final String[] TK_BOTTOM_OK = {%s};' % arr)
    A_('')
    A_('    private boolean tkBottomAllowed(android.view.View v) {')
    A_('        try {')
    A_('            if (v.getId() != android.view.View.NO_ID) {')
    A_('                String n = getResources().getResourceEntryName(v.getId());')
    A_('                for (String w : TK_BOTTOM_OK) { if (w.equals(n)) return true; }')
    A_('                return false;')
    A_('            }')
    A_('            if (v instanceof android.view.ViewGroup) {')
    A_('                android.view.ViewGroup vg = (android.view.ViewGroup) v;')
    A_('                for (int i = 0; i < vg.getChildCount(); i++) {')
    A_('                    if (tkBottomAllowed(vg.getChildAt(i))) return true;')
    A_('                }')
    A_('            }')
    A_('        } catch (Throwable ignored) {')
    A_('        }')
    A_('        return false;')
    A_('    }')
    A_('')
    A_('    // 底栏层级监听：任何被塞进来的非法节点，在添加瞬间就移除（不等到下一帧，所以看不到闪）')
    A_('    private void tkWatchBottom() {')
    A_('        try {')
    A_('            android.view.ViewGroup root = findViewById(R.id.bottom_container);')
    A_('            if (root == null) return;')
    A_('            tkInstallWatch(root);')
    A_('            tkPurgeButtons();')
    A_('            if (myHandle != null) {')
    A_('                myHandle.postDelayed(new Runnable() {')
    A_('                    @Override public void run() { tkPurgeButtons(); }')
    A_('                }, 300);')
    A_('            }')
    A_('        } catch (Throwable ignored) {')
    A_('        }')
    A_('    }')
    A_('')
    A_('    private boolean tkIsParse(android.view.View v) {')
    A_('        try { return v.getId() == R.id.parse_root; } catch (Throwable t) { return false; }')
    A_('    }')
    A_('')
    A_('    private void tkInstallWatch(android.view.ViewGroup g) {')
    A_('        if (g == null || tkIsParse(g)) return;')
    A_('        g.setOnHierarchyChangeListener(new android.view.ViewGroup.OnHierarchyChangeListener() {')
    A_('            @Override public void onChildViewAdded(android.view.View parent, final android.view.View child) {')
    A_('                if (tkBottomAllowed(child)) {')
    A_('                    if (child instanceof android.view.ViewGroup && !tkIsParse(child)) tkInstallWatch((android.view.ViewGroup) child);')
    A_('                    return;')
    A_('                }')
    A_('                final android.view.ViewGroup pg = (android.view.ViewGroup) parent;')
    A_('                try { pg.removeView(child); } catch (Throwable ignored) { }')
    A_('                try {')
    A_('                    child.post(new Runnable() {')
    A_('                        @Override public void run() {')
    A_('                            try { pg.removeView(child); } catch (Throwable ignored) { }')
    A_('                        }')
    A_('                    });')
    A_('                } catch (Throwable ignored) { }')
    A_('            }')
    A_('            @Override public void onChildViewRemoved(android.view.View parent, android.view.View child) { }')
    A_('        });')
    A_('        for (int i = 0; i < g.getChildCount(); i++) {')
    A_('            android.view.View c = g.getChildAt(i);')
    A_('            if (c instanceof android.view.ViewGroup && !tkIsParse(c)) tkInstallWatch((android.view.ViewGroup) c);')
    A_('        }')
    A_('    }')
    A_('')
    A_('    // 整棵底栏扫一遍：id 不在白名单 / 文字是搜弹幕·视轨·推送·Zx 的，一律删')
    A_('    private void tkPurgeButtons() {')
    A_('        try {')
    A_('            android.view.ViewGroup root = findViewById(R.id.bottom_container);')
    A_('            if (root == null) return;')
    A_('            tkPurgeDeep(root);')
    A_('        } catch (Throwable ignored) { }')
    A_('    }')
    A_('')
    A_('    private void tkPurgeDeep(android.view.ViewGroup g) {')
    A_('        if (g == null || tkIsParse(g)) return;')
    A_('        for (int i = g.getChildCount() - 1; i >= 0; i--) {')
    A_('            android.view.View c = g.getChildAt(i);')
    A_('            boolean drop = false;')
    A_('            try {')
    A_('                // 只按 id 白名单判断：布局里本来就有的一律保留（含已隐藏的视轨/搜弹幕），')
    A_('                // 外来塞进来的（无论带不带 id、文字是什么）一律删除')
    A_('                drop = !tkBottomAllowed(c);')
    A_('            } catch (Throwable ignored) { }')
    A_('            if (drop) {')
    A_('                try { g.removeView(c); } catch (Throwable ignored) { }')
    A_('                continue;')
    A_('            }')
    A_('            if (c instanceof android.view.ViewGroup && !tkIsParse(c)) tkPurgeDeep((android.view.ViewGroup) c);')
    A_('        }')
    A_('    }')
    method = L.join(body)

    vp = jp(VOD)
    vc = read_text(vp)

    # 清掉上一版的白名单常量与方法，换成这一套
    import re as _re
    vc = _re.sub(r'    private static final String\[\] TK_BTN_OK = \{[^}]*\};\n\n', '', vc, count=1)
    a = '    private int tkUiKey = 0;'
    if a not in vc:
        sys.exit('守卫锚点丢失：tkUiKey')
    # 删旧 tkPurgeButtons
    k = vc.find('    private void tkPurgeButtons() {')
    if k > 0:
        j = vc.index('{', k)
        dep = 0
        e = j
        while e < len(vc):
            if vc[e] == '{':
                dep += 1
            elif vc[e] == '}':
                dep -= 1
                if dep == 0:
                    break
            e += 1
        vc = vc[:k] + vc[e + 2:]
    vc = vc.replace(a, a + L + method, 1)

    # initView 里挂上监听
    anchor = '        mBottomRoot = findViewById(R.id.bottom_container);'
    if anchor not in vc:
        sys.exit('initView 锚点丢失：mBottomRoot')
    if 'tkWatchBottom();' not in vc:
        vc = vc.replace(anchor, anchor + L + '        tkWatchBottom();', 1)

    write_text(vp, vc)
    vcx = read_text(vp)
    for must in ('TK_BOTTOM_OK', 'tkWatchBottom();', 'tkInstallWatch', 'tkPurgeDeep'):
        if must not in vcx:
            sys.exit('守卫没写入：' + must)
    if 'TK_BTN_OK' in vcx:
        sys.exit('旧白名单没清掉')
    log('底栏守卫：层级监听已挂上（任何非法节点在添加瞬间被移除），并在 initView 先扫一遍')


def apply_pause_keep():
    """暂停状态不再被闲置计时器打掉面板；唤出底栏时先清掉待执行的隐藏消息，外层同步可见。
    只碰显隐时序，不碰播放内核、不动任何按钮。"""
    L = chr(10)
    vp = jp(VOD)
    vc = read_text(vp)
    if 'tkPauseKeep' in vc:
        log('  = 暂停保活已存在，跳过')
        return

    old1 = ('        myRunnable = new Runnable() {' + L +
            '            @Override' + L +
            '            public void run() {' + L +
            '                hideBottom();' + L +
            '            }' + L +
            '        };')
    new1 = ('        // tkPauseKeep：暂停时闲置计时器不收起底栏' + L +
            '        myRunnable = new Runnable() {' + L +
            '            @Override' + L +
            '            public void run() {' + L +
            '                if (videoPlayState == VideoView.STATE_PAUSED) return;' + L +
            '                hideBottom();' + L +
            '            }' + L +
            '        };')
    if vc.count(old1) != 1:
        sys.exit('暂停保活锚点丢失：myRunnable 闲置隐藏')
    vc = vc.replace(old1, new1, 1)

    # 1002 的暂停面板保持上游原样（hidePauseRoot 无条件）

    old3 = ('    void showBottom() {' + L +
            '        mHandler.removeMessages(1003);' + L +
            '        mHandler.sendEmptyMessage(1002);')
    new3 = ('    void showBottom() {' + L +
            '        mHandler.removeMessages(1003);' + L +
            '        setVisibility(VISIBLE); // tkPauseKeep：外层一并可见，避免"点了没反应"' + L +
            '        mBottomRoot.setVisibility(VISIBLE); // tkPauseKeep：底栏直接置可见，不等消息排队' + L +
            '        mHandler.sendEmptyMessage(1002);')
    if vc.count(old3) != 1:
        sys.exit('暂停保活锚点丢失：showBottom')
    vc = vc.replace(old3, new3, 1)

    old4 = ('    public boolean onSingleTapConfirmed(MotionEvent e) {' + L +
            '        myHandle.removeCallbacks(myRunnable);')
    new4 = ('    public boolean onSingleTapConfirmed(MotionEvent e) {' + L +
            '        myHandle.removeCallbacks(myRunnable);' + L +
            '        mHandler.removeMessages(1003); // tkPauseKeep：清掉遗留的隐藏消息')
    if vc.count(old4) != 1:
        sys.exit('暂停保活锚点丢失：单击')
    vc = vc.replace(old4, new4, 1)

    bc = jp('app/src/main/java/com/github/tvbox/osc/player/controller/BaseController.java')
    b = read_text(bc)  # 暂停面板保持上游原样，不加置顶

    write_text(vp, vc)
    write_text(bc, b)
    log('暂停保活：暂停时闲置计时器不再把底栏/时间面板收掉')
    log('唤出底栏：底栏直接置可见，外层同步可见（不会点了没反应）')


def apply_ad_safety():
    """两个真实缺陷（各自独立开关，互不牵连）：
    1) 3.5s 超时放行是"裸"排队的：切集后旧地址的超时仍会抢到起播权，
       把播放拉回上一集（上一集往往正是那段广告）→ 表现为广告放完又回到广告、正片不出来。
    2) 走净化代理起播后没有任何回落：代理清单一旦不可播，只会一直黑着。
    """
    if not FEAT_FAST_START or not (FEAT_SEQ_GUARD or FEAT_PROXY_WATCHDOG):
        log('广告兜底：已关闭（强起关了，不再有需要作废的超时回调）')
        return
    L = chr(10)
    vp = jp(VOD)
    vc = read_text(vp)
    if 'tkPlaySeq' in vc:
        log('  = 起播序号防抢已存在，跳过')
        return

    # 看门狗单独开、序号关时，补一个只在形式上存在的序号字段（恒等于 0，判断永远成立）
    if FEAT_PROXY_WATCHDOG and not FEAT_SEQ_GUARD:
        a = '    private boolean tkTakeOver() {'
        if vc.count(a) != 1:
            sys.exit('广告兜底锚点丢失：tkTakeOver')
        vc = vc.replace(a, '    private long tkPlaySeq = 0L;' + L + L + a, 1)

    if FEAT_SEQ_GUARD:
        # 1) 序列号：切集后旧超时作废
        a = '    private boolean tkTakeOver() {'
        if vc.count(a) != 1:
            sys.exit('广告兜底锚点丢失：tkTakeOver')
        vc = vc.replace(a, '    private long tkPlaySeq = 0L; // 每次起播递增，旧超时自动作废' + L + L + a, 1)

        b = ('        tkPlayed = false;' + L +
             '        try {' + L +
             '            final android.os.Handler tkHandler = new android.os.Handler(android.os.Looper.getMainLooper());')
        b2 = ('        tkPlayed = false;' + L +
              '        final long tkSeqNow = ++tkPlaySeq;' + L +
              '        try {' + L +
              '            final android.os.Handler tkHandler = new android.os.Handler(android.os.Looper.getMainLooper());')
        if vc.count(b) != 1:
            sys.exit('广告兜底锚点丢失：playM3u8 超时块')
        vc = vc.replace(b, b2, 1)

        c = ('                public void run() {' + L +
             '                    if (!tkTakeOver()) return;' + L +
             '                    LOG.i("echo-m3u8起播超时放行: " + url);')
        c2 = ('                public void run() {' + L +
              '                    if (tkSeqNow != tkPlaySeq) return; // 已切到别的集，这次超时作废' + L +
              '                    if (!tkTakeOver()) return;' + L +
              '                    LOG.i("echo-m3u8起播超时放行: " + url);')
        if vc.count(c) != 1:
            sys.exit('广告兜底锚点丢失：超时 runnable')
        vc = vc.replace(c, c2, 1)
        log('广告兜底：切集后旧的 3.5s 超时作废（不会再被拉回上一集的广告）')

    if FEAT_PROXY_WATCHDOG:
        # 2) 代理播放看门狗：12 秒还没进播放态就回落原地址
        d = ('            listener.onM3u8ProxyUrl(proxyUrl, url);' + L +
             '            listener.startPlayUrl(proxyUrl, headers);')
        d2 = ('            listener.onM3u8ProxyUrl(proxyUrl, url);' + L +
              '            listener.startPlayUrl(proxyUrl, headers);' + L +
              '            tkWatchProxy(url, headers); // 净化代理不认账时回落原地址')
        if vc.count(d) != 1:
            sys.exit('广告兜底锚点丢失：代理起播')
        vc = vc.replace(d, d2, 1)

        e = '    private void processM3u8Content(String url, String content, HashMap<String, String> headers) {'
        if vc.count(e) != 1:
            sys.exit('广告兜底锚点丢失：processM3u8Content')
        watch = (
            '    // 净化代理看门狗：起播后 12 秒仍未进入播放态，说明代理清单不可播，直接回落原地址' + L +
            '    private void tkWatchProxy(final String origUrl, final HashMap<String, String> headers) {' + L +
            '        final long seq = tkPlaySeq;' + L +
            '        try {' + L +
            '            new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() {' + L +
            '                @Override public void run() {' + L +
            '                    try {' + L +
            '                        if (seq != tkPlaySeq) return;' + L +
            '                        if (videoPlayState == VideoView.STATE_PLAYING || videoPlayState == VideoView.STATE_PAUSED) return;' + L +
            '                        tkPlayed = false;' + L +
            '                        LOG.e("tk净化代理无画面，回落原地址");' + L +
            '                        listener.startPlayUrl(origUrl, headers);' + L +
            '                    } catch (Throwable ignored) {}' + L +
            '                }' + L +
            '            }, 12000);' + L +
            '        } catch (Throwable ignored) {}' + L +
            '    }' + L + L)
        vc = vc.replace(e, watch + e, 1)
        log('广告兜底：净化代理 12 秒没画面自动回落原地址（不会黑在那儿不切）')

    write_text(vp, vc)
def apply_ad_replay():
    """这个源的实际结构：先给一条"广告 m3u8"（几十秒、自带 ENDLIST），播完才该重新解析出正片。
    上游在播完时一律走 playNext —— 而网页源通常只有一集，于是直接弹"已经是最后一集了"，
    正片就永远出不来。改成：整段时长 <= 120 秒的播完，重新解析当前集（最多两次），
    还不行才走原来的下一集逻辑。"""
    if not FEAT_AD_REPLAY:
        log('广告段播完重解析：已关闭，播完仍走上游"下一集"逻辑')
        return
    L = chr(10)
    vp = jp(VOD)
    fp = jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java')
    vc = read_text(vp)
    pf = read_text(fp)
    if 'tkReplayShort' in vc and 'tkReplayShort' in pf:
        log('  = 广告段播完重解析已存在，跳过')
        return

    # 1) 接口加方法
    a = ('    public interface VodControlListener {' + L +
         '        void playNext(boolean rmProgress);')
    a2 = ('    public interface VodControlListener {' + L +
          '        void playNext(boolean rmProgress);' + L +
          '        void tkReplayShort();')
    if vc.count(a) != 1:
        sys.exit('广告重解析锚点丢失：VodControlListener')
    vc = vc.replace(a, a2, 1)

    # 2) 播完分支：短时长先重解析
    b = ('            case VideoView.STATE_PLAYBACK_COMPLETED:' + L +
         '                listener.playNext(true);' + L +
         '                break;')
    b2 = ('            case VideoView.STATE_PLAYBACK_COMPLETED:' + L +
          '                int tkDur = safeTimeMs(mControlWrapper.getDuration());' + L +
          '                if (tkDur > 0 && tkDur <= 120000) {' + L +
          '                    // 广告段播完：重新解析当前集拿正片，而不是当成"最后一集"' + L +
          '                    listener.tkReplayShort();' + L +
          '                } else {' + L +
          '                    listener.playNext(true);' + L +
          '                }' + L +
          '                break;')
    if vc.count(b) != 1:
        sys.exit('广告重解析锚点丢失：播完分支')
    vc = vc.replace(b, b2, 1)
    write_text(vp, vc)

    # 3) PlayFragment 实现 + 计数
    c = ('            public void playNext(boolean rmProgress) {' + L +
         '                String preProgressKey = progressKey;' + L +
         '                PlayFragment.this.playNext(rmProgress);' + L +
         '                if (rmProgress && preProgressKey != null)' + L +
         '                    CacheManager.delete(MD5.string2MD5(preProgressKey), 0);' + L +
         '            }')
    c2 = (c + L + L +
          '            @Override' + L +
          '            public void tkReplayShort() {' + L +
          '                if (tkShortRetry >= 2) {' + L +
          '                    tkShortRetry = 0;' + L +
          '                    playNext(true);' + L +
          '                    return;' + L +
          '                }' + L +
          '                tkShortRetry++;' + L +
          '                LOG.i("tk短时长播完，重新解析当前集 " + tkShortRetry + "/2");' + L +
          '                reusePlayerOnSwitch = true;' + L +
          '                play(false);' + L +
          '            }')
    if pf.count(c) != 1:
        sys.exit('广告重解析锚点丢失：PlayFragment 监听实现')
    pf = pf.replace(c, c2, 1)

    d = '    public void playNext(boolean isProgress) {' + L + '        triedLineFlags.clear();'
    d2 = '    private int tkShortRetry = 0; // 广告段播完后重解析当前集的次数' + L + L + d.replace('        triedLineFlags.clear();', '        tkShortRetry = 0;' + L + '        triedLineFlags.clear();')
    if pf.count(d) != 1:
        sys.exit('广告重解析锚点丢失：playNext 重置')
    pf = pf.replace(d, d2, 1)

    e = '    public void playPrevious() {' + L + '        triedLineFlags.clear();'
    e2 = e.replace('        triedLineFlags.clear();', '        tkShortRetry = 0;' + L + '        triedLineFlags.clear();')
    if pf.count(e) != 1:
        sys.exit('广告重解析锚点丢失：playPrevious 重置')
    pf = pf.replace(e, e2, 1)
    write_text(fp, pf)
    log('广告段播完：整段 <=120 秒就重新解析当前集（最多 2 次），不再直接判"最后一集"')


def apply_speed_fix():
    """1) 净化结果复用：切软解/硬解/换播放器都会重走 playM3u8，原来每次都干等 3.5 秒拉清单；
       同一地址已经净化过就直接走代理起播，秒切。
       2) seekBar 高度原本写死 30mm（手机约 66dp，把底栏顶得很高、进度条看着悬在中间），
       改成按屏型分级的静态 dp，底栏收回来贴底。"""
    L = chr(10)
    vp = jp(VOD)
    vc = read_text(vp)
    lay = jp(LAYOUT)
    xt = read_text(lay)
    acted = []

    # ---- 1) 净化缓存 ----
    if FEAT_PURIFY_CACHE and 'tkLastPurifyUrl' not in vc:
        fld = '    private JSONObject mPlayerConfig = null;'
        if vc.count(fld) != 1:
            sys.exit('净化缓存锚点丢失：mPlayerConfig 字段')
        vc = vc.replace(fld, fld + L + '    private String tkLastPurifyUrl = null; // 上次净化成功的主清单地址', 1)

        b = '        OkGo.getInstance().cancelTag("m3u8-2");'
        if vc.count(b) != 1:
            sys.exit('净化缓存锚点丢失：cancelTag m3u8-2')
        b2 = (b + L +
              '        // tkPurifyCache：同一地址已净化过，直接走代理起播，不再重复拉清单' + L +
              '        if (tkLastPurifyUrl != null && tkLastPurifyUrl.equals(url)' + L +
              '                && RemoteServer.m3u8Content != null && M3u8.currentAdCount > 0) {' + L +
              '            try {' + L +
              '                String cProxy = ControlManager.get().getAddress(true) + "proxyM3u8";' + L +
              '                listener.onM3u8ProxyUrl(cProxy, url);' + L +
              '                listener.startPlayUrl(cProxy, headers);' + L +
              '                return;' + L +
              '            } catch (Throwable ignored) {}' + L +
              '        }')
        vc = vc.replace(b, b2, 1)

        c = ('            listener.onM3u8ProxyUrl(proxyUrl, url);' + L +
             '            listener.startPlayUrl(proxyUrl, headers);')
        c2 = ('            listener.onM3u8ProxyUrl(proxyUrl, url);' + L +
              '            tkLastPurifyUrl = url; // tkPurifyCache：记住这份净化结果，切解码时复用' + L +
              '            listener.startPlayUrl(proxyUrl, headers);')
        if vc.count(c) != 1:
            sys.exit('净化缓存锚点丢失：记录净化地址（找到 %d 处）' % vc.count(c))
        vc = vc.replace(c, c2, 1)
        write_text(vp, vc)
        acted.append('净化缓存：同一地址切软解/硬解/换播放器不再重复拉一遍清单')

    # ---- 2) seekBar 高度静态化 ----
    if 'tk_seek_h' not in xt:
        key = 'android:id="@+id/seekBar"'
        if xt.count(key) != 1:
            sys.exit('seekBar 锚点丢失')
        i = xt.find(key)
        old = 'android:layout_height="@dimen/vs_30"'
        j = xt.find(old, i)
        if j < 0 or j - i > 700:
            sys.exit('seekBar 高度锚点丢失')
        xt = xt[:j] + 'android:layout_height="@dimen/tk_seek_h"' + xt[j + len(old):]
        write_text(lay, xt)
        acted.append('seekBar 高度：30mm → @dimen/tk_seek_h')

    dims = {'values': '16dp', 'values-port': '14dp', 'values-sw720dp': '20dp'}
    for d in dims:
        p = jp('app/src/main/res', d, 'tk_dimens.xml')
        if not os.path.exists(p):
            sys.exit('tk_dimens.xml 缺失：' + d)

    for d in dims:
        p = jp('app/src/main/res', d, 'tk_dimens.xml')
        s = read_text(p)
        if 'tk_seek_h' in s:
            continue
        v = dims[d]
        s = s.replace('</resources>', '<dimen name="tk_seek_h">%s</dimen>' % v + L + '</resources>', 1)
        write_text(p, s)

    for x in acted:
        log(x)
    log('底栏进度条行高：手机 16dp / 竖屏 14dp / 电视 20dp（静态，不再受 30mm 影响）')


def apply_static_ui():
    """把底栏边距/时间字号/按钮间距全部静态化到 dimen（按屏宽与方向自动生效），
    干掉运行时 tkAdaptiveUi 重排 —— 消除"先小字后大字"的跳变与重复 requestLayout。"""
    L = chr(10)
    res = jp('app/src/main/res')
    # 幂等：间距已经全换成 tk_btn_gap、且找不到旧的 vs_5 锚点，说明这一趟已经做过了。
    # 不跳过的话第二次跑会在"锚点 0 处"上 sys.exit，还会把 tk_dimens 覆盖回半成品。
    _x = read_text(jp(LAYOUT))
    if '@dimen/tk_btn_gap' in _x and 'android:layout_marginEnd="@dimen/vs_5"' not in _x:
        log('  = 底栏尺寸已静态化，跳过')
        return
    d = os.path.join(res, 'values')
    dim = jp('app/src/main/res/values/tk_dimens.xml')
    base = ['<?xml version="1.0" encoding="utf-8"?>', '<resources>',
            '    <dimen name="tk_seek_inset">0dp</dimen>',
            '    <dimen name="tk_time_minw">0dp</dimen>',
            '    <dimen name="tk_time_ts">14dp</dimen>',
            '    <dimen name="tk_row_pad_lr">24dp</dimen>',
            '    <dimen name="tk_time_gap">0.5dp</dimen>',
            '    <dimen name="tk_btn_gap">3dp</dimen>',
            '</resources>']
    write_text(dim, L.join(base) + L)
    # 电视/大屏（小米 X65 等：最小宽度 >= 720dp）
    tv = os.path.join(res, 'values-sw720dp')
    os.makedirs(tv, exist_ok=True)
    write_text(os.path.join(tv, 'tk_dimens.xml'), L.join([
        '<?xml version="1.0" encoding="utf-8"?>', '<resources>',
        '    <dimen name="tk_time_ts">24dp</dimen>',
        '    <dimen name="tk_row_pad_lr">60dp</dimen>',
        '    <dimen name="tk_btn_gap">3dp</dimen>',
        '</resources>']) + L)
    # 手机竖屏：底栏左右贴边
    pt = os.path.join(res, 'values-port')
    os.makedirs(pt, exist_ok=True)
    write_text(os.path.join(pt, 'tk_dimens.xml'), L.join([
        '<?xml version="1.0" encoding="utf-8"?>', '<resources>',
        '    <dimen name="tk_seek_inset">0dp</dimen>',
        '    <dimen name="tk_time_minw">0dp</dimen>',
        '    <dimen name="tk_time_ts">10dp</dimen>',
        '    <dimen name="tk_row_pad_lr">5dp</dimen>',
        '    <dimen name="tk_time_gap">0.6dp</dimen>',
        '    <dimen name="tk_btn_gap">3dp</dimen>',
        '</resources>']) + L)
    log('底栏尺寸：已静态化（手机竖屏贴边 / 手机横屏 24dp / 电视 60dp，inflate 即最终形态，不再起播后突变）')

    lp = jp(LAYOUT)
    x = read_text(lp)
    n = x.count('android:layout_marginEnd="@dimen/vs_5"')
    x = x.replace('android:layout_marginEnd="@dimen/vs_5"', 'android:layout_marginEnd="@dimen/tk_btn_gap"')
    x = x.replace('android:layout_marginRight="@dimen/vs_5"', 'android:layout_marginRight="@dimen/tk_btn_gap"')
    if n < 10:
        sys.exit('按钮间距锚点异常：只找到 %d 处' % n)
    write_text(lp, x)
    log('按钮间距：%d 处改为 @dimen/tk_btn_gap（静态）' % n)

    vp = jp(VOD)
    vc = read_text(vp)
    key = 'private void tkAdaptiveUi() {'
    i = vc.find(key)
    if i < 0:
        sys.exit('tkAdaptiveUi 锚点丢失')
    j = vc.index('{', i)
    depth = 0
    k = j
    while k < len(vc):
        if vc[k] == '{':
            depth += 1
        elif vc[k] == '}':
            depth -= 1
            if depth == 0:
                break
        k += 1
    if depth != 0:
        sys.exit('tkAdaptiveUi 括号没闭合')
    body_new = ('private void tkAdaptiveUi() {' + L +
                '        // tk：尺寸已全部静态化到 dimen（按屏宽/方向自动生效），不再运行时重排' + L +
                '    }')
    vc = vc[:i] + body_new + vc[k + 1:]
    write_text(vp, vc)
    if 'setPadding(edgePx' in read_text(vp):
        sys.exit('运行时 padding 还没去掉')
    log('去掉了起播后的运行时重排（不再先小后大）')


def apply_spacing():
    """
    行距与贴边。上游这批尺寸走的是 mm 副单位（vs_5≈14dp、vs_20≈57dp），
    在电视上会把顶部两行之间撑到能再塞一整行字。这里统一换成固定 dp：
      片名与分辨率缝隙 4dp（2+2）；进度条线到按钮图标 16dp；按钮汉字到底边 10dp。
    固定值天然幂等，重复跑不会变。
    """
    path = jp('app/src/main/res/layout/player_vod_control_view.xml')
    if not os.path.isfile(path):
        return
    tree = ET.parse(path)
    root = tree.getroot()
    A = '{http://schemas.android.com/apk/res/android}'

    def by_id(name):
        for e in root.iter():
            if e.get(A + 'id') == '@+id/' + name:
                return e
        return None

    def put(e, k, v):
        if e is not None and e.get(A + k) != v:
            e.set(A + k, v)
            return 1
        return 0

    n = 0
    # 左上两行：片名 / 分辨率
    n += put(by_id('tv_info_name1'), 'paddingBottom', '2dp')
    n += put(by_id('tv_videosize'), 'layout_marginTop', '2dp')
    n += put(by_id('tv_videosize'), 'paddingTop', '0dp')
    # 右上两行：时间 / 网速
    for tid in ('tv_info_name1', 'tv_videosize', 'tv_screen_display',
                'tv_play_load_net_speed_right_top'):
        n += put(by_id(tid), 'includeFontPadding', 'false')
    n += put(by_id('tv_screen_display'), 'paddingBottom', '2dp')
    n += put(by_id('tv_play_load_net_speed_right_top'), 'layout_marginTop', '2dp')
    n += put(by_id('tv_play_load_net_speed_right_top'), 'paddingTop', '0dp')
    # 底栏上下留白
    n += put(by_id('bottom_container'), 'paddingTop', '12dp')
    n += put(by_id('bottom_container'), 'paddingBottom', '4dp')
    # 进度条行 → 按钮行
    bc = by_id('bottom_container')
    seek_row = None
    if bc is not None:
        for c in list(bc):
            if c.tag == 'LinearLayout':
                seek_row = c
                break
    n += put(seek_row, 'layout_marginBottom', '0dp')
    # 每个按钮的图标距行顶 4dp（原 10dp）
    group = by_id('play_btn_group')
    if group is not None:
        for c in list(group):
            if c.get(A + 'paddingTop') is not None:
                n += put(c, 'paddingTop', '4dp')
                # 片头尾容器原先没有右边距，会和邻居贴得过近，统一补上
                if c.get(A + 'layout_marginEnd') is None:
                    n += put(c, 'layout_marginEnd', '@dimen/tk_btn_gap')
                # 按钮自身底部留白清零，汉字到屏幕底边只由容器的 4dp 决定
                if c.get(A + 'paddingBottom') is not None:
                    n += put(c, 'paddingBottom', '0dp')
    if n:
        tree.write(path, encoding='utf-8', xml_declaration=True)
        log('行距收紧：顶部两行 4dp、进度条到按钮 16dp、按钮行贴边 12dp（改 %d 处）' % n)
    else:
        log('行距收紧：已是目标值，跳过')


def apply_search_source_fix():
    """「指定搜索源」：勾了就只搜勾的，一个都不勾就真的不搜（上游会回退成全部源）。"""
    L = chr(10)
    p = jp('app/src/main/java/com/github/tvbox/osc/util/SearchHelper.java')
    t = read_text(p)
    if '明确设置过就用设置' in t:
        log('搜索源筛选：已修复，跳过')
        return
    i = t.find('    public static HashMap<String, String> getSourcesForSearch() {')
    if i < 0:
        sys.exit('搜索源锚点丢失：getSourcesForSearch')
    k = t.find('    public static void putCheckedSources', i)
    if k < 0:
        sys.exit('搜索源锚点丢失：putCheckedSources')
    j = t.rfind('    }' + L, i, k)
    if j < 0:
        sys.exit('搜索源锚点丢失：getSourcesForSearch 收尾')
    j += len('    }')
    new = ('    public static HashMap<String, String> getSourcesForSearch() {' + L
           + '        HashMap<String, String> mCheckSources;' + L
           + '        try {' + L
           + '            String api = Hawk.get(HawkConfig.API_URL, "");' + L
           + '            if (api.isEmpty()) return null;' + L
           + '            HashMap<String, HashMap<String, String>> mCheckSourcesForApi =' + L
           + '                    Hawk.get(HawkConfig.SOURCES_FOR_SEARCH, new HashMap<>());' + L
           + '            mCheckSources = mCheckSourcesForApi.get(api);' + L
           + '        } catch (Exception e) {' + L
           + '            return null;' + L
           + '        }' + L
           + '        // tk：勾了就只搜勾的（不自动补源，勾选才说了算）；' + L
           + '        //     一个都没勾 = 不指定 → 全部源照搜，源池一个不少。' + L
           + '        if (mCheckSources == null || mCheckSources.isEmpty()) {' + L
           + '            mCheckSources = getSources();' + L
           + '        }' + L
           + '        return mCheckSources;' + L
           + '    }')
    t = t[:i] + new + t[j:]
    write_text(p, t)
    if '勾了就只搜勾的' not in read_text(p):
        sys.exit('搜索源筛选没写进去')
    log('搜索源筛选：勾哪个只搜哪个；一个不勾 = 全源照搜')

    # 每次发起搜索前重读一次勾选，改完勾选不用退出搜索页也能立刻生效
    for rel in ('app/src/main/java/com/github/tvbox/osc/ui/activity/FastSearchActivity.java',
                'app/src/main/java/com/github/tvbox/osc/ui/activity/SearchActivity.java'):
        act = read_text(jp(rel))
        if 'tk勾选重读' in act:
            continue
        head = '    private void search(String title) {' + L
        if head not in act:
            sys.exit('搜索入口锚点丢失：' + rel)
        act = act.replace(head, head + '        // tk勾选重读：每次搜索都按当前勾选走，不沿用进页面时的旧快照' + L
                          + '        initCheckedSourcesForSearch();' + L, 1)
        write_text(jp(rel), act)
    log('搜索源筛选：发起搜索前重读勾选（不沿用旧快照）')


def apply_full_preview_fix():
    """详情页全屏预览必须满屏（旋屏不重建 Activity 时上游不会再设 LayoutParams）。"""
    L = chr(10)
    da = jp('app/src/main/java/com/github/tvbox/osc/ui/activity/DetailActivity.java')
    t = read_text(da)
    if 'tkForceFullPreview' in t:
        log('全屏预览满屏：已存在，跳过')
        return
    a = '    void setFullPreview(boolean full) {'
    if a not in t:
        sys.exit('锚点丢失：setFullPreview')
    blk = ('    // tk：全屏预览必须是满屏。上游只在切换那一刻设一次 LayoutParams，' + L
           + '    // 旋屏时 Activity 不重建就不会再设，容器停在旧尺寸上 —— 实机竖屏底栏就浮在屏幕半空。' + L
           + '    private void tkForceFullPreview() {' + L
           + '        try {' + L
           + '            if (!fullWindows || llPlayerFragmentContainer == null) return;' + L
           + '            llPlayerFragmentContainer.setLayoutParams(new android.widget.FrameLayout.LayoutParams(' + L
           + '                    android.view.ViewGroup.LayoutParams.MATCH_PARENT,' + L
           + '                    android.view.ViewGroup.LayoutParams.MATCH_PARENT));' + L
           + '            llPlayerFragmentContainer.requestLayout();' + L
           + '        } catch (Throwable ignored) {' + L
           + '        }' + L
           + '    }' + L + L)
    t = t.replace(a, blk + a, 1)

    a2 = '        toggleSubtitleTextSize();' + L + '    }' + L + L + '    @Override' + L + '    public void onConfigurationChanged(Configuration newConfig) {'
    if a2 not in t:
        sys.exit('锚点丢失：setFullPreview 收尾')
    t = t.replace(a2, '        toggleSubtitleTextSize();' + L + '        tkForceFullPreview();' + L + '    }' + L + L
                  + '    @Override' + L + '    public void onConfigurationChanged(Configuration newConfig) {', 1)

    a3 = '        super.onConfigurationChanged(newConfig);'
    if a3 not in t:
        sys.exit('锚点丢失：onConfigurationChanged')
    t = t.replace(a3, a3 + L
                  + '        // tk：旋屏后预览容器缓存的是上一个方向的尺寸，清掉重取，并让全屏预览重新铺满' + L
                  + '        windowsPreview = null;' + L
                  + '        tkForceFullPreview();', 1)
    if 'tkForceFullPreview();' not in t or 'windowsPreview = null;' not in t:
        sys.exit('全屏预览满屏没写进去')
    write_text(da, t)
    log('详情页：全屏预览强制满屏 + 旋屏后重取预览尺寸')


def apply_download_anywhere():
    """详情页加「下载」按钮；播放时把真实地址记进 TkUrlMemo，之后不播放也能下。"""
    L = chr(10)
    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/TkUrlMemo.java'), TK_URL_MEMO_JAVA)
    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/TkDownloadPicker.java'), TK_DL_PICKER_JAVA)
    write_text(jp('app/src/main/java/com/github/tvbox/osc/util/TkDownloadCenter.java'), TK_DL_CENTER_JAVA)

    lay = jp('app/src/main/res/layout/activity_detail.xml')
    x = read_text(lay)

    def _tune_dl(seg):
        """把「下载」按钮收成按文字自适应的窄按钮。
        这一排前面已经有 5 个 vs_120（约 107dp）的按钮，再塞一个同宽的会顶出父容器，
        圆角背景右边被裁掉——实机上看到的「底板显示不全」就是这个溢出。
        """
        seg = seg.replace('android:layout_width="@dimen/vs_120"',
                          'android:layout_width="wrap_content"', 1)
        if 'android:minWidth' not in seg:
            seg = (seg.replace('android:layout_width="wrap_content"',
                               'android:layout_width="wrap_content"'
                               + L + '                        android:minWidth="@dimen/vs_80"'
                               + L + '                        android:paddingLeft="@dimen/vs_10"'
                               + L + '                        android:paddingRight="@dimen/vs_10"', 1))
        seg = seg.replace('android:layout_marginEnd="@dimen/vs_10"',
                          'android:layout_marginEnd="0dp"')
        seg = seg.replace('android:layout_marginRight="@dimen/vs_10"',
                          'android:layout_marginRight="0dp"')
        return seg

    if '@+id/tvDownload' not in x:
        k = x.find('@+id/tvChangeSource')
        if k < 0:
            sys.exit('详情页布局锚点丢失：tvChangeSource')
        st = x.rfind('<TextView', 0, k)
        ind = st
        while ind > 0 and x[ind - 1] in ' \t':
            ind -= 1
        indent = x[ind:st]
        en = x.find('/>', k) + 2
        node = x[st:en]
        if 'layout_marginEnd' not in node:
            node = node.replace('android:layout_width="@dimen/vs_120"',
                                'android:layout_width="@dimen/vs_120"' + L
                                + '                        android:layout_marginEnd="@dimen/vs_10"' + L
                                + '                        android:layout_marginRight="@dimen/vs_10"', 1)
        btn = (node.replace('@+id/tvChangeSource', '@+id/tvDownload')
               .replace('@drawable/button_detail_change_source', '@drawable/button_detail_collect')
               .replace('android:text="切源"', 'android:text="下载"'))
        btn = _tune_dl(btn)
        x = x[:st] + node + L + indent + btn + x[en:]
        write_text(lay, x)
        log('详情页新增按钮：下载（紧跟切源右侧，宽度按文字自适应，不再溢出）')
    else:
        # 老树里可能还是 107dp 宽，就地修正
        m = re.search(r'<TextView[^>]*@\+id/tvDownload[^>]*/>', x, re.S)
        if m and 'android:layout_width="wrap_content"' not in m.group(0):
            x = x[:m.start()] + _tune_dl(m.group(0)) + x[m.end():]
            write_text(lay, x)
            log('详情页下载按钮：宽度已收回自适应（修掉溢出裁切）')
        else:
            log('详情页下载按钮已存在，跳过布局')

    da = jp('app/src/main/java/com/github/tvbox/osc/ui/activity/DetailActivity.java')
    t = read_text(da)
    if 'tvDownload' not in t:
        a = '    private TextView tvChangeSource;'
        if a not in t:
            sys.exit('详情页锚点丢失：tvChangeSource 字段')
        t = t.replace(a, a + L + '    private TextView tvDownload;', 1)
        a = '        tvChangeSource = findViewById(R.id.tvChangeSource);'
        if a not in t:
            sys.exit('详情页锚点丢失：tvChangeSource 绑定')
        t = t.replace(a, a + L + '        tvDownload = findViewById(R.id.tvDownload);', 1)
        a = '        tvChangeSource.setOnClickListener(new View.OnClickListener() {'
        if a not in t:
            sys.exit('详情页锚点丢失：tvChangeSource 点击')
        block = ('        if (tvDownload != null) {' + L
                 + '            tvDownload.setOnClickListener(new View.OnClickListener() {' + L
                 + '                @Override' + L
                 + '                public void onClick(View v) {' + L
                 + '                    FastClickCheckUtil.check(v);' + L
                 + '                    try {' + L
                 + '                        if (vodInfo == null) return;' + L
                 + '                        com.github.tvbox.osc.util.TkDownloadPicker.show((android.content.Context) DetailActivity.this, vodInfo);' + L
                 + '                    } catch (Throwable ignored) {' + L
                 + '                    }' + L
                 + '                }' + L
                 + '            });' + L
                 + '        }' + L)
        t = t.replace(a, block + a, 1)
        write_text(da, t)
        log('详情页：下载按钮已接上选集框')
    else:
        log('详情页下载按钮代码已存在，跳过')
    # 按钮上的字跟着任务走：下载 → 下载 3/10，长按看列表
    t = read_text(da)
    if 'TkDownloadCenter.bind' not in t:
        a = '        tvDownload = findViewById(R.id.tvDownload);'
        if a not in t:
            sys.exit('详情页锚点丢失：tvDownload 绑定（状态显示）')
        t = t.replace(a, a + L + '        com.github.tvbox.osc.util.TkDownloadCenter.bind(tvDownload);', 1)
        write_text(da, t)
        log('详情页：下载按钮已接状态显示（进度/完成/失败）')

    pf = jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java')
    t = read_text(pf)
    # 旧的下载弹窗实现（含自己的判断逻辑）统一换成 Picker
    i = t.find('    public void tkShowDownloadDialog() {')
    if i >= 0 and 'TkDownloadPicker.show(requireContext()' not in t:
        j = t.find(L + '    }' + L, i)
        if j > 0:
            t = t[:i] + TK_DL_DIALOG.strip(L) + L + t[j + len(L + '    }' + L):]
    # 播放页拿到真实地址就记账
    if 'TkUrlMemo.remember' not in t:
        a = '    void playUrl(String url, HashMap<String, String> headers) {'
        if a not in t:
            sys.exit('地址记账锚点丢失：playUrl')
        t = t.replace(a, a + L
                      + '        try {' + L
                      + '            com.github.tvbox.osc.util.TkUrlMemo.remember(mVodInfo, url);' + L
                      + '        } catch (Throwable ignored) {' + L
                      + '        }', 1)
    write_text(pf, t)
    if 'TkUrlMemo.remember' not in read_text(pf):
        sys.exit('地址记账没写进 PlayFragment')
    for f in ('TkUrlMemo.java', 'TkDownloadPicker.java', 'TkDownloadCenter.java'):
        if not os.path.isfile(jp('app/src/main/java/com/github/tvbox/osc/util', f)):
            sys.exit('新文件没生成：' + f)
    log('下载链路：详情页入口 + 地址记忆 + UA/Referer 已就绪')


def apply_parse_hardening():
    """解析接口时好时坏：同一条线路内自动换解析器重试（最多 3 个），失败提示给清楚。"""
    L = chr(10)
    pf = jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java')
    t = read_text(pf)
    if 'tkNextParse(' in t:
        log('解析加固：已存在，跳过')
        return

    a = '    private String parseFlag;'
    if a not in t:
        sys.exit('解析加固锚点丢失：parseFlag 字段')
    t = t.replace(a, a + L
                  + '    private String tkParseName = "";' + L
                  + '    private final java.util.ArrayList<String> tkParseTried = new java.util.ArrayList<String>();', 1)

    a = '    private void doParse(ParseBean pb) {' + L + '        stopParse();'
    if a not in t:
        sys.exit('解析加固锚点丢失：doParse')
    t = t.replace(a, '    private void doParse(ParseBean pb) {' + L
                  + '        try {' + L
                  + '            tkParseName = (pb == null || pb.getName() == null) ? "" : pb.getName();' + L
                  + '        } catch (Throwable ignored) {' + L
                  + '        }' + L
                  + '        stopParse();', 1)

    a = '        parseFlag = flag;'
    if a not in t:
        sys.exit('解析加固锚点丢失：initParse')
    t = t.replace(a, a + L + '        try { tkParseTried.clear(); } catch (Throwable ignored) { }', 1)

    method = (
        '    /** 解析失败时在同一条线路里换下一个 json 解析器再试，最多试 3 个。 */' + L
        + '    private boolean tkNextParse() {' + L
        + '        try {' + L
        + '            java.util.List<ParseBean> all = ApiConfig.get().getParseBeanList();' + L
        + '            if (all == null || all.size() < 2) return false;' + L
        + '            if (tkParseTried.isEmpty()) tkParseTried.add(tkParseName);' + L
        + '            for (ParseBean pb : all) {' + L
        + '                if (pb == null || pb.getType() != 1) continue;' + L
        + '                String nm = pb.getName();' + L
        + '                if (nm == null) nm = "";' + L
        + '                if (tkParseTried.contains(nm)) continue;' + L
        + '                if (tkParseTried.size() >= 3) break;' + L
        + '                tkParseTried.add(nm);' + L
        + '                doParse(pb);' + L
        + '                try {' + L
        + '                    Toast.makeText(mContext, "解析失败，换解析器重试：" + nm, Toast.LENGTH_SHORT).show();' + L
        + '                } catch (Throwable ignored) {' + L
        + '                }' + L
        + '                return true;' + L
        + '            }' + L
        + '        } catch (Throwable ignored) {' + L
        + '        }' + L
        + '        return false;' + L
        + '    }' + L + L)
    a = '    private void doParse(ParseBean pb) {'
    t = t.replace(a, method + a, 1)

    # errorWithRetry 内：解析类错误先横向换解析器
    k = t.find('    void errorWithRetry(String err, boolean finish) {')
    if k < 0:
        sys.exit('解析加固锚点丢失：errorWithRetry')
    q = t.find('        if (!autoRetry()) {', k)
    if q < 0:
        sys.exit('解析加固锚点丢失：autoRetry 调用')
    hook = ('        // 解析接口时好时坏：同一线路先横向换一个解析器重试（最多 3 个），' + L
            + '        // 都失败才落到原来的换线路/换播放器逻辑，避免一挂就直接换源。' + L
            + '        if (err != null && err.indexOf("解析") >= 0 && webPlayUrl == null && tkNextParse()) return;' + L)
    t = t[:q] + hook + t[q:]
    write_text(pf, t)
    log('解析加固：同线路自动换解析器重试（最多 3 个）')


def apply_slot_align():
    """① 片头片尾「00:00」与汉字行对齐；② 旋屏图标描边 0.8 → 0.6。"""
    L = chr(10)
    path = jp(LAYOUT)
    tree = ET.parse(path)
    root = tree.getroot()
    # 片头尾格子内部只有上下两层（时间 / 汉字），自身不再需要任何左右外边距；
    # 早先为了把 00:00 往里挪而给它们加过 marginEnd，反而把容器撑宽，
    # 这里统一清掉，容器宽度只由「时间宽 + 2dp + 2dp」决定。
    changed = 0
    for nid in ('tk_slot_start', 'tk_slot_end', 'play_time_start', 'play_time_end'):
        v = find_id(root, nid)
        if v is None:
            continue
        for k in ('layout_marginEnd', 'layout_marginRight', 'layout_marginStart', 'layout_marginLeft'):
            if v.get(A + k) is not None:
                v.attrib.pop(A + k, None)
                changed += 1
    if changed:
        tree.write(path, encoding='utf-8', xml_declaration=True)
    root2 = ET.parse(path).getroot()
    for nid in ('tk_slot_start', 'tk_slot_end', 'play_time_start', 'play_time_end'):
        v = find_id(root2, nid)
        if v is not None and (v.get(A + 'layout_marginEnd') is not None
                              or v.get(A + 'layout_marginStart') is not None):
            sys.exit('左右外边距没清干净：' + nid)
    log('片头尾对齐：时间/汉字三层左右外边距已清空，宽度只由内容决定')

    hp = jp('app/src/main/res/drawable/htov.xml')
    if os.path.exists(hp):
        hx = read_text(hp)
        if 'android:strokeWidth="0.6"' not in hx:
            sys.exit('旋屏图标描边没改到（应为 0.6）')
        log('旋屏图标：描边 0.6（原 0.8）')


def apply_text_stroke():
    """按你的要求取消：顶部文字恢复标准 TextView，不再描边，也不再需要那个自定义类。"""
    cls = 'com.github.tvbox.osc.ui.tv.widget.TkStrokeTextView'
    lay = jp(LAYOUT)
    s = read_text(lay)
    n = 0
    if cls in s:
        n = s.count(cls)
        s = s.replace('<' + cls, '<TextView').replace(cls, 'TextView')
        write_text(lay, s)
    if cls in read_text(lay):
        sys.exit('描边类未能还原')
    fp = jp('app/src/main/java/com/github/tvbox/osc/ui/tv/widget', 'TkStrokeTextView.java')
    if os.path.exists(fp):
        os.remove(fp)
    if n:
        log('顶部文字：描边已撤销，' + str(n) + ' 处恢复标准 TextView')
    else:
        log('顶部文字：保持原样，不加描边')


def apply_top_transparent():
    """左上片名/分辨率、右上时间行/网速：去掉半透明底板，只留文字。"""
    L = chr(10)
    ids = ['tv_info_name1', 'tv_videosize', 'tv_screen_display', 'tv_play_load_net_speed_right_top']
    path = jp(LAYOUT)
    tree = ET.parse(path)
    root = tree.getroot()
    n = 0
    for sid in ids:
        v = find_id(root, sid)
        if v is None:
            sys.exit('透明化锚点丢失：' + sid)
        if v.get(A + 'background') != '@null':
            v.set(A + 'background', '@null')
            n += 1
    if n:
        tree.write(path, encoding='utf-8', xml_declaration=True)
    root2 = ET.parse(path).getroot()
    for sid in ids:
        v = find_id(root2, sid)
        if v.get(A + 'background') != '@null':
            sys.exit('透明化没生效：' + sid)
    log('顶部透明：%d 处去掉半透明底板（片名/分辨率/时间行/网速），只剩白字' % len(ids))


def apply_top_fix_DISABLED():
    """只保留一处纯性能改动：自适应 UI 在尺寸没变时不再重排。
    顶部网速/时间的显隐、屏显开关全部回到上游原样。"""
    L = chr(10)
    vc_path = jp(VOD)
    vc = read_text(vc_path)
    if 'tkUiKey' in vc:
        log('  = 自适应 UI 节流已存在，跳过')
        return
    a = '    private JSONObject mPlayerConfig = null;'
    if vc.count(a) != 1:
        sys.exit('顶部修复锚点丢失：mPlayerConfig 字段')
    vc = vc.replace(a, a + L + '    private int tkUiKey = 0;', 1)
    a2 = '            if (mActivity == null) return;'
    if vc.count(a2) != 1:
        sys.exit('顶部修复锚点丢失：tkAdaptiveUi 开头')
    b2 = ('            if (mActivity == null) return;' + L +
          '            // tk：尺寸没变就别再重排一次，避免每次刷新配置都 requestLayout' + L +
          '            int tkKey = getWidth() * 31 + getHeight();' + L +
          '            if (tkKey > 0 && tkKey == tkUiKey) return;' + L +
          '            if (tkKey > 0) tkUiKey = tkKey;')
    vc = vc.replace(a2, b2, 1)
    write_text(vc_path, vc)
    log('自适应 UI：尺寸不变不再重排（减卡顿）')


def apply_danmu_alpha():
    """弹幕透明度下限从 10% 放宽到 0%（彻底看不见，但仍算开启）"""
    h = jp('app/src/main/java/com/github/tvbox/osc/util/DanmuHelper.java')
    if not os.path.isfile(h):
        sys.exit('找不到 DanmuHelper.java')
    t = read_text(h)
    changed = False
    old = 'Hawk.put(HawkConfig.DANMU_ALPHA, Math.max(0.1f, Math.min(alpha, 1.0f)));'
    if old in t:
        t = t.replace(old, 'Hawk.put(HawkConfig.DANMU_ALPHA, Math.max(0f, Math.min(alpha, 1.0f)));', 1)
        write_text(h, t)
        changed = True
    elif 'Math.max(0f,' not in t:
        sys.exit('锚点丢失：DanmuHelper.setAlpha')

    d = jp('app/src/main/java/com/github/tvbox/osc/ui/dialog/DanmuSettingDialog.java')
    if not os.path.isfile(d):
        sys.exit('找不到 DanmuSettingDialog.java')
    dt = read_text(d)
    old2 = '            if (alpha.get() <= 10) return;'
    if old2 in dt:
        dt = dt.replace(old2, '            if (alpha.get() <= 0) return;', 1)
        write_text(d, dt)
        changed = True
    elif 'alpha.get() <= 0)' not in dt:
        sys.exit('锚点丢失：透明度减档下限')
    if changed:
        log('弹幕透明度：下限 10% -> 0%（0% 时彻底不可见）')
    else:
        log('  = 弹幕透明度下限已放宽，跳过')


def apply_danmu_doubletap():
    """弹幕按钮：双击 = 持久关闭；开启时图标左下角带小对号"""
    NL = chr(10)
    v = read_text(jp(VOD))
    # 幂等：字段 метода 都已写过就整体跳过（否则第二次跑会拿旧锚点去找不到）
    if 'tkDanmuClickTs' in v and 'updateDanmuBtn' in v and 'tkDanmuSingleClick' in v:
        log('  = 弹幕双击已装好，跳过')
        return

    field = ("    private long tkDanmuClickTs = 0L;" + NL + NL +
             "    private final Runnable tkDanmuSingleClick = new Runnable() {" + NL +
             "        @Override" + NL +
             "        public void run() {" + NL +
             "            tkDanmuClickTs = 0L;" + NL +
             "            if (mDanmuSettingBtn == null) return;" + NL +
             "            if (!DanmuHelper.isOpen()) {" + NL +
             "                DanmuHelper.setOpen(true);" + NL +
             "                updateDanmuBtn();" + NL +
             "                try {" + NL +
             "                    org.greenrobot.eventbus.EventBus.getDefault().post(new com.github.tvbox.osc.event.RefreshEvent(com.github.tvbox.osc.event.RefreshEvent.TYPE_SET_DANMU_SETTINGS, false));" + NL +
             "                } catch (Throwable ignored) {" + NL +
             "                }" + NL +
             "                Toast.makeText(getContext(), \"弹幕已开启\", Toast.LENGTH_SHORT).show();" + NL +
             "                return;" + NL +
             "            }" + NL +
             "            if (listener != null) listener.showDanmuSetting();" + NL +
             "        }" + NL +
             "    };" + NL + NL)
    anchor = '    public void updateDanmuBtn() {'
    if anchor not in v:
        sys.exit('锚点丢失：updateDanmuBtn 定义')
    v = v.replace(anchor, field + anchor, 1)

    old_vis = ("    public void updateDanmuBtn() {" + NL +
               "        if (mDanmuSettingBtn == null) return;" + NL +
               "        mDanmuSettingBtn.setVisibility(DanmuHelper.isOpen() ? VISIBLE : GONE);" + NL +
               "        updatePlayLabelVisibility();" + NL +
               "    }")
    new_vis = ("    public void updateDanmuBtn() {" + NL +
               "        if (mDanmuSettingBtn == null) return;" + NL +
               "        boolean isPortraitNow = getResources().getConfiguration().orientation == Configuration.ORIENTATION_PORTRAIT;" + NL +
               "        mDanmuSettingBtn.setVisibility(isPortraitNow ? GONE : VISIBLE);" + NL +
               "        mDanmuSettingBtn.setCompoundDrawablesWithIntrinsicBounds(0, DanmuHelper.isOpen() ? R.drawable.v_danmu_on : R.drawable.v_danmu, 0, 0);" + NL +
               "        mDanmuSettingBtn.setCompoundDrawablePadding(0);" + NL +
               "        mDanmuSettingBtn.setAlpha(DanmuHelper.isOpen() ? 1.0f : 0.45f);" + NL +
               "        updatePlayLabelVisibility();" + NL +
               "    }")
    if old_vis not in v:
        sys.exit('锚点丢失：updateDanmuBtn 主体')
    v = v.replace(old_vis, new_vis, 1)

    old_click = ("        mDanmuSettingBtn.setOnClickListener(new OnClickListener() {" + NL +
                 "            @Override" + NL +
                 "            public void onClick(View view) {" + NL +
                 "                FastClickCheckUtil.check(view);" + NL +
                 "                listener.showDanmuSetting();" + NL +
                 "            }" + NL +
                 "        });")
    new_click = ("        mDanmuSettingBtn.setOnClickListener(new OnClickListener() {" + NL +
                 "            @Override" + NL +
                 "            public void onClick(View view) {" + NL +
                 "                long now = System.currentTimeMillis();" + NL +
                 "                if (now - tkDanmuClickTs < 380) {" + NL +
                 "                    tkDanmuClickTs = 0L;" + NL +
                 "                    mDanmuSettingBtn.removeCallbacks(tkDanmuSingleClick);" + NL +
                 "                    DanmuHelper.setOpen(false);" + NL +
                 "                    updateDanmuBtn();" + NL +
                 "                    try {" + NL +
                 "                        org.greenrobot.eventbus.EventBus.getDefault().post(new com.github.tvbox.osc.event.RefreshEvent(com.github.tvbox.osc.event.RefreshEvent.TYPE_SET_DANMU_SETTINGS, true));" + NL +
                 "                    } catch (Throwable ignored) {" + NL +
                 "                    }" + NL +
                 "                    Toast.makeText(getContext(), \"弹幕已关闭，再点一下即可恢复\", Toast.LENGTH_SHORT).show();" + NL +
                 "                    hideBottom();" + NL +
                 "                    return;" + NL +
                 "                }" + NL +
                 "                tkDanmuClickTs = now;" + NL +
                 "                mDanmuSettingBtn.removeCallbacks(tkDanmuSingleClick);" + NL +
                 "                mDanmuSettingBtn.postDelayed(tkDanmuSingleClick, 380);" + NL +
                 "            }" + NL +
                 "        });")
    if old_click not in v:
        sys.exit('锚点丢失：弹幕按钮点击')
    v = v.replace(old_click, new_click, 1)
    write_text(jp(VOD), v)
    log('弹幕按钮：双击 = 持久关闭；单击 = 设置面板（关着时单击=恢复）；开启时带小对号')


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


def apply_single_layout():
    """播放页只留一份控制布局：box_vod_control_view（上游死文件，全工程零引用）及其专属背景一并删除。"""
    L = chr(10)
    root = jp('app/src/main/res')
    box = os.path.join(root, 'layout', 'box_vod_control_view.xml')
    bg = os.path.join(root, 'drawable', 'box_controller_top_bg.xml')
    # 删之前先确认真的没人引用，避免误删
    for dirpath, _, files in os.walk(jp('app/src/main')):
        for fn in files:
            if not fn.endswith(('.java', '.kt', '.xml')):
                continue
            f = os.path.join(dirpath, fn)
            if f == box:
                continue
            try:
                t = read_text(f)
            except Exception:
                continue
            if 'box_vod_control_view' in t:
                sys.exit('box 布局仍被引用，不能删：' + f)
    if os.path.exists(box):
        os.remove(box)
        log('删除重复布局：box_vod_control_view.xml（零引用的上游死文件）')
    if os.path.exists(bg):
        os.remove(bg)
        log('删除其专属背景：box_controller_top_bg.xml')
    left = [f for f in os.listdir(os.path.join(root, 'layout')) if 'vod_control' in f]
    if left != ['player_vod_control_view.xml']:
        sys.exit('播放控制布局没有合成一份：%s' % left)
    log('播放控制布局现在只有一份：player_vod_control_view.xml')


def apply_app_name():
    """把 APP_NAME 写进 values/strings.xml 的 app_name（桌面图标名 + 任务列表名）。"""
    p = jp(SRC, 'app/src/main/res/values/strings.xml')
    if not os.path.isfile(p):
        print('  ! 跳过应用名：未找到 values/strings.xml')
        return
    safe = APP_NAME.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    want = '<string name="app_name">%s</string>' % safe
    src = read_text(p)
    m = re.search(r'<string name="app_name">[^<]*</string>', src)
    if m:
        if m.group(0) == want:
            print('  + 应用名已是 %s，无需修改' % APP_NAME)
            return
        src = src[:m.start()] + want + src[m.end():]
    else:
        if '</resources>' not in src:
            raise RuntimeError('strings.xml 里找不到 app_name，也没有 </resources>')
        src = src.replace('</resources>', '    %s\n</resources>' % want, 1)
    write_text(p, src)
    if want not in read_text(p):
        raise RuntimeError('应用名写入失败')
    print('  + 应用名：%s（桌面显示 + 最近任务）' % APP_NAME)


def apply_render_fix():
    """画面被拉扁的两处上游 bug（只改比例换算，不碰解码、不碰播放内核）。

    22-1 MeasureHelper 的「填充」档：
         width = widthMeasureSpec / height = heightMeasureSpec
         MeasureSpec 不是尺寸，是打包了模式位的 int（EXACTLY 下约 10.7 亿 + 真实尺寸）。
         直接丢给 setMeasuredDimension，画面会被算到天文数字再被父容器裁掉。
         上面已经把等比尺寸算好了，这两行本来就该是空的。

    22-2 EXO / IJK 上报视频宽高时把像素宽高比丢了：
         anamorphic 片源（老剧、录播、部分 m3u8 很常见）是 1440×1080 存、
         1.333 像素比、应该显示成 1920×1080。裸报编码宽，渲染层拿到错的宽高比，
         再按等比一算，画面必然被拉宽（也就是"扁"）。
    """
    L = chr(10)
    MH = 'player/src/main/java/xyz/doikki/videoplayer/render/MeasureHelper.java'
    EXO = 'player/src/main/java/xyz/doikki/videoplayer/exo/ExoMediaPlayer.java'
    IJK = 'player/src/main/java/xyz/doikki/videoplayer/ijk/IjkPlayer.java'
    hit = 0

    # ---- 22-1 「填充」档 ----
    p = jp(MH)
    t = read_text(p)
    if 'tkRenderFixFill' not in t:
        a = ('            case VideoView.SCREEN_SCALE_MATCH_PARENT:' + L
             + '                width = widthMeasureSpec;' + L
             + '                height = heightMeasureSpec;' + L
             + '                break;')
        b = ('            case VideoView.SCREEN_SCALE_MATCH_PARENT:' + L
             + '                /* tkRenderFixFill：上游拿 MeasureSpec 原值当尺寸，这里沿用上面的等比结果 */' + L
             + '                break;')
        if t.count(a) != 1:
            sys.exit('画面比例锚点丢失：MeasureHelper MATCH_PARENT')
        write_text(p, t.replace(a, b, 1))
        hit += 1

    # ---- 22-2 EXO 补像素宽高比 ----
    p = jp(EXO)
    t = read_text(p)
    if 'tkRenderFixExo' not in t:
        a = ('    public void onVideoSizeChanged(VideoSize videoSize) {' + L
             + '        if (mPlayerEventListener != null) {' + L
             + '            mPlayerEventListener.onVideoSizeChanged(videoSize.width, videoSize.height);')
        b = ('    public void onVideoSizeChanged(VideoSize videoSize) {' + L
             + '        if (mPlayerEventListener != null) {' + L
             + '            /* tkRenderFixExo：补回像素宽高比，否则 anamorphic 片源被拉扁 */' + L
             + '            int tkW = videoSize.width;' + L
             + '            float tkR = videoSize.pixelWidthHeightRatio;' + L
             + '            if (tkR > 0.5f && tkR < 3.0f && Math.abs(tkR - 1.0f) > 0.01f) tkW = (int) (tkW * tkR + 0.5f);' + L
             + '            mPlayerEventListener.onVideoSizeChanged(tkW, videoSize.height);')
        if t.count(a) != 1:
            sys.exit('画面比例锚点丢失：ExoMediaPlayer.onVideoSizeChanged')
        write_text(p, t.replace(a, b, 1))
        hit += 1

    # ---- 22-2 IJK 按 SAR 折算 ----
    p = jp(IJK)
    t = read_text(p)
    if 'tkRenderFixIjk' not in t:
        a = ('    public void onVideoSizeChanged(IMediaPlayer mp, int width, int height, int sar_num, int sar_den) {' + L
             + '        int videoWidth = mp.getVideoWidth();' + L
             + '        int videoHeight = mp.getVideoHeight();' + L
             + '        if (videoWidth != 0 && videoHeight != 0) {')
        b = ('    public void onVideoSizeChanged(IMediaPlayer mp, int width, int height, int sar_num, int sar_den) {' + L
             + '        int videoWidth = mp.getVideoWidth();' + L
             + '        int videoHeight = mp.getVideoHeight();' + L
             + '        /* tkRenderFixIjk：按 SAR 折算显示宽（sar 为 0 或相等时不动，折算后超过 4 倍视为异常放弃） */' + L
             + '        if (sar_num > 0 && sar_den > 0 && sar_num != sar_den) {' + L
             + '            int tkW = (int) ((long) videoWidth * sar_num / sar_den);' + L
             + '            if (tkW > 0 && tkW <= videoWidth * 4) videoWidth = tkW;' + L
             + '        }' + L
             + '        if (videoWidth != 0 && videoHeight != 0) {')
        if t.count(a) != 1:
            sys.exit('画面比例锚点丢失：IjkPlayer.onVideoSizeChanged')
        write_text(p, t.replace(a, b, 1))
        hit += 1

    log('画面比例：修「填充」档 1 处、补像素宽高比 2 处（EXO 用 pixelWidthHeightRatio / IJK 用 SAR）')


def apply_dns_default():
    """上游 DoH 默认值是 0（=关闭）——出厂就是走系统 DNS，很多源域名解析不出来、拉不到数据。
    这里只改"读取默认值"的那几处，把它变成 1（腾讯 DoH）；用户手动选过就尊重用户选择。"""
    files = [
        'app/src/main/java/com/github/tvbox/osc/util/OkGoHelper.java',
        'app/src/main/java/com/github/tvbox/osc/ui/fragment/ModelSettingFragment.java',
        'app/src/main/java/com/github/tvbox/osc/server/ControlManager.java',
    ]
    hit = 0
    for rel in files:
        fp = jp(rel)
        t = read_text(fp)
        if 'tkDnsDefault' in t:
            continue
        n = t.count('Hawk.get(HawkConfig.DOH_URL, 0)')
        if n:
            t = t.replace('Hawk.get(HawkConfig.DOH_URL, 0)', 'Hawk.get(HawkConfig.DOH_URL, 1) /* tkDnsDefault */')
            write_text(fp, t)
            hit += n
    log('DNS 默认：%d 处默认值由"关闭"改为腾讯 DoH（关掉 DNS 会解析不出源）' % hit)


def apply_push_button():
    """底栏 play_cast 改造成「推送」入口：
    - 汉字从「投屏」改成「推送」，图标原样保留
    - 点击不再开 DLNA 投屏设备列表，改成显示本机局域网推送地址（手机浏览器打开、后面接视频地址即可推到电视）
    """
    L = chr(10)
    lay = jp(LAYOUT)
    xt = read_text(lay)
    if 'android:text="推送"' in xt:
        log('  = 推送按钮已改好，跳过')
        return
    if xt.count('android:text="投屏"') != 1:
        sys.exit('推送按钮锚点丢失：text="投屏"')
    xt = xt.replace('android:text="投屏"', 'android:text="推送"', 1)
    write_text(lay, xt)

    vp = jp(VOD)
    vc = read_text(vp)
    a = '                if (listener != null) listener.clickCast();'
    if vc.count(a) != 1:
        sys.exit('推送按钮锚点丢失：clickCast')
    vc = vc.replace(a, '                tkShowPushAddr(); // tkPush：不再开投屏列表，改为显示推送地址', 1)

    anchor = '    private void showScaleDialog() {'
    if vc.count(anchor) != 1:
        sys.exit('推送按钮锚点丢失：showScaleDialog')
    method = (
        '    // tkPush：推送按钮 —— 显示本机局域网推送地址（手机浏览器打开，后面接视频地址即可推过来）' + L +
        '    private void tkShowPushAddr() {' + L +
        '        String a = "";' + L +
        '        try {' + L +
        '            a = ControlManager.get().getAddress(true);' + L +
        '        } catch (Throwable ignored) {}' + L +
        '        if (a == null || a.isEmpty()) {' + L +
        '            try { android.widget.Toast.makeText(mActivity, "推送服务没起来，退出重进一次", android.widget.Toast.LENGTH_SHORT).show(); } catch (Throwable ignored) {}' + L +
        '            return;' + L +
        '        }' + L +
        '        if (!a.endsWith("/")) a = a + "/";' + L +
        '        final String base = a + "push/";' + L +
        '        String msg = "手机和电视连同一个 WiFi，用手机浏览器打开这个地址，后面直接接视频地址：\\n\\n" + base + "\\n\\n例：" + base + "https://xxx.com/a.m3u8";' + L +
        '        try {' + L +
        '            new android.app.AlertDialog.Builder(mActivity)' + L +
        '                    .setTitle("推送到电视")' + L +
        '                    .setMessage(msg)' + L +
        '                    .setPositiveButton("复制地址", new android.content.DialogInterface.OnClickListener() {' + L +
        '                        @Override public void onClick(android.content.DialogInterface d, int w) {' + L +
        '                            try {' + L +
        '                                android.content.ClipboardManager cm = (android.content.ClipboardManager) mActivity.getSystemService(android.content.Context.CLIPBOARD_SERVICE);' + L +
        '                                cm.setPrimaryClip(android.content.ClipData.newPlainText("push", base));' + L +
        '                                android.widget.Toast.makeText(mActivity, "地址已复制", android.widget.Toast.LENGTH_SHORT).show();' + L +
        '                            } catch (Throwable ignored) {}' + L +
        '                        }' + L +
        '                    })' + L +
        '                    .setNegativeButton("关闭", null)' + L +
        '                    .show();' + L +
        '        } catch (Throwable ignored) {}' + L +
        '    }' + L + L)
    vc = vc.replace(anchor, method + anchor, 1)
    write_text(vp, vc)
    log('推送按钮：汉字改「推送」，点击显示局域网推送地址（不再进 DLNA 投屏列表）')


def apply_scrim_bg():
    """顶部/底部改成整块半透明底板（不渐变）。

    渐变那版是"贴屏幕边最深、往中间渐透"，实机看着还是一层灰雾、边界也不干净，
    而且渐变 drawable 一旦被布局引用就关不掉。这里退回最朴素的做法：
    通宽的半透明黑板，顶底各一条，透明度均匀，一块就是一块。
    """
    L = chr(10)
    lay = jp(LAYOUT)
    dr = jp('app/src/main/res/drawable')
    if not os.path.isdir(dr):
        os.makedirs(dr)
    t = read_text(lay)
    # 幂等要按"两处都指向 tk_scrim"来判断：只查"出现过 tk_scrim"是不够的，
    # apply_layout 每趟都会把 bottom_container 的底板清成 @null，只判出现就会漏掉底部。
    if t.count('@drawable/tk_scrim') >= 2:
        log('  = 半透明底板已存在，跳过')
        return

    write_text(os.path.join(dr, 'tk_scrim.xml'),
               '<?xml version="1.0" encoding="utf-8"?>' + L +
               '<shape xmlns:android="http://schemas.android.com/apk/res/android"' + L +
               '    android:shape="rectangle">' + L +
               '    <solid android:color="#8C000000" />' + L +
               '</shape>')

    import re

    def put_bg(tag):
        if 'android:background=' in tag:
            return re.sub('android:background="[^"]*"',
                          'android:background="@drawable/tk_scrim"', tag, count=1)
        return tag[:-1] + L + '        android:background="@drawable/tk_scrim">'

    # 1) 底部菜单整条
    m = re.search(r'<LinearLayout[^>]*@\+id/bottom_container[^>]*>', t)
    if not m:
        sys.exit('半透明底板锚点丢失：bottom_container')
    t = t[:m.start()] + put_bg(m.group(0)) + t[m.end():]

    # 2) 顶部整条（rootView 下第一个 LinearLayout，装片名/分辨率/时间/网速）
    i = t.find('@+id/rootView')
    if i < 0:
        sys.exit('半透明底板锚点丢失：rootView')
    k = t.find('<LinearLayout', t.find('>', i) + 1)
    e = t.find('>', k) + 1
    if k < 0 or e <= k:
        sys.exit('半透明底板锚点丢失：顶部行容器')
    nt = put_bg(t[k:e])
    # 渐变那版为了让渐变带往下延伸加的 40dp 内边距，纯色不需要，去掉让高度回原样
    nt = nt.replace(L + '        android:paddingBottom="40dp"', '')
    t = t[:k] + nt + t[e:]

    write_text(lay, t)
    log('顶部/底部底板：整块半透明 #8C000000（均匀，不渐变；顶部 40dp 延伸内边距已撤）')


def apply_screen_default():
    """屏显默认开：右上角网速 / 播放时间 / 系统时间出厂就显示。

    上游默认值是 GONE，装完什么都不显示，得手动点一下底栏「屏显」才出来；
    换包清零又会把这个键删掉，等于每升一版又回到隐藏。
    这里把默认值改成 VISIBLE，同时清零清单里已去掉这个键，用户点掉的会一直记住。
    """
    vp = jp(VOD)
    t = read_text(vp)
    if 'tkScreenOn' in t:
        log('  = 屏显默认已开，跳过')
        return
    pairs = (
        ('Hawk.get(HawkConfig.SCREEN_DISPLAY,GONE)',
         'Hawk.get(HawkConfig.SCREEN_DISPLAY,VISIBLE) /* tkScreenOn */'),
        ('Hawk.get(HawkConfig.SCREEN_DISPLAY, GONE)',
         'Hawk.get(HawkConfig.SCREEN_DISPLAY, VISIBLE) /* tkScreenOn */'),
    )
    n = 0
    for a, b in pairs:
        c = t.count(a)
        if c:
            t = t.replace(a, b)
            n += c
    if n == 0:
        sys.exit('屏显默认锚点丢失：SCREEN_DISPLAY 默认值一处都没找到')
    write_text(vp, t)
    log('屏显：%d 处默认值 GONE → VISIBLE（右上角网速/时间出厂即显示）' % n)


def apply_gradient_bg():
    """顶部/底部整条渐变底板：靠屏幕边不透明，往画面中间逐渐透明，正中不动。
    原来是每个小标签挂一块 @drawable 半透明方块，边角生硬、还能看出方块边界；
    改成整行一条线性渐变，从头到尾没有边界。"""
    L = chr(10)
    lay = jp('app/src/main/res/layout/player_vod_control_view.xml')
    dr = jp('app/src/main/res/drawable')
    if not os.path.isdir(dr):
        os.makedirs(dr)
    t = read_text(lay)
    if 'tk_gradient_bottom' in t and 'tk_gradient_top' in t:
        log('  = 渐变底板已存在，跳过')
        return

    def shape(angle, sc, cc, ec):
        return ('<?xml version="1.0" encoding="utf-8"?>' + L +
                '<shape xmlns:android="http://schemas.android.com/apk/res/android"' + L +
                '    android:shape="rectangle">' + L +
                '    <gradient' + L +
                '        android:angle="' + str(angle) + '"' + L +
                '        android:type="linear"' + L +
                '        android:startColor="' + sc + '"' + L +
                '        android:centerColor="' + cc + '"' + L +
                '        android:endColor="' + ec + '" />' + L +
                '</shape>')

    # angle 270 = 从上往下，startColor 在顶部：屏幕最上沿最深，往下渐透
    write_text(os.path.join(dr, 'tk_gradient_top.xml'), shape(270, '#B4000000', '#76000000', '#00000000'))
    # angle 90 = 从下往上，startColor 在底部：底栏最下沿最深，往上渐透
    write_text(os.path.join(dr, 'tk_gradient_bottom.xml'), shape(90, '#B8000000', '#78000000', '#00000000'))

    def put_bg(tag, drawable):
        if 'android:background=' in tag:
            import re as _re
            return _re.sub('android:background="[^"]*"', 'android:background="' + drawable + '"', tag, count=1)
        return tag[:-1] + L + '        android:background="' + drawable + '">'

    # 1) 底部菜单整条
    import re
    m = re.search(r'<LinearLayout[^>]*@\+id/bottom_container[^>]*>', t)
    if not m:
        sys.exit('渐变底板锚点丢失：bottom_container')
    nb = put_bg(m.group(0), '@drawable/tk_gradient_bottom')
    t = t[:m.start()] + nb + t[m.end():]

    # 2) 顶部整条（rootView 下第一个 LinearLayout，装片名/分辨率/时间/网速）
    i = t.find('@+id/rootView')
    if i < 0:
        sys.exit('渐变底板锚点丢失：rootView')
    j = t.find('>', i) + 1
    k = t.find('<LinearLayout', j)
    e = t.find('>', k) + 1
    if k < 0 or e <= k:
        sys.exit('渐变底板锚点丢失：顶部行容器')
    nt = put_bg(t[k:e], '@drawable/tk_gradient_top')
    # 文字位置不动，只往下补 24dp 内边距，让渐变带自然延伸，避免"渐变太短像硬边"
    nt = nt[:-1] + L + '        android:paddingBottom="40dp">'
    t = t[:k] + nt + t[e:]

    write_text(lay, t)
    log('顶部/底部整条渐变底板：屏幕边最深 → 往中间渐透，正中不动（方块边界取消）')


def apply_ad_switch_final():
    """设置页「去广告」开关 = M3U8_PURIFY，是唯一总开关。
    之前订阅 json 带 rules 时会无条件 BuiltinAdRules.apply()，虽然 isAd() 内部还有开关判断、
    实际不会误杀，但"关了开关却仍在装规则"这件事本身不干净。这里把它也包进开关判断。"""
    ap = jp('app/src/main/java/com/github/tvbox/osc/api/ApiConfig.java')
    s = read_text(ap)
    if 'tkAdSwitchFinal' in s:
        log('  = 广告开关已收敛到最终判定，跳过')
        return
    L = chr(10)
    old = ('            BuiltinAdRules.apply();' + L +
           '            com.github.tvbox.osc.util.AdRuleUpdater.loadCache();')
    new = ('            // tkAdSwitchFinal：开关是唯一总开关，关掉就一条规则都不装' + L +
           '            if (Hawk.get(HawkConfig.M3U8_PURIFY, true)) {' + L +
           '                BuiltinAdRules.apply();' + L +
           '                com.github.tvbox.osc.util.AdRuleUpdater.loadCache();' + L +
           '            }')
    if s.count(old) != 1:
        sys.exit('广告开关锚点丢失：ApiConfig 订阅规则分支')
    s = s.replace(old, new, 1)
    write_text(ap, s)
    log('广告开关：订阅规则分支也受 M3U8_PURIFY 控制，关闭时零规则加载')


def apply_top_time_fix():
    """右上角"7.93KB 压在 02:28 上"的根因：上一版只把 XML 里 net_play_speed 设了 gone，
    但 VodController 里 1003（隐藏底栏）那段还留着一句 net_play_speed.setVisibility(VISIBLE)，
    只要设置里"屏幕显示"不是关，每次底栏自动隐藏它就会冒出来，和 tv_seek_time 挤在一行。
    同时 1003 只隐藏了左边片名块（mTopRoot1），漏了右边时间块（mTopRoot2），
    所以底栏都收了、右上角时间还挂在画面上。
    这里统一成：右上角 = 当前播放时间 + 系统时间，网速控件一律不显示；显隐跟随底栏。"""
    L = chr(10)
    vp = jp(VOD)
    s = read_text(vp)
    if 'tkTopTimeFix' in s:
        log('  = 右上角时间行已修，跳过')
        return
    Q = ' ' * 24
    # 1) 1002 显示：不再放网速出来
    a = (Q + 'mPlayLoadNetSpeedRightTop.setVisibility(VISIBLE);' + L +
         Q + 'if(Hawk.get(HawkConfig.SCREEN_DISPLAY,GONE)==GONE){' + L +
         Q + '    mPlayPauseTime.setVisibility(VISIBLE);' + L +
         Q + '}else {' + L +
         Q + '    net_play_speed.setVisibility(GONE);' + L +
         Q + '}')
    a2 = (Q + '// tkTopTimeFix：右上角只留播放时间与系统时间，网速控件不显示' + L +
          Q + 'mPlayPauseTime.setVisibility(VISIBLE);' + L +
          Q + 'net_play_speed.setVisibility(GONE);')
    if s.count(a) != 1:
        sys.exit('右上角锚点丢失：1002 网速分支')
    s = s.replace(a, a2, 1)

    # 2) 1003 隐藏：补上右边整块，并且不再把网速放出来
    b = Q + 'mPlayLoadNetSpeedRightTop.setVisibility(GONE);' + L
    b2 = Q + 'mTopRoot2.setVisibility(GONE);' + L
    if s.count(b) != 1:
        sys.exit('右上角锚点丢失：1003 网速 GONE')
    s = s.replace(b, b2, 1)

    c = (Q + 'if(Hawk.get(HawkConfig.SCREEN_DISPLAY,GONE)==GONE){' + L +
         Q + '    mPlayPauseTime.setVisibility(GONE);' + L +
         Q + '}else {' + L +
         Q + '    net_play_speed.setVisibility(VISIBLE);' + L +
         Q + '}')
    c2 = (Q + 'mPlayPauseTime.setVisibility(GONE);' + L +
          Q + 'net_play_speed.setVisibility(GONE);')
    if s.count(c) != 1:
        sys.exit('右上角锚点丢失：1003 时间分支')
    s = s.replace(c, c2, 1)
    write_text(vp, s)
    log('右上角：网速控件不再冒出来，时间块随底栏一起收（原来只收了左边片名块）')


def self_check():
    dax = read_text(jp('app/src/main/java/com/github/tvbox/osc/ui/activity/DetailActivity.java'))
    sh = read_text(jp('app/src/main/java/com/github/tvbox/osc/util/SearchHelper.java'))
    if '勾了就只搜勾的' not in sh:
        sys.exit('搜索源筛选没写入')
    if 'tkForceFullPreview' not in dax or 'windowsPreview = null;' not in dax:
        sys.exit('全屏预览满屏没写入')
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

    # ---- 产物体检：把"该开的功能是否真的写进了树"逐条验一遍，杜绝静默失效 ----
    fails = []
    man = read_text(jp('app/src/main/AndroidManifest.xml'))
    if OPT_APP_ICON:
        if '@mipmap/ic_launcher"' not in man:
            fails.append('manifest 的 android:icon 没指向 @mipmap/ic_launcher')
        if '@mipmap/ic_launcher_round' not in man:
            fails.append('manifest 缺 android:roundIcon')
        if not os.path.isfile(jp('app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml')):
            fails.append('缺 mipmap-anydpi-v26/ic_launcher.xml（加减速机图标）')
        fg = read_text(jp('app/src/main/res/drawable/ic_launcher_foreground.xml'))
        if 'android:scaleX="3.32"' not in fg:
            fails.append('启动图标前景 scale 不是 3.32（三角形尺寸被改回去了）')
        for q in ('mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi'):
            if not os.path.isfile(jp('app/src/main/res/mipmap-%s/ic_launcher.png' % q)):
                fails.append('缺 mipmap-%s/ic_launcher.png' % q)
    if OPT_APP_NAME:
        st = read_text(jp('app/src/main/res/values/strings.xml'))
        if ('<string name="app_name">%s</string>' % APP_NAME) not in st:
            fails.append('app_name 不是 %s' % APP_NAME)
    lay = read_text(jp(LAYOUT))
    for rid in ('play_pre', 'play_next', 'play_retry', 'play_refresh', 'play_scale', 'play_speed',
                'play_player', 'play_time_start', 'play_time_end', 'play_time_reset', 'play_cast',
                'landscape_portrait', 'screen_display'):
        if ('@+id/%s"' % rid) not in lay:
            fails.append('播放布局缺 @+id/%s' % rid)
    if 'play_download' in lay:
        fails.append('播放布局里还留着 play_download（底栏下载按钮没删干净）')
    if '@drawable/tk_space' not in lay:
        fails.append('片头/片尾 汉字没走 drawableTop 占位（底边会与「重置」错开）')
    layroot = ET.parse(jp(LAYOUT)).getroot()
    if 'tk_slot_start' in lay or 'tk_slot_end' in lay:
        fails.append('片头/片尾 的 00:00 时间格没删干净')
    for tid in ('play_time_start', 'play_time_end'):
        v = find_id(layroot, tid)
        if v is None:
            fails.append('播放布局缺 %s' % tid)
            continue
        for par in layroot.iter():
            if par is not v and par.tag != layroot.tag and find_id(par, tid) is not None and par.tag == 'FrameLayout':
                fails.append('%s 还被包在 FrameLayout 里（应直接与「重置」同排）' % tid)
                break
    vc = read_text(jp(VOD))
    for kw in ('tkSelfHeal();', 'tkStopHeal();'):
        if kw not in vc:
            fails.append('VodController 缺 %s（自愈兜底失效或未清理）' % kw)
    if OPT_DOWNLOAD:
        if 'android.permission.WAKE_LOCK' not in man:
            fails.append('manifest 缺 WAKE_LOCK（下载会因息屏断流）')
        pf = read_text(jp('app/src/main/java/com/github/tvbox/osc/ui/fragment/PlayFragment.java'))
        if 'tkShowDownloadDialog()' not in pf:
            fails.append('PlayFragment 缺 tkShowDownloadDialog()（下载入口没了）')
        dlp = jp('app/src/main/java/com/github/tvbox/osc/util/TkDownloader.java')
        if not os.path.isfile(dlp):
            fails.append('TkDownloader.java 未生成')
        else:
            t = read_text(dlp)
            for kw in ('public static void enqueue', 'downloadM3u8', 'AES/CBC', 'getBytesRetry', 'wlOn'):
                if kw not in t:
                    fails.append('TkDownloader 缺 %s' % kw)
    if fails:
        print('  !! 产物体检不通过 %d 项：' % len(fails))
        for f in fails[:20]:
            print('     - ' + f)
        sys.exit(1)
    log('产物体检通过：启动图标 / 应用名 / 底栏结构 / 自愈链 / 下载入口 全部就位')


# ---------------------------------------------------------------- 入口
STEP_STATS = []


def _snap():
    """记录 java/res/manifest 的（大小, mtime），用来判定每一步到底动了什么。"""
    d = {}
    for root in ('app/src/main/java', 'app/src/main/res', 'app/src/main/AndroidManifest.xml'):
        p = jp(root)
        if os.path.isfile(p):
            try:
                st = os.stat(p)
                d[p] = (st.st_size, st.st_mtime_ns)
            except OSError:
                pass
            continue
        for dp, dns, fs in os.walk(p):
            for f in fs:
                fp = os.path.join(dp, f)
                try:
                    st = os.stat(fp)
                except OSError:
                    continue
                d[fp] = (st.st_size, st.st_mtime_ns)
    return d


def _step(name, fn):
    """包一层：打印每步真实改动文件数/耗时；崩溃时把步名和堆栈写进 tk-step-fail.txt。"""
    t0 = time.time()
    s0 = _snap()
    log('▶ ' + name)
    try:
        fn()
    except SystemExit as e:
        print('  !! 步骤主动中止：%s（%s）' % (name, e))
        raise
    except BaseException:
        tb = traceback.format_exc()
        print('  !! 步骤崩溃：%s' % name)
        print(tb)
        try:
            root = os.path.dirname(SRC.rstrip(os.sep))
            write_text(os.path.join(root, 'tk-step-fail.txt'),
                       'VER: %s\nSTEP: %s\n\n%s\n' % (VER, name, tb))
        except Exception:
            pass
        raise SystemExit(1)
    s1 = _snap()
    mod = sum(1 for k, v in s1.items() if k in s0 and s0[k] != v)
    new = sum(1 for k in s1 if k not in s0)
    dl = sum(1 for k in s0 if k not in s1)
    dt = time.time() - t0
    STEP_STATS.append((name, mod, new, dl, dt))
    log('  · 改 %d / 增 %d / 删 %d · %.2fs' % (mod, new, dl, dt))


def main():
    t_all = time.time()
    print('*** 脚本版本 %s ***' % VER)
    print('=== 底部菜单：图标 %s / 汉字 %s / 结构对齐 / 不动内核 ===' % (ICON_SIZE, TEXT_SIZE))
    print('源码：', SRC)
    _step('write_icons', write_icons)
    _step('apply_layout', apply_layout)          # 底座：布局骨架，其余界面改动都挂在它生成的结构上
    _step('apply_top_width', apply_top_width)    # 顶部右栏加宽：修上游 1/4 宽导致的叠字
    _step('apply_fast_start', apply_fast_start)  # 底座：即便强起关闭，也只插入空壳方法供下游作锚点
    if OPT_BTN_TEXT: _step('apply_java', apply_java)
    if OPT_PUSH_BTN: _step('apply_push_button', apply_push_button)
    if OPT_SINGLE_LAYOUT: _step('apply_single_layout', apply_single_layout)
    if OPT_APP_NAME: _step('apply_app_name', apply_app_name)
    if OPT_APP_ICON: _step('apply_app_icon', apply_app_icon)
    # apply_top_fix() 已撤：尺寸节流不在保留清单内，全部回上游
    if OPT_TOPBAR_TRANSPARENT: _step('apply_top_transparent', apply_top_transparent)
    if OPT_TEXT_STROKE: _step('apply_text_stroke', apply_text_stroke)
    if OPT_STATIC_UI: _step('apply_static_ui', apply_static_ui)
    if OPT_SLOT_ALIGN: _step('apply_slot_align', apply_slot_align)
    if OPT_BTN_WHITELIST: _step('apply_btn_whitelist', apply_btn_whitelist)
    if OPT_BTN_GUARD: _step('apply_btn_guard', apply_btn_guard)
    if OPT_PAUSE_KEEP: _step('apply_pause_keep', apply_pause_keep)
    _step('apply_ad_safety', apply_ad_safety)
    _step('apply_speed_fix', apply_speed_fix)
    _step('apply_ad_replay', apply_ad_replay)
    if OPT_DANMU_ALPHA: _step('apply_danmu_alpha', apply_danmu_alpha)
    if OPT_DANMU_DOUBLE: _step('apply_danmu_doubletap', apply_danmu_doubletap)
    if OPT_GRADIENT_BG: _step('apply_gradient_bg', apply_gradient_bg)
    if OPT_SCRIM_BG: _step('apply_scrim_bg', apply_scrim_bg)
    if OPT_SCREEN_ON: _step('apply_screen_default', apply_screen_default)
    if OPT_AD_SWITCH: _step('apply_ad_switch_final', apply_ad_switch_final)
    if OPT_RENDER_FIX: _step('apply_render_fix', apply_render_fix)
    if OPT_DNS_DEFAULT: _step('apply_dns_default', apply_dns_default)
    if OPT_TOP_TIME_FIX: _step('apply_top_time_fix', apply_top_time_fix)
    if OPT_DOWNLOAD: _step('apply_download', apply_download)
    if OPT_SEARCH_BOOST: _step('apply_search_boost', apply_search_boost)
    if OPT_SPACING: _step('apply_spacing', apply_spacing)
    _step('apply_download_anywhere', apply_download_anywhere)
    _step('apply_full_preview_fix', apply_full_preview_fix)
    _step('apply_search_source_fix', apply_search_source_fix)
    _step('apply_parse_hardening', apply_parse_hardening)
    _step('self_check', self_check)
    print('-' * 46)
    print('步骤明细（改=修改已有文件，增/删=文件数）：')
    for name, mo, ne, de, dt in STEP_STATS:
        print('  %-26s 改%-3d 增%-3d 删%-3d %6.2fs' % (name, mo, ne, de, dt))
    zero = [n for n, mo, ne, de, dt in STEP_STATS if mo + ne + de == 0]
    if zero:
        print('  注意：以下步骤 0 改动，若它本应生效，说明锚点漂移了 —— ' + '、'.join(zero))
    print('总耗时 %.1fs' % (time.time() - t_all))
    print('=' * 46)
    print('=== 完成 ===')


if __name__ == '__main__':
    main()
