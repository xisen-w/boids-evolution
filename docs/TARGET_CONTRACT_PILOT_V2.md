# 参数化目标契约与小规模 pilot v2

2026-10-07。用户授权修复代码、准备小 pilot 并 push，**没有授权本次启动付费实验**。

## 1. 解决的衔接问题

上一轮 48 个真实工具全部 `TARGET NONE`，quality-based alignment 没有机会选择通过任务验证的样例，M_cross 全部未识别。这不证明 Boids 无效，也不意味着所有参数化工具有 bug。

旧契约只承认无参数的完整任务调用；新契约让工具在生成时同时声明：

```text
TARGET: <当前开发菜单中的一个任务 ID，或 NONE>
TARGET_PARAMS: <一行 JSON 对象，例如 {"col":"price_cents","factor":0.01}>
```

验证对象为 `execute(table, lookup, **TARGET_PARAMS)`，必须完成目标任务的全部操作。参数只用于调用工具，绝不改 reference。单个 primitive 只能声明真正完整匹配的一步任务，不能冒充完成多步任务。没有合适目标时仍允许 NONE；不强制依赖、不要为制造正结果附加导入。

这是明确的开发协议修订 `declared-task-params-v1`，不是对旧结果的重新标注。四组同时使用同一修订，S/A/C 主比较、任务集、阈值、模型和轮次不变。论文方法部分应说明绑定参数、公开反馈调用与冻结保留规则的更新。

代码已贯通：

- Builder：新格式严格解析 JSON，拒绝重复键、非有限数、非对象、table/lookup 覆盖和菜单外目标。错误声明保留为失败记录，不修模型回答或补生成。
- Alignment：仍然使用“通过完整开发目标优先，最高 TCI，缺失则 fallback”；现在通过信号可来自有显式参数的完整任务调用。没有用 primitive 覆盖替代任务正确性。
- 公开反馈：新契约使用声明的合法参数调用公共输入，明确记录调用参数；不反馈 reference 或额外测试答案。旧契约反馈不变。
- 冻结：旧工具的无参数行为与独立 primitive 验证保留。新契约下，带参数目标或声明了 IMPLEMENTS 的工具先做独立 primitive 验证，即便 TARGET NONE 也不能因为默认调用都返回原表而合并不同参数化能力。没有可验证的 standalone primitive 时，有效的无参数行为沿用原规则；需要参数的完整工具按声明任务、参数与带参信号指纹验证/去重。不会自动补 TARGET，也不会给 NONE 工具虚构功能依赖证据。
- Solver：获得声明的开发任务调用参数，明确标记不是当前任务成功保证。调用仍受原 glue gate 限制，不放开新的数据变换逻辑。
- M_cross：在独立输入上，使用同一声明任务和相同参数运行 intact 与 importer-specific identity 消融。分母仍为 solver 可见工具；静态导入、结构性崩溃、unknown 均不当作功能依赖。
- 停止：冻结验证中的权限、超时等关键异常也会熔断；普通错误答案保留为失败。
- 报告：自动列出无成功目标、仅 fallback、缺少 S 机会、效用地板/天花板、M_cross 未识别等诊断，不按胜负自动加跑。
- 旧源码结果、旧配置和旧账本不覆盖。新解析与提示显式 opt-in；旧记录缺少参数元数据时仍按无参数调用解释。新旧契约不能混合汇总。
- 单请求网关诊断拒绝 Stage B 配置，避免把 8×12 pilot 静默套入旧首请求路径。

## 2. 小实验：一批数据，四项分析

- **实验目的：**
  - 判断完整轮次是否产生可测量的可靠工具库和 separation 开发信号。
  - 主比较 111−011、111−000，辅助比较 100−000。不把开发差值当论文确定结论。
- **实验 setup：**
  - 四组 000 / 100 / 011 / 111；各自从空库开始，000 保留同样社会信息但不加方向性指导。
  - 每组 8 agents × 12 同步轮，每 agent 每轮 1 次机会；每组 1 个社会，seed=2001。固定两邻居环，每次菜单 8 道开发题。
  - 环境 22 primitives、60 道 dev，任务 seed=0。只评估固定 6 道 dev：`dev-6311-d1`、`dev-6890-d1`、`dev-2407-d2`、`dev-5081-d2`、`dev-1528-d3`、`dev-6534-d3`。
  - 每题 2 次独立 solver 尝试，每次 8 张 reference 表，全对才计该次成功；两个尝试平均，不用 best-of-2。正式 test 保持封闭。
  - AgentPort `azure:DeepSeek-V4-Flash`，temperature=0.7，thinking disabled，当前 wire 参数 `reasoning_effort=none`。
  - Builder / solver 输出上限 4000 / 1500 tokens，输入上限 32768 bytes；没有物理 15 行限制。
  - S 阈值 0.3，A 最近 3 轮，C 上一轮全局声明统计；无额外总结模型。
  - 模型串行、零自动重试、零自动恢复；请求 deadline 90 秒，工具 probe 5 秒；同一 Mac 的固定 Docker 隔离。
  - 调用 384 builder + 48 solver = 432；本地预留上限 60 元，单请求上限 0.15 元。完整最坏预留 59.513472 元，系本地记账，不是供应商账单保证。
- **实验流程：**
  - 1. 用新源码准备审核包，核对配置、版本、Docker、契约、金额和输出目录。新契约的真实小验证仍需另行批准；离线 fixture 不能代替真实模型兼容性验证。
  - 2. 获得该运行的明确批准后，按 011 → 100 → 111 → 000 执行。每轮使用轮初快照，新工具下一轮可见。
  - 3. 每组构建结束后冻结工具库，完成 6 题 × 2 次评分。
  - 4. 在同一批工具上运行文字/行为重复、可靠能力覆盖、跨 agent 功能依赖、任务深度与逐轮覆盖分析；这些步骤不调用模型。
  - 5. 对账全部请求、失败、缺失、预算和机制触发。保存 `research_readiness` 诊断后停止，不自动转入主实验。
- **期待结果：**
  - 希望 separation 伴随更可靠的互补能力与正向效用差，但不保证为正。
  - 新契约只是提供可测量路径，不能保证真实模型会声明目标、产生依赖或赢过基线。无效声明、未识别与负结果必须保留。
  - 一社会/组只支持开发诊断，不提供 society 间不确定性或显著性。全零、全满或缺少机制机会时应解释原因，不能重跑到赢。

## 3. Mac 上如何准备（不调用模型）

在仓库根目录、Docker Desktop 已运行时：

```sh
.venv/bin/python -m boidsnet.runner.small_pilot prepare \
  --out review/stage-b-v2 --run-out runs/stage-b-v2
```

此入口默认读取 `configs/agentport_flash_stage_b_v2.json`。仅检查本地 Docker、运行人工 identity 检查并生成审核包；不读取 key、不构造真实模型客户端。目录必须全新，不能覆盖历史。

审核包包含 `config.json`、`resolved_config.json`、`sandbox_receipt.json`、`approval.template.json`。批准模板为 `approved=false`；模板存在不等于用户批准。完整配置、源码、协议和唯一运行路径共同绑定，变更任意一项后旧批准失效。

**仅在用户明确批准对应审核包后**，由操作者保存批准文件，并执行：

```sh
.venv/bin/python -m boidsnet.runner.small_pilot execute \
  --config review/stage-b-v2/config.json \
  --review review/stage-b-v2/resolved_config.json \
  --approval review/stage-b-v2/approval.json \
  --out runs/stage-b-v2 --allow-spend
```

Key 使用终端隐藏输入或临时运行环境注入，不放在命令、JSON、`.env` 或 Git 中。没有 key 或批准时停下，不自动寻找其他账号凭据。

新契约最小四组 revalidation 的**待审核配置**另存 `configs/agentport_flash_contract_smoke.json`：4 agents × 3 轮、96 次、7.5 元上限。它与 pilot 共用代码，只改已有 smoke 规模；不是本次已批准的运行，也不能继续消耗已经关闭的历史修复批次。

## 4. 验证与证据边界

研究链条仍然是：S/A/C 指令 → 机制实际触发 → 可靠覆盖、冗余与功能依赖变化 → 工具库效用。旧 smoke 只打通了工程链路；其全部 TARGET NONE、alignment 仅 fallback、M_cross 未识别，说明后面几环尚不可据此判定。本次只修复可测量路径，不把人工正例当作这条研究链成立的证据。

新增测试覆盖声明解析、旧协议兼容、菜单边界、目标参数不改变 reference、带参完整工具冻结保留、错误声明剔除、冻结异常停止、四组一致开关、非 fallback alignment、真实 Docker 执行的 identity 消融及 solver 全链路。响应都是明确标记的人工 fixture，不是 LLM 实验结果。

本次双轮审查及最终测试回执见下方验收记录。新契约的付费 smoke 与 432 次 pilot 均未执行；旧 smoke 不能冒充新源码、新契约的真实验证。

### 验收记录

- 第一轮：检查目标声明 → 公开反馈 → 完整任务验证 → alignment → 冻结 → solver → 独立依赖分析的参数传递与四组一致性，并做全量离线回归。
- 第二轮：检查失败分支、旧协议兼容和预算，修复默认 identity 误去重（包括 TARGET NONE 的可选参数工具）、CRLF 声明误判、NONE 缺失参数字段漏报、无法解析代码时契约错误漏记；为这些边界补回归，并在独立进程重验最终版本的四组 Docker 全链路。
- 修复后的解析、SAC、网关与 v2 调度专项 58 项通过；包括失败先复现、修复后再通过的去重、解析与日志测试。
- 最终版本独立 Docker/目标契约专项：33 项全部通过（352.818 秒），无跳过。含四组构建、冻结、solver、非 fallback alignment、功能依赖消融及 NONE/默认 identity 边界；无模型请求。
- 旧真实 smoke 的四组共 48 条归档 solver 响应已在新源码下离线重放：全部 gate、逐项 verdict、冻结结果一致，四组原始文件哈希未变。重放不是新实验，新模型请求为 0。
- 432 次最坏输入/输出预算模拟预留 59.513472 元，第 433 次在发送前被拒绝。模拟无 HTTP 请求。
- 本机 `small_pilot prepare` 实际通过：432 次计划请求，配置检查无阻塞，`approved=false`；验证该模板确实不能执行，目标实验目录不存在。
- 最终 runner/env/Docker 构建脚本指纹：`687388c3ff9bb1731259366c48ac75420b29aa23d675571e83be317e802df559`。本机最终待批准包位于 `review/stage-b-v2-2026-10-07-final/`；已验证 live source 一致、模板不能执行、实验输出目录未创建。旧待批准包因源码变化失效，不覆盖、不批准。
- 全量 Docker 兼容回归：296 项，293 通过、3 跳过、0 失败/错误（5450.795 秒）。已单独核实跳过原因：两项旧图形检查缺少可选 matplotlib；一项 mount-escape 检查无法在宿主 `/etc` 创建 canary，故该具体场景未验证。不能把跳过项算作通过。
- 全量轮次在最后几处边界修补前启动；修补后另开独立进程，完成上列最终源码的 33 项专项和 48 条旧响应回放。不同轮次不相加冒充独立实验或同一源码的全量结果。
- 本次提交只含代码、配置、人工测试和说明；不上传 key、审批文件或当前原始实验数据。当前未发现未解决的工程阻塞，但不保证未来输入绝无 bug，也不把测试通过当作 separation 已获支持。

复验最终目标契约专项（只跑软件测试）：

```sh
BOIDS_SANDBOX=docker \
BOIDS_DOCKER_IMAGE=sha256:0e379b4303072d494085de56dbfc73924845f30daa1a91d0aaee19fb50f6cdf1 \
.venv/bin/python -m unittest -v tests.test_target_contract
```

本文件与配置本身不构成实验执行授权。
