# 汽水音乐看广告 · scrcpy 投屏自动点击脚本

用 **scrcpy 把手机画面投到电脑**，再用 `pyautogui` 按电脑屏幕上的绝对坐标点击 scrcpy 窗口，让手机自动完成「看广告 → 关直播间 → 关广告」的循环。

## 这套方案是怎么工作的

```
Python 脚本 --鼠标点击--> scrcpy 窗口 --ADB 注入--> 手机（汽水音乐）
     ^                                                   |
     +------------- 手机画面经 scrcpy 实时回传 ------------+
```

脚本点的不是手机坐标，是**电脑屏幕上的坐标**。scrcpy 收到鼠标事件后转成 ADB 触摸事件送进手机，手机画面再回传到电脑窗口。所以：

- 手机上不用 root、不用装 Auto.js / Appium、不用开无障碍服务
- 看到什么就点什么，纯视觉定位
- **代价是坐标强依赖窗口位置和分辨率**，窗口一动就得重校

## 准备

### 1. 手机
- 设置 → 开发者选项 → 打开 **USB 调试**
- 首次连接时在手机上点「允许调试」
- 脚本运行期间保持亮屏、别断开连接

### 2. 电脑
```bash
# 安装 scrcpy（Windows 可用 scoop / winget，或去 GitHub Releases 下 zip）
scoop install scrcpy

# Python 依赖
pip install -r requirements.txt
```

### 3. 启动 scrcpy，并固定窗口

**这一步是最关键的。** 脚本记的是屏幕绝对坐标，窗口大小或位置一变，所有点击都会偏。

```bash
scrcpy --window-x 0 --window-y 0 --window-width 900 --window-height 1600 --always-on-top
```

建议：
- 固定 `--window-x` / `--window-y` / `--window-width` / `--window-height`
- 别拖拽、别最大化/还原、别改系统显示缩放比例
- 多显示器时注意：副屏在左/上方时坐标可能是**负数**

## 校准坐标

启动 scrcpy，把手机停在广告界面，然后：

```bash
python tools/get_coords.py
```

把鼠标移到三个按钮上，记下坐标填进 `config.json`：

| 配置项 | 对应按钮 |
| --- | --- |
| `btn_next` | 「下一个广告」 |
| `btn_close_live` | 广告跳进直播间后的关闭按钮（右上角） |
| `btn_close_ad` | 普通广告的关闭按钮（右上角） |

默认坐标是在本机 2560 宽屏下调的，**换机器基本都要重校**。

## 运行

```bash
python soda_ad_auto.py --dry-run   # 先空跑，只打印要点哪里，不真的点
python soda_ad_auto.py --rounds 3  # 试跑 3 轮
python soda_ad_auto.py             # 正式跑，无限循环
```

紧急停止：把鼠标甩到**屏幕左上角**（pyautogui FAILSAFE），或按 `Ctrl+C`。

## 一轮脚本做什么

| 步骤 | 动作 | 等待 |
| --- | --- | --- |
| 1 | 点 `btn_next`，进入下一个广告 | — |
| 2 | 广告播放 | 默认 45 秒（可改 `ad_wait`） |
| 3 | 点 `btn_close_live`，退出广告跳转的直播间 | 1.0–1.5 秒 |
| 4 | 点 `btn_close_ad`，关闭广告 | 1.0–1.5 秒 |
| 5 | 界面恢复 | 1.5–2.5 秒，进入下一轮 |

每次点击坐标会随机抖动 ±4 像素，移动耗时 0.15–0.35 秒，模拟人手操作。抖动幅度可在 `config.json` 的 `jitter` 调整。

## 常见问题

**点了没反应**
- scrcpy 窗口被遮挡或最小化了 —— pyautogui 点的是屏幕坐标，点到别的窗口上就没用
- 手机锁屏或 scrcpy 断连了
- 窗口刚启动还没获得焦点，第一次点击可能被系统吃掉，先手动点一下窗口

**坐标全偏了**
- 窗口被拖动 / 缩放过 → 用固定的 `--window-*` 参数重启 scrcpy，再重校
- Windows 显示缩放改了（100% → 125%）→ 重校，或把 Python 进程设为「替代高 DPI 缩放」

**第一次点击无效**
- 窗口没在前台。建议加 `--always-on-top`，或先手动点一下窗口再启动脚本。

**广告时间变长 / 点早了**
- 调大 `config.json` 里的 `ad_wait`。

## 说明

仅供个人学习 GUI 自动化和 scrcpy 使用。自动刷广告可能违反平台用户协议，公开仓库也可能带来账号风险，使用时请自行判断并遵守相关规则。
