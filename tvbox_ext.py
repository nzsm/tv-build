#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import glob
import shutil
import xml.etree.ElementTree as ET

# ===================== 配置区 =====================
BASE_DIR = os.getcwd()
RES_PATH = os.path.join(BASE_DIR, "app/src/main/res")
LAYOUT_PATH = os.path.join(RES_PATH, "layout")
JAVA_PATH = os.path.join(BASE_DIR, "app/src/main/java")
VOD_CONTROL_XML = os.path.join(LAYOUT_PATH, "player_vod_control_view.xml")
VOD_CONTROLLER_JAVA = None
for fp in glob.glob(os.path.join(JAVA_PATH, "**/VodController.java"), recursive=True):
    VOD_CONTROLLER_JAVA = fp
    break

# 投屏图标资源
CAST_DRAWABLE_NAME = "ic_cast_tv"
CAST_DRAWABLE_XML = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M21,3H3C1.9,3 1,3.9 1,5v12c0,1.1 0.9,2 2,2h5v2h8v-2h5c1.1,0 2,-0.9 2,-2V5C23,3.9 22.1,3 21,3zM21,17H3V5h18V17zM5,14v2h2c0,-1.11 -0.89,-2 -2,-2zM5,11v2c2.21,0 4,1.79 4,4h2c0,-3.31 -2.69,-6 -6,-6z"/>
</vector>
"""

# 自动补齐缺失dimen
def auto_fix_dimen():
    dimen_file = os.path.join(RES_PATH, "values/dimens.xml")
    if not os.path.exists(dimen_file):
        return
    with open(dimen_file, "r", encoding="utf-8") as f:
        dimen_text = f.read()
    # 扫描所有vs_xx
    used_dimen = set()
    for xmlf in glob.glob(os.path.join(LAYOUT_PATH, "*.xml")) + glob.glob(os.path.join(RES_PATH, "drawable/*.xml")):
        try:
            with open(xmlf, "r", encoding="utf-8") as f:
                txt = f.read()
            matches = re.findall(r"@dimen/(vs_\d+)", txt)
            for m in matches:
                used_dimen.add(m)
        except:
            continue
    for item in used_dimen:
        if item in dimen_text:
            continue
        num = re.search(r"vs_(\d+)", item).group(1)
        insert_line = f'    <dimen name="{item}">{num}mm</dimen>\n'
        dimen_text = re.sub(r"(</resources>)", insert_line + r"\1", dimen_text)
    with open(dimen_file, "w", encoding="utf-8") as f:
        f.write(dimen_text)

# 写入投屏drawable
def add_cast_icon():
    dr_path = os.path.join(RES_PATH, "drawable", f"{CAST_DRAWABLE_NAME}.xml")
    os.makedirs(os.path.dirname(dr_path), exist_ok=True)
    with open(dr_path, "w", encoding="utf-8") as f:
        f.write(CAST_DRAWABLE_XML)

# 修改布局：底部按钮栏末尾增加投屏按钮，根容器默认GONE消除一闪
def modify_layout():
    if not os.path.exists(VOD_CONTROL_XML):
        print("player_vod_control_view.xml not found, skip layout modify")
        return
    with open(VOD_CONTROL_XML, "r", encoding="utf-8") as f:
        xml_txt = f.read()
    # 根容器默认 gone，解决加载一闪
    xml_txt = re.sub(r'(android:visibility="visible")', r'android:visibility="gone"', xml_txt)
    xml_txt = re.sub(r'(android:visibility="invisible")', r'android:visibility="gone"', xml_txt)
    # 找到HorizontalScrollView里面的LinearLayout按钮容器末尾追加投屏按钮
    cast_btn = '''
        <LinearLayout
            android:id="@+id/v_cast"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:gravity="center"
            android:orientation="vertical"
            android:padding="@dimen/vs_8">
            <ImageView
                android:layout_width="@dimen/vs_40"
                android:layout_height="@dimen/vs_40"
                android:src="@drawable/ic_cast_tv"/>
            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="投屏"
                android:textColor="#ffffff"
                android:textSize="@dimen/ts_12"/>
        </LinearLayout>'''
    # 匹配按钮容器闭合标签
    xml_txt = re.sub(r"(\s*</LinearLayout>\s*</HorizontalScrollView>)", cast_btn + r"\1", xml_txt, count=1)
    with open(VOD_CONTROL_XML, "w", encoding="utf-8") as f:
        f.write(xml_txt)

# 修改VodController.java：只绑定投屏按钮，其余全部不动，删掉所有自定义时间/暂停面板注入
def modify_vod_controller():
    if not VOD_CONTROLLER_JAVA or not os.path.exists(VOD_CONTROLLER_JAVA):
        print("VodController.java not found, skip java bind")
        return
    with open(VOD_CONTROLLER_JAVA, "r", encoding="utf-8") as f:
        java_code = f.read()
    # 增加投屏控件声明
    if "private LinearLayout mCastBtn;" not in java_code:
        java_code = re.sub(r"(public class VodController extends BaseController \{)", r"\1\n    private LinearLayout mCastBtn;", java_code, count=1)
    # 在initView里面增加findViewById和点击事件
    bind_code = '''
        mCastBtn = findViewById(R.id.v_cast);
        if(mCastBtn != null){
            mCastBtn.setOnClickListener(v -> {
                // 投屏跳转逻辑，这里预留，不额外加复杂代码
                try{
                    if(mControlWrapper != null){
                        mControlWrapper.cast();
                    }
                }catch (Exception e){
                    e.printStackTrace();
                }
            });
        }'''
    # 找到initView内部末尾插入，不改动原有任何其他绑定
    java_code = re.sub(r"(\s*\}\s*// end initView marker|void initView\(\)\s*\{)", r"\1\n" + bind_code, java_code, count=1)
    # 清理之前所有我们注入的北京时间、影片剩余、tv_pause_container相关代码
    clean_patterns = [
        r"//=====CUSTOM_TIME_START.*?//=====CUSTOM_TIME_END",
        r"//=====PAUSE_PANEL_START.*?//=====PAUSE_PANEL_END",
        r"tv_time_end.*?setText.*?;",
        r"tv_sys_time.*?setText.*?;",
        r"ll_pause.*?setVisibility.*?;",
    ]
    for pat in clean_patterns:
        java_code = re.sub(pat, "", java_code, flags=re.DOTALL)
    with open(VOD_CONTROLLER_JAVA, "w", encoding="utf-8") as f:
        f.write(java_code)

def main():
    print("===== tvbox_ext start, only add cast, keep takagen original player ui =====")
    auto_fix_dimen()
    add_cast_icon()
    modify_layout()
    modify_vod_controller()
    print("===== tvbox_ext finished, no extra custom time / pause panel code =====")

if __name__ == "__main__":
    main()
