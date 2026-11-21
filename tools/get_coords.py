"""
鼠标坐标探测器
================

把鼠标移到目标按钮上，读这行数字，填进 config.json 就行。

用法：
    python tools/get_coords.py

按 Ctrl+C 退出。
"""

import sys
import time

try:
    import pyautogui
except ImportError:
    sys.exit("缺少依赖，请先执行：pip install pyautogui")


def main():
    print("🎯 鼠标坐标探测器")
    print("👉 把鼠标移到目标按钮上，屏幕上会实时显示坐标")
    print("   （按 Ctrl+C 退出）\n")

    try:
        while True:
            x, y = pyautogui.position()
            print(f"\r当前坐标：X = {x:5d},  Y = {y:5d}", end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        x, y = pyautogui.position()
        print(f"\n\n✅ 最后记录：X = {x}, Y = {y}")
        print("   把这两个数字填进 config.json 对应的坐标项即可。")


if __name__ == "__main__":
    main()
