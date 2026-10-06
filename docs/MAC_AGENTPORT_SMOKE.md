# Mac + AgentPort smoke：运行与审核说明

状态：本机 Docker 隔离入口已实现；真实模型调用仍被完整计费口径、smoke 专用服务端限额、返回模型确认和人工批准 gate 锁定。已使用用户指定 key 查询只读模型目录及费用估算，没有发送生成请求，没有真实模型实验结果。凭据及账户限额不进入本仓库。

## 固定 smoke 配置

- 网关：`https://agentport.world/v1`。待审请求模型已改为目录和只读估价接口都接受的 `azure:DeepSeek-V4-Flash`；旧占位符 `deepseek-flash` 在本网关返回 `unknown_model`。这是网关上的 Azure 路由，不是 DeepSeek 官方直连。返回的 model 字段仍必须匹配经确认的允许列表，不能把请求 ID 当作已经观察到的响应 ID。
- 条件：`000 / 100 / 011 / 111`；实际执行顺序 `000 → 111 → 100 → 011`。
- 每组：4 个 agent、3 个同步轮次、1 个 seed（1001）、环上 2 个邻居、每轮任务菜单 8 项。
- Builder 可见固定的 60 个 dev 任务。Solver 每组只评估 6 个 dev 任务（深度 1/2/3 各 2 个），每题 2 次；不打开 test。
- 调用数：构建 `4 × 4 × 3 = 48`；solver `4 × 6 × 2 = 48`；合计最多 96 次。串行运行，HTTP 自动重试关闭，不自动补跑或扩规模。
- 采样：temperature 0.7、thinking disabled。Builder 输出上限 4,000 tokens，solver 1,500 tokens；单次 system+user 输入上限 16,000 UTF-8 bytes。
- separation 阈值 0.3；alignment window 3；单次模型请求总 deadline 90 秒；每个工具 probe 超时 5 秒。
- 本地费用上限暂定人民币 8 元，尚待用户审核。该入口不接受大于 8 元的上限。

这是开发诊断，不是论文主实验，也不足以证明 separation 有效。

## 预算与异常停机

- 输入/输出单价必须是已确认的每百万 token 人民币价格。未知值保持 `null`，不能使用官方 DeepSeek 的价格冒充网关价格。如果后台以美元计费，必须先确认保守换算口径，并记入 `pricing_reference`。
- 网关的只读入口为 `POST /v1/rmg/estimate`，正文形如 `{"request": {"model": "azure:DeepSeek-V4-Flash", "messages": [{"role": "user", "content": "estimate only"}], "max_tokens": 1000}}`。它返回美元估价、路由和当前 key 预算，无须调用 `/chat/completions`。本次返回还明确提示缓存写入价格未知、估价未包含该费用，因此不能将 `worst_usd` 宣称为完整账单硬上限。账户级查询结果只保留在本地 `review/`，不公开。
- 开跑前计算整场最坏预留：`[96 × (16000 + 512) × 输入单价 + 48 × (4000 + 1500) × 输出单价] / 1,000,000`。超出本地上限或已确认的网关 key 限额时，第一条请求也不发送。
- 每次请求前再以实际输入 bytes + 512 和输出 token 上限预留费用。使用 Decimal 比较，费用不足或达到 96 次后永久停止本次运行；较少的实际用量不释放预留额度。
- token usage 缺失、负数、异常、超过预留假设时停止。已经完成的有效 usage 先记账，再检查返回模型、结束原因和响应格式。
- 截断、空回复、错误模型 ID、意外 thinking/function call、builder 解析失败、工具执行异常、空冻结库或 solver glue 不合法时停止；保留诊断，不重采样。
- 正常执行但答案错误仍是正常任务结果，不因分数低而停止。上述严格停机仅用于此 dev smoke，不改变正式 test 的评分规则。
- Builder 在下一位 agent 请求前完成执行检查，但各 agent 仍只读取本轮开始的同一个 snapshot，维持同步轮次语义。
- 停止后写 `FAILED.json`，缺失结果不计作零分。不能自动恢复；修改源码、配置、价格或镜像后都需要新的审核文件。

本地 gate 只能控制自己发送的请求，无法撤回已经被服务端计费的请求。因此本入口还要求确认**独立 smoke key 的服务端限额不超过 8 元**。`provider_spend_cap_cny` 是人工确认信息，不是假装已经通过 API 设置或读回的账户额度。没有该确认则不开跑。

## 同一台 Mac 的隔离结构

- 主程序在 Mac 上运行并调用模型；生成的工具只在本机 Docker Linux 容器执行。
- 工具镜像只含 Python 标准库、解释器及动态链接依赖，不包含仓库、评测答案、应用配置或 key。
- 非特权 UID/GID 65534；清空 capabilities；启用 no-new-privileges；只读根目录；无对外网络；1 CPU、256 MiB RAM、64 个进程上限。
- 唯一宿主机挂载是临时目录中按 ACL 可达的工具源码副本，而且只读。不会挂载仓库、用户目录或 Docker socket。
- Docker CLI 也使用干净环境与临时空配置，不继承 API key；容器不接收模型凭据。
- 每批 probe 后删除仅属于本次调用的临时容器；CLI 超时或异常也会显式清理该容器。不会停止其他容器或 Docker 服务。
- 容器 image ID 绑定进审批，运行期间不隐式 pull。构建脚本与 Dockerfile 纳入源码 hash。旧的 Linux namespace 后端继续保留；本次验收证明的是 Docker 后端，不冒称原生 Linux namespace 路径也已验证。

## 使用方法

在仓库根目录运行。不要把 key 写进命令、JSON、`.env` 或任何文件。

```sh
open -a Docker
docker build -t boids-tool-sandbox:v1 docker/tool-sandbox
.venv/bin/python -m boidsnet.runner.mac_smoke check
```

`check` 只运行手写 identity 工具，不读取 key，不调用模型。

配置模板是 `configs/agentport_flash_smoke.json`。先确认并填入实际模型 ID、允许的返回模型 ID、人民币输入/输出单价、价格出处、`pricing_confirmed` 和独立 key 服务端限额。未知值必须继续保持空缺，不能为了通过检查而填测试单价。

```sh
.venv/bin/python -m boidsnet.runner.mac_smoke prepare \
  --config configs/agentport_flash_smoke.json \
  --out review/agentport_smoke_review \
  --run-out smoke/agentport_smoke_run
```

这会验证 Docker、固定镜像 ID，输出 `config.json`、`resolved_config.json`、`sandbox_receipt.json` 和默认未批准的 `approval.template.json`。即使价格未填，也可以生成“禁止付费”的待审版本。输出目录必须全新。

只有在用户明确批准完整配置、费用和源码后，才可以形成 `approval.json`。下列命令是批准后的执行说明，**不是本次已执行的操作**：

```sh
.venv/bin/python -m boidsnet.runner.mac_smoke execute \
  --config review/agentport_smoke_review/config.json \
  --review review/agentport_smoke_review/resolved_config.json \
  --approval review/agentport_smoke_review/approval.json \
  --out smoke/agentport_smoke_run --allow-spend
```

所有 gate 通过后，若运行环境没有 `BOIDS_PARTNER_API_KEY`，终端会提供隐藏输入提示；非交互模式且没有运行时 key 时直接拒绝。只使用本次指定的 key，不从其他变量或文件寻找凭据。真实模型响应、thinking 参数支持及实际服务路由仍需获批后的第一条生成请求检验；只读查询通过不等于生成链路通过，字段自报的模型 ID 也不是独立的上游模型身份认证。

## 本轮离线验证

- Docker 预检查及手写工具的双 probe：通过；实际 `os-docker`，Linux Python 3.11.2。
- `tests.test_sandbox + tests.test_reaudit_regressions`：43 项，42 通过，1 项跳过（Mac 无权在 `/etc` 植入 canary 的 mount-escape fixture）。网络、宿主文件、父进程凭据、只读工具源码及非特权运行检查已实际在 Docker 执行。
- 四组完整 build → freeze → solver → ledger 集成：通过，96 次**模拟**模型调用、192 条预留/usage 账目；SDK 被禁止构造。外部 API 请求 0 次，费用 0。这不是 DeepSeek 的能力结果。
- 新增 AgentPort 回归：19 项，其中 Docker 集成在普通单元测试运行中跳过；该集成已另外启用 Docker 并通过。另验证了旧 USD 账目字段保留、CNY 不被误标成 USD，以及未知 usage 请求单独计数。
- 最新核心/新增回归：118 项，113 通过，5 跳过；旧构建、评分、批处理和确定性流程：50 项全部通过。合计覆盖全部测试模块，168 项报告结果（163 通过、5 跳过），不是把重复运行次数相加。
- 原生测试中的 5 个跳过是两个可选绘图检查、一个 Linux/容器对抗测试类、一个 OS 只读检查和一个显式 Docker 端到端检查。后面三类另在 Docker 验收中执行，不把跳过当成通过。
- 最终 Docker 专项重跑：62 项，61 通过，1 项 `/etc` canary fixture 跳过，零失败；包含全部 AgentPort 检查、四组完整离线集成、沙箱与旧缺陷回归。此次固定同一 image ID，没有再次出现镜像查询异常。它与原生测试有重叠，不能加成 230 项独立测试。

上述完整验收对应的历史包是 `review/agentport_mac_smoke_2026-10-06-r2/`，源码 hash 为 `9ce5a30740bf4ea9a6f2487dd964b836411877f85455c0fbd0afb8c63fd2d534`。它和此前不带 `-r2` 的包都不能批准后续路由修正后的源码。Docker image ID：`sha256:0e379b4303072d494085de56dbfc73924845f30daa1a91d0aaee19fb50f6cdf1`。

## 2026-10-06 网关查询后的补充修正

- 配置现在只接受目录中的显式 DeepSeek V4 Flash provider pin，拒绝旧占位符、动态 latest、tier/role 和其他模型。最终使用哪个 pin 仍以用户批准的完整配置为准。
- 修复了大小写和 `azure:` / `openrouter:` 前缀导致模型识别失败的问题。所有 AgentPort 请求仍强制专用凭据变量、disabled thinking、严格参数、零自动重试和禁止 HTTP 重定向，前缀不能绕过这些保护。
- 增加目录 ID 检查和 11 种保护绕过回归用例。它们只使用离线 SDK 替身，不调用模型。
- 路由修正后的核心/新增回归：120 项，115 通过、5 跳过，零失败；模型、配置和预算子集另行运行 54 项，53 通过、1 跳过。
- Docker AgentPort 复测首次为 20 通过、1 错误，完整集成被 `SandboxInfrastructureError` 中止。Docker 事件中观察到一个自有工具容器退出码 1，但该次 stderr 未保留，无法确定根因。随后在相同源码和固定镜像下启用失败诊断重跑：21 项全部通过（253.915 秒），含四组完整离线集成，未复现异常。重跑通过不消除该未定位的瞬态风险；任何相同异常仍停止真实 smoke，不自动重试，不改计零分。
- 当前源码 hash：`4959d70d0ec5a7493bcb473014b536f66b5b6df9af1f6d13c7763efca1faae11`。只有针对当前源码重新生成并由用户批准的审核文件才可启动；模板继续保持 `pricing_confirmed=false`，不把估价和账户月额度伪装成完整计费上界或 smoke 限额。
- 已生成当前待审包 `review/agentport_mac_smoke_2026-10-06-r3/`：同一固定镜像通过预检查，`approved=false`，模型请求 0 次。此前版本只保留作历史记录。

本轮曾遇到一次 Docker 标签查询返回“镜像不存在”：入口在读 key 前拒绝了 PREPARE；不可变 image ID 仍可读取，随后标签恢复。没有重建或替换镜像，也没有付费请求。无法确定该瞬态查询失败的根因，不将其隐藏为“从未发生异常”；真实执行使用审核过的不可变 image ID，任何容器启动/清理异常仍会停止整个 smoke。

Docker 运行参数依据 [Docker run 文档](https://docs.docker.com/engine/containers/run/)；实际边界以本机探测和对抗测试为准，不声称任意 Python interpreter tampering 都已被证明安全。
