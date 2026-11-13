# tvbox_ext.py 【精简测试版A】用于排错
import os
import re
import shutil

BASE = "app/src/main"
RES = f"{BASE}/res"
JAVA = f"{BASE}/java"

# 基础注入：广告、DNS，不碰播放器布局、时间、自定义图标
def inject_base():
    print("[+] 注入基础配置：去广告、DNS")
    cfg_path = f"{JAVA}/com/xxx/Config.java"
    if os.path.exists(cfg_path):
        txt = open(cfg_path, "r", encoding="utf-8").read()
        # DNS开关注入
        if "DNS_SWITCH" not in txt:
            insert = 'public static boolean DNS_SWITCH = true;\n'
            txt = re.sub(r'(public class Config \{)', r'\1\n    ' + insert, txt)
        open(cfg_path, "w", encoding="utf-8").write(txt)
    print("[+] 基础注入完成")

def main():
    print("===== 精简测试版A启动（无播放器UI、无自定义图标、无时间控件） =====")
    inject_base()
    print("===== 脚本执行完毕 =====")
    print("说明：本版本只保留基础功能，播放器UI全部不改动，用来验证编译是否正常")

if __name__ == "__main__":
    main()
