# 游戏机制知识速查（一）：国策与政治 · 工业建设与资源 · 科研与装备

> 来源：hagane.works「钢之工坊」HOI4 模组知识社区（https://scharnhorst.hagane.works/zh），基于 1.19.2.0（Operation Postern）原版核对与游戏内实测。可信度标注：「(实测)」=文章有游戏内实测记录；「(核对)」=对照原版静态核对。写模组时用这些数值/写法让内容符合游戏机制，而不仅是语法正确。

## 目录
1. [国策与政治](#1-国策与政治)
2. [工业建设与资源](#2-工业建设与资源)
3. [科研与装备](#3-科研与装备)

---

## 1 国策与政治

### 1.1 国策节点基础 (核对/实测)
- `cost = 5` 是**进度成本**（默认每点 7 天 → 5 点约 35 天），不是政治点花费。
- 奖励只写在 `completion_reward`（完成时发放）；`select_effect` 是点击开始时执行，别把奖励放那。
- **条件写 `available`，不写进奖励块**；「奖励 150 政治点」≠「需要拥有 150」。
- `ai_will_do = { factor = 1 }` 是 AI 选择权重，factor = 0 则 AI 永不点。
- 本地化：国策键 = 焦点 ID（+`_desc`）；改节点 ID 两个键一起改。
- 常见搜索过滤器：`search_filters = { FOCUS_FILTER_POLITICAL FOCUS_FILTER_INDUSTRY }`。

### 1.2 政治数值单位速查（易混，实测/核对）
| 写法 | 含义 |
|---|---|
| `add_political_power = 150` | 一次性 +150 政治点（不是每日、不是设余额） |
| `has_political_power > 100` | 判断，不扣费；≥ / < / > 不同条件 |
| `political_power_gain = 0.5` | 每日**固定 +0.5 点**（不是 +50%） |
| `political_power_factor = 0.15` | 每日政治点比例 +15% |
| `add_stability = 0.05` | 基础稳定度 +5 个百分点（50% → 55%，**不是** 52.5%） |
| `stability_weekly = 0.01` | 每周 ±1 个百分点（持续时间另行安排） |
| `has_stability < 0.95` | 稳定度严格低于 95% |
| `add_war_support = 0.05` | 战争支持 +5 个百分点 |

### 1.3 国策/事件给领袖加特质 (实测)
- 领袖特质：国家作用域直接写
  ```paradox
  add_country_leader_trait = my_leader_reformer      # 加给当前在任领袖
  swap_country_leader_traits = { remove = my_leader_old  add = my_leader_reformer }  # 一步到位，原版 78 处都这么写
  remove_country_leader_trait = X
  ```
- `swap_country_leader_traits` 只在人物作用域可用；一个人物有多个领袖身份时 add/remove 都要加 `ideology = <子意识形态>` 指明改哪个。
- 判断在任领袖：`has_country_leader_with_trait = X`（国家作用域）；人物作用域用 `has_trait`。
- 将领特质必须先进人物作用域（见文件二 §4.1）。

### 1.4 动态精神（变量驱动的实时修正，实测核心知识）
**idea 的修正值只认数字，写变量名=静默无效（不报错）**。"数值会动"的精神必须用动态修正，每天 00:00 重算（先把绑变量修正值清零，再按挂载顺序逐个代入）。

**五件套文件**：
1. `common/dynamic_modifiers/` 修正本体：
```paradox
my_thorn_in_throat = {
    icon = GFX_idea_unknown
    enable = { always = yes }
    army_attack_factor = my_thorn_attack          # 等号右边是变量名
    custom_modifier_tooltip = my_thorn_in_throat_tt   # 说明行手写，引擎只自动渲染总数行
}
```
2. `common/scripted_effects/` 重算（计数 → 折算 → 封顶）：
```paradox
my_thorn_recalc = {
    set_variable = { my_thorn_states = 0 }
    every_state = {
        limit = { is_core_of = ROOT  NOT = { is_controlled_by = ROOT } }
        ROOT = { add_to_variable = { my_thorn_states = 1 } }   # 必须切回国家作用域！
    }
    set_variable = { my_thorn_attack = my_thorn_states }
    multiply_variable = { my_thorn_attack = 0.03 }
    clamp_variable = { var = my_thorn_attack max = 0.5 }
}
```
3. `common/on_actions/` 每日钩子：
```paradox
on_actions = {
    on_daily_MYT = { effect = { my_thorn_recalc = yes } }   # 只对本国跑；全局 on_daily 性能开销大，别用
}
```
4. `history/countries/` 初始化：**先 `set_variable` 再 `add_dynamic_modifier = { modifier = ... }`**（顺序反了第一天为 0 且 has_variable 走错分支）。同一 TAG 可有多个历史文件，勿改原版文件。
5. `localisation/` 文案：`[?my_thorn_states|Y0]`——竖线后格式字符：`0-5`=小数位、`%`=×100 加百分号、`+`=正绿零黄负红、`=`=正数加号、`Y/G/R`=固定颜色。问号不能漏。

- **引擎内建动态变量**（`documentation/dynamic_variables_documentation.md`，国家作用域）：`num_subjects`、`num_faction_members`、`num_owned_states`、`num_of_controlled_states`、`num_core_states`、`num_of_civilian_factories`、`num_of_military_factories`、`casualties_k`、`stability`、`surrender_progress`、`enemies_strength_ratio`。有现成变量就 `set_variable = { x = num_subjects }` 直接复制，别写循环。
- 国策/事件里改变量带提示：`add_to_variable = { my_cavalry_attack = 0.05 tooltip = my_cavalry_attack_tt }`，文案用 `$RIGHT$`（本次加量）/`$LEFT$`（加之前）。
- 想让数字当天就变：在 `on_state_control_changed` 钩子里重算 + `force_update_dynamic_modifier = yes`（该钩子 ROOT=新控制者、FROM=旧控制者、FROM.FROM=州）。
- 坑：循环里不切 ROOT = 计数加到州身上永远 0；修正名本地化键无统一规律（骑兵攻击 `MODIFIER_CAVALRY_ATTACK_FACTOR`，陆军师攻击 `MODIFIERS_ARMY_ATTACK_FACTOR` 多一个 S），用前先搜原版 localisation；loc 键名只允许字母数字下划线点连字符撇号，一个非法字符毁掉文件后面全部条目。

### 1.5 国策通用设计检查
- 奖励只有一次性效果（政治点/精神/外交）时直接写；需要持续修正用精神（`add_timed_idea` 限时）或动态修正。
- 宣战/外交/自治相关写法见文件二 §5；科技加成见 §3.6。

---

## 2 工业建设与资源

### 2.1 建设速度与工厂（核对/实测）
- `production_speed_buildings_factor = 0.10` = 建设速度 +10%。（这里的 production 是**建筑建设**，不是装备生产；不创建建筑；不是直接送工厂。）
- 立即建建筑用效果（需检查所有权/控制权/空槽位）：
  ```paradox
  add_building_construction = { type = industrial_complex level = 1 state = 123 }   # 或省略 state 建在当前州
  ```
- 工厂数量门槛：`num_of_civilian_factories > 10`（触发器，**判断不扣除/预留**；`NOT = { num_of_civilian_factories < 10 }` = 至少 10 座，恰好 10 也满足）。`num_of_factories` 不含贸易/租借临时来源。
- 限时精神（期限写在授予效果里，不写进 modifier）：
  ```paradox
  add_timed_idea = { idea = hag_knowledge_construction_plan  days = 180 }
  ```

### 2.2 工业 modifier 速查（1.19 名）
| modifier | 含义 |
|---|---|
| `industrial_capacity_factory` | 民用+军用工厂产出效率（1.19 名；旧 `factory_output` 已移除） |
| `industrial_capacity_dockyard` | 船坞产出效率 |
| `consumer_goods_factor` | 消费品占用比例 |
| `civilian_factory_use` | 规定效果占用多少民用工厂 |
| `production_factory_max_efficiency_factor` / `..._efficiency_gain_factor` | 工厂效率上限 / 涨速 |
| `local_resources_factor` | 州资源开采量 |
| `production_lack_of_resource_penalty_factor` | 缺资源惩罚 |
| `trade_opinion_factor` | 贸易对好感影响 |

### 2.3 工业/资源常用效果与触发器
- 效果：`add_extra_state_shared_building_slots`（加共享建筑位）、`add_equipment_production`（为装备开新生产线）、`add_resource = { type = steel amount = 5 state = 42 }`（1.19 单数）、`add_offsite_building`、`damage_building`、`build_railway`、`give_resource_rights`、`create_production_license`、`remove_building`、`set_building_level`
- 触发器：`free_building_slots`、`num_of_factories`、`num_of_civilian_factories_available_for_projects`、`has_resources_in_country`、`num_of_military_factories`、`num_of_naval_factories`、`fuel_ratio`、`num_of_controlled_factories`
- ideas 文件 `picture = generic_production_bonus`（填后半段名，自动加 `GFX_idea_` 前缀，别重复写）；`removal_cost = -1` 只挡玩家手动移除，不挡 `remove_ideas`。**定义 ≠ 授予**：保存文件不会让已完成的国策重跑。

---

## 3 科研与装备

### 3.1 科技定义与前置（重点，实测/核对）
```paradox
technologies = {
    my_infantry_smg_1 = {
        research_cost = 1.5          # 默认速度约 150 天；原版主线常用 1.5–2.5
        start_year = 1936            # 超时代惩罚基准年（每早一年 +200% 成本）
        folder = {
            name = infantry_folder
            position = { x = 1 y = 2 }
        }
    }
}
```
- 🔴 **科技前置写在「前置科技」里**，用 `path`（一个键做两件事：画线 + 建立先后要求）：
  ```paradox
  infantry_weapons = {
      path = {
          leads_to_tech = my_infantry_smg_1
          research_cost_coeff = 1
      }
  }
  ```
- 🔴 **科技块里写 `prerequisites` 会报 `Unknown modifier: prerequisites` 且整块被忽略**（prerequisites 是国策/将领特质的关键字；原版 common/technologies/ 零出现）。
- 🔴 **坐标方向**：folder 的 position 是相对偏移，**y 是横轴（往右=年份方向）、x 是纵轴（往下换行）**——填反不报错，节点会落进别人的链条。原版把年份写成常量再用于 y（`@1936 = 2`）。
- `start_year` 只决定超时代惩罚，`position` 只决定画在哪，两者无关。

### 3.2 解锁与加成（两类东西，互不依赖）
```paradox
my_infantry_smg_1 = {
    enable_equipments = { my_smg_equipment_1 }     # 永久解锁；装备须先存在于 common/units/equipment/（ID 拼错静默）
    infantry = { soft_attack = 0.05 }              # 兵种类别块持续加成
}
```
- `enable_subunits`（解锁兵种）、`enable_equipment_modules`、`enable_tactic = my_tactic`（无大括号）、`enable_building = { building = my_building level = 5 }`（块写法）。
- 持续数值也可写 `modifier = { ... }`（与精神同一套 stat 叠加）。
- 完成瞬间弹事件：`on_research_complete = { ... }` + `on_research_complete_limit = { ... }` 防重复触发。
- 「不能自己研究只能国策给」：`allow = { always = no }` + 国策里 `set_technology = { my_tech = 1 }`。
- 🔴 成本类 stat 减号是加成：`build_cost_ic = -0.1` = 生产成本 -10%；写成正数单位更贵；符号写反不报错。科技/学说常见 -5%~-15%。
- `xp_research_type` / `xp_boost_cost` 属装备设计器 DLC 机制，无 DLC 存档不生效。

### 3.3 `allow` vs `allow_branch`（看得见 vs 看不见）
- `allow = { ... }`：持续检查，不满足仍显示但不可手动研究（「看得到但点不了」用这个）。
- `allow_branch = { ... }`：决定可见性，不满足该科技及相连科技一起从界面消失（原版用它配合 `has_dlc` 隐藏 DLC 分支）。

### 3.4 自建科技页签五件套（实测，缺一不可）
科技存在却画不出来，是因为这五处不全：
1. **科技定义**（`common/technologies/*.txt`）：指定 folder 与格子。
2. **folder 声明**（`common/technology_tags/*.txt`）：
   ```paradox
   technology_folders = { mymod_infantry_folder = { ledger = army } }   # ledger: army/navy/air/civilian/hidden
   ```
   同文件 `technology_categories = { }`：科技 `categories = { }` 里每个名字必须先在这里登记（原版登记 134）。
3. **界面容器**（`interface/countrytechtreeview.gui`）：`containerWindowType` 的 **name 必须 = folder id**，内含固定的 `techtree_stripes` 画布容器（名字固定不可改不可省——缺它页签和节点一并不显示且零日志）+ `gridboxtype`。
4. **页签按钮**：name 必须 `<folder_id>_tab`，横向等距 `x = 22 + 89 × n`（22/111/200/289…）。
5. **节点模板**：与 folder 平级、name = `techtree_<folder_id>_item` 的容器（最容易漏的一处）——最省事整段复制原版同类 folder 模板只改名字。

**gridbox 命名规则**：`gridboxtype` 名 = **根科技 id + `_tree`**；「根科技」= folder 内没有被同 folder 任何 path 指向的科技；同一条 path 链共用一个格子。

**失败模式速查**（真实报错）：
| 症状 | 原因 |
|---|---|
| 科技完全不显示 | 根科技没格子；日志 `Found no grid box for tech <id>` |
| 整页科技不显示但页签正常 | 缺 `techtree_<folder>_item`；日志 `Undefined GUI_TYPE`（点开页签后才打印） |
| 页签不出现 | `available` 假 / 没 buttonType / 没声明——**无日志** |
| 页签点了空白 | 容器名与 folder id 不一致——**无日志** |
| 页签节点都不出现 | 漏 `techtree_stripes`——**完全静默** |
| 画出来了但在别人链条 | 两轴搞反（见 3.1） |
| 空框 | 缺 `GFX_<tech_id>_medium` |

🔴 **不要用有 DLC 替换关系的 folder**（1.19.2 中以下名字同时存在但同一时刻只绘制一个，玩家开对应 DLC 你的科技凭空消失零报错）：
- `armour_folder` → `nsb_armour_folder`（No Step Back）
- `air_techs_folder` → `bba_air_techs_folder`（By Blood Alone）
- `naval_folder` → `mtgnavalfolder`（Man the Guns）
- **安全**：`infantry_folder` / `industry_folder` / `electronics_folder` / `support_folder` / `artillery_folder`

### 3.5 研究加成三板斧（区分清楚）
| 写法 | 含义 |
|---|---|
| `add_tech_bonus = { name = HW_industry_bonus  bonus = 0.50  uses = 1  category = industry }` | 限次研究加成（「一次 50% 工业研究」，**不直接解锁**；`category = industry` 是原版科技类别 ID；加成名也要本地化，勿重复定义同一键） |
| `research_speed_factor = 0.05` | 持续百分比加速（精神存在期间一直生效，不按次数） |
| `set_technology = { X = 1 }` | 直接设置科技状态（解锁） |

### 3.6 本地化与编码（科技/通用）
- 科技键 = 科技 ID（+`_desc`）；图标 sprite 名 = `GFX_<tech_id>_medium`（缺失只显空框，不影响研究）。
- **覆盖原版键放 `localisation/<语言>/replace/` 目录**（放普通目录也生效但 error.log 记 loc key collisions）。
- `.yml` 必须 UTF-8 BOM；`.txt` / `.gui` 不能带 BOM；`l_simp_chinese:` 的 l 是小写 L；扩展名 .yml 不是 .yaml 不是 .yml.txt。
- 控制台测试入口：`add_ideas <ID>`（空格无等号，是控制台命令不是 .txt 写法）。
- 验收四查：括号平衡（剥掉 # 注释后数）、与原版 diff 删除行数必须为 0、每个根科技有 `<id>_tree` 格子、每个自建 folder 有 `techtree_<id>_item` 和 `techtree_stripes`。「日志干净 ≠ 做对了」，必须肉眼验收。
