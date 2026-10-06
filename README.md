# HOI4 AI Modding Skills

为 AI 助手编写的**《钢铁雄心 4》模组开发技能包**（Agent Skills / `SKILL.md` 格式），适用于 Claude Code、Cherry Studio 等支持技能机制的客户端。

> AI agent skills for **Hearts of Iron IV** modding — targeted at game version 1.19.2 (Operation Postern). Written in Chinese.

## 收录技能

| 技能 | 说明 |
|---|---|
| [`hoi4-modding`](hoi4-modding/SKILL.md) | 编写、修改与调试 HOI4 模组代码：国策树、事件、决议、国家精神、科技、州与省份、国家历史、角色、本地化、脚本效果 / 触发器、`descriptor.mod`…… |

## 技能内容

- **工作流**：需求理解 → 结构规划 → 代码与本地化同步编写 → 脚本验证 → 交付自检
- **语法速查**（`references/hoi4-syntax-reference.md`）：各系统全部字段、常见坑与 1.14–1.19 版本差异
- **机制知识库**（`references/gameplay-*.md`）：政治 / 工业 / 科研 / 军事 / 外交 / 领土 / 人物 / 情报八大主题的数值与机制参考（来源：hagane.works 钢之工坊社区，基于 1.19.2 核对与实测）——让设计符合游戏机制，而不只是语法正确
- **验证脚本**（`scripts/validate_hoi4_mod.py`）：括号配对、引用闭环、事件 namespace、整数 id、本地化覆盖、BOM 规范自检
- **评估用例**（`evals/`）：技能触发与输出质量评测样例

## 安装

### Claude Code

将技能文件夹复制到技能目录（保持文件夹名与技能名一致）：

```bash
# 用户级（所有项目可用）
cp -r hoi4-modding ~/.claude/skills/

# 或项目级（仅当前项目）
mkdir -p .claude/skills && cp -r hoi4-modding .claude/skills/
```

### Cherry Studio

- 方法一：设置 → 技能 → 通过本仓库 `hoi4-modding/SKILL.md` 的 GitHub 链接安装；
- 方法二：把 `hoi4-modding/` 文件夹复制到 Cherry 技能库目录（Windows：`%APPDATA%\CherryStudio\Data\Skills\`）。

### 其他客户端

任何支持 Agent Skills（`SKILL.md`）机制的客户端：把 `hoi4-modding/` 整个文件夹放进其技能目录即可；`SKILL.md` 的 YAML frontmatter（name / description）已包含触发条件。

## 使用示例

安装完成后与 AI 对话即可自动触发，例如：

- “帮我的德国国策树加个工业分支”
- “给这个 tag 写一个 1936 年开局事件”
- “这段 HOI4 代码报错（附 error.log），帮我看看哪里不对”
- “设计一条材料学国家精神链，数值要符合 1.19 机制”

## 目录结构

```
hoi4-ai-modding-skills/
└── hoi4-modding/                  # 技能本体（整个文件夹即一个技能）
    ├── SKILL.md                   # 技能定义（frontmatter 描述触发条件）
    ├── references/                # 语法速查 + 机制知识库
    ├── scripts/                   # 验证脚本
    └── evals/                     # 评估用例
```

## 说明与致谢

- 技能面向 AI 助手撰写，默认中文交流；目标游戏版本 **1.19.2（Operation Postern）**，写法与 1.14–1.18 基本兼容（差异在参考文档中标注）。
- 游戏机制参考数据来源：hagane.works「钢之工坊」HOI4 模组知识社区，基于原版 1.19.2 核对与实测。
- 本仓库为社区非官方项目，与 Paradox Interactive 无关联；《Hearts of Iron IV》及相关内容的版权归 Paradox Interactive 所有。

## 许可

[MIT License](LICENSE)
