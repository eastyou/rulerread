# rulerread

[![CI](https://github.com/eastyou/rulerread/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/rulerread/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

厘米尺读数：长度换算、SVG 尺子与可打印练习纸，专门练习零刻度与非零起点。

## 特性

- 0–10 厘米刻度尺，毫米、半厘米、厘米三级刻度
- 色块标出物体，端点用竖线对齐刻度
- 零刻度读数与非零起点读数两类题
- 答案支持厘米、毫米、厘米 + 毫米多种写法
- A4 练习纸，可选答案页
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

```bash
rulerread length 0 7.5
rulerread length 2 9 --svg
rulerread sheet --count 12 --seed 3 --answers -o sheet.html
rulerread sheet --count 8 --kinds offset -o offset.html
```

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--count` | 题目数量 | 12 |
| `--kinds` | 题型，`read` 或 `offset`，逗号分隔 | 两种都出 |
| `--seed` | 随机种子 | 无 |
| `--answers` | 追加参考答案 | 关闭 |

## 题型

- `read`：物体左端对齐 0 刻度，直接读右端
- `offset`：物体左端不在 0 刻度，用右端刻度减左端刻度

## 答案写法

`4.5`、`4.5cm`、`4.5 厘米`、`45mm`、`4厘米5毫米` 都可以，判分时统一换算成毫米比较。

## 示例

- [examples/rulerread.html](examples/rulerread.html)：12 道读数练习，带参考答案

## 测试

```bash
python -m unittest discover -s tests -v
```

## 说明

尺子按真实比例绘制，打印时请关闭“适合纸张”缩放，选择 100% 或实际大小，以免刻度失真。

## 协议

MIT © 2026 eastyou
