#!/usr/bin/env python3
"""Generic Frappe app rename codemod. Rewrites tracked text files, git mv's paths. Does not commit.

  frappe_rename.py REPO --old old_app --new new_app --old-title "Old App" --new-title "New App"
      [--keep-prefix old_app_tpl_ ...] [--map map.json] [--protect STR ...] [--skip-top progress ...]
      [--dry-run] [--scan]

map.json: {"old_app_some_key": "rename" | "keep"}. Unclassified `old_app_<word>` identifiers abort
with exit 2 before anything is written. --scan exits 1 if any old-name hit remains outside keeps.
"""
import argparse, json, os, re, subprocess, sys

B = r"(?:(?<![A-Za-z0-9_])|(?<=\\[ntr]))"  # also matches JSON-escaped glue like \nold_app.x


def git(root, *a):
    return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True, check=True).stdout


def text(p):
    if os.path.islink(p) or not os.path.isfile(p):
        return None
    b = open(p, "rb").read()
    if b"\0" in b:
        return None
    try:
        return b.decode()
    except UnicodeDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--old-title", required=True)
    ap.add_argument("--new-title", required=True)
    ap.add_argument("--keep-prefix", action="append", default=[])
    ap.add_argument("--map")
    ap.add_argument("--protect", action="append", default=[])
    ap.add_argument("--skip-top", action="append", default=["progress", "reports", "screenshots"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--scan", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    kebab_o, kebab_n = a.old.replace("_", "-"), a.new.replace("_", "-")
    camel = lambda s: "".join(w.capitalize() for w in s.split("_"))
    ident = re.compile(B + re.escape(a.old) + r"_[A-Za-z0-9_]+")
    cmap = json.load(open(a.map)) if a.map else {}
    rules = [
        (re.compile(B + re.escape(a.old) + r"(?![A-Za-z0-9_])"), a.new),
        (re.compile(B + re.escape(a.old_title) + r"(?![A-Za-z0-9_])"), a.new_title),
        (re.compile(B + re.escape(kebab_o) + r"(?![A-Za-z0-9_])"), kebab_n),
        (re.compile(B + re.escape(camel(a.old)) + r"(?=[A-Z]|(?![A-Za-z0-9_]))"), camel(a.new)),
        (re.compile(B + re.escape(a.old.upper()) + r"(?![A-Za-z0-9_])"), a.new.upper()),
    ]
    prot = sorted(a.protect, key=len, reverse=True)
    files = [f for f in git(root, "ls-files", "-z").split("\0") if f and f.split("/")[0] not in a.skip_top]
    unmapped = set()

    def kept(w):
        return any(w.startswith(k) for k in a.keep_prefix) or cmap.get(w) == "keep"

    def conv(s):
        for i, p in enumerate(prot):
            s = s.replace(p, f"\x00P{i}\x00")

        def sub(m):
            w = m.group()
            if kept(w):
                return w
            if cmap.get(w) == "rename":
                return a.new + w[len(a.old):]
            unmapped.add(w)
            return w
        s = ident.sub(sub, s)
        for rx, rep in rules:
            s = rx.sub(rep, s)
        for i, p in enumerate(prot):
            s = s.replace(f"\x00P{i}\x00", p)
        return s

    if a.scan:
        rx = re.compile(r"(?i)" + re.escape(a.old).replace("_", "[_ -]?") + r"\w*")
        bad = 0
        for f in files:
            if rx.search(f):
                print(f"{f}: PATH"); bad += 1
            s = text(os.path.join(root, f))
            for n, line in enumerate((s or "").split("\n"), 1):
                for p in prot:
                    line = line.replace(p, " ")
                for m in rx.finditer(line):
                    if not kept(m.group()):
                        print(f"{f}:{n}: {m.group()}"); bad += 1
        print(json.dumps({"leftover_hits": bad}))
        sys.exit(1 if bad else 0)

    edits, moves = {}, []
    for f in files:
        s = text(os.path.join(root, f))
        if s is not None:
            t = conv(s)
            if t != s:
                edits[f] = t
        nf = "/".join(conv(seg) for seg in f.split("/"))
        if nf != f:
            moves.append((f, nf))
    clash = [n for _, n in moves if os.path.exists(os.path.join(root, n))]
    print(json.dumps({"files_changed": len(edits), "paths_moved": len(moves)}))
    if unmapped or clash:
        print("ABORT (nothing written). unclassified:", sorted(unmapped), "path clashes:", clash, file=sys.stderr)
        sys.exit(2)
    if a.dry_run:
        return
    for f, t in edits.items():
        with open(os.path.join(root, f), "w", encoding="utf-8", newline="") as fh:
            fh.write(t)
    for o, n in moves:
        os.makedirs(os.path.dirname(os.path.join(root, n)) or root, exist_ok=True)
        git(root, "mv", o, n)


if __name__ == "__main__":
    main()
