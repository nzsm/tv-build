# tvbox_ext.py 【阶段2：布局 + 4个自定义图标】
# 保留：DNS、去广告、播放栏布局（居中、间距、紧贴、扁字）
# 新增：重播、字幕三点、倍速码表、屏显四角 四个矢量图标
# 仍然不加入右下角北京时间、剩余/结束时间
import os
import re

BASE = "app/src/main"
RES = f"{BASE}/res"
JAVA = f"{BASE}/java"
DRAWABLE = f"{RES}/drawable"

# 4个自定义矢量图标
ICON_REPLAY = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:pathData="M12,5.4a6.6,6.6 0 1 0 4.8,2.4" android:strokeColor="#FFFFFF" android:strokeWidth="2" android:fillColor="none"/>
    <path android:pathData="M9.9,10.3 L13.2,12 L9.9,13.7 Z" android:strokeColor="#FFFFFF" android:strokeWidth="1.5" android:fillColor="#FFFFFF"/>
</vector>'''

ICON_SUB = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:pathData="M3,7 L21,7 L21,17 L3,17 Z" android:strokeColor="#FFFFFF" android:strokeWidth="2" android:fillColor="none"/>
    <circle android:cx="7.2" android:cy="12" android:r="1.1" android:fillColor="#FFFFFF"/>
    <circle android:cx="12" android:cy="12" android:r="1.1" android:fillColor="#FFFFFF"/>
    <circle android:cx="16.8" android:cy="12" android:r="1.1" android:fillColor="#FFFFFF"/>
</vector>'''

ICON_SPEED = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:pathData="M3.6,16.2 a8.4,8.4 0 0 1 16.8,0" android:strokeColor="#FFFFFF" android:strokeWidth="2" android:fillColor="none"/>
    <path android:pathData="M12,16.2 L16.6,10.4" android:strokeColor="#FFFFFF" android:strokeWidth="2" android:fillColor="none"/>
</vector>'''

ICON_SCREEN = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:pathData="M4,9 V4 H9" android:strokeColor="#FFFFFF" android:strokeWidth="2" android:fillColor="none"/>
    <path android:pathData="M15,4 H20 V9" android:strokeColor="#FFFFFF" android:strokeWidth="2" android:fillColor="none"/>
    <path android:pathData="M20,15 V20 H15" android:strokeColor="#FFFFFF" android:strokeWidth="2" android:fillColor="none"/>
    <path android:pathData="M9,20 H4 V15" android:strokeColor="#FFFFFF" android:strokeWidth="2" android:fillColor="none"/>
</vector>'''

def inject_base():
    print("[+] 注入基础配置：去广告、DNS")
    cfg_path = f"{JAVA}/com/xxx/Config.java"
    if os.path.exists(cfg_path):
        txt = open(cfg_path, "r", encoding="utf-8").read()
        if "DNS_SWITCH" not in txt:
            insert = 'public static boolean DNS_SWITCH = true;\n'
            txt = re.sub(r'(public class Config \{)', r'\1\n    ' + insert, txt)
        open(cfg_path, "w", encoding="utf-8").write(txt)
    print("[+] 基础注入完成")

def inject_player_layout():
    print("[+] 注入播放控制栏布局参数：居中、间距、图标文字紧贴、扁文字")
    layout_file = f"{RES}/layout/player_vod_control_view.xml"
    if os.path.exists(layout_file):
        content = open(layout_file, "r", encoding="utf-8").read()
        content = re.sub(r'<HorizontalScrollView[^>]*>',
            r'<HorizontalScrollView android:layout_width="match_parent" android:layout_height="wrap_content" android:gravity="center_horizontal" android:paddingHorizontal="8dp">',
            content)
        item_pattern = r'<LinearLayout[^>]*android:orientation="vertical"'
        item_new = '''<LinearLayout android:orientation="vertical" android:layout_width="wrap_content" android:layout_height="wrap_content" android:padding="3dp">
<ImageView android:layout_width="26dp" android:layout_height="26dp" android:layout_gravity="center_horizontal"/>
<TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:textSize="8sp" android:includeFontPadding="false" android:textScaleX="1.1" android:layout_gravity="center_horizontal"/>'''
        content = re.sub(item_pattern, item_new, content)
        open(layout_file, "w", encoding="utf-8").write(content)
    print("[+] 播放栏布局注入完成")

def write_icons():
    if not os.path.exists(DRAWABLE):
        os.makedirs(DRAWABLE, exist_ok=True)
    open(f"{DRAWABLE}/ic_replay_custom.xml", "w", encoding="utf-8").write(ICON_REPLAY)
    open(f"{DRAWABLE}/ic_sub_custom.xml", "w", encoding="utf-8").write(ICON_SUB)
    open(f"{DRAWABLE}/ic_speed_custom.xml", "w", encoding="utf-8").write(ICON_SPEED)
    open(f"{DRAWABLE}/ic_screen_custom.xml", "w", encoding="utf-8").write(ICON_SCREEN)
    print("[+] 4个自定义图标写入drawable完成")

def replace_icon_ref():
    print("[+] 替换按钮图标引用为自定义图标")
    layout_file = f"{RES}/layout/player_vod_control_view.xml"
    if os.path.exists(layout_file):
        content = open(layout_file, "r", encoding="utf-8").read()
        content = content.replace('@drawable/v_replay', '@drawable/ic_replay_custom')
        content = content.replace('@drawable/v_subtitle', '@drawable/ic_sub_custom')
        content = content.replace('@drawable/v_ffwd', '@drawable/ic_speed_custom')
        content = content.replace('@drawable/v_screen', '@drawable/ic_screen_custom')
        open(layout_file, "w", encoding="utf-8").write(content)
    print("[+] 图标引用替换完成")

def main():
    print("===== 阶段2 启动：布局 + 4个自定义图标，无时间控件 =====")
    inject_base()
    inject_player_layout()
    write_icons()
    replace_icon_ref()
    print("===== 阶段2脚本执行完毕，等待编译 =====")

if __name__ == "__main__":
    main()
