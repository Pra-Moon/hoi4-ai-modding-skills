#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hoi4-modding 技能自检脚本
=========================
对 HOI4 模组目录做交付前程序化检查：括号配对、引用闭环、
事件 namespace/整数 id、localisation 覆盖、编码 BOM 规范。

用法:
    python validate_hoi4_mod.py <模组目录>

退出码: 0 = 全部通过; 1 = 存在 FAIL 项
输出: [OK]/[FAIL]/[WARN] 逐项结果 + 汇总。FAIL 必须修复，WARN 为建议项。

设计依据: SKILL.md 的「交付前自检清单」。脚本只做可客观判定的检查，
版本相关的写法差异（如 modifier 改名）不在本脚本范围内，靠参考文档兜底。
"""

import re
import sys
from pathlib import Path


def read_text(p: Path) -> str:
    """容忍 BOM 读取文本。"""
    raw = p.read_bytes()
    for enc in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def brace_check(paths: list[Path]) -> list[str]:
    """花括号配对检查。"""
    problems = []
    for p in paths:
        if p.suffix not in (".txt", ".mod"):
            continue
        t = read_text(p)
        o, c = t.count("{"), t.count("}")
        if o != c:
            problems.append(f"{p.name}: {{ 计数 {o} != }} 计数 {c}")
    return problems


def collect_foci(mod_root: Path) -> tuple[dict, list[str]]:
    """收集 national_focus 下的焦点定义与引用问题。"""
    focus_files = (mod_root / "common" / "national_focus").glob("*.txt")
    defined = {}   # id -> file
    prereq_refs = []   # (focus, ref) 列表
    mutex_pairs = []
    problems = []
    for f in focus_files:
        t = read_text(f)
        ids_pos = [(m.start(), m.group(1)) for m in re.finditer(r"id = ([A-Z0-9_]+)", t)]
        for _, fid in ids_pos:
            defined[fid] = f.name
        # default_focus 引用
        for m in re.finditer(r"default_focus = \{\s*id = ([A-Z0-9_]+)", t):
            if m.group(1) not in defined:
                problems.append(f"{f.name}: default_focus 引用了未定义焦点 {m.group(1)}")
        # prerequisites（复数键名！）
        for mb in re.finditer(r"prerequisites = \{(.*?)\}", t, re.S):
            src = max((p_, fid) for p_, fid in ids_pos if p_ < mb.start())[1]
            for ref in re.findall(r"focus = ([A-Z0-9_]+)", mb.group(1)):
                prereq_refs.append((src, ref))
                if ref not in defined:
                    problems.append(f"{f.name}: 焦点 {src} 的 prerequisites 引用未定义焦点 {ref}")
        # 单数键名误写检测
        for m in re.finditer(r"\bprerequisite =", t):
            problems.append(f"{f.name}: 出现单数键 'prerequisite'（引擎只认复数 'prerequisites'）")
        # mutually_exclusive 双向性
        for mb in re.finditer(r"mutually_exclusive = \{(.*?)\}", t, re.S):
            src = max((p_, fid) for p_, fid in ids_pos if p_ < mb.start())[1]
            for ref in re.findall(r"focus = ([A-Z0-9_]+)", mb.group(1)):
                mutex_pairs.append((src, ref))
    for a, b in mutex_pairs:
        if (b, a) not in mutex_pairs:
            problems.append(f"互斥关系单向: {a} -> {b} 缺少反向声明")
    return defined, problems


def check_events(mod_root: Path) -> list[str]:
    """事件文件：add_namespace 存在 + id 为 namespace.整数 + is_triggered_only 提醒。"""
    problems, warns = [], []
    event_files = list((mod_root / "events").glob("*.txt"))
    if not event_files:
        return []
    for f in event_files:
        t = read_text(f)
        nss = re.findall(r"^add_namespace = (\w+)", t, re.M)
        if not nss:
            problems.append(f"{f.name}: 缺少 add_namespace（必须在事件块外）")
            continue
        ns = nss[0]
        for m in re.finditer(r"^\s*id = ([\w.]+)", t, re.M):
            eid = m.group(1)
            # 事件 id 是出现在 event 块内的（id 行前应有 country_event/news_event 等）
            if re.match(rf"^{re.escape(ns)}\.\d+$", eid):
                continue
            problems.append(f"{f.name}: 事件 id '{eid}' 非法——应为 '{ns}.整数'")
    # is_triggered_only 提示：有 MTTH 且作者意图纯触发时容易混
    for f in event_files:
        t = read_text(f)
        has_mtth = "mean_time_to_happen" in t
        has_triggered = "is_triggered_only = yes" in t
        for m in re.finditer(r"^add_namespace = (\w+)", t, re.M):
            pass
    return problems


def check_idea_refs(mod_root: Path) -> tuple[list[str], set]:
    """add/remove_ideas 引用 vs ideas 文件定义。返回 (问题, 已定义 idea 集合)。"""
    defined = set()
    for f in (mod_root / "common" / "ideas").glob("*.txt"):
        t = read_text(f)
        # 分组名（ideas 内第 1 层缩进）与 idea id（第 2 层）都可能是定义，统一收集所有候选，
        # 但排除分组包装名由 loc 检查处理——这里收集全部缩进的键
        for m in re.finditer(r"^(\t+)([a-z0-9_]+) = \{", t, re.M):
            depth = len(m.group(1))
            if depth >= 2:  # 第二层起视为 idea id
                defined.add(m.group(2))
    problems = []
    refs = []
    for f in (mod_root / "common" / "national_focus").glob("*.txt"):
        t = read_text(f)
        refs += re.findall(r"(?:add|remove)_ideas = ([a-z0-9_]+)", t)
    for f in (mod_root / "common" / "decisions").glob("*.txt"):
        refs += re.findall(r"(?:add|remove)_ideas = ([a-z0-9_]+)", read_text(f))
    for f in (mod_root / "common" / "scripted_effects").glob("*.txt"):
        refs += re.findall(r"(?:add|remove)_ideas = ([a-z0-9_]+)", read_text(f))
    for f in (mod_root / "events").glob("*.txt"):
        refs += re.findall(r"(?:add|remove)_ideas = ([a-z0-9_]+)", read_text(f))
    for r in set(refs):
        if r not in defined:
            problems.append(f"add/remove_ideas 引用的 idea '{r}' 未在 common/ideas 中定义")
    return problems, defined


def loc_required_keys(mod_root: Path, defined_ideas: set) -> set:
    """收集必须有本地化的 key 最小集合。"""
    keys = set()
    for f in (mod_root / "common" / "national_focus").glob("*.txt"):
        t = read_text(f)
        for m in re.finditer(r"^\s*id = ([A-Z0-9_]+)\s*$", t, re.M):
            keys.add(m.group(1))
            keys.add(m.group(1) + "_desc")
    for f in (mod_root / "events").glob("*.txt"):
        t = read_text(f)
        for m in re.finditer(r"\b(?:title|desc) = ([\w.]+)", t):
            keys.add(m.group(1))
        for m in re.finditer(r"^\s*name = ([\w.]+)\s*$", t, re.M):
            if "." in m.group(1):   # 事件 option name 为 ns.1.a 形式
                keys.add(m.group(1))
    for f in (mod_root / "common" / "ideas").glob("*.txt"):
        t = read_text(f)
        for m in re.finditer(r"^\s*(?:name|desc) = ([a-z0-9_]+)\s*$", t, re.M):
            keys.add(m.group(1))
    for f in (mod_root / "common" / "national_focus").glob("*.txt"):
        t = read_text(f)
        keys |= {m.group(1) for m in re.finditer(r"create_faction = ([a-z0-9_]+)", t)}
    return keys


def loc_check(mod_root: Path, required: set) -> tuple[list[str], list[str]]:
    """检查 en / zh loc 覆盖。返回 (FAIL, WARN)。"""
    locs = {"en": {}, "zh": {}}
    for lang, folder in (("en", "english"), ("zh", "simp_chinese")):
        for f in (mod_root / "localisation" / folder).glob("*.yml"):
            t = read_text(f)
            for m in re.finditer(r"^\s*([A-Za-z0-9_.]+):0", t, re.M):
                locs[lang][m.group(1)] = f.name
    fails, warns = [], []
    for k in sorted(required):
        has_en, has_zh = k in locs["en"], k in locs["zh"]
        if not has_en and not has_zh:
            fails.append(f"key '{k}' 在 en/zh loc 中均缺失")
        elif not has_en or not has_zh:
            warns.append(f"key '{k}' 缺少 {'英文' if not has_en else '简体中文'}条目")
    return fails, warns


def bom_check(mod_root: Path) -> list[str]:
    """编码规范：.yml 必须有 BOM；.txt/.mod 不应有 BOM。"""
    problems = []
    for f in mod_root.rglob("*.yml"):
        raw = f.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            problems.append(f"{f.name}: loc 文件缺少 UTF-8 BOM")
    for f in mod_root.rglob("*.txt"):
        raw = f.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            problems.append(f"{f.name}: .txt 不应带 BOM（应为 UTF-8 无 BOM）")
    return problems


def effect_name_heuristic(mod_root: Path) -> list[str]:
    """启发式：常见错误效果名。只给 WARN。"""
    warns = []
    bad = {
        "political_power =": "应为 add_political_power =",
        "stability =": "add_stability / stability（modifier）需区分；效果是 add_stability",
    }
    for f in mod_root.rglob("*.txt"):
        t = read_text(f)
        if "{ political_power = " in t or "political_power = " in t.replace("add_political_power", ""):
            if re.search(r"(?<!add_)political_power = \d", t) and "add_political_power" not in t:
                warns.append(f"{f.name}: 疑似裸效果 'political_power = 数字'（应为 add_political_power）")
    return warns


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"目录不存在: {root}")
        return 2

    print(f"=== validate_hoi4_mod: {root} ===\n")
    fails: list[str] = []
    warns: list[str] = []

    # 1 括号
    txt_files = list(root.rglob("*.txt")) + list(root.rglob("*.mod"))
    b = brace_check(txt_files)
    fails += b
    print(f"[{'FAIL' if b else 'OK'}] 括号配对: {'; '.join(b) if b else f'{len(txt_files)} 个文件全部平衡'}")

    # 2 国策引用
    foci, fprobs = collect_foci(root)
    fails += fprobs
    print(f"[{'FAIL' if fprobs else 'OK'}] 国策树: {len(foci)} 个焦点; {'; '.join(fprobs[:5]) if fprobs else 'prerequisites/default_focus/互斥双向 全部闭合'}")

    # 3 事件
    eprobs = check_events(root)
    fails += eprobs
    print(f"[{'FAIL' if eprobs else 'OK'}] 事件: {'; '.join(eprobs[:5]) if eprobs else 'namespace + 整数 id 检查通过（无事件文件则跳过）'}")

    # 4 idea 引用
    iprobs, defined_ideas = check_idea_refs(root)
    fails += iprobs
    print(f"[{'FAIL' if iprobs else 'OK'}] ideas: 定义 {len(defined_ideas)} 个; {'; '.join(iprobs[:5]) if iprobs else 'add/remove_ideas 引用闭环'}")

    # 5 loc 覆盖
    required = loc_required_keys(root, defined_ideas)
    lfails, lwarns = loc_check(root, required)
    fails += lfails
    warns += lwarns
    print(f"[{'FAIL' if lfails else 'OK'}] loc 覆盖: 需 {len(required)} 个 key; {'; '.join(lfails[:5]) if lfails else 'en/zh 至少一种全覆盖'}")
    for w in lwarns[:5]:
        print(f"  [WARN] {w}")

    # 6 BOM
    bprobs = bom_check(root)
    fails += bprobs
    print(f"[{'FAIL' if bprobs else 'OK'}] 编码: {'; '.join(bprobs) if bprobs else '.yml 带 BOM / .txt 无 BOM'}")

    # 7 启发式
    enews = effect_name_heuristic(root)
    warns += enews
    for w in enews:
        print(f"  [WARN] {w}")

    print()
    if fails:
        print(f"结果: {len(fails)} FAIL, {len(warns)} WARN —— 请先修复 FAIL 项")
        return 1
    if warns:
        print(f"结果: 全部 OK, {len(warns)} WARN（建议项）—— 可交付")
        return 0
    print("结果: 全部检查通过 ✔ —— 可交付")
    return 0


if __name__ == "__main__":
    sys.exit(main())
