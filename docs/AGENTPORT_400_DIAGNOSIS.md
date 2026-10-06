# AgentPort HTTP 400：定位与修复记录

2026-10-06。Azure 请求映射已在真实请求中通过。用户批准的四组 r4 在第 7 次请求后因生成工具错误停止，未完成端到端；已补清公共 lookup 格式和失败验证记录，r5 仅准备、待确认。原始失败记录保持不变。

## 最新：r4 已执行并安全停止，r5 待审

- r4：7 次真实请求、7 次 usage、零重试；000 第一轮完整，第二轮第 3 个工具失败，其他组/冻结/solver 尚未开始。6 个有效参数化构件各自验证 12/12；第 7 个 lookup_ratio 为 0/12。
- 生成代码把 lookup 列表当作 region-keyed 字典。使用原源码在 Docker 中离线重放，0/12 正确、0 次崩溃，外部请求为 0；因此不是只缺参数，也不是网关故障。原代码没有被人工修成成功样本。
- 新补丁给所有组明确相同公共接口：table/lookup 都是 list[dict]，lookup 行有 region/target/manager；失败的 primitive verdict 也保存，停止原因为 builder_parametric_verification_failed。未改变验证阈值、评分、任务、SAC 机制或 solver。
- 本轮本地预留 0.3536416 CNY，usage 本地折算 0.0388352 CNY；所有已执行运行合计预留 0.4925152 CNY。实际账单未知。此次停机不是预算超限。
- 新源码 `4ae712228c9a45c1f135a51b083becd59bbed397b698b44a977fcdd9b770065d`，专项测试 120 项（116 通过、4 跳过）；Docker 参数化构件与完整四组离线集成 2 项通过（144.358 秒），没有新模型调用。源码/摘要、依赖、diff、凭据扫描检查通过。
- 新审核包 `review/agentport_local_smoke_2026-10-06-r5/`：保留 96 请求/4组×4agents×3轮，收紧本地限额到 7.5 CNY，使此前预留与下轮限额之和小于 8 CNY。审核摘要 `c7e7aec0ef40296e40bb5959c4e093cae3759527e6f612095ed3892684b99530`。未批准、未执行。
- r4 复盘与离线重放证据：`review/agentport_local_smoke_2026-10-06-r4/RESULT_REFLECTION.md`、`OFFLINE_DIAGNOSIS.json`。原运行保持 INCOMPLETE_NOT_SCORED_AS_ZERO；尚无 separation 效果证据。

## 历史：真实单请求成功，r4 执行前的工具接口修复

- r2 只发送 1 次请求，返回 `DeepSeek-V4-Flash`、stop，937 输入 / 138 输出 tokens，builder 解析成功。没有执行生成代码、solver 或后续模型请求。
- 本地预留 0.0462912 CNY，报告 usage 按本地费率折算 0.0041576 CNY；累计三个已执行运行预留 0.1388736 CNY，实际账单仍不确定。
- 生成的 unit_convert 需要 col/factor，却把 TARGET 写成多步任务。公开反馈、信号和目标 harness 都不传 kwargs。它不是端到端正确工具，不能只因 API 和解析成功就宣布 smoke 完成。
- 已有 D16/冻结规则允许参数化构件，但 strict smoke 在验证前把缺参视为异常。现在仅对 TARGET NONE、所有声明 primitive 独立验证通过、精确缺少已知参数 KeyError 的构件分类为预期接口行为；信号输出逐条核对，原错误计数保留。timeout、其他异常、验证失败、错误宣称目标任务等仍停止。
- 所有组共用的 builder prompt 明确完整任务与可复用构件的区别，不引入默认实现或隐藏答案。未改冻结/评分算法、SAC 机制或预算。
- 四组 r3 审核包未执行，因源码更新已标记作废并保留。新 r4 源码 `346818d200ad9aa5069d2695ae24ce9e9060a3a416c5f3a8031d0311ee66709a`，尚未批准/执行。
- 最新专项回归 118 项：114 通过、4 跳过。Docker 参数化构件/错误 TARGET 与完整四组构建—冻结—solver—记账集成共 2 项通过（164.302 秒）；后者为 96 次模拟模型请求，不是真实模型实验。前一版本完整测试 206 项：200 通过、6 跳过；不把它冒充为新源码的完整测试。
- r4 审核摘要 `fdbe3fd166cbdbdeb3d0b3a365dd04df5bab144b0fa01bb7681f068057b733ac`，运行 ID `aa899336-e370-4a84-a3e1-4cdf500b360b`。完整配置已在当前对话展示并请求确认；未生成批准文件、未启动完整 smoke。源码/摘要复核、依赖检查、差异空白检查和本次产物凭据扫描通过。

详细复盘保存在 `review/agentport_first_request_2026-10-06-r2/RESULT_REFLECTION.md`（本地运行产物，不含密钥）。下文保留 r2 执行前的历史诊断与批准边界。

## 实际诊断结果与针对性修复

- 用户明确批准 `agentport_first_request_2026-10-06-r1` 后，实际发送且仅发送 1 次原 builder 请求，返回 HTTP 400；立即熔断，没有重试。
- 新诊断记录提取到 `upstream_error`、`unrecognized_request_argument`、`unknown_request_parameter`，唯一参数提及为 `thinking`。证据在 `smoke/agentport_first_request_2026-10-06-r1/FAILED.json`。服务商未提供单独的 `param`，不伪造该字段。
- 这与 [Azure Foundry 调用者在 OpenClaw 仓库提交的原始复现](https://github.com/openclaw/openclaw/issues/87737) 一致：即使值为 disabled，该 Azure 路径也拒绝 DeepSeek-native `thinking` 对象。这是辅助交叉证据，实际定位以本轮真实响应为准。
- 现在 Azure 路由将实验意图 `thinking=disabled` 映射为顶层 `reasoning_effort=none`，不同时发送两种格式；DeepSeek 官方直连原格式保持不变。参考 [Azure DeepSeek V4 调用者的原始参数复现](https://github.com/BerriAI/litellm/issues/33202)；该记录是 Pro 部署，不能单凭它宣称本 Flash 网关已经验证。
- 完整审核包及 manifest 显示实际 `provider_request_body` / `thinking_request_body`，防止只记录意图而隐藏实际发出的参数。
- 收到 reasoning_content、reasoning、reasoning_details、非零或非法 reasoning_tokens、显式 think 块时，在记账后停止。不把 absence of reasoning 字段当成独立的内部推理关闭证明。
- 修复后新包：`review/agentport_first_request_2026-10-06-r2/`，源码 `005a484287664915dbfc39667be980869700082e57ff066e7dabdb7fa9b66bc6`。仍限 1 次、0.10 CNY；旧批准不可复用。尚未调用。

金额：原 smoke 与本轮诊断各预留 0.0462912 CNY，合计 0.0925824 CNY；两次均无 usage。预留不等于实际扣费，不据此宣称实际账单为零。

## 已确认并修复

1. **HTTP 错误缺少可用诊断。** 现在 `FAILED.json` 增加白名单错误码、服务商明确给出的参数名、有限错误类别和合规 request ID。支持错误信息里嵌套的 JSON。原始消息、headers、任意字段、凭据不保存。信息不足时明确标记 `unclassified_error`，不猜原因。
2. **请求失败后没有 prompt 记录。** Builder 现在在发送前保存 `REQUEST_PREPARED`，收到内容后改为 `RESPONSE_RECEIVED`。未收到内容时 `response=null`，不伪造结果。此改动不改变 prompt 内容、采样或 agent 顺序。
3. **响应缺少整个 usage 属性时，客户端未锁住后续调用。** 现在与 `usage=null` 一样终止，不允许再次请求。
4. **准备入口忽略传入的 Docker 镜像 ID。** 现场镜像标签查询失败，但原不可变镜像 ID 仍存在。两个准备入口现在都尊重配置中的已有 pin，并核对实际检查的镜像；不重建镜像、不静默切换环境。

## 首次真实诊断前的定位记录（保留历史）

- 原运行只发出 1 次请求；SDK 报 `BadRequestError`，HTTP 400。没有工具、solver 或对照结果。
- 只读模型目录和估价接口接受 `azure:DeepSeek-V4-Flash`，不等于实际生成成功或支持全部请求字段。
- 用真实 SDK 和内存 MockTransport 检查到：请求路径正确，无 `api-version` 查询参数；`thinking` 位于 JSON 顶层，不是错误地发送一个 `extra_body` 字段；temperature 与 max_tokens 与审核配置相同。这个检查没有访问模型服务。
- 估价接口提示 `/openai/v1` 上游路由不应带 `api-version`。本地实际 SDK 请求没有该参数；目前没有证据确认网关实际转发时是否引入其他不兼容字段。
- 在单请求诊断前，thinking 不兼容、网关转发错误或其他上游拒绝原因都只是候选解释。旧错误响应没有留存，不能从旧文件恢复具体原因。后续复现的新增证据见上节。

## 最小下一步：仅复现第一条请求

新增 `boidsnet.runner.gateway_probe`，与完整 smoke 是两个独立批准范围。

- 从真实 `Society` 路径重建 000 组第一个 builder prompt，不手写替代 prompt。
- 保持 dev seed 0、society seed 1001、4 agent × 3 轮方案的第一个已排序 agent、8 道任务菜单、temperature 0.7、thinking disabled、输出上限 4,000 tokens。
- **实际只调用模型一次，不运行剩余 agent 或轮次，不执行生成代码，不进入 solver。**
- 重建请求输入 3,454 bytes，按现有本地费率预留 0.0462912 CNY；诊断执行器总预留上限 0.10 CNY、请求硬上限 1。
- 90 秒总 deadline，零重试、零重定向；无论成功或失败都停止。未知 usage 不退还预留。
- 只能收紧既有预算，不能借诊断入口放宽 8 元 smoke 上限；诊断批准无法用于启动完整 smoke。凭据依然只接受本次专用环境变量或隐藏交互输入。
- 成功只意味着拿到通过响应合同的 API 内容，不代表 Boids 链路跑通；另行报告 builder 解析情况。完整 smoke 仍需新的明确配置确认。

准备（不调用模型；用前一份配置中的不可变镜像 ID）：

```sh
.venv/bin/python -m boidsnet.runner.gateway_probe prepare \
  --config review/agentport_local_smoke_2026-10-06-r2/config.json \
  --out review/agentport_first_request_2026-10-06-r1 \
  --run-out smoke/agentport_first_request_2026-10-06-r1
```

上述 r1 目录现已实际执行并消费批准，不能覆盖或重用。审批模板仍是 `approved=false`，独立 `approval.json` 记录了真实批准；没有保存任何模型凭据。修复后的待审包为 r2。

以下是已经执行过一次的 r1 命令形式，**不可重跑**。r2 必须取得新的明确确认并使用 r2 的所有路径：

```sh
.venv/bin/python -m boidsnet.runner.gateway_probe execute \
  --review review/agentport_first_request_2026-10-06-r1/resolved_config.json \
  --approval review/agentport_first_request_2026-10-06-r1/approval.json \
  --out smoke/agentport_first_request_2026-10-06-r1 --allow-spend
```

这段保留 r1 的使用记录，不构成 r2 批准。确认前不会调用下一次模型。实际扣费与本地预留仍须区分，不能将本地预算宣称为未知服务端费用的绝对上限。

## 验证记录

- 错误诊断修复时的针对性回归：112 项，109 通过、3 跳过，零失败。
- Azure 参数映射与 reasoning 检查修复后：114 项，111 通过、3 跳过，零失败。真实 SDK 内存传输确认顶层 reasoning_effort=none，不发送 thinking 或 api-version。
- 已覆盖真实 SDK 的内存 HTTP 400、嵌套错误、密钥 canary、失败 prompt、usage 缺失、单请求上限、预算只能收紧、停止后禁止重用、两种批准不可混用、Docker pin。
- Docker 准备检查通过；第一请求为 3,454 bytes，与原失败预留记录相符。
- 诊断版本 433a243339ef 的 Docker 四组模拟集成：1 项通过（222.493 秒），96 次模拟调用；未调用真实模型。后续 Azure wire 修改由 SDK 内存传输检查覆盖，不能把模拟集成写成修复后网关实测。
- 完整测试集的最终状态另行补充；模拟结果不当作真实模型证据。

## 研究结论

本轮仍是接口故障定位，separation → 互补工具 → 冻结库效用这条研究链尚未得到真实观测。没有科学正面或负面结果，不调整实验假设、不选取有利样本，也不扩大实验规模。
