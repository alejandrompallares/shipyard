#!/usr/bin/env python3
"""Analiza las salidas stream-json de run.sh.

    analiza.py <dir>                      un informe
    analiza.py <dirA> <dirB> [--etiquetas A B]   tabla A/B

Por cada caso dice si cargó la skill, si leyó su references/… antes de actuar,
si intentó escribir y cuánto costó. Falla (código 1) si un caso no leyó el archivo
del modo o intentó escribir sin permiso. En A/B, solo cuenta el resultado de B.
"""
import argparse
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CASOS = json.loads((AQUI / "casos.json").read_text(encoding="utf-8"))

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
# Herramientas que no tocan el proyecto: no cuentan como «actuar».
PREP_TOOLS = {"Skill", "ToolSearch", "TodoWrite", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet"}
BASH_WRITE = re.compile(
    r"(^|[;&|(]\s*|\s)("
    r"git\s+(add|commit|checkout|switch|reset|stash|init|push|merge|rebase|mv|rm|restore|worktree\s+add|branch\s+-[dDmM])"
    r"|rm|mv|cp|mkdir|touch|tee|chmod|ln|npm\s+(i|install|init|ci)|pnpm\s+(i|add|install)|yarn\s+add|npx|sed\s+-i|perl\s+-i"
    r")\b"
    r"|(?<![0-9&>])>>?\s*(?!/dev/null|&)[\w./~$\"']"
)


def events(path):
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def tool_uses(evs):
    """Lista de (n.º de mensaje, nombre, input, ¿dio error?) en orden."""
    failed = set()
    for e in evs:
        if e.get("type") == "user":
            content = e.get("message", {}).get("content", [])
            for c in content if isinstance(content, list) else []:
                if c.get("type") == "tool_result" and c.get("is_error"):
                    failed.add(c.get("tool_use_id"))
    res = []
    for i, e in enumerate(evs):
        if e.get("type") == "assistant":
            for c in e.get("message", {}).get("content", []):
                if c.get("type") == "tool_use":
                    res.append((i, c["name"], c.get("input", {}), c.get("id") in failed))
    return res


def text_of(inp):
    return json.dumps(inp, ensure_ascii=False)


def is_write(name, inp):
    if name in WRITE_TOOLS:
        return True
    return name == "Bash" and bool(BASH_WRITE.search(inp.get("command", "")))


def touches_plugin_or_profile(name, inp, skill):
    """Mirar la skill o el perfil (CLAUDE.md) no cuenta como actuar sobre el proyecto."""
    t = text_of(inp)
    if name == "Read" and inp.get("file_path", "").endswith("/CLAUDE.md"):
        return True
    return f"/skills/{skill}" in t or "/.claude/CLAUDE.md" in t or "shipwright:perfil" in t


def reads(name, inp, skill, rel):
    """¿Esta llamada lee <skill>/<rel>?"""
    target = f"/skills/{skill}/{rel}"
    if name == "Read":
        return inp.get("file_path", "").endswith(target)
    if name == "Bash":  # cat …/skills/x/references/y.md  o  cd …/skills/x; cat references/y.md
        cmd = inp.get("command", "")
        return target in cmd or (f"/skills/{skill}" in cmd and re.search(rf"(?<![\w-]){re.escape(rel)}", cmd) is not None)
    return False


def analyze_turn(evs, skill, espera, info):
    uses = tool_uses(evs)
    r = {}
    r["skills"] = sorted({u[2].get("skill", "") for u in uses if u[1] == "Skill"})
    r["skill_ok"] = any(s.split(":")[-1] == skill for s in r["skills"]) or any(
        reads(n, i, skill, "SKILL.md") for _, n, i, _ in uses)
    # primera acción sobre el proyecto
    first_action = next((m for m, n, i, _ in uses if n not in PREP_TOOLS
                         and not touches_plugin_or_profile(n, i, skill)), None)
    if espera:
        # solo cuenta una lectura que devolvió contenido (no una denegada)
        read_at = next((m for m, n, i, err in uses if not err and reads(n, i, skill, espera)), None)
        r["leyo"] = read_at is not None
        r["antes"] = r["leyo"] and (first_action is None or read_at <= first_action)
    else:
        r["leyo"] = r["antes"] = None
    r["info"] = {rel: any(not err and reads(n, i, skill, rel) for _, n, i, err in uses) for rel in info or []}
    r["escrituras"] = [f"{n}: {(i.get('command') or i.get('file_path') or '')[:80]}"
                       for _, n, i, _ in uses if is_write(n, i)]
    result = next((e for e in reversed(evs) if e.get("type") == "result"), {})
    denials = result.get("permission_denials", []) or []
    r["denegadas"] = len(denials)
    r["coste"] = result.get("total_cost_usd") or 0.0
    r["error"] = None if result else "sin evento result (¿se cortó o falló claude?)"
    if result.get("is_error"):
        r["error"] = f"is_error ({result.get('subtype')})"
    r["respuesta"] = (result.get("result") or "")[:4000]
    return r


def analyze_dir(d):
    d = Path(d)
    rows = {}
    for caso in CASOS:
        turns = []
        for t, turno in enumerate(caso["turnos"], 1):
            f = d / f"{caso['id']}.t{t}.jsonl"
            if not f.exists():
                break
            turns.append(analyze_turn(events(f), caso["skill"], turno.get("espera"), turno.get("info")))
        if not turns:
            continue
        rows[caso["id"]] = summarize(caso, turns)
    return rows


def summarize(caso, turns):
    s = {
        # en una sesión reanudada la skill ya está cargada: basta con que se cargue una vez
        "skill": any(t["skill_ok"] for t in turns),
        "skills": sorted({x for t in turns for x in t["skills"]}),
        "leyo": [t["leyo"] for t in turns],
        "antes": [t["antes"] for t in turns],
        "escrituras": [w for t in turns for w in t["escrituras"]],
        "denegadas": sum(t["denegadas"] for t in turns),
        "coste": sum(t["coste"] for t in turns),
        "info": {k: v for t in turns for k, v in t["info"].items()},
        "errores": [t["error"] for t in turns if t["error"]],
        "turnos_esperados": len(caso["turnos"]),
        "turnos": len(turns),
        "respuesta": turns[-1]["respuesta"],
    }
    fallos = []
    if s["turnos"] < s["turnos_esperados"]:
        fallos.append("faltan turnos")
    if any(l is False for l in s["leyo"]):
        fallos.append("no leyó el archivo del modo")
    if s["escrituras"]:
        fallos.append("intentó escribir sin permiso")
    if not s["skill"]:
        fallos.append("no cargó la skill")
    fallos += s["errores"]
    s["fallos"] = fallos
    s["avisos"] = ["leyó el modo tarde"] if any(a is False for a, l in zip(s["antes"], s["leyo"]) if l) else []
    return s


def yn(v):
    return {True: "sí", False: "**no**", None: "–"}[v]


def fmt_seq(vals):
    return " → ".join(yn(v) for v in vals)


def estado(s):
    if s["fallos"]:
        return "❌ " + "; ".join(s["fallos"])
    if s["avisos"]:
        return "⚠️ " + "; ".join(s["avisos"])
    return "✅"


def report(rows):
    print("| Caso | Skill | Leyó el modo | Antes de actuar | Escrituras | Denegadas | Coste | Resultado |")
    print("|---|---|---|---|---|---|---|---|")
    for cid, s in rows.items():
        print(f"| {cid} | {yn(s['skill'])} | {fmt_seq(s['leyo'])} | {fmt_seq(s['antes'])} | "
              f"{len(s['escrituras'])} | {s['denegadas']} | ${s['coste']:.3f} | {estado(s)} |")
    total = sum(s["coste"] for s in rows.values())
    ok = sum(not s["fallos"] for s in rows.values())
    print(f"\n**{ok}/{len(rows)} casos correctos · coste total ${total:.2f}**")
    for cid, s in rows.items():
        extra = []
        if s["escrituras"]:
            extra.append("escrituras: " + " | ".join(s["escrituras"]))
        if s["info"]:
            extra.append("lecturas extra: " + ", ".join(f"{k}={yn(v)}" for k, v in s["info"].items()))
        if s["skills"] and not s["skill"]:
            extra.append("skills cargadas: " + ", ".join(s["skills"]))
        if extra:
            print(f"- **{cid}**: " + "; ".join(extra))


def compare(a, b, la, lb):
    print(f"| Caso | {la} | {lb} | Coste {la} | Coste {lb} |")
    print("|---|---|---|---|---|")
    for cid in [c["id"] for c in CASOS if c["id"] in a or c["id"] in b]:
        sa, sb = a.get(cid), b.get(cid)
        print(f"| {cid} | {estado(sa) if sa else '–'} | {estado(sb) if sb else '–'} | "
              f"{'$%.3f' % sa['coste'] if sa else '–'} | {'$%.3f' % sb['coste'] if sb else '–'} |")
    ca, cb = sum(s["coste"] for s in a.values()), sum(s["coste"] for s in b.values())
    oka, okb = sum(not s["fallos"] for s in a.values()), sum(not s["fallos"] for s in b.values())
    print(f"\n**{la}: {oka}/{len(a)} correctos, ${ca:.2f} · {lb}: {okb}/{len(b)} correctos, ${cb:.2f}**")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--etiquetas", nargs=2, default=["A", "B"])
    ap.add_argument("--json", action="store_true", help="vuelca el análisis en JSON")
    args = ap.parse_args()
    if len(args.dirs) == 1:
        rows = analyze_dir(args.dirs[0])
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            report(rows)
        sys.exit(1 if not rows or any(s["fallos"] for s in rows.values()) else 0)
    a, b = analyze_dir(args.dirs[0]), analyze_dir(args.dirs[1])
    compare(a, b, *args.etiquetas)
    print(f"\n### Detalle {args.etiquetas[1]}\n")
    report(b)
    sys.exit(1 if not b or any(s["fallos"] for s in b.values()) else 0)


if __name__ == "__main__":
    main()
