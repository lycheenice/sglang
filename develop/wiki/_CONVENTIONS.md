# Wiki 编写约定与交叉链接规范

> 本文件是规范说明，不进入 mkdocs nav。

## 子系统目录与编号

| 编号 | slug | 子系统 |
|---|---|---|
| 00 | overview | 总览 |
| 01 | frontend | 前端与客户端层 |
| 02 | server-api | 服务入口与 API 层 |
| 03 | orchestration | 核心调度与编排管线 |
| 04 | model-execution | 模型执行 |
| 05 | model-loading | 模型加载与注册 |
| 06 | layers | Layers |
| 07 | kv-cache | KV Cache 与内存管理 |
| 08 | distributed | 分布式与并行 |
| 09 | disaggregation | 分离式推理 |
| 10 | speculative | 投机解码 |
| 11 | sampling-control | 采样与解码控制 |
| 12 | multimodal | 多模态 |
| 13 | lora | LoRA 与适配器服务 |
| 14 | session-state | 会话、状态与检查点 |
| 15 | kernels-hardware | 内核与硬件后端 |
| 16 | config-runtime | 配置与运行时上下文 |
| 17 | observability-ops | 可观测性与运维 |
| 18 | gateway | 模型网关与代理 |
| 19 | build-ci-dev | 构建、CI 与开发 |

## 相对链接格式

- 跨子系统: `[`03 核心编排`](../03-orchestration/index.md)`
- 子系统内具体页: `[调度循环](03.4.3-scheduler-event-loop.md)`（同目录无需 `../`）
- 指向另一子系统具体页: `[`04.1 ModelRunner`](../04-model-execution/04.1-model-runner.md)`

## Mermaid

- 流程图用 `flowchart LR`/`TD`；序列图用 `sequenceDiagram`
- 节点名用方括号 `[文本]`，避免特殊字符
- 代码块用三反引号 `mermaid`

## 交叉引用矩阵

最终在 `develop/wiki/cross-references.md` 汇总一张"子系统依赖矩阵"表。各叶子页的"交叉引用"小节是它的局部体现。

## 行号核实

写每页前，用 Read/Grep 核实你引用的 `file:line`。若源码中找不到对应符号，不要写行号，只写文件路径并在说明里标注"（位置待核）"。
