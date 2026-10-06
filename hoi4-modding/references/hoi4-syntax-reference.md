# 钢铁雄心 4（HOI4）模组语法速查笔记（1.19 Operation Postern）

本文为 AI 编写 HOI4 模组的中文速查参考，**以 1.19.2（Operation Postern v1.19.2.0.3eb1）为本机实证基准**，写法与 1.14–1.18 基本兼容，1.19 差异处已标注。脚本文件用 **UTF-8 无 BOM**，本地化 `.yml` 用 **UTF-8 带 BOM**。语法为 `key = value`，`{ }` 为块；触发器与 modifier 对大小写敏感。

> 证据来源约定：标注「(原版 1.19.2)」的条目来自本机游戏安装目录 `common/`、`documentation/`、`localisation/` 等真实文件；其余为知识库补全。

## 1. 国策树（National Focus Modding）

位置：`common/national_focus/*.txt`，文件名无关。顶级块 `focus_tree = { ... }`：

- `id = my_tree`（必填，须全局唯一）
- `country = { factor/add + modifier }`（MTTH 评分块，开局前评估；最高分树被采用，默认分 1）：**评分块 modifier 内用 `tag = FRA`**（原版 1.19.2 法国树原文：`focus_tree = { id = french_focus country = { factor = 0 modifier = { add = 10 tag = FRA } } }`）。`original_tag = XXX` 是**触发器**，用于 `allowed` 等条件位置（原版 `common/ideas/GER.txt`：`allowed = { original_tag = GER }`；决策类别 `SAF_anti_colonialist_crusade = { allowed = { original_tag = SAF } }`），不要混用。
- `default = yes`：全游戏恰有一棵默认树，其余树分数为 0 时启用
- `shared_focus = TAG_focusname`：引入共享国策，**指向不存在的国策会导致主菜单加载崩溃**；这是"保留原版树并扩展"的正确机制
- `continuous_focus_position` / `initial_show_position`：持续/初始面板位置
- `focus = { ... }`：国策本体，**必须嵌在 focus_tree 内**，否则 error.log 报 `[focus] unexpected token`

国策 `focus = { }` 内关键词：
- `icon`（`GFX_focus_...`）、`x/y`（x≈96px/格、y≈130px/行）、`texture = { texture_rotation }`、`search_filters = { FOCUS_FILTER_INDUSTRY }`
- `prerequisites = { focus = TAG_a focus = TAG_b }`（**复数键**，单数 `prerequisite` 引擎不认、整条前置链静默失效）
- `mutually_exclusive = { focus = TAG_c }`（互斥；**双向声明**更稳妥：A 排除 B 的同时 B 排除 A）
- `available_if_capable = yes` / `bypass = { 触发器 }` / `available_if_capitulated = no`
- `cancel_if_not_valid = yes`（一次性分支用）
- `relative_position`、`continue_focus` / `auto = yes`（1.14+ 中断后续做）
- `completion_reward = { 效果块 }`、`available = { 触发器 }`、`ai_will_do = { factor ... }`

**坑**：焦点 ID 即本地化 key（+`_desc`）；`id` 冲突报错；prerequisites 引用缺失 → 焦点永远置灰；国策/精神里的 `add_timed_idea = { idea = X days = 365 }` 是常见限时手法（原版 france.txt completion_reward 中使用）；效果可接受变量值（`add_stability = communism_temp`）。

## 2. 事件（Event Modding）

位置：`events/*.txt`。类型：`country_event`、`news_event`、`state_event`、`unit_leader_event`、`operative_leader_event`（除外观/默认 scope/新闻可关闭弹窗外几乎无差别，ROOT 都是该国；state 事件易混淆，不推荐）。

**命名空间与 ID**：`add_namespace = my_event` 写在**文件顶部、事件块之外**（1.19 原版 events/france.txt 即此写法）；事件 `id = my_event.123`（`<namespace>.<整数>`，整数才合法）。

事件块关键字段：
- `hidden = yes`（隐藏弹窗，仍需 title 或 desc 之一）
- `title = my_event.123.t`、`desc = my_event.123.d`、`option name = my_event.123.a`（loc 惯例与 1.19 原版一致，见 events/france.txt）
- `picture = news_event_...`、`soundeffect`、`timeout_days`
- `is_triggered_only = yes`（只能被效果触发）；若带 `mean_time_to_happen` 而未写此字段则会**随机触发**
- `fires_once = yes`、`trigger = { ... }`、`weight = { base ... }`（多事件竞选）
- `hidden_effect`（触发即执行、无弹窗）、`immediate`（弹窗前执行）
- option 内：效果块 + `ai_chance = { base factor }`、`trigger = { }` 条件化、`execute_as = { 目标 }`
- 触发：`country_event = { id = my_event.5 days = 1 }`；**FROM 即发件方**

**坑**：namespace 未建/ID 非整数/`add_namespace` 置于事件内部 → 静默失效或 malformed token；loc key 缺失只在控制台与 error.log 提示。

## 3. 决议与任务（Decision Modding）

1.19 惯例：**类别定义与决议本体分两个目录**——`common/decisions/categories/*.txt`（00_decision_categories.txt 等）与 `common/decisions/*.txt`（按国别 GER.txt 等）；决议文件顶级块 = 类别 id，类别 id 需与 categories 目录中一致。全部放 `common/decisions/某文件.txt` 的类别块内也能加载，但拆目录是原版风格。

```
my_category = {
    my_decision = {
        priority = 100
        fire_only_once = yes
        days_remove = 30                   # 完成后从列表移除延迟
        days_re_enable = 365               # 可重复决策冷却
        allowed = { original_tag = POL }   # 仅开局/读档查一次（此处用 original_tag 触发器合法）
        visible = { is_subject = no }      # 逐帧查，控制显示
        available = { has_war = yes }      # 逐帧查，控制可点
        complete_effect = { ... }
        remove_effect = { add_political_power = -25 }
        cancel_effect = { ... }
        ai_will_do = { factor = 10 modifier = { ... } }
        target_trigger = { ... }           # 目标型决策（targeted decision）
    }
}
```

**loc 惯例（1.19 实证）**：决议块**没有 `name =` 字段**；显示名 key = 决议 id 本身（`GER_democratic_shield_send_support:0 "Send Military Support to [FROM.GetName]"`），描述为 `<决议id>_desc`；类别显示名 key = 类别 id（原版 `political_actions:0 "Political Actions"`）。**不要写旧式 `category_decision_name` key**。

**坑**：`allowed` 只查一次，别放逐帧条件；mission 不支持 `visible`；`complete_effect`/`remove_effect`/`cancel_effect` 语义不同勿混。

## 4. 国家精神 / 理念（National Spirit / Ideas）

文件 `common/ideas/*.txt`。**嵌套分组写法合法且是原版风格**（原版 1.19.2 `common/ideas/GER.txt`：`ideas = { country = { sour_loser = { ... } } }`——分组名不是 id，第二层缩进的才是 idea id）。

```
ideas = {
    fra_spirits = {
        fra_recovery = {
            name = fra_recovery            # loc key
            modifiers = { stability_factor = 0.10 }
        }
    }
}
```

- 定位字段：`name`（loc key）、`picture`/`texture`、`desc`、`remove_tooltip`
- 生命周期：`cancel_if_not_valid = yes`、`available`、`removal_cost`（原版 -1 表示不可手动移除）、`cancelled_by_idea`
- 数值：`modifiers = { ... }`；可并列 `rule = { can_create_factions = yes }`、`research_bonus = { jet_technology = 0.10 }`（原版 GER.txt 结构）

**1.19 modifier 名对照（实证：modifiers_documentation.md + 原版 common/ideas/GER.txt:126-127）**：

| 旧名（≤1.18） | 1.19 标准名 | 备注 |
|---|---|---|
| `stability` | `stability_factor` | 另有 `stability_weekly`、`stability_weekly_factor`、`war_stability_factor` |
| `war_support` | `war_support_factor` | 另有 `war_support_weekly`、`war_support_weekly_factor` |
| `factory_output` | `industrial_capacity_factory` | 另有 `industrial_capacity_dockyard`、`industrial_capacity_factory_powered` |
| `political_power_gain` | 不变 | |
| `consumer_goods_factor` | 不变 | |
| `research_speed_factor` | 不变 | |
| `production_factory_efficiency_gain_factor` | 不变 | 另有 `_max` / `_start` 变体 |
| `recruitable_population_factor` | 不变 | |
| `local_manpower` | 不变 | 州级 |
| `democratic_drift` 等 | 不变 | 官方文档以 `<Ideology>_drift` 占位符呈现 |

数值支持最多 3 位小数（modifiers_documentation.md 头部声明）。

## 5. 科技（Technology Modding）

科技 `common/technologies/*.txt`；分类 `common/technology_tags/*.txt`。

```
early_fighter = {
    folder = { name = fighter_folder  position = { x = 1 y = 2 } }   # y=横轴（年份方向）、x=纵轴（换行）
    search_filters = { fighter }
    start_year = 1933
    allow = { original_tag = ... }     # 持续检查：不满足仍显示但不可手动研究；allow_branch 控制可见性
    research_cost = 200
    ai_will_do = { factor = ... }
    enable_equipments = { ... }        # 永久解锁装备（装备须先存在于 common/units/equipment/）
    sub_technologies = { ... }
}
```

- 🔴 **前置写法（重要）**：科技的前置写在**前置科技**里：`path = { leads_to_tech = 后续科技 research_cost_coeff = 1 }`（一个键同时画线 + 建立依赖）；**科技块内写 `prerequisites` 会报 `Unknown modifier: prerequisites` 且整块被忽略**（原版 common/technologies/ 零出现；prerequisites 是国策/将领特质的关键字）。
- `research_slots` 是国家属性（`common/countries` 或 `add_research_slot` 效果），不在技术文件里。
- `start_year` 决定超时代惩罚基准（每早一年 +200% 成本），与画图位置无关。
- 加成三类：`enable_equipments`/`enable_subunits`/`enable_building` 解锁；兵种类别块（`infantry = { soft_attack = ... }`）或 `modifier` 持续数值；`on_research_complete` + limit 一次性脚本。
- doctrin 自 1.11 起非"研究"科技，仍按科技定义。
- 自建页签需五件套：technology_tags 声明（ledger + categories 登记）、.gui 容器（名 = folder id + 固定 techtree_stripes 画布）、gridbox（名 = 根科技 id + `_tree`）、页签按钮（`<id>_tab`）、节点模板（`techtree_<id>_item`）——详见 `references/gameplay-politics-economy-research.md` §3.4；🔴 **避开 DLC 会整体替换的 folder**（armour_folder / air_techs_folder / naval_folder）。

## 6. 省份与州治（Province / State Modding）

地图 `map/`：`provinces.bmp`、`definition.csv`、`terrain.bmp`、`heightmap.bmp`、`buildings.txt`。

州治历史 `history/states/*.txt`，`state = { id = 123 ... }`：
- **必填 `id` 且从 1 连续无缺号**，删州要重排 ID 并修正引用，否则无 debug 加载崩溃
- `name = "..."`、`manpower`、`state_category`、`resources = { oil/aluminium/chromium/rubber/tungsten/steel }`（产量语义）、`victory_points = { 省ID = 分 }`、`buildings = { infrastructure/industrial_complex/air_base/naval_base/arms_factory/dockyard 等 }`、`state_buildings`（1.13+ 别名）、`impassable`、`provinces = { }`、`history = { }`
- **查州/省 ID 的方法（本机实证）**：`history/states/<id>-<名>.txt` 文件名 + `localisation/english/state_names_l_english.yml` 的 `STATE_<id>` 条目互证。示例（1.19.2）：云南 = 州 325（`history/states/325-Yunnan.txt`，owner=YUN，provinces 含 1114/1172/1196/1319/1383/1522/1653/4192/4501/5072/7446/7606/8023/10346/10776/12262/12282/12841，VP 1319=昆明），蒙自=4501、普洱=12262、镇雄=5072。
- **新国家不要凭空占位州 ID**（可能与原版冲突）：要么覆盖原版州文件（同名同 ID），要么用"原版最大州 ID + 1"并标注核实

## 7. 国家与角色（Country / Characters）

- 国家标签 `common/country_tags/*.txt`（3 大写字母全局唯一，如 `YUN = "countries/Yunnan.txt"`）
- 历史 `history/countries/<TAG>_....txt`：首 3 字母须为标签；`set_technology`、`add_ideas`、`set_politics`、`load_oob`
- OOB `history/units`，须 `load_oob = TAG_...`（否则建筑分配异常）
- **角色系统 `common/characters/*.txt`**：`characters = { name = { name = loc_key country = TAG role = ... } }`；类型：将领/元帅（`combat_traits`/`leader_rank`/`role = army_leader`）、政治家（`role = politician`）、设计师（`role = military_theorist` 等带 `research_bonus`）、特工（`role = operative` + 谍报机制，La Résistance 起）
- `set_politics` 内 `ruling_party`/`last_election`；`add_officer_ratio`、`set_officer_corps`

**坑**：标签非唯一崩溃/冲突；角色名须本地化；`gfx/` 缺资源灰图标。

## 8. 本地化（Localisation）

目录 `localisation/<语言>/<任意名>_l_<语言>.yml`，**文件名必须含语言内部名**（`l_english` / `l_simp_chinese` / `l_french` …），`l_simp_chinese` 勿写 `l_chinese`。格式：

```
l_english:
 my_focus:0 "我的国策"
 my_focus_desc:0 "$my_desc$ 附加文本 [FROM.GetName]"
```

- **UTF-8 带 BOM**；行首不缩进；数值最多 3 位小数
- 命名惯例：国策/决议 id 即 key（+`_desc`）；决议类别 id 即 key；事件 `namespace.id.t/.d/.a`；精神/角色用 `name` 字段的 key
- 回退：当前语言缺失 → 回退语言（通常英文）→ 显示裸 key
- 动态渲染：`scripted localisation`（§9）与 `[GetName]` 作用域引用

**坑**：BOM 缺失/语言名拼错 → 整文件不读；同 key 后者覆盖前者（加载按文件名序）；引号需转义 `\"`。

## 9. 脚本效果 / 触发器 / 动态本地化 / 1.19 新能力

- **Scripted Effects**：`common/scripted_effects/*.txt`，`my_effect = { 效果 }`，调用 `my_effect = yes`
- **Scripted Triggers**：`common/scripted_triggers/*.txt`，`my_trigger = { 条件 }`，调用 `my_trigger = yes`（大小写敏感，勿大写）
- **Scripted Localisation**：`common/scripted_localisation/*.txt`，`my_loc = { base = XXX trigger = { ... } localisation_key = ... }`，loc 中用 `[MyLoc]` 渲染
- 完整清单：本机游戏 `documentation/triggers_documentation`、`effects_documentation`、`modifiers_documentation`（.md/.html 两种）
- 触发器运算符仅 `=` / `>` / `<`；裸列表默认 AND 短路
- **1.19 资源效果（实证）**：只有单数 `add_resource = { type = steel amount = 5 state = 42 days = 60 show_state_in_tooltip = no }`（Scopes: STATE, COUNTRY；原版 `common/decisions/AFG.txt` 使用）。`add_resources` 复数在文档与原版中均无——不要写。
- **1.19 阵营效果（实证）**：`create_faction = X` 仍存在但**标记 deprecated**："prefer create_faction_from_template instead. It will use the FACTION_DEFAULT_EFFECT_TEMPLATE if the Deeper Factions DLC is enabled."——新机制模板化阵营；兼容性写作保留 `create_faction`，教学推荐 `create_faction_from_template`。
- **1.19 新脚本能力**：数学函数 `pow/sqrt/cos/sin/tan/exp/log`（`common/script_math_functions`）；`impassable_ignored_links`（impassable 州连通忽略列表）；`add_timed_idea = { idea = X days = N }` 限时精神。
- 效果示例（1.19 均存在，拼写不变）：`add_stability`、`add_war_support`、`add_political_power`、`add_ideas`、`remove_ideas`、`add_opinion_modifier = { target = ENG modifier = xxx }`、`create_faction`。

## 10. 模组结构（Mod Structure）

本地模组放 `~/Documents/Paradox Interactive/Hearts of Iron IV/mod`（Windows）：
- **`.mod` 文件** + **模组文件夹**（结构与游戏目录一致）或 zip 并存
- 模组文件夹内含 **`descriptor.mod`**（必须此名，UTF-8 无 BOM）
- 缩略图 `thumbnail.png`（<1MB）

```
name="Test1"
path="mod/test1"                    # 本地路径；Workshop 用 archive
tags={ "Alternative History" }
picture="thumbnail.png"
supported_version="1.19.*"          # 或精确 "1.19.2.0.3eb1"；通配即可
version="1.0b"
replace_path="map/terrain"          # 整目录替换
dependencies={ "OtherMod" }
```

规则：同名文件覆盖、异名文件追加、全覆盖目录用 `replace_path`；`.txt` 无 BOM、loc 带 BOM；Workshop 内容在 `workshop/content/394360/<remote_id>`。**本地 mod 路径不能含非 ASCII 字符**；同名模组只第一个加载生效。

## 11. 常见错误与调试

- 日志：`文档/Paradox Interactive/Hearts of Iron IV/logs/error.log`（启动时截断重写），每行首列文件+行号
- 控制台热重载：`reload focus` / `reload events` / `reload decisions` / `reload localisation` / `tdebug`（显示 tooltip id）
- 常见报错与含义：
  - `[focus] unexpected token` → `focus={}` 错位/括号未闭合
  - `[event] malformed token` → namespace 缺失或事件 id 非整数
  - 裸 key 显示 → loc 缺条目/key 拼写不一致/缺 BOM/语言名错
  - 焦点置灰 → prerequisites 引用缺失或单数 `prerequisite` 键
  - 点击完成无效果 → 效果名错（`political_power` 而非 `add_political_power`）或 modifier 用旧名（`stability`/`war_support`/`factory_output`，1.19 已改名），全部静默无效
  - `[state] duplicate state`/缺号 → 州 ID 冲突或未重排
  - 国策图标重叠 → x/y 布局未调好
  - 科技不显示 → 未改 countrytechtreeview.gui/无 path
  - 角色/旗子灰 → gfx 资源缺失

**原版质量提示**：原版代码也有笔误（如 GER.txt 的 `army_org_Factor` F 大写）——不要模仿；引擎大小写敏感，宁可少写不要写错大小写。

## 版本兼容性要点（1.14 → 1.19.2）

- 多数基础语法自 1.9–1.11 起稳定：shared_focus、事件结构、决议结构
- **1.19 破坏性变更（本机实证）**：modifier 改名（`stability_factor`/`war_support_factor`/`industrial_capacity_factory`）；`add_resource` 取代 `add_resources`；`create_faction` deprecated（推荐 `create_faction_from_template`）
- 1.19.1 新增：math 函数、impassable_ignored_links
- 1.14 AAT / 1.15 Götterdämmerung：未引入核心语法破坏性大改
- 旧版本写法的模组升到 1.19：modifier 旧名会静默失效（error.log 报 unknown modifier），不是崩溃——查文档改名为主

【总体提示】最稳的顺序：descriptor → 本地化 → 国策/事件/决议 → 跑 `scripts/validate_hoi4_mod.py` → 控制台 reload 验。任何 id 类 key 都要配 loc，任何文件夹级覆盖都用 `replace_path`，任何删除都要检查州 ID 连续性，任何 modifier 都要对 1.19 文档核对。
