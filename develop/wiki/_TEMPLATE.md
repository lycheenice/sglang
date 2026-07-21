# 页面模板（所有叶子页统一遵循）

> 本文件是 wiki 写作规范，不进入 mkdocs nav。每个 subagent 写作前必须先读本文件与 `_CONVENTIONS.md`。

## 文件命名

- 每个子系统目录: `develop/wiki/<NN>-<slug>/`
- 叶子页: `<NN.M>-<leaf-slug>.md`（或 `<NN.M.K>-<leaf>.md`），slug 用小写连字符
- 子系统首页: `index.md`

## 每页结构（中文，600–1000 字，含 Mermaid）

```markdown
# <编号> <页面标题>

## 定位
一两句话说明此模块在 SGLang 整体架构中的位置（属于哪个子系统、解决什么问题）。

## 职责
- 列点说明此模块负责的功能

## 关键类与函数

| 名称 | 定义位置 | 说明 |
|---|---|---|
| `ClassName` / `func_name` | `path/file.py:行号` | 简述其作用 |

（列 3–8 行最关键的，不要穷举）

## 子模块树

- `sub_dir/` — 一句话说明
  - `leaf.py` — 一句话说明
- `file.py` — 一句话说明

## 数据流 / 控制流

（用 Mermaid 流程图或序列图表达，至少在数据/控制密集的页面给出）

```mermaid
flowchart LR
    A[输入] --> B[处理] --> C[输出]
```

文字补充说明上述流程的关键步骤。

## 交叉引用

- 上游/依赖: [`04 模型执行`](../04-model-execution/index.md) — 由 `ModelRunner` 调用
- 下游/被依赖: [`07 KV Cache`](../07-kv-cache/index.md) — 持有内存池引用
- 相关: [`03.4 调度循环`](../03-orchestration/03.4.3-scheduler-event-loop.md)
- 相关 skill: `.claude/skills/<name>`

（所有跨子系统引用用相对路径 markdown 链接；同子系统页也用相对路径）

## 进一步阅读

- 源码: `path/to/dir`
- 文档/Blog: <仅当确实存在时给出>
- 相关 PR: <仅当确实存在时给出>
```

## 写作要求

1. **中文为主**，类名/函数名/路径/file:line/代码标识符保持英文原文。
2. 每页 600–1000 字正文，关键页面含 1 个 Mermaid 图。
3. **精确 `file:line`**：行号来自实际源码，写前用 Read/Grep 核实，不要凭空猜测。若不确定行号，宁可省略行号只给文件路径。
4. 交叉引用必须用相对路径链接到目标 `index.md` 或具体叶子页。
5. 不编造不存在的 PR/Blog 链接；"进一步阅读"只放确实存在的源码路径。
6. 每个叶子页顶部标题用 `# <编号空格标题>` 一级标题。
7. 子系统 `index.md` 是该子系统总览（200–400 字 + 该子系统内导航列表 + 1 张 Mermaid 子系统边界图）。
8. 不要写 emoji。
