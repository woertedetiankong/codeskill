---
name: transparent-workshop-illustrations
description: "Generate D-style Chinese article illustrations for any technical topic: white background, hand-drawn wireframe boxes, orange arrows, red/blue labels, a small operator, plus captions and 80-150 word explanations. Use for AI, Codex, Claude Code, workflows, tools, hardware, tutorials, and concept explainers."
---

# D 风格正文配图

这个 skill 只做一件事：把任意主题转成 **D 风格 16:9 中文正文配图**，并配上能帮助读者理解的图注和短正文解释。

默认不再提供其他视觉方向。无论用户给的是 AI 工作流、Claude Code、Codex、产品方法论、硬件联动、教程路线、debug 经验还是普通概念解释，都使用同一种 D 风格。

## D 风格定义

画面必须像一张白底方向板上的轻手绘文章配图原型：

- 16:9 横版，纯白背景，大量留白。
- 黑色轻手绘线框，矩形流程块，线条略微不完美。
- 橙色箭头表示主流程、分支、回环或正在操作的线缆。
- 红色贴纸表示风险、错误、噪音、证据不足、假发现。
- 蓝色贴纸表示判断、状态、证据、可重跑、后台跑、关键路径。
- 只放少量中文：主框标签 2-6 字，贴纸 2-8 字，底部灰字短句不超过 24 字。
- 必须有小方头线稿工坊员参与核心动作：递任务卡、拉线、调旋钮、拿放大镜、检查清单、剪断噪音、把卡片放进盒子等。

绝对不要：玻璃 3D、半透明产品渲染、渐变、阴影、厚重质感、圆角卡片堆叠、PPT 信息图、正式架构图、UML、泳道、复杂 UI、商业科技海报、赛博背景、大标题、可爱吉祥物、黑色实心小怪物、猫、儿童卡通、游戏特效。

## 视觉参考

需要确认风格时，查看 `assets/reference-d-style.png`。这张图只作为风格锚点：

- 学习白底、线框、橙色箭头、红蓝贴纸、工坊员动作、留白比例。
- 不要复制它的主题、文字、布局或具体流程。
- 如果用户给了自己的参考图，以用户参考图为准，但仍保持 D 风格规则。

## 工作流

### 1. 先找认知锚点

先理解用户内容，挑 1-6 个最值得画的点。不要平均配图，优先画这些：

- 一个机制如何工作。
- 一个流程如何从输入走到输出。
- 一个概念和另一个概念的区别。
- 一个失败点如何被发现或修复。
- 一个黑盒内部最关键的 2-4 个结构。
- 一个结果为什么可信。
- 一个动态过程如何分支、循环、补查或收敛。

短内容通常 1-3 张，长文最多 6 张。每张图只讲一个核心意思。

### 2. 设计 shot list

如果用户要规划、解释、配图建议或没有明确要求直接生图，先输出 shot list。

每张图写清楚：

- 放置位置
- 主题
- 核心意思
- D 风格构图
- 工坊员动作
- 中文短标注
- 图注
- 80-150 字正文解释要点
- 是否适合直接生图

默认顺序是：`是什么` → `怎么运作` → `和旧方式区别` → `为什么可信/有什么价值`。

### 3. 生图或输出 prompt

如果用户明确说“生成 / 生图 / 做图 / 出图 / 直接画”，并且当前环境有图像生成工具，则每张图单独生成。不要把多张图拼在一张里。

如果不能生图，就输出完整可复制 prompt。每张图使用这个结构：

```text
Create a 16:9 Chinese technical article body illustration in sparse hand-drawn D-style.

Visual style:
- Pure white background with lots of empty space.
- Minimal black hand-drawn line art, thin slightly imperfect lines.
- Simple wireframe rectangular boxes and simple arrows.
- Orange arrows for the main path, branch, loop, or active cable.
- Small red and blue sticker-like handwritten Chinese labels.
- One tiny line-art workshop operator with a square head, two dot eyes, tiny mouth, and simple body. The operator must actively {动作}.
- Looks like a rough article illustration direction-board card, not a polished infographic.
- No 3D glass, no transparency rendering, no gradients, no shadows.

Subject: {主题}
Core idea: {核心意思}
Composition: {方块、箭头、分支/回环/过滤/对比/汇总如何摆放}

Text (verbatim only):
Main box labels: "{标签1}", "{标签2}", "{标签3}"
Sticker labels: blue "{蓝标1}", red "{红标1}"
Bottom-left gray caption: "{不超过 24 字的短句}"

Avoid: extra text, big title, formal architecture diagram, UML, swimlane, PPT look, app UI, cyberpunk, commercial poster, cute mascot, black solid creature, copied IP style, watermark.
```

### 4. 生成后检查

生成或交付前检查：

- 是否纯白底、大量留白、16:9 横版。
- 是否只有少量黑色线框方块和橙色箭头。
- 是否有红蓝贴纸，但没有五颜六色。
- 工坊员是否参与核心动作，而不是站在旁边装饰。
- 中文是否少、短、可读；错字严重就减少文字重生成。
- 是否一张图只讲一个概念。
- 是否没有跑成玻璃 3D、PPT、正式架构图、商业海报或儿童卡通。

### 5. 配套文字解释

解释型内容不要只交付图。每张图默认配：

```text
图注：{一句话说明这张图的结构，不超过 28 字}

正文解释：
{80-150 字。先说图里发生了什么，再解释它代表的思想，最后点出为什么重要。不要逐字复述图上标签，不要写成营销文案。}
```

如果用户只要图片，可以简短说明保存路径；如果用户要文章配图，必须给图注和正文解释。

## 交付格式

### 只做规划

| 序号 | 放置位置 | 主题 | 核心意思 | D 风格构图 | 工坊员动作 | 中文标注 | 图注 | 正文解释要点 |

### 输出 prompt

```text
文件名建议：01-topic-name.png
用途：放在“...”段落后
图注：...
正文解释：...
Prompt：...
```

### 已生成图片

说明：

- 生成了几张。
- 每张图保存路径。
- 每张图适合放在哪里。
- 每张图的图注和 80-150 字正文解释。

默认保存到：

```text
assets/<article-slug>-d-style/
```

按顺序命名：

```text
01-topic-name.png
02-topic-name.png
03-topic-name.png
```

## 常用构图

- 横向流程：`输入 -> 判断 -> 输出`
- 对比：左边旧方式，右边新方式，中间不画重分隔线。
- 分支循环：一个判断点向下分出补查，再回到判断点。
- 互查过滤：多个来源进入检查盒，假发现被红色叉号踢出。
- 黑盒拆开：一个大线框盒里只放 2-4 个关键小零件。
- 工具抽屉：少量抽屉代表工具类别，工坊员只拉开一个。
- 路线折线：橙色路线穿过 3-5 个节点，像轻量路线图。

## 标注词库

- 流程：输入 / 判断 / 分派 / 执行 / 校验 / 输出 / 报告
- Workflow：任务 / 脚本 / 后台跑 / 可重跑 / 分支 / 循环 / 补查 / 加派
- Agent：子任务 / 互查 / 证据 / 假发现 / 收敛 / 反馈
- 编程工具：需求 / 改代码 / 跑测试 / 看日志 / 提交 / 回滚
- 上下文：上下文 / 压缩 / 噪音 / 关键信息 / 回收
- Debug：报错 / 断点 / 权限 / 重试 / 修复 / 风险
- 硬件：传感器 / 控制板 / Agent / 执行器 / 状态 / 反馈
