# Mac + AgentPort smoke：运行与审核说明

**最新复验：**补齐新增分析后，在两次审查及修复后又完整运行四组真实 smoke，96 次请求/96 份 usage，分析与原响应重放均通过。新单次预留 4.5227456 元；合并旧批次及更早历史为 **24.2141056 / 30 元**。旧账本保持关闭，不能仍以旧账本余额当作当前可花金额。详见 [SMOKE_REVALIDATION_2026-10-07.md](SMOKE_REVALIDATION_2026-10-07.md)。下文保留历史批次记录。

状态：默认入口使用 **v2 本地预算熔断**，金额按本地保守预留值记账，不冒充实际账单。2026-10-07 用户将修复预算从 7.50 CNY 提高为**累计 30 CNY**，授权在此范围内持续修复和重跑，不再逐次询问。此前预留全部结转，不是另加 30 元或每轮各 30 元，也不因跨日重置。完整状态见下节；旧记录按历史保留。凭据及账户限额不进入仓库。

## 当前累计修复批次（2026-10-06 至 10-07）

**最终状态：run-12 四组核心 smoke（构建至评分、记账）已验收，累计预留 19.1988448 / 30 CNY，批次已关闭且停止模型请求。** [当次结果、修复与核验](SMOKE_COMPLETE_2026-10-07.md)。原始结果和失败历史全部保留。后续严格审核区分了核心完成与全计划就绪；新增的独立分析和阶段 B 入口见 [STAGE_B_AND_ANALYSIS.md](STAGE_B_AND_ANALYSIS.md)，不是新增付费运行。

- 授权：`review/agentport_repair_campaign_2026-10-06/authorization.json`；唯一跨运行账本：`smoke/agentport_repair_campaign_2026-10-06/ledger.jsonl`。此前 0.4925152 CNY 预留不在这个新授权的起算范围内，单独保留。
- 原始授权与 7.50 元账本不改写；`budget-amendment-30-CNY.json` 和追加的预算变更事件记录本次用户增额，并绑定旧账本哈希和 7.4853408 CNY 已预留金额。
- 每次发送前先在跨运行账本预留，再记单次运行账本；排他锁、哈希链、持久写入、不可重置。失败调用不退款，下一请求会超过累计 30 元时禁止发送。单轮审核配置仍为 7.50 元，不改网关服务端额度。
- 修复限于同一模型、四组、4 agents × 3 rounds、同一 dev 任务和采样设置，不扩大实验，不打开 test，不修改历史生成输出。
- 用户要求不要使用不必要的限制：已移除 solver 的物理 15 行限制。输出 token 上限不变；solver 仍只能组合已有工具，不能自己重写变换算法。新增公开调用签名，避免猜错参数名。
- 接口/安全/预算问题仍会停止。Solver 的非法 glue 不执行，记 0；Builder 与 solver 中已明确归类的普通 Python 编程错误也记失败，保留原响应与诊断，不修答案、不重采样。Builder 解析失败记录为未产出工具；错误构件仍按原规则冻结/剔除。超时、权限、未知执行错误和沙箱基础设施故障仍停止。合法参数化工具的缺参数提示可为 KeyError、ValueError 或 Python 的缺参数 TypeError；仍需独立验证带参数的实际功能。
- 已修复 solver 误拒绝 `-1` 等带正负号数字常量的问题；只允许数字字面量，未放开对表格或函数调用的运算。不能用 `float(...)`、变量取负或算术实现变换。
- 历史 `run-08` 在 7.50 元累计上限处熔断，000/111 完成、100 部分完成、011 未开始。其[当时结果与核验](SMOKE_REPAIR_RESULT_2026-10-07.md)保持不变。增额后的 run-09/10 分别定位了缺参数异常分类和普通模型错误触发全局停机的问题；run-11 完成 96 次请求，但验收发现数字常量误拒绝，不能视为最终验收。run-12 使用修正 gate 的新源码和同一配置重新运行，96 次真实请求完整完成，48 条 solver 原始响应离线重放与原评分完全一致。此前所有原始目录与逐次 `REFLECTION.json` 均保留，不能拼接成一次完整结果。
- 这些属于开发阶段的协议调整；正式论文实验前需要重新冻结最终版本，不能声称已沿用原始 15 行协议。

## 历史：累计修复批次之前的 r4（2026-10-06）

完整定位与代码修复见 [AGENTPORT_400_DIAGNOSIS.md](AGENTPORT_400_DIAGNOSIS.md)。

- 批准与结果：`review/agentport_local_smoke_2026-10-06-r4/`、`smoke/agentport_local_smoke_2026-10-06-r4/`。7 请求、7 usage、零重试，停止后没有第 8 请求；批准已消费。
- 第 7 个模型生成的 lookup_ratio 错把 list[dict] 的 lookup 当作字典；独立 verifier 0/12，不能作为有效参数化构件放行。前 6 个各 12/12。
- 本地预留 0.3536416 CNY，报告 usage 按本地费率折算 0.0388352 CNY；非实际账单。未达到预算上限。没有完整组、冻结或 solver 结果；科学效果不可评估。
- 现补清所有组相同的公开数据容器格式，并保留失败 primitive verdict。没有修改旧生成结果，没有降低停止或评测标准。
- r4 停止当时，下一包 r5 尚未批准/执行；其后执行与增额见上方当前批次。默认模板仍为单轮上限 8 CNY，实际执行以获批包为准。

## 历史：最早完整 smoke r2 的失败（保留）

- 批准包：`review/agentport_local_smoke_2026-10-06-r2/`；输出：`smoke/agentport_local_smoke_2026-10-06-r2/`。批准已消费，不能重用或恢复。
- 启动前 97 项复查：94 通过、3 跳过；Docker 预检查通过。真实运行在 000 组第一条 builder 请求返回 `BadRequestError` / HTTP 400 后停止。
- 已发送请求 1，完成组数 0；没有工具、冻结结果或 solver 结果。科学效果不可判断，缺失结果不计零分。
- 本地预留 0.0462912 CNY；无服务端 usage，实际扣费未知。这是异常熔断，不是达到 8 元上限；本地预留不是账单。
- 当前回执只有异常类型和状态码，无法确定具体拒绝字段或上游原因。不要未经证据就认定 thinking、模型或路由是根因。
- 原始结果与本地 `RESULT_REFLECTION.md` 保留；本轮没有补跑。安全诊断改进和新的最小兼容性检查须另行处理，任何新调用仍需新配置批准。

## 固定 smoke 配置

- 网关：`https://agentport.world/v1`。请求模型为目录和只读估价接口都接受的 `azure:DeepSeek-V4-Flash`；旧占位符 `deepseek-flash` 会被拒绝。这是网关上的 Azure 路由，不是 DeepSeek 官方直连。预期返回 ID 只允许 `azure:DeepSeek-V4-Flash` 或 `DeepSeek-V4-Flash`，其他 ID 立即停止。实际 smoke 响应已观察到 `DeepSeek-V4-Flash`；字段自报不是独立上游身份认证。
- 条件：`000 / 100 / 011 / 111`；实际执行顺序 `000 → 111 → 100 → 011`。
- 每组：4 个 agent、3 个同步轮次、1 个 seed（1001）、环上 2 个邻居、每轮任务菜单 8 项。
- Builder 可见固定的 60 个 dev 任务。Solver 每组只评估 6 个 dev 任务（深度 1/2/3 各 2 个），每题 2 次；不打开 test。
- 调用数：构建 `4 × 4 × 3 = 48`；solver `4 × 6 × 2 = 48`；合计最多 96 次。串行运行，HTTP 自动重试关闭，不自动补跑或扩规模。
- 采样：temperature 0.7、thinking disabled。Builder 输出上限 4,000 tokens，solver 1,500 tokens；单次 system+user 输入上限 16,000 UTF-8 bytes。
- separation 阈值 0.3；alignment window 3；单次模型请求总 deadline 90 秒；每个工具 probe 超时 5 秒。
- 本地记账上限 8 元，单次预留最多 0.10 元。预留值：每百万输入 tokens 3.2 元、输出 tokens 8.4 元；它们是本地风控参数，不是网关报价或实时汇率。整场最大预留 7.2900864 元，单次 builder 最大预留 0.0864384 元。

这是开发诊断，不是论文主实验，也不足以证明 separation 有效。

## 预算与异常停机

- v2 配置明确使用 `reservation_*` 和 `reservation_basis`，没有 `pricing_confirmed=true` 或伪填的 `provider_spend_cap_cny`。本地预留值留有额外余量，但不声称覆盖未知的服务端收费。本地限额仅适用于本次经批准的运行，不能约束其他人同时使用同一 key。
- 网关的只读入口为 `POST /v1/rmg/estimate`，正文形如 `{"request": {"model": "azure:DeepSeek-V4-Flash", "messages": [{"role": "user", "content": "estimate only"}], "max_tokens": 1000}}`。它返回美元估价、路由和当前 key 预算，无须调用 `/chat/completions`。本次返回还明确提示缓存写入价格未知、估价未包含该费用，因此不能将 `worst_usd` 宣称为完整账单硬上限。账户级查询结果只保留在本地 `review/`，不公开。
- 开跑前计算整场最大本地预留：`[96 × (16000 + 512) × 3.2 + 48 × (4000 + 1500) × 8.4] / 1,000,000 = 7.2900864` 元；超出本地上限或单次上限时，第一条请求也不发送。这是所选预留参数下的上界，不是服务端账单上界。
- 每次请求前，以实际输入 bytes + 512 和输出 token 上限预留费用。使用 Decimal 比较；下一次请求会越过 8 元、单次预留超过 0.10 元或已预留 96 次请求时立即熔断。较少的实际 token 用量不释放预留额度。
- 预留账目先写入并 `fsync`，成功后才允许发送。写入失败立即停机。账本以 0600 权限独占创建，已有账本不能重新初始化。预算配置是只读快照，调用者修改原始配置不能抬高运行中的额度。
- 同时最多一个未结算请求。发生超时、断连或 usage 缺失后，原请求预留保留，不允许发下一条；计数器不会在异常后清零。线程间的预留操作加锁，意外并发也触发熔断。
- token usage 缺失、负数、异常、超过预留假设时停止。已经完成的有效 usage 先记账，再检查返回模型、结束原因和响应格式。
- 截断、空回复、错误模型 ID、意外 thinking/function call、未知/权限/超时执行错误、空冻结库时停止；保留诊断，不重采样。Builder 解析失败记录为失败；已归类的普通代码错误和非法 solver glue 按上方当前规则处理，不重启全场。
- 正常执行但答案错误仍是正常任务结果，不因分数低而停止。不能把模型每次都写对作为 smoke 通过条件，也不能把失败答案改成通过。
- Builder 在下一位 agent 请求前完成执行检查，但各 agent 仍只读取本轮开始的同一个 snapshot，维持同步轮次语义。
- 停止后写 `FAILED.json`，缺失结果不计作零分。不能自动恢复；修改源码、配置、价格或镜像后都需要新的审核文件。

**边界：v2 不再把独立服务端小额限额作为开跑条件。** 本地熔断能停止后续请求，不能撤回已发送请求，也不能保证未知服务端收费绝不超过 8 元。报告使用 `local_allowance_not_provider_invoice`，不把 token 用量乘以预留费率称作实际扣款。网关账户限额不被修改。若仍明确选择旧 `agentport_flash_smoke.json`，v1 原有的完整价格与服务端限额 gate 继续保留。

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

当前默认配置是 `configs/agentport_flash_local_smoke.json`。预留参数、预期响应 ID 及不保证服务端账单的边界都已明文记录；用户需要批准它们，而不是去控制台改 key 额度。

```sh
.venv/bin/python -m boidsnet.runner.mac_smoke prepare \
  --config configs/agentport_flash_local_smoke.json \
  --out review/agentport_local_smoke_review \
  --run-out smoke/agentport_local_smoke_run
```

这会验证 Docker、固定镜像 ID，输出 `config.json`、`resolved_config.json`、`sandbox_receipt.json` 和默认未批准的 `approval.template.json`。`resolved_config.json` 同时记录本地预算策略及整场预留值。输出目录必须全新。

只有在用户明确批准完整配置、费用和源码后，才可以形成 `approval.json`。对于上方明确委托的有限修复批次，逐次审核文件如实注明助手依据用户累计授权审核，不冒充用户逐次审阅；执行必须同时接入 `CampaignBudget`，不能通过下方独立单轮示例绕开累计账本。下列命令是独立单轮获批后的执行说明，**不是修复批次的启动方式**：

```sh
.venv/bin/python -m boidsnet.runner.mac_smoke execute \
  --config review/agentport_local_smoke_review/config.json \
  --review review/agentport_local_smoke_review/resolved_config.json \
  --approval review/agentport_local_smoke_review/approval.json \
  --out smoke/agentport_local_smoke_run --allow-spend
```

所有 gate 通过后，若运行环境没有 `BOIDS_PARTNER_API_KEY`，终端会提供隐藏输入提示；非交互模式且没有运行时 key 时直接拒绝。只使用本次指定的 key，不从其他变量或文件寻找替代凭据。本机当前版本已通过真实生成请求验证；新环境或路由仍需实测。只读查询通过不等于生成链路通过，字段自报的模型 ID 也不是独立的上游模型身份认证。

## 当前 v2 离线验证（2026-10-06）

- 核心、新旧预算与异常回归：141 项，135 通过、6 跳过，零失败。跳过包括两个可选绘图检查及另行启用的 OS/Docker 检查，不冒称跳过项已通过。
- 新增本地预算检查覆盖精确金额边界、96 次上限、单次限额、不退还预留、并发、未知用量、超用量、重启复用、账本落盘失败、模型错误后不重试，以及异常停止回执不记录原始错误消息。
- 最新 v2 Docker 四组 build → freeze → solver → ledger 完整集成：1 项通过（175.679 秒），96 次模拟模型调用、192 条记账记录；禁止构造外部 SDK，真实模型调用 0 次。这不是 separation 效果证据。
- 完整离线集成对应源码 hash：`cc47b8a37bbd64fe3f477b8d0acb95865a774bc9cb15e90b4575d8ae10ebb7d0`；随后仅更新模块说明文字，当前源码 hash 为 `e6ddd880e6d0f139d0885dbc69fffee51988009ed9ff50417e73226762071555`，141 项回归再次通过（135 通过、6 跳过）。
- 当时待审包：`review/agentport_local_smoke_2026-10-06-r2/`。离线准备时 Docker 预检查通过，`spend_blockers=[]`、模板 `approved=false`，真实模型调用 0 次。后续用户批准后的实际执行见上方“最近一次真实执行”；模板保持未批准，独立 `approval.json` 记录实际批准。此前所有待审包均不能批准当前源码。

## 历史 v1 离线验证

- Docker 预检查及手写工具的双 probe：通过；实际 `os-docker`，Linux Python 3.11.2。
- `tests.test_sandbox + tests.test_reaudit_regressions`：43 项，42 通过，1 项跳过（Mac 无权在 `/etc` 植入 canary 的 mount-escape fixture）。网络、宿主文件、父进程凭据、只读工具源码及非特权运行检查已实际在 Docker 执行。
- 四组完整 build → freeze → solver → ledger 集成：通过，96 次**模拟**模型调用、192 条预留/usage 账目；SDK 被禁止构造。外部 API 请求 0 次，费用 0。这不是 DeepSeek 的能力结果。
- 新增 AgentPort 回归：19 项，其中 Docker 集成在普通单元测试运行中跳过；该集成已另外启用 Docker 并通过。另验证了旧 USD 账目字段保留、CNY 不被误标成 USD，以及未知 usage 请求单独计数。
- 最新核心/新增回归：118 项，113 通过，5 跳过；旧构建、评分、批处理和确定性流程：50 项全部通过。合计覆盖全部测试模块，168 项报告结果（163 通过、5 跳过），不是把重复运行次数相加。
- 原生测试中的 5 个跳过是两个可选绘图检查、一个 Linux/容器对抗测试类、一个 OS 只读检查和一个显式 Docker 端到端检查。后面三类另在 Docker 验收中执行，不把跳过当成通过。
- 最终 Docker 专项重跑：62 项，61 通过，1 项 `/etc` canary fixture 跳过，零失败；包含全部 AgentPort 检查、四组完整离线集成、沙箱与旧缺陷回归。此次固定同一 image ID，没有再次出现镜像查询异常。它与原生测试有重叠，不能加成 230 项独立测试。

上述完整验收对应的历史包是 `review/agentport_mac_smoke_2026-10-06-r2/`，源码 hash 为 `9ce5a30740bf4ea9a6f2487dd964b836411877f85455c0fbd0afb8c63fd2d534`。它和此前不带 `-r2` 的包都不能批准后续路由修正后的源码。Docker image ID：`sha256:0e379b4303072d494085de56dbfc73924845f30daa1a91d0aaee19fb50f6cdf1`。

## 历史 v1 网关路由修正

- 配置现在只接受目录中的显式 DeepSeek V4 Flash provider pin，拒绝旧占位符、动态 latest、tier/role 和其他模型。最终使用哪个 pin 仍以用户批准的完整配置为准。
- 修复了大小写和 `azure:` / `openrouter:` 前缀导致模型识别失败的问题。所有 AgentPort 请求仍强制专用凭据变量、disabled thinking、严格参数、零自动重试和禁止 HTTP 重定向，前缀不能绕过这些保护。
- 增加目录 ID 检查和 11 种保护绕过回归用例。它们只使用离线 SDK 替身，不调用模型。
- 路由修正后的核心/新增回归：120 项，115 通过、5 跳过，零失败；模型、配置和预算子集另行运行 54 项，53 通过、1 跳过。
- Docker AgentPort 复测首次为 20 通过、1 错误，完整集成被 `SandboxInfrastructureError` 中止。Docker 事件中观察到一个自有工具容器退出码 1，但该次 stderr 未保留，无法确定根因。随后在相同源码和固定镜像下启用失败诊断重跑：21 项全部通过（253.915 秒），含四组完整离线集成，未复现异常。重跑通过不消除该未定位的瞬态风险；任何相同异常仍停止真实 smoke，不自动重试，不改计零分。
- 该历史源码 hash：`4959d70d0ec5a7493bcb473014b536f66b5b6df9af1f6d13c7763efca1faae11`；旧 v1 模板保持 `pricing_confirmed=false`，不把估价和账户月额度伪装成完整计费上界或 smoke 限额。
- 历史待审包 `review/agentport_mac_smoke_2026-10-06-r3/`：同一固定镜像通过预检查，`approved=false`，模型请求 0 次。它不能批准最新 v2 代码。

本轮曾遇到一次 Docker 标签查询返回“镜像不存在”：入口在读 key 前拒绝了 PREPARE；不可变 image ID 仍可读取，随后标签恢复。没有重建或替换镜像，也没有付费请求。无法确定该瞬态查询失败的根因，不将其隐藏为“从未发生异常”；真实执行使用审核过的不可变 image ID，任何容器启动/清理异常仍会停止整个 smoke。

Docker 运行参数依据 [Docker run 文档](https://docs.docker.com/engine/containers/run/)；实际边界以本机探测和对抗测试为准，不声称任意 Python interpreter tampering 都已被证明安全。
