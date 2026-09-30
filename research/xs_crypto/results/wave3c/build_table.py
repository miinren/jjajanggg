# Build a clean results table from the run logs (results_raw.csv is ragged: extra fields were appended without headers).
import re, glob, ast, pandas as pd
rows = {}
for f in sorted(glob.glob("run*.log")):
    for line in open(f):
        if line.startswith("{'id'"):
            d = ast.literal_eval(re.sub(r"np\.(float64|int64)\(([^)]*)\)", r"\2", line.strip()))
            rows[d["id"]] = d                      # last run of an id wins (V01 was re-run after the empty-leg fix)
import csv
with open("results_raw.csv") as fh:                 # E04 was run interactively (no log); its row is the file's first row with a correct header
    rd = csv.reader(fh); hdr = next(rd)
    for r in rd:
        if r[0] not in rows: rows[r[0]] = {k: (ast.literal_eval(v) if re.fullmatch(r"-?[0-9.]+(e-?[0-9]+)?|True|False", v) else v) for k, v in zip(hdr, r)}
t = pd.DataFrame(rows.values())
t.to_csv("results.csv", index=False); print(t[["id", "SR", "SR8", "SR12", "t", "years", "groups", "padopt", "adopt", "to", "clocks_won"]].to_string(index=False))
