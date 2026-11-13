# tvbox_ext.py 【阶段1：布局调整版】
# 保留：DNS、去广告
# 新增：底部播放栏布局参数（间距、大小、文字紧贴、扁字、居中不越进度条）
# 不新增自定义图标、不加时间控件，图标全部takagen原版
import os
import re

BASE = "app/src/main"
RES = f"{BASE}/res"
JAVA = f"{BASE}/java"

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
        # 修改滚动容器：水平居中，控制总宽度不超出进度条
        content = re.sub(r'<HorizontalScrollView[^>]*>',
            r'<HorizontalScrollView android:layout_width="match_parent" android:layout_height="wrap_content" android:gravity="center_horizontal" android:paddingHorizontal="8dp">',
            content)
        # 修改按钮item：图标26dp、文字8sp、图标文字间距0dp、关闭字体内边距、文字横向1.1扁化
        item_pattern = r'<LinearLayout[^>]*android:orientation="vertical"'
        item_new = '''<LinearLayout android:orientation="vertical" android:layout_width="wrap_content" android:layout_height="wrap_content" android:padding="3dp">
<ImageView android:layout_width="26dp" android:layout_height="26dp" android:layout_gravity="center_horizontal"/>
<TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:textSize="8sp" android:includeFontPadding="false" android:textScaleX="1.1" android:layout_gravity="center_horizontal"/>'''
        content = re.sub(item_pattern, item_new, content)
        open(layout_file, "w", encoding="utf-8").write(content)
    print("[+] 播放栏布局注入完成")

def main():
    print("===== 阶段1 启动：仅布局调整，原版图标、无时间 =====")
    inject_base()
    inject_player_layout()
    print("===== 阶段1脚本执行完毕，等待编译 =====")

if __name__ == "__main__":
    main()
