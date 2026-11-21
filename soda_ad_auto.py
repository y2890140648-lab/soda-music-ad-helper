"""
汽水音乐 · 看广告自动点击脚本
================================

用 pyautogui 模拟人手点击，自动完成「下一个广告 → 等待播放 → 关闭直播间 → 关闭广告」
的循环，省掉全程盯屏幕的功夫。

坐标是本机屏幕的绝对坐标，换机器 / 换分辨率 / 改窗口大小都要重新校准，
方法见 README.md，校准工具在 tools/get_coords.py。

用法：
    python soda_ad_auto.py             # 一直循环，Ctrl+C 或鼠标甩到左上角停止
    python soda_ad_auto.py --rounds 5  # 只跑 5 轮
    python soda_ad_auto.py --dry-run   # 只打印要点的位置，不真的点

仅供个人学习自动化操作使用，请自行遵守平台规则。
"""

import argparse
import json
import os
import random
import time

import pyautogui

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

# --- 默认配置（config.json 存在时以文件为准）---
DEFAULT_CONFIG = {
    # 下一个广告按钮
    "btn_next": [2241, 825],
    # 直播间关闭按钮（广告会跳进直播间）
    "btn_close_live": [2516, 163],
    # 普通广告关闭按钮
    "btn_close_ad": [2502, 146],
    # 广告播放保底等待秒数
    "ad_wait": 45,
    # 两步关闭之间的短等待范围 [最小, 最大]
    "click_gap": [1.0, 1.5],
    # 一轮结束后的等待范围
    "round_gap": [1.5, 2.5],
    # 点击坐标随机抖动像素数，模拟手抖
    "jitter": 4,
}

pyautogui.PAUSE = 0.2
pyautogui.FAILSAFE = True


def load_config(path=CONFIG_PATH):
    """读取 config.json，缺失的键用默认值补齐。"""
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            cfg.update({k: v for k, v in user_cfg.items() if k in DEFAULT_CONFIG})
            print(f"⚙️  已加载配置：{path}")
        except (json.JSONDecodeError, OSError) as e:
            print(f"⚠️  配置文件读取失败（{e}），改用默认配置")
    else:
        print("⚙️  未找到 config.json，使用内置默认坐标")
    return cfg


def wait_rand(min_val, max_val):
    t = round(random.uniform(min_val, max_val), 1)
    print(f"⏳ 等待 {t} 秒")
    time.sleep(t)


def human_click(x, y, desc, jitter=4, dry_run=False):
    x += random.randint(-jitter, jitter)
    y += random.randint(-jitter, jitter)
    duration = random.uniform(0.15, 0.35)
    if dry_run:
        print(f"[dry-run] 本应点击 [{desc}] ({x}, {y})")
        return
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click()
    print(f"👆 点击 [{desc}] ({x}, {y})")


def run(cfg, rounds=0, dry_run=False):
    jitter = cfg["jitter"]
    cycle = 0

    print("🎯 汽水音乐广告自动观看脚本")
    print("⚠️  鼠标移到屏幕左上角可紧急停止（FAILSAFE）")
    if rounds:
        print(f"🔁 本次计划运行 {rounds} 轮")

    try:
        while True:
            cycle += 1
            print(f"\n==================== 第 {cycle} 轮 ====================")

            # 1. 进入下一个广告
            print("🟢 进入下一个广告...")
            human_click(*cfg["btn_next"], "下一个广告", jitter, dry_run)

            # 2. 等待广告播放
            print(f"📺 广告播放中（保底 {cfg['ad_wait']} 秒）...")
            if not dry_run:
                time.sleep(cfg["ad_wait"])

            # 3. 退出广告跳转的直播间
            print("🔴 尝试退出直播间...")
            human_click(*cfg["btn_close_live"], "直播间关闭按钮", jitter, dry_run)
            if not dry_run:
                wait_rand(*cfg["click_gap"])

            # 4. 关闭广告
            print("🔴 关闭广告...")
            human_click(*cfg["btn_close_ad"], "广告关闭按钮", jitter, dry_run)
            if not dry_run:
                wait_rand(*cfg["click_gap"])

            # 5. 等界面恢复，进入下一轮
            if not dry_run:
                wait_rand(*cfg["round_gap"])

            if rounds and cycle >= rounds:
                print(f"\n✅ 已完成 {rounds} 轮，正常退出")
                break

    except KeyboardInterrupt:
        print("\n🛑 脚本已停止")


def main():
    parser = argparse.ArgumentParser(description="汽水音乐看广告自动点击脚本")
    parser.add_argument("--rounds", type=int, default=0,
                        help="运行轮数，0 表示无限循环（默认 0）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只打印点击位置，不实际点击")
    parser.add_argument("--config", default=CONFIG_PATH, help="配置文件路径")
    args = parser.parse_args()

    cfg = load_config(args.config)
    run(cfg, rounds=args.rounds, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
