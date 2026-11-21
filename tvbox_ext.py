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
            '<path android:pathData="M16.48 2.52c3.27 1.55 5.61 4.72 5.97 8.48h1.5C23.44 4.84 18.29 0 12 0l-.66.03 3.81 3.81 1.33-1.32z" android:fillColor="#FFFFFF" android:strokeColor="#FFFFFF" android:strokeWidth="0.8" android:strokeLineJoin="round"/>'
            '<path android:pathData="M10.23 1.75c-.59-.59-1.54-.59-2.12 0L1.75 8.11c-.59.59-.59 1.54 0 2.12l12.02 12.02c.59.59 1.54.59 2.12 0l6.36-6.36c.59-.59.59-1.54 0-2.12L10.23 1.75m4.6 19.44L2.81 9.17l6.36-6.36 12.02 12.02-6.36 6.36z" android:fillColor="#FFFFFF" android:strokeColor="#FFFFFF" android:strokeWidth="0.8" android:strokeLineJoin="round"/>'
            '<path android:pathData="M7.52 22.25C4.25 19.94 1.91 16.76 1.55 13H.05C.56 19.16 5.71 24 12 24l.66-.03-3.81-3.81-1.33 1.32z" android:fillColor="#FFFFFF" android:strokeColor="#FFFFFF" android:strokeWidth="0.8" android:strokeLineJoin="round"/>'
            '</vector>')

ICONS = {'htov': HTVO_XML, 'v_prev': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="11.950" android:pivotY="10.575" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.050" android:translateY="1.425"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.826" android:scaleY="1.826"\n        android:translateX="-0.045" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M7,6c0.55,0 1,0.45 1,1v10c0,0.55 -0.45,1 -1,1s-1,-0.45 -1,-1L6,7c0,-0.55 0.45,-1 1,-1zM10.66,12.82l5.77,4.07c0.66,0.47 1.58,-0.01 1.58,-0.82L18.01,7.93c0,-0.81 -0.91,-1.28 -1.58,-0.82l-5.77,4.07c-0.57,0.4 -0.57,1.24 0,1.64z"/></group></group></vector>', 'v_next': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.833" android:scaleY="1.833"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M7.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L7.58,7.11C6.91,6.65 6,7.12 6,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM16,7v10c0,0.55 0.45,1 1,1s1,-0.45 1,-1V7c0,-0.55 -0.45,-1 -1,-1s-1,0.45 -1,1z"/></group></group></vector>', 'v_replay': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="11.975" android:pivotY="10.575" android:scaleX="0.9929" android:scaleY="0.9929" android:translateX="0.025" android:translateY="1.425"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.136" android:scaleY="1.136"\n        android:translateX="-0.057" android:translateY="-1.123"><path android:fillColor="@android:color/white" android:pathData="M12,5V2.21c0,-0.45 -0.54,-0.67 -0.85,-0.35l-3.8,3.79c-0.2,0.2 -0.2,0.51 0,0.71l3.79,3.79c0.32,0.31 0.86,0.09 0.86,-0.36V7c3.73,0 6.68,3.42 5.86,7.29 -0.47,2.27 -2.31,4.1 -4.57,4.57 -3.57,0.75 -6.75,-1.7 -7.23,-5.01 -0.07,-0.48 -0.49,-0.85 -0.98,-0.85 -0.6,0 -1.08,0.53 -1,1.13 0.62,4.39 4.8,7.64 9.53,6.72 3.12,-0.61 5.63,-3.12 6.24,-6.24C20.84,9.48 16.94,5 12,5z"/></group></group></vector>', 'v_replay_play': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="24" android:viewportHeight="24"\n    android:tint="#FFFFFF"><group android:pivotX="11.925" android:pivotY="10.875" android:scaleX="1.1382" android:scaleY="1.1382" android:translateX="0.075" android:translateY="1.125"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.136" android:scaleY="1.136"\n        android:translateX="-0.057" android:translateY="-1.123"><path android:strokeColor="@android:color/white" android:strokeWidth="2.2" android:fillColor="@android:color/transparent" android:pathData="M12,5 A7,7 0 1 1 11.99,5"/><path android:fillColor="@android:color/white" android:pathData="M9.85,8.4 L16.25,12.0 L9.85,15.6 Z"/></group></group></vector>', 'v_aspect': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M18,12c-0.55,0 -1,0.45 -1,1v2h-2c-0.55,0 -1,0.45 -1,1s0.45,1 1,1h3c0.55,0 1,-0.45 1,-1v-3c0,-0.55 -0.45,-1 -1,-1zM7,9h2c0.55,0 1,-0.45 1,-1s-0.45,-1 -1,-1L6,7c-0.55,0 -1,0.45 -1,1v3c0,0.55 0.45,1 1,1s1,-0.45 1,-1L7,9zM21,3L3,3c-1.1,0 -2,0.9 -2,2v14c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2zM20,19.01L4,19.01c-0.55,0 -1,-0.45 -1,-1L3,5.99c0,-0.55 0.45,-1 1,-1h16c0.55,0 1,0.45 1,1v12.02c0,0.55 -0.45,1 -1,1z"/></group></group></vector>', 'v_ffwd': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.309" android:scaleY="1.309"\n        android:translateX="-0.523" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M5.58,16.89l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63L5.58,7.11C4.91,6.65 4,7.12 4,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82zM13,7.93v8.14c0,0.81 0.91,1.28 1.58,0.82l5.77,-4.07c0.56,-0.4 0.56,-1.24 0,-1.63l-5.77,-4.07c-0.67,-0.47 -1.58,0 -1.58,0.81z"/></group></group></vector>', 'v_type': '<vector android:height="26dp"\n    android:tint="#FFFFFF"\n    android:viewportHeight="24"\n    android:viewportWidth="24"\n    android:width="26dp"\n    xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M21,3L3,3c-1.11,0 -2,0.89 -2,2v12c0,1.1 0.89,2 2,2h5v2h8v-2h5c1.1,0 1.99,-0.9 1.99,-2L23,5c0,-1.11 -0.9,-2 -2,-2zM21,17L3,17L3,5h18v12zM16,11l-7,4L9,7z" /></group></group></vector>', 'v_subtitle': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.1" android:scaleY="1.1"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M20,4L4,4c-1.1,0 -2,0.9 -2,2v12c0,1.1 0.9,2 2,2h16c1.1,0 2,-0.9 2,-2L22,6c0,-1.1 -0.9,-2 -2,-2zM4,12h4v2L4,14v-2zM14,18L4,18v-2h10v2zM20,18h-4v-2h4v2zM20,14L10,14v-2h10v2z"/></group></group></vector>', 'v_audio': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9906" android:scaleY="0.9906" android:translateX="0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.222" android:scaleY="1.222"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M12,5v8.55c-0.94,-0.54 -2.1,-0.75 -3.33,-0.32 -1.34,0.48 -2.37,1.67 -2.61,3.07 -0.46,2.74 1.86,5.08 4.59,4.65 1.96,-0.31 3.35,-2.11 3.35,-4.1V7h2c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2h-2c-1.1,0 -2,0.9 -2,2z"/></group></group></vector>', 'v_danmu': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp"\n    android:height="26dp"\n    android:viewportWidth="436"\n    android:viewportHeight="419"><group android:pivotX="218.000" android:pivotY="185.058" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="24.442"><group android:pivotX="218.0" android:pivotY="209.5"\n        android:scaleX="0.916" android:scaleY="0.916"\n        android:translateX="0.0" android:translateY="-25.507"><path\n      android:pathData="M322.65,272.14L274.13,272.14L274.13,290.36L328.16,290.36L328.16,318.2L274.13,318.2L274.13,347.96L242.96,347.96L242.96,318.2L188.7,318.2L188.7,290.36L242.96,290.36L242.96,272.14L194.21,272.14L194.21,147.1L216.3,147.1L209.39,129.82L238.16,129.82L245.13,147.1L271.73,147.1L278.7,129.82L307.53,129.82L300.32,147.1L322.88,147.1L322.65,272.14ZM115.05,189.58L152.26,189.58L152.26,164.62L110.25,164.62L110.25,135.09L182.96,135.09L182.96,218.35L143.59,218.35L142.18,244.78L184.66,244.78L177.92,347.02L117.22,347.02L117.22,316.79L148.39,316.79L151.79,273.55L110.25,273.55L115.05,189.58ZM244.89,243.08L244.89,223.16L222.81,223.16L222.81,243.08L244.89,243.08ZM244.89,195.79L244.89,176.11L222.81,176.11L222.81,195.79L244.89,195.79ZM294.06,243.08L294.06,223.16L272.02,223.16L272.02,243.08L294.06,243.08ZM294.06,195.79L294.06,176.11L272.02,176.11L272.02,195.79L294.06,195.79Z"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"/><path\n      android:pathData="M20.27,79.27Q0.5,99.04 0.5,127L0.5,351Q0.5,378.96 20.27,398.73Q40.04,418.5 68,418.5L368,418.5Q395.96,418.5 415.73,398.73Q435.5,378.96 435.5,351L435.5,127Q435.5,99.04 415.73,79.27Q395.96,59.5 368,59.5L68,59.5Q40.04,59.5 20.27,79.27ZM35.5,351L35.5,127Q35.5,113.54 45.02,104.02Q54.54,94.5 68,94.5L368,94.5Q381.46,94.5 390.98,104.02Q400.5,113.54 400.5,127L400.5,351Q400.5,364.46 390.98,373.98Q381.46,383.5 368,383.5L68,383.5Q54.54,383.5 45.02,373.98Q35.5,364.46 35.5,351Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FCFCFC"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/><path\n      android:pathData="M208.26,55.63L128.98,0.62L109.02,29.38L188.31,84.39Q201.24,93.36 216.98,93.4Q232.71,93.44 245.69,84.53L325.91,29.42L306.09,0.57L225.87,55.68Q221.89,58.41 217.06,58.4Q212.23,58.39 208.26,55.63Z"\n      android:strokeLineJoin="miter"\n      android:strokeWidth="35"\n      android:fillColor="#FFFFFF"\n      android:fillType="evenOdd"\n      android:strokeLineCap="butt"/></group></group></vector>', 'v_back': '<vector android:autoMirrored="true" android:height="26dp"\n    android:tint="#FFFFFF" android:viewportHeight="24"\n    android:viewportWidth="24" android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.575" android:scaleX="0.9929" android:scaleY="0.9929" android:translateX="0.000" android:translateY="1.425"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.169" android:scaleY="1.169"\n        android:translateX="0.468" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M16.62,2.99c-0.49,-0.49 -1.28,-0.49 -1.77,0L6.54,11.3c-0.39,0.39 -0.39,1.02 0,1.41l8.31,8.31c0.49,0.49 1.28,0.49 1.77,0s0.49,-1.28 0,-1.77L9.38,12l7.25,-7.25c0.48,-0.48 0.48,-1.28 -0.01,-1.76z"/></group></group></vector>', 'ic_clock': '<vector android:height="26dp" android:tint="#FFFFFF"\n    android:viewportHeight="24" android:viewportWidth="24"\n    android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9906" android:scaleY="0.9906" android:translateX="-0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.047" android:scaleY="1.047"\n        android:translateX="-0.262" android:translateY="-1.31"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M11,8H13V14H11V8M12,20C8.13,20 5,16.87 5,13S8.13,6 12,6 19,9.13 19,13C19.7,13 20.36,13.13 21,13.35C21,13.23 21,13.12 21,13C21,10.88 20.26,8.93 19.03,7.39L20.45,5.97C20,5.46 19.55,5 19.04,4.56L17.62,6C16.07,4.74 14.12,4 12,4C7.03,4 3,8.03 3,13S7.03,22 12,22C12.59,22 13.16,21.94 13.71,21.83C13.4,21.25 13.18,20.6 13.08,19.91C12.72,19.96 12.37,20 12,20M15,1H9V3H15V1M16.5,16.5V21.5H21.5V16.5H16.5Z"/></group></group></vector>', 'play_skip': '<vector android:height="26dp" android:viewportHeight="1000"\n    android:viewportWidth="1000" android:width="26dp" xmlns:android="http://schemas.android.com/apk/res/android"><group android:pivotX="500.000" android:pivotY="423.958" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="76.042"><group android:pivotX="500.0" android:pivotY="500.0"\n        android:scaleX="0.932" android:scaleY="0.932"\n        android:translateX="0.0" android:translateY="-76.375"><path android:fillColor="#FFFFFFFF" android:pathData="M10,499.5c0,301.7 0.3,319.9 4.5,316.5C24,808.3 345.7,501.9 345.7,500.3c0,-0.8 -75.3,-73.4 -167.7,-161.1L10,179.6L10,499.5z"/><path android:fillColor="#FFFFFFFF" android:pathData="M414.1,498.9c0,203.1 1.1,319.9 2.6,319.4c2.6,-0.8 335.5,-316.2 335.5,-318c0,-0.5 -234,-223.5 -328.1,-312.5l-10,-9.3L414.1,498.9z"/><path android:fillColor="#FFFFFFFF" android:pathData="M820.9,500.5l0,321l84.5,-0L990,821.5L990,500.5l0,-320.9l-84.5,-0l-84.5,-0L820.9,500.5z"/></group></group></vector>', 'tk_unlock': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp"\n    android:height="26dp"\n    android:tint="#FFFFFF"\n    android:viewportWidth="24"\n    android:viewportHeight="24"><group android:pivotX="12.000" android:pivotY="10.600" android:scaleX="0.9906" android:scaleY="0.9906" android:translateX="-0.000" android:translateY="1.400"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.047" android:scaleY="1.047"\n        android:translateX="0.0" android:translateY="-1.31"><path\n        android:fillColor="@android:color/white"\n        android:pathData="M18,8h-1L17,6c0,-2.76 -2.24,-5 -5,-5S7,3.24 7,6h2c0,-1.66 1.34,-3 3,-3s3,1.34 3,3v2L6,8c-1.1,0 -2,0.9 -2,2v10c0,1.1 0.9,2 2,2h12c1.1,0 2,-0.9 2,-2L20,10c0,-1.1 -0.9,-2 -2,-2zM18,20L6,20L6,10h12v10zM12,17c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2z" /></group></group></vector>', 'v_cast': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="24" android:viewportHeight="24"\n    android:tint="#FFFFFF"><group android:pivotX="12.000" android:pivotY="10.175" android:scaleX="0.9545" android:scaleY="0.9545" android:translateX="0.000" android:translateY="1.825"><group android:pivotX="12.0" android:pivotY="12.0"\n        android:scaleX="1.0" android:scaleY="1.0"\n        android:translateX="0.0" android:translateY="-1.833"><path android:fillColor="@android:color/white" android:pathData="M1,18v3h3c0,-1.66 -1.34,-3 -3,-3zM1,14v2c2.76,0 5,2.24 5,5h2c0,-3.87 -3.13,-7 -7,-7zM1,10v2c4.97,0 9,4.03 9,9h2c0,-6.08 -4.93,-11 -11,-11zM21,3L3,3c-1.1,0 -2,0.9 -2,2v3h2L3,5h18v14h-7v2h7c1.1,0 2,-0.9 2,-2L23,5c0,-1.1 -0.9,-2 -2,-2z"/></group></group></vector>', 'tk_space': '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="26dp" android:height="26dp"\n    android:viewportWidth="26" android:viewportHeight="26"><path android:fillColor="#00000000" android:pathData="M0,0 L26,0 L26,26 L0,26 Z" /></vector>'}


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
    for rel, inset, minw, rowpad in (('values', '0dp', '0dp', '35dp'), ('values-port', '0dp', '0dp', '5dp')):
        d = os.path.join(SRC, 'app/src/main/res', rel)
        os.makedirs(d, exist_ok=True)
        xml = ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
               + '    <dimen name="tk_seek_inset">' + inset + '</dimen>\n'
               + '    <dimen name="tk_time_minw">' + minw + '</dimen>\n'
               + '    <dimen name="tk_time_ts">' + ('16dp' if rel == 'values' else '10dp') + '</dimen>\n'
               + '    <dimen name="tk_row_pad_lr">' + rowpad + '</dimen>\n'
               + '    <dimen name="tk_time_gap">' + ('0.5dp' if rel == 'values' else '0.6dp') + '</dimen>\n'
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
     'mCurrentTime.setText(tkSeekTime(safeTimeMs(newPosition)));'),
    ('mCurrentTime.setText(stringForTime(position));',
     'mCurrentTime.setText(tkSeekTime(position));'),
    ('mTotalTime.setText(stringForTime(duration));',
     'mTotalTime.setText(tkSeekTime(duration));'),
    ('Toast.makeText(getContext(), "已移除视频广告 "+M3u8.currentAdCount+" 条", Toast.LENGTH_SHORT).show();',
     '// 静默：不再弹出广告过滤条数提示'),
]

HELPERS = '''
    // 竖屏只到分钟：00:17（横屏保持 hh:mm:ss）
    private String tkSeekTime(long timeMs) {
        int w = getWidth(), h = getHeight();
        if (w > 0 && h > w) {
            if (timeMs < 0) timeMs = 0;
            long total = timeMs / 1000;
            long m = total / 60;
            long sec = total % 60;
            return String.format("%02d:%02d", m, sec);
        }
        return formatHMS(timeMs);
    }

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
                if (s.contains("搜") || s.contains("视轨") || s.contains("推送") || s.contains("Zx") || s.contains("ZX")) {
                    g.removeView(c);
                    continue;
                }
            }
            purgeSearchViews(c);
        }
    }

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

BUILTIN_STREAM_RE = ['#EXT-X-DISCONTINUITY[^#]*#EXTINF[^#]*adjump', '#EXT-X-DISCONTINUITY[^#]*#EXTINF[^#]*p1ayer', '#EXTINF:\s*([0-4]\.\d+|5\.0),.*?(\/ad\/|_ad_|preroll|midroll|postroll)']

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
    t = read_text(jp(VOD))

    for old, new in TIME_PATCH:
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
          '                    mPlayerConfig.put("st",current/1000);\n'
          '                    Toast.makeText(getContext(), "片头已设为 " + stringForTime(current), Toast.LENGTH_SHORT).show();')
    if a1 not in t:
        sys.exit('锚点丢失：片头点击')
    t = t.replace(a1, b1, 1)

    a2 = ('                    if (current < duration / 2) return;\n'
          '                    mPlayerConfig.put("et", (duration - current)/1000);')
    b2 = ('                    if (current < duration / 2) return;\n'
          '                    mPlayerConfig.put("et", (duration - current)/1000);\n'
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

    # (1) 默认 ads 字面量：只留国内影视仓真实出现的 3 个（海外联盟对国内源无效）
    i0 = h.find('\\"ads\\":[')
    i1 = h.find(']}', i0)
    assert i0 > 0 and i1 > i0, '锚点丢失：ads 字面量'
    ADS_LIT = r'''\"mimg.0c1q0l.cn\",\"mc.usihnbcq.cn\",\"mg.g1mm3d.cn\"'''
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

    a5 = '                    String ijk = mPlayerConfig.getString("ijk");'
    if a5 in t:
        t = t.replace(a5, '                    if (mPlayerConfig.getInt("pl") != 1) {' + NL
                      + '                        try { hideBottom(); } catch (Throwable ignored) {}' + NL
                      + '                        return;' + NL
                      + '                    }' + NL
                      + a5, 1)
        log('硬解按钮：非 IJK 播放器下点击无效')
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

def apply_danmu_alpha():
    """弹幕透明度下限从 10% 放宽到 0%（彻底看不见，但仍算开启）"""
    h = jp('app/src/main/java/com/github/tvbox/osc/util/DanmuHelper.java')
    if not os.path.isfile(h):
        sys.exit('找不到 DanmuHelper.java')
    t = read_text(h)
    old = 'Hawk.put(HawkConfig.DANMU_ALPHA, Math.max(0.1f, Math.min(alpha, 1.0f)));'
    if old not in t:
        sys.exit('锚点丢失：DanmuHelper.setAlpha')
    t = t.replace(old, 'Hawk.put(HawkConfig.DANMU_ALPHA, Math.max(0f, Math.min(alpha, 1.0f)));', 1)
    write_text(h, t)

    d = jp('app/src/main/java/com/github/tvbox/osc/ui/dialog/DanmuSettingDialog.java')
    if not os.path.isfile(d):
        sys.exit('找不到 DanmuSettingDialog.java')
    dt = read_text(d)
    old2 = '            if (alpha.get() <= 10) return;'
    if old2 not in dt:
        sys.exit('锚点丢失：透明度减档下限')
    dt = dt.replace(old2, '            if (alpha.get() <= 0) return;', 1)
    write_text(d, dt)
    log('弹幕透明度：下限 10% -> 0%（0% 时彻底不可见）')


def apply_danmu_doubletap():
    """弹幕按钮：双击 = 持久关闭；开启时图标左下角带小对号"""
    NL = chr(10)
    v = read_text(jp(VOD))

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
    apply_danmu_alpha()
    apply_danmu_doubletap()
    self_check()
    print('-' * 46)
    print('=== 完成 ===')


if __name__ == '__main__':
    main()
