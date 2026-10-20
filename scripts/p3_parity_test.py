"""Tasks 3.35, 3.36: JS vs Python parity on the 10 test farms (AC-06) and JS timing (NFR-03).

Pass = every percentile, loss chance, win rate, break-even within 1% (relative; absolute 1 Rs
or 0.001 for values near zero) and identical ranks and exclusions for every farm.
Writes parity_test_log.md.
Usage: python3 scripts/p3_parity_test.py
"""
import json
import subprocess

from p2_asof import DATA, ROOT
from p3_engine import run

FIELDS = [("net_acre", "p10"), ("net_acre", "p50"), ("net_acre", "p90"), ("yield_q", "p50"), ("price", "p50"),
          ("loss_chance", None), ("win_rate", None), ("break_even_price", None), ("break_even_yield", None)]
JS = """
const E = require(process.argv[1] + '/web/js/engine.js');
const d = require(process.argv[1] + '/data/engine_data.json');
const farms = require(process.argv[1] + '/tests/test_farms.json').farms;
const out = {}; const t0 = process.hrtime.bigint();
farms.forEach(f => { out[f.id] = E.run(d, f); });
const ms = Number(process.hrtime.bigint() - t0) / 1e6;
console.log(JSON.stringify({results: out, ms_total: ms, ms_per_farm: ms / farms.length}));
"""


def close(a, b):
    return abs(a - b) <= max(0.01 * abs(b), 1.0 if abs(b) > 10 else 0.001)


def main():
    farms = json.loads((ROOT / "tests" / "test_farms.json").read_text())["farms"]
    data = json.loads((DATA / "engine_data.json").read_text())
    js = json.loads(subprocess.check_output(["node", "-e", JS, str(ROOT)]))
    lines, failures, max_rel = [], 0, 0.0
    for f in farms:
        py, jr = run(data, f), js["results"][f["id"]]
        ranks_py = [c["crop"] for c in py["ranked"]]
        ranks_js = [c["crop"] for c in jr["ranked"]]
        ok = ranks_py == ranks_js and [c["crop"] for c in py["excluded"]] == [c["crop"] for c in jr["excluded"]]
        for cp, cj in zip(py["ranked"], jr["ranked"]):
            for a, b in FIELDS:
                vp = cp[a][b] if b else cp[a]
                vj = cj[a][b] if b else cj[a]
                if not close(vj, vp):
                    ok = False
                if abs(vp) > 1:
                    max_rel = max(max_rel, abs(vj - vp) / abs(vp))
        failures += not ok
        lines.append(f"| {f['id']} | {f['district']} | {f['risk']} | {' > '.join(ranks_py)} | {' > '.join(ranks_js)} | "
                     f"{', '.join(c['crop'] for c in py['excluded']) or '—'} | {'PASS' if ok else 'FAIL'} |")
    log = ["# Polaris CropPilot: JS / Python Parity Test Log (tasks 3.35, 3.36)", "",
           "**Run:** 20 October 2026 · engine_data.json v0.2 · 10 farms in `tests/test_farms.json` · 2,000 draws per crop", "",
           "| Farm | District | Risk | Python ranking | JS ranking | Excluded | Result |", "|---|---|---|---|---|---|---|", *lines, "",
           f"**AC-06:** {'PASS' if failures == 0 else 'FAIL'}: {10 - failures} of 10 farms match. "
           f"Largest relative difference on any compared value: {max_rel:.2e} (limit 1%).", "",
           f"**NFR-03 timing (Node, this machine):** {js['ms_per_farm']:.1f} ms per farm "
           f"(4 crops × 2,000 draws), {js['ms_total']:.0f} ms for all 10. Limit 2 s."]
    (ROOT / "parity_test_log.md").write_text("\n".join(log) + "\n")
    print("\n".join(log))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
