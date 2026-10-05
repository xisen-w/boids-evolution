# Bug 修复与两轮复核

后续严格复查又发现了本报告未覆盖的缺陷。最新修复、反例和验证边界见
[STRICT_REAUDIT_2026-10-06.md](STRICT_REAUDIT_2026-10-06.md)。
下面保留此前审计记录；历史测试通过不代表后续发现的问题当时已被覆盖。

日期：2026-10-06。范围：本分支的 SAC / DeepSeek 小规模开发诊断路径，以及共用的工具沙箱、冻结和 solver 代码。

两轮均由同一位代码助手自行复核，不冒充独立审稿。没有真实模型实验，没有使用真实 API key；所有反例均为人工 fixture 或模拟客户端。先前的审核文件已失效，必须重新准备并经用户批准。

## 1. 严格审查列出的 11 项问题

| 编号 | 原问题 | 修复及反例验证 |
|---|---|---|
| 1 | Python 模块缓存可绕过历史 import ACL | 在普通 import、相对 import、importlib 和跨工具函数调用入口检查权限。已缓存的未来工具仍不能被早期工具调用；合法传递依赖继续工作。 |
| 2 | 工具的 print 污染 JSON，正确工具被判失败 | 结果走独立 pipe；工具 stdout/stderr 丢弃，不进入结果通道。导入时 print、执行时 print、stderr 和 os.write 均不影响返回值。 |
| 3 | 沙箱启动/挂载/传输故障被算成任务零分 | 使用 SandboxInfrastructureError，穿过 harness 和行为指纹计算直接中止。命令构建、非零退出、非法 envelope、缺失可执行文件均覆盖；pilot 写 INCOMPLETE，不产出完整效用报告。 |
| 4 | 同一审批可在多个新目录重复花费 | 审批绑定代码、配置、run UUID、绝对输出目录；启动前核对当前源码。原子创建单次消费标记，失败后保留；并发只有一个启动者可取得资格。 |
| 5 | 哈希种子没有真正固定 | 干净环境强制 PYTHONHASHSEED=0；不用会忽略它的 -I，改用 -s -S，并在导入模块前删除 cwd 搜索路径。不同父进程种子得到相同 hash / set 顺序。 |
| 6 | 开发 solver 的有效响应和逐次结果被删除 | 私有审计目录保留 prompt、response、glue、imports、verdict、token usage 和 probe seeds；先落盘请求与响应，再评分。公开摘要继续隐藏逐次结果，私有证据明确可由所有者解盲。 |
| 7 | Library(existing_path) 清空原有元信息 | 非空库直接拒绝重新初始化；添加源码使用独占创建，拒绝覆盖。测试逐字节比较已有索引、ACL 和源码不变。 |
| 8 | 400 字符截断删除 execute 签名和 IMPLEMENTS | 优先保留 ID、作者、完整签名和声明，只截断描述/docstring；超长必要元信息受总 prompt 上限约束，不截坏接口。 |
| 9 | Glue 假调用工具后可返回常量或原输入 | 跟踪变量当前值是否来自库调用；最终 return 必须返回工具调用结果或其赋值别名。覆盖死调用、变量被重新覆盖、返回 [] / table。 |
| 10 | 只清理 tools 模块，标准库/builtins 状态仍跨 probe 共享 | 每个 probe 从没有加载生成代码的干净 driver 单独 fork；工具对 builtins/json 的修改不传到下一条 probe。每条 probe 单独计时与回收。 |
| 11 | 本地 SDK/类型错误被当成网络错误重试 | 仅指定 transport 异常及 408/409/429/5xx 可重试。TypeError、ValueError、重定向等立即中止；已收到响应后的解析/usage 错误不会再采样。 |

注意：Python 层的 ACL 检查不是面对任意恶意反射/解释器篡改的安全证明。主机文件和凭据的安全边界仍须由 Linux namespaces、只读最小根和降权提供；本机没有验证这个 OS 边界。

## 2. 复核发现的关联问题

- 冻结库原来只复制静态 import 闭包，会遗漏合法的 importlib 延迟依赖。改为复制历史 ACL 闭包；多保留的模块仍为 dependency-only，不列给 solver，不计为成功协作。
- Library.add 现在同时拒绝非法 ID / 路径穿越以及已有但未入索引的同名源码。
- 旧模型 auto 参数适配若发生在最后一次请求，可能循环结束后返回 None。现在最后一次失败直接抛出，不假装请求成功。DeepSeek 仍固定 strict，不进行参数自适应。
- 第二轮发现 SDK 默认自动跟随重定向，会使单次预算登记对应多次 HTTP 请求。DeepSeek 客户端显式关闭 follow_redirects；真实 SDK 配合内存 302 响应的回归断言只有 1 次请求、1 次预算登记。

## 3. 两轮审核

### 第一轮：代码与实验要求

- 对照 11 个原始反例检查真实控制流；逐项增加回归测试。
- 核对 000 / 100 / 011 / 111 同快照证据、共同权限、同步轮次和共同预算；不改为独立无共享 baseline。
- 核对真实调用只接受伙伴凭据、先用户审核、开发诊断不升级为正式实验。
- 初轮专项：61 项测试，60 通过，1 组 Linux 专属测试跳过。之后补充关联问题、并发消费和错误传播反例。
- 中间修复版本的完整回归：120 项，117 通过、3 跳过，耗时 821.977 秒。耗时主要来自旧协议的 stub 多轮构建及逐 probe 隔离，不是 API 等待。

### 第二轮：完整回归、传输复核与交付检查

- 再次检查缓存导入、每条 probe 状态、退出状态、返回值数据流、审批重放、审计文件权限和失败报告。
- 第二轮完整离线回归：126 项，123 通过、3 跳过，耗时 806.425 秒，没有失败。
- 完整回归启动后，第二轮传输复核又关闭了 SDK 自动重定向。该最后局部修复之后重新运行全部缺陷反例、SAC、sandbox 和 model 专项：68 项，67 通过、1 组 Linux 专属测试跳过，耗时 5.381 秒。
- 静态编译、依赖一致性和 git whitespace 检查已通过。
- 新生成的审核模板仍是 PENDING_HUMAN_REVIEW / approved=false，准备过程 0 次模型请求。
- 仅源码、配置、测试和文档进入提交；运行目录、审批实例、私有审计数据和消费标记不进入 Git。
- 最终 runner + env 的 SHA-256：`f6fc30a0cc9af656cdd6b4bbf7f3b507d20537d4f833f05caa93de93ebbd77cf`。最终缺陷反例文件共 22 个测试。

## 4. 运行边界

- 这不是“整个仓库绝无 bug”的保证，也不是 Boids 有效性的证据。
- 本次 macOS / Python 3.9.13 离线检查无法验证 Linux OS 隔离。真实执行仍拒绝 hook-only。
- 缺少可选 matplotlib 的两个历史绘图测试不计为通过；不因修复实验路径而安装或修改无关绘图依赖。
- 新超时定义为每条 probe 5 秒，不再是整批共 5 秒。新审批须包含这个配置语义。
- 没有启动 DeepSeek 验证、pilot 或主实验；每次真实调用仍需用户先审核完整配置。现有一次 seed / 四个工具库的提案不变。
- 尚未实现的论文级 M_cross / edge ablation / 汇总分析不在这次 bug 修复范围内，详见 [SAC 审核卡](SAC_DEEPSEEK_REVIEW.md)。

## 5. 复核入口

```bash
python -m unittest tests.test_bugfix_regressions -v
python -m unittest discover -s tests -t . -v
python -m compileall -q boidsnet tests
python -m pip check
git diff --check
```

`tests/test_bugfix_regressions.py` 是本轮反例集合。测试使用临时目录和人工代码；不向模型服务发送请求。完整回归还覆盖旧 behavioral 协议，防止共用模块修复破坏原路径。
