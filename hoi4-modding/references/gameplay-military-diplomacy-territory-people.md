# 游戏机制知识速查（二）：军事与后勤 · 外交与战争 · 领土与占领 · 人物与情报

> 来源：hagane.works「钢之工坊」HOI4 模组知识社区（https://scharnhorst.hagane.works/zh），基于 1.19.2.0（Operation Postern）原版核对与游戏内实测。可信度标注：「(实测)」=有游戏内实测记录；「(核对)」=对照原版静态核对。情报主题在站点无专题页（404），本文件情报部分来自站点 wiki 收录的游戏自带文档命令。

## 目录
4. [军事与后勤](#4-军事与后勤)
5. [外交与战争](#5-外交与战争)
6. [领土与占领](#6-领土与占领)
7. [人物与情报](#7-人物与情报)

---

## 4 军事与后勤

### 4.1 将领特质系统（实测核心知识）

**文件位置**：`common/unit_leader/*.txt`（外层 `leader_traits = { }`）；loc 键 = 特质名 + `_desc`；图标精灵名固定 `GFX_trait_<特质名>`（登记在 `interface/*.gfx`，不登记显示问号奖章）。

**两类获得方式**——靠打仗攒 vs 直接给/买：

```paradox
leader_traits = {
    my_plains_fighter = {
        type = corps_commander        # 元帅写 field_marshal；两者皆可写 land
        gain_xp = {                   # 攒经验条件：战斗作用域（每场正在打的仗都检查）
            is_fighting_in_terrain = plains
        }
        # 将领本人条件（如部队数量）写 gain_xp_leader = { ... }（将领作用域）
        custom_gain_xp_trigger_tooltip = my_plains_fighter_when   # 「获取经验值当：」后的文案键
        cost = 100                    # 攒到多少经验才能分配（门槛，原版常见 500–1500）
        modifier = { army_infantry_attack_factor = 0.05 }         # 给带的部队；给本人用 non_shared_modifier
        ai_will_do = { factor = 1 }   # 0 = AI 永不点
        gui_row = 0                   # ≥0 才进树；不写玩家看不见
    }
}
```

- 机制数值：分配特质时额外扣**全局固定 15 点陆军经验**（`UNIT_LEADER_ASSIGN_TRAIT_COST`，与 cost 无关）；经验攒到 5% 以上提示框才显示进度（`LEADER_TRAITS_XP_SHOW`）。
- 剧情直接给（不看 cost/gain_xp）：人物档案 `corps_commander = { traits = { ... } }` 或 `random_army_leader = { limit = { NOT = { has_trait = X } } add_unit_leader_trait = X }`；海军 `random_navy_leader`；全部 `every_army_leader`。
- 限时特质（仅将领）：`add_timed_unit_leader_trait = { trait = X days = 90 }` 到期自动移除；`add_timed_country_leader_trait` 原版零使用。
- 扩展块：`modifier`（带的部队）、`non_shared_modifier`（本人）、`field_marshal_modifier`（仅元帅时）、`corps_commander_modifier`、`sub_unit_modifiers`（按兵种）；33 条带 `slot = high_command` 可被雇为高级指挥。
- 坑：**国家作用域直接写 add_unit_leader_trait 无效**（只认人物作用域）；将领条件写进 gain_xp 失效（作用域不对）；修正不包 `modifier = { }` 块（那是领袖特质写法）就无效；兵种比例写法参考原版步兵指挥官：`gain_xp = { check_expr = { value = num_infantry greater_than = { value = num_units multiply = 0.8 } } }`。

**将领特质树**（实测）：
- 前置三种：`any_parent = { a b c }`（任一，原版 41 处）、`all_parents = { a b c }`（全部，0 处）、`parent = { traits = { a b c } num_parents_needed = 2 }`（点亮 N 个，1 处）。any_parent = num_parents_needed=1 的简写。
- 起点（根）**不写 trait_type**（原版 16 条根特质都这样）；分支写 `trait_type = assignable_trait` + `gain_xp = { always = no }`。起点写了 assignable_trait 会报 `wrong kind of parent`、树画不出来。
- 互斥 `mutually_exclusive = <对方id>` **必须两边都写**。`prerequisites = { }` 是树之外的门槛（将领作用域判断，原版仅 3 处、均 has_trait 人格类），与 any_parent 连线是两回事。
- 行列：`gui_row` 从 0 数（原版陆军用到第 15 行，自建从 16 行起不冲突）；`gui_column` 不写引擎按 trait_type 自动分列（原版仅海军 29 条写）；**同行同类都不写列 → 两特质叠同一格只显示后加载的**；`gui_column = 3` 会被滚动条挡一半。
- `trait_type` 取值：`assignable_trait`（可买）、`personality_trait`（随机人格）、`basic_terrain_trait`/`assignable_terrain_trait`（地形）、`status_trait`（伤病/被俘状态）、`basic_trait`（特工）、`exile`。

### 4.2 补给与后勤（实测/核对）
- `supply_consumption_factor = -0.10` 才是**减少 10% 补给消耗**（负号不能省略；写 +0.10 更耗）。只改**需求侧**（地面部队所需补给量）；铁路/补给枢纽/运输是供给侧，不是同一参数；燃油（坦克）另算。
- 完整精神文件示例：
  ```paradox
  ideas = {
      country = {
          HW_supply_training = {
              picture = generic_army_war_college     # 引原版图，不写 GFX_idea_ 前缀
              removal_cost = -1
              modifier = { supply_consumption_factor = -0.10 }
          }
      }
  }
  ```
- 定义 ≠ 获得：`add_ideas = ...` 写在国策 completion_reward / 事件 option；已完成的国策不会重跑。

### 4.3 军事相关钩子与效果精选
- 派遣类钩子：`on_send_attache`、`on_send_volunteers`、`on_lend_lease`（外交面板「派遣军事顾问」脚本里就是 attaché）；判断 `has_attache_from`、`has_volunteers_amount_from`、`is_lend_leasing`。
- 完整 effect/trigger/modifier 查本机 `documentation/` 或站点 wiki 词典（§8 说明）。

---

## 5 外交与战争

### 5.1 外交三层结构（写错层 = 最常见的错误）
1. **开局状态** → `history/countries/<TAG>.txt` 顶层（开局执行一次）：`add_to_faction`、`give_guarantee`、`set_autonomy`、`diplomatic_relation`、`add_opinion_modifier`。
2. **运行时效果** → 国策 `completion_reward` / 事件 `option` / 决议效果块（同一批效果，仅时机不同）。
3. **定义** → `common/wargoals/`（宣战理由类型）、`common/opinion_modifiers/`（好感修正）、`common/autonomous_states/`（自治档）——**定义自身不做任何事，被效果引用才起作用**。

参考计数：历史文件 `diplomatic_relation` 的 relation 原版只出现六种值：`non_aggression_pact`(139)、`guarantee`(110)、`military_access`(35)、`docking_rights`(14)、`puppet`(2)、`air_base_access`(2)——别发明新值。国策最常见外交效果：create_wargoal(1072)、add_opinion_modifier(913)、add_state_claim(507)、set_autonomy(149)；事件 add_to_faction(494)。

### 5.2 好感修正（opinion_modifiers）
```paradox
# common/opinion_modifiers/my_mod.txt —— 先定义再引用！
opinion_modifiers = {
    my_league_friendship = {
        value = 50
        months = 12
        decay = 1        # 带计时：每天衰减 1 点，一年消失；永久只写 value
    }
}
```
- 方向性（写反不报错）：A 作用域 `add_opinion_modifier = { target = B modifier = X }` 改 **A 对 B** 的好感；`reverse_add_opinion_modifier` 改 **B 对 A**——想让别国喜欢你用 `reverse_`（原版 87 处全是「签约后对方好感上升」场景）。
- 引用未定义的好感修正：不崩溃，什么都不发生。
- 判断：`has_opinion = { target = GER value > 50 }`（**原版写法是 `value >` 不是 `=`**）。

### 5.3 宣战理由与宣战
```paradox
completion_reward = {
    create_wargoal = {
        type = annex_everything
        target = BEL
    }
}
# 后续国策条件：
available = { has_wargoal_against = BEL }   # 或 has_wargoal_against = { target = BEL type = annex_everything }
# 直接开战（原版国策仅 64 处，剧情一般把开战决定留给玩家）：
completion_reward = { declare_war_on = { target = BEL type = annex_everything } }
```
- `type` 必须存在于 `common/wargoals/`：原版国策用得多 `annex_everything`(533，吞并全部)、`puppet_wargoal_focus`(226，傀儡化)；要指定州用 `take_state_focus` + `generator = { 州编号 ... }`。
- 类型定义里 `allowed = { always = no }` 只挡**玩家手动正当化**，不挡国策直接发放（不经过正当化、不涨紧张度）。
- 过期：类型定义可写 `expire`；效果里 `expire = 0` = 永不过期（实测不写与写 0 相同，都不显示逾期日期）；写正数天才会显示。后续条件 `has_wargoal_against`（没有 `has_war_goal_against` 这种拼写）。
- 坑（实测）：type 不存在 → 加载时 error.log `invalid war goal: <名字>: type`（带文件名行号）；**target 写错标签 → 无日志、无效果**（荷兰是 HOL 不是 NED，以 `common/country_tags/` 为准）；历史文件写 create_wargoal 原版仅 1 处。

### 5.4 阵营
```paradox
completion_reward = {
    set_rule = { can_create_factions = yes }   # 只开玩家手动建阵营按钮（默认无国能手动建）
    create_faction = my_league_name            # 值是本地化键！（写中文会显示键名原文）
}
# 拉人（必须由阵营领袖作用域执行；available 用 is_faction_leader = yes 守门）：
completion_reward = { add_to_faction = BEL }
# 加入别国阵营：GER = { add_to_faction = ROOT }
```
- `set_rule` 管手动按钮、**不拦效果**（实测不写真照建）。
- 对方已在别的阵营时不进来——先 `is_in_faction = no` 判断。同阵营判断 `is_in_faction_with = BEL`。
- 🔴 1.19：`create_faction` 官方标记 deprecated，推荐 `create_faction_from_template`，但模板机制要求「No Compromise, No Surrender」DLC（原版 171 处模板用法全包 `has_dlc`）；**不做 DLC 的 Mod 继续用 `create_faction`**（原版 1.19.2 自己还有 27 处国策这么写）。

### 5.5 自治档与附庸（实测）
- 位置：`common/autonomous_states/`，一档一个文件，骨架照原版 `puppet.txt` 改数值最稳：
  ```paradox
  autonomy_state = {
      id = my_autonomy_protectorate   # set_autonomy/has_autonomy_state 引用它；本地化键必须 = id
      is_puppet = yes                 # 决定 is_puppet_of 是否为真
      min_freedom_level = 0.55        # 自由度下限，各档必须互不相同
      manpower_influence = 0.5        # 宗主可抽人力份额（原版傀儡 0.9）
      rule = { can_not_declare_war = yes  can_decline_call_to_war = no }
      modifier = { autonomy_manpower_share = 0.5  extra_trade_to_overlord_factor = 0.5 }
      ai_subject_wants_higher = { factor = 1.0 }
      ai_overlord_wants_lower = { factor = 1.0 }
  }
  ```
- 机制数值：**升降一级所需自治点数 = 相邻两档 min_freedom_level 之差 × 5000**；各档下限不能相同（原版 21 档各不相同）；`freedom_level = 0.6` 实测显示 150/250 点。
- 🔴 `default = yes` 只有原版傀儡档能写（和平会议优先用）；自定义档写了会和原版打架。
- 设置：`set_autonomy = { target = HOL autonomy_state = my_autonomy_protectorate freedom_level = 0.6 }`；自带 `end_wars`/`end_civil_wars` 开关默认 yes。
- **两种拼写都接受**：国策/事件里 540 处用 `autonomy_state`，历史文件里 23 处用 `autonomous_state`——按文件类型沿用。
- 图标：精灵名固定 `GFX_<id>_icon`（定义在 interface/*.gfx、贴图 gfx/interface/autonomy/）；不定义档照样生效只显示问号。
- 解除附庸 `end_puppet = HOL`（原版事件 36 处）；条件：`HOL = { has_autonomy_state = ... }`、`is_subject_of`（含所有档）、`is_puppet_of`（只看 is_puppet）。
- 坑：target 标签错 → error.log `_set_autonomy_: invalid target tag ---` 且不执行。

### 5.6 常用外交条件速查
`has_wargoal_against = BEL`（可块限定 type）· `is_in_faction_with = BEL` / `is_in_faction = yes` · `is_subject_of = GER` · `has_autonomy_state = autonomy_puppet` · `has_guaranteed = BEL` · `has_opinion = { target = GER value > 50 }`（用 `value >`）· `has_rule = can_create_factions`。

---

## 6 领土与占领

### 6.1 州文件结构（核对/实测）
```paradox
# history/states/8-Luxembourg.txt（原版 1.19.2 示例）
state = {
    id = 8
    name = "STATE_8"              # 本地化键，不是文本
    state_category = town         # 决定建筑槽位
    manpower = 294748
    resources = { steel = 14 }
    history = {
        owner = LUX
        add_core_of = LUX
        buildings = { infrastructure = 3  arms_factory = 1  industrial_complex = 3 }   # 州级建筑直接写
        6583 = { naval_base = 1 }            # 省级建筑（港口/碉堡）套在省份编号子块
        victory_points = { 6583 5 }
        1939.1.1 = { ... }                    # 历史可放日期子块
    }
    provinces = { 6583 13375 }
}
```
- **文件名规则**：同名文件替换原版；**文件名不同但州编号相同 → 报 `State ID conflict`，后加载的赢**。覆盖原版必须用原版确切文件名（原版文件名不全是「编号-州名」，如 `560-TS 2.txt`，照抄磁盘目录）。
- 本地化：州名 `STATE_<编号>`；地图城市标签 `VICTORY_POINTS_<省份编号>`；覆盖键放 `localisation/<语言>/replace/`（放普通目录也生效但 error.log 记 loc key collisions）。
- 原版数字（1.19.2.0）：1081 州、13414 省份（陆地 10155、湖泊 126、海洋 3133）；**湖泊也属于州**，切州筛选按「排除海洋」不要按「只要陆地」。

### 6.2 五条硬规矩（每条都有实测后果）
1. **州编号必须从 1 连续到最大值**（原版最大 1081）：缺一个 → `Missing State ID` + 主菜单地图加载失败；新建 1083 跳过 1082 就进不去。
2. **一个州所有省份必须同属一个战略区**（`map/strategicregions/`，原版 304 个文件）：违反 → MAP_ERROR 并印出两个区名，主菜单进不去。
3. **一个省份只能属于一个州**：违反 → 启动崩溃（最严重）。
4. **改了省份归属必须同步 `map/buildings.txt`**（第一列是州编号，见 §6.4）。
5. **首都必须指向自己拥有的州**：违反 → `Attempting to set capital state #N ... they dont own it!`，引擎拒绝并回落。
- 其他坑：州文件带 BOM → 报 `Unexpected token: ï»¿state` 整份作废（连锁触发编号缺失）；`.yml` 正相反必须带 BOM；陆地省份不属于任何州 → 游戏能进但弹 MAP_ERROR；州引用不存在的省份 → `Malformed token` 只丢那一个引用。

### 6.3 州层 vs 国家层效果对照（六个效果两种写法，实测）
| 效果 | 作用域 | 写法 | 用途 |
|---|---|---|---|
| `transfer_state = 6` | 国家层 | 直接写州编号 | 转交（所有者和控制者一起变）；不接受列表，一行一个州 |
| `add_state_core = 6` | 国家层 | 直接写 | 给本国加核心 |
| `set_state_controller = 7` | 国家层 | 直接写 | 只改控制者 = 占领（顺从/抵抗机制保留） |
| `add_claim_by = GER` | 州层 | `6 = { add_claim_by = GER }` | 给某国加宣称 |
| `add_compliance = 50` | 州层 | `7 = { add_compliance = 50 }` | 加顺从度 |
| `set_state_name = "..."` | 州层 | `7 = { set_state_name = "新名" }` | 改显示名（运行时改，不是 loc 键） |

- 🔴 坑：**州层效果直接写在国策奖励里 = 拿不到州、什么都不发生**（无报错）；只转交不加核心 = 非核心领土（人力/工厂按非核心打折）；想要占领区却用 transfer_state 会把所有者一起改掉；州编号 ≠ 省份编号（两套系统）；`available` 用 `owns_state` 做「拥有某州」条件；移除核心同加核心（`remove_core` 类）。

### 6.4 重切州（不重画地图只重分组，实测方法论）
- 白拿：省份邻接、地形加成、海岸线港口位坐标、河流渡口、胜利点位置。代价：州界只能落在原版省界上。
- 约束实操：① 被吃空的编号必须由新州认领（用原版那个文件名输出）；② **先按战略区切块再按行政区划分组**（战略区不可拆）；③ 一省一州，重编号后清空输出目录防残留旧文件；④ 建筑表以州编号为键必须重写；⑤ 复用被吃空编号可能抢原版国家首都——扫 `history/countries/` 把首都落在已占用州上的国家改指。
- 「洞」检查：取所有未被认领的非海洋省份求**连通分量**，最大的是外部世界，其余每个都是被你包围的洞（含湖）。

### 6.5 建筑表 map/buildings.txt（最反直觉的一章，实测）
- 原版 66664 行、第一列州编号、**文件末尾没有换行符**。
- 引擎从坐标反查省份再校验：对不上**丢弃该行并把正确答案印在报错里**——`map/buildings.txt error at line 50927: ... Supposed to be '8 - ...' but was '1082 - ...' for province 13375. BUILDING IGNORED!`——**照抄报错里的答案，不要自己模拟引擎采样像素**（差一个像素取到邻州、港口坐标采到海洋省份是两条真实损坏路径）。
- 港口不靠像素定位：每行最后一个 `sea_province` 字段 + 真实邻接。边界未动的州原版键仍权威（可做逐行比对的事前回归检查）。
- **十类建筑位每州定额**（全表行数是 1081 的整数倍）：机场/火箭基地/要塞网/合成炼油厂/核反应堆/雷达站/燃料库 各 1 行；军用/民用工厂 各 6 行；防空阵地 3 行。缺了报 `MAP_ERROR: no air base site defined for state N`；**后三类（工厂 2 类 + 防空）缺失时引擎不写任何日志、点开始游戏当场死**（实测）；修法 = 整行搬迁（州键和坐标一起改，坐标必须落在目标州境内）。港位 ≠ 港口：港口建筑写在州文件 buildings 块按省份编号（`6583 = { naval_base = 1 }`），两件事分开。
- 调试纪律：`-debug` 启动参数（否则闪退时 error.log 可能是空的）；六个致命模式关键词：`BUILDING IGNORED`、`no port building in the nudger`、`Missing State ID`、`provinces belonging to different strategic areas`、`dont own it`、`invalid province building`；MAP_ERROR 前缀也出现在大量无害噪音里（如「你这个时代不该有的机场位缺失」占日志九成），要建良性噪音清单；崩溃看四处：error.log / game.log / crashes/<最新>/exception.txt / 快照 logs。

---

## 7 人物与情报

### 7.1 人物系统（实测核心知识）
- **一个人物 = 一份档案 + 一到多个身份块**（`country_leader` / `corps_commander` / `field_marshal` / `navy_leader` / `advisor` / `scientist` / `operative`），可兼任。「一人两职是一个人物不是两个」——古德里安式将军兼理论家要写两个块挂**同一档案**；建两个人会得到互不知道的两个角色，无任何报错。
- 文件：`common/characters/*.txt`，外层 `characters = { }`：
  ```paradox
  characters = {
      my_leader = {
          name = my_leader
          portraits = { civilian = { large = GFX_portrait_my_leader  small = GFX_portrait_my_leader_small } }
          country_leader = {
              ideology = conservatism     # 🔴 必须子意识形态（conservatism 级，不是 democratic 大类）！
              traits = { ... }
              expire = "1965.1.1.1"       # 出场期限
              id = -1
          }
      }
  }
  ```
- 🔴 **领袖身份必须填子意识形态**，否则报两条错（无效意识形态/没有对应政党）、领袖身份作废。
- **定义为在场 ≠ 在国**：必须在该国 `history/countries/` 文件里 `recruit_character = 人物ID`——**这条效果只能写历史文件**，写进 on_actions 会被引擎明确拒绝。
- 坑：头像缺失**不报错**、直接显示通用脸（必须肉眼验收；「error.log 会报 Could not find portrait」在 1.19.2 不成立）；科学家特质只对特殊计划生效；特工身份块需要 La Résistance DLC，`nationalities = { ... }` 列出可招募国、留空 = 任何国家可招。

### 7.2 政治顾问（实测）
```paradox
advisor = {
    slot = political_advisor
    idea_token = my_advisor
    allowed = { original_tag = MYT }
    traits = { silent_workhorse }
    cost = 150
    visible = { has_completed_focus = my_focus_unlock_advisor }   # 不满足=完全不在候选（隐藏用这个）
    available = { ... }                                           # 不满足=在候选但灰掉点不了
    on_add = { owner = { add_stability = 0.05 } }                 # 🔴 必须 owner = {} 跳回国家作用域！
    on_remove = { owner = { add_stability = -0.05 } }
    modifier = { political_power_gain = 0.25 }                    # 每日固定 +0.25 点，不是 +25%
}
```
- 🔴 **裸写 `add_stability` 在 on_add 里：引擎加载时直接拒绝**，error.log 报 `Invalid scope type for effect add_stability in common/characters/...`，雇用时无事发生。原版 188 处 on_add 里 123 处用 `owner = { }`、**零处裸写**。
- 三块效果别混：`on_add`（雇用瞬间一次）、`on_remove`（解雇瞬间）、`modifier`（任期内持续，解雇即消失）。持续加成放特质可复用（原版 4459 个顾问只有 1 个直接带 modifier 块）。
- `removal_cost = -1` 做不可解雇 1.12.8 之后失效 → 用 `can_be_fired = no`。
- 覆盖原版 loc 键放 `localisation/<语言>/replace/`，否则被原版压掉且无提示。

### 7.3 换领袖与继位（实测）
- **同意识形态的第二位领袖开局不会自动上台**（正常引擎行为，只是候选人）。
- 提拔：`promote_character = 人物ID`（推到该党首位，执政党即国家领袖；多意识形态须指明）。
- 退场：`retire_country_leader = yes`（卸任，原版 157 处，人还在）vs `kill_country_leader = yes`（死亡并移除，48 处）；下一顺位都是该党另一位领袖。指定不在任的人退场：`retire_character = 人物ID`（移除全部身份）。
- 🔴 实测坑：**已死亡的人再 promote——弹窗照常、无事发生、日志零输出**。剧情上可能「先死后被提拔」的人用退休不要用死亡。
- 临时领袖（不建人物）：`create_country_leader = { name = "..." picture = GFX_... expire = "1965.1.1" ideology = conservatism }`——之后无法按名字 promote/retire（没有人物档案）。
- **替换原版领袖**：不要重复定义同名人物（报 `Multiple character have the tag`）。标准做法 = 开局隐藏事件（`hidden = yes` 的 country_event，immediate 里 `retire_country_leader = yes` + `create_country_leader`）+ 把同一段退休/创建写进该国历史文件（让国家选择屏直接显示新人）。

### 7.4 情报 / 间谍命令速查（wiki 收录 1.19.2 游戏文档）
**效果**（常用 14+）：
- 机构：`create_intelligence_agency = yes`（或 `{ name = "..." icon = "GFX_..." }`；无机构时才生效，重复调用无效；自定义 icon 要先在 .gfx 注册）；`upgrade_intelligence_agency = upgrade_army_department`（机构必须已存在）。
- 特工：`create_operative_leader = { bypass_recruitment = no  available_to_spy_master = yes  portrait_tag_override = TAG  gfx = GFX_...  gender = male }`（先建机构；bypass_recruitment=no + available_to_spy_master=no 时特工凭空消失）；`every_operative` / `random_operative`（COUNTRY/OPERATION 作用域；random 的 limit 写在子块里）；`turn_operative`（策反，转移并在原国「死亡」、触发 on_operative_death）；`capture_operative = PREV` 或 `{ captured_by = GER }`；`free_operative` / `free_random_operative`（`all` 参数=释放全部）；`kill_operative`（杀死并锁槽位）；`harm_operative_leader`（人物作用域，非特工角色则无效不报错）；`force_operative_leader_into_hiding = 12`；`operative_leader_event`（必须在 CHARACTER 作用域）。
- 情报值：`add_intel = { target = POL  civilian_intel = 3  army_intel = 1 }`（四类：civilian/army/navy/airforce，0 可省略）；`add_decryption`；`add_operation_token = { tag = GER token = some_token_id }`（token 大小写敏感、tag 是**目标国**不是自己）；`remove_operation_token`；`set_faction_spymaster`。

**触发器**（常用）：`has_intelligence_agency`、`has_done_agency_upgrade`、`agency_upgrade_number`、`has_operation_token`、`is_spymaster`、`is_operative`、`operative_leader_mission`（任务）、`operative_leader_operation`（行动，均 CHARACTER 作用域）。

**modifier**：`<army/navy/airforce/civilian>_intel_factor`（对目标情报获得）、`_intel_to_others`、`_intel_decryption_bonus`、`decryption` / `decryption_power` / `encryption` 系、`enemy_operative_detection_chance(_factor)`、`enemy_operative_capture_chance_factor`、`agency_upgrade_time`、`intelligence_operation_speed`、`intelligence_agency_defense`、`enemy_intel_network_gain_factor_over_occupied_tag`。

---

## 8 脚本参考与通用排错

### 8.1 站点脚本参考 wiki 结构
三本「词典」（条目页 = 游戏文档定义 + 游戏内提示文案 + 实战坑）：effect 553 条、trigger 596 条、modifier 数百条（按字母索引）。查具体关键字比翻文章快，本机同源资料在游戏 `documentation/` 目录。

### 8.2 跨主题通用坑（从网站全部实测文章提炼）
- 占位 ID（人物/特质/科技/精神/修正）必须全局唯一；ID 拼错多为静默失败。
- 覆盖原版本地化键 → 放 `localisation/<语言>/replace/`。
- **error.log 无报错 ≠ 生效**。静默失败清单：装备 ID 拼错、好感修正未定义、国家标签写错（HOL/BEL，以 common/country_tags/ 为准）、缺 .gui 声明、缺 BOM、idea 里写变量名、州层效果写错作用域。
- 「已核对资料」与「游戏内实测」是两档可信度——写数值时优先用实测结论。
- 验收流程：error.log 搜自己的文件名/ID（`-debug` 启动）→ 逐层回查（加载→获得→显示→生效）→ 报错行往前找缺引号/缺右括号。
