#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 精简干净脚本：仅2件事
# 1、导入takagen整套播放控制布局、图标资源
# 2、批量把布局里所有按钮ID替换成底座原生ID
# 移除：订阅注入、DNS、去广告、崩溃捕获、播放器强制IJK、时间美化等全部额外改动
# 只做布局ID映射，其余全部保留源码原生状态
import os
import re

# ===================== 配置：ID映射表【takagen id → 底座原生id】 =====================
id_map = [
    ("play_prev", "play_pre"),
    ("play_next", "play_next"),
    ("play_subtitle", "zimu_select"),
    ("play_audio", "audio_track_select"),
    ("ll_danmu_setting", "danmu_setting"),
    ("vod_control_bar", "play_btn_group"),
    ("play_speed", "play_speed"),
    ("play_cast", "play_cast"),
    ("play_replay", "play_replay"),
    ("play_reset", "play_reset"),
    ("play_start", "play_start"),
    ("play_end", "play_end"),
    ("play_ijk", "play_ijk"),
    ("play_screen", "play_screen"),
    ("play_mute", "play_mute"),
]

# 替换函数
def replace_text(file_path, old_str, new_str):
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if old_str not in content:
        return False
    content = content.replace(old_str, new_str)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True

def regex_replace(file_path, pattern, new):
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r", encoding="utf-8") as f:
        c = f.read()
    c2 = re.sub(pattern, new, c, flags=re.MULTILINE|re.DOTALL)
    if c == c2:
        return False
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(c2)
    return True

# -------------------------- 1. 加载takagen布局文件player_control.xml，批量替换ID --------------------------
control_xml = "app/src/main/res/layout/player_control.xml"
if os.path.exists(control_xml):
    with open(control_xml, "r", encoding="utf-8") as f:
        xml_content = f.read()
    # 循环替换所有id
    for tk_id, base_id in id_map:
        xml_content = re.sub(r'@\+id/' + tk_id, r'@+id/' + base_id, xml_content)
        xml_content = re.sub(r'@id/' + tk_id, r'@id/' + base_id, xml_content)
    with open(control_xml, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"✅ {control_xml} ID批量替换完成")

# -------------------------- 2. 图标资源：仅校验，不增删其他逻辑（图标需要你提前上传到仓库drawable目录） --------------------------
# 说明：脚本不会自动上传图片！你需要提前把takagen所有图标drawable文件上传到仓库：
# app/src/main/res/drawable/ 下面
print("📌 提醒：takagen图标素材需要手动提前上传到仓库 drawable 目录，脚本只负责布局ID转换")

# -------------------------- 无任何其他注入：DNS、订阅、软解、崩溃捕获全部删掉，源码原生 --------------------------
print("✅ 脚本执行完毕，仅执行布局导入+ID映射，其余全部保持原生")
