#!/usr/bin/env python3
"""두 프리비즈 명세(previz_spec) 비교 — 수정 판이 '말한 부위만' 바꿨는지 숫자로 확인한다.

사용:
  python3 spec_diff.py <직전 판 spec.json> <이번 판 spec.json> [--fps 24] [--json 결과.json]

previz.py --prev <직전 판 폴더>를 주면 렌더 끝에 같은 비교를 저절로 돌린다(diff_prev.json).

보는 것:
  - 물체가 더해졌나·빠졌나
  - 물체마다 pos·rot·rot_x·bend·scale·visible이 어느 시간대에 얼마나 달라졌나(매 프레임 비교 — 키를 다시 찍어도
    값이 같으면 '안 바뀜'), follow·크기·모양·색 칸이 달라졌나
  - 카메라(cuts)·세트(world.set)·palette·길이(render, 미리보기 배율은 뺌)가 달라졌나
허용 오차: 위치 1cm · 각도 0.5° · 배율 0.01.

보간은 build_previz.py와 같다(뒤 키의 ease, 기본 quintic inout). 블렌더 없이 돈다.
"""
import argparse
import json
import sys

POS_TOL, ANG_TOL, SCALE_TOL = 0.01, 0.5, 0.01
FIELDS = (("pos", POS_TOL, "m"), ("rot", ANG_TOL, "°"), ("rot_x", ANG_TOL, "°"), ("bend", ANG_TOL, "°"),
          ("scale", SCALE_TOL, ""))
DEFAULTS = {"pos": [0, 0, 0], "rot": 0.0, "rot_x": 0.0, "bend": 0.0, "scale": 1.0, "visible": True}


def ease(p, mode="inout"):
    p = max(0.0, min(1.0, p))
    if mode == "linear":
        return p
    if mode == "in":
        return p * p * p
    if mode == "out":
        q = 1 - p
        return 1 - q * q * q
    return p * p * p * (p * (p * 6 - 15) + 10)


def sample_keys(keys, t, field, default=None):
    ks = [k for k in keys if field in k]
    if not ks:
        return default
    if t <= ks[0]["t"]:
        return ks[0][field]
    if t >= ks[-1]["t"]:
        return ks[-1][field]
    for a, b in zip(ks, ks[1:]):
        if a["t"] <= t <= b["t"]:
            span = b["t"] - a["t"]
            p = ease(0 if span <= 0 else (t - a["t"]) / span, b.get("ease", "inout"))
            va, vb = a[field], b[field]
            if isinstance(va, (bool, str)):
                return va if p < 0.5 else vb
            if isinstance(va, (list, tuple)):
                return [x + (y - x) * p for x, y in zip(va, vb)]
            return va + (vb - va) * p
    return ks[-1][field]


def _keys(o):
    return sorted(o.get("keys", [{"t": 0, "pos": [0, 0, 0]}]), key=lambda k: k["t"])


def _dist(field, a, b):
    if field == "visible":
        return 0.0 if bool(a) == bool(b) else 1.0
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        a = a if isinstance(a, (list, tuple)) else [a] * 3
        b = b if isinstance(b, (list, tuple)) else [b] * 3
        return max(abs(float(x) - float(y)) for x, y in zip(a, b))
    return abs(float(a) - float(b))


def _windows(flags, times):
    """연속으로 달라진 프레임 묶음 → [(시작 초, 끝 초)]."""
    out, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        if not f and start is not None:
            out.append((times[start], times[i - 1]))
            start = None
    if start is not None:
        out.append((times[start], times[-1]))
    return out


def _duration(spec):
    r = spec.get("render", {})
    cuts = spec.get("cuts", [])
    return float(r.get("duration") or (cuts[-1]["end"] if cuts else 0))


def _cut_key(c):
    """컷 비교용 — 사람이 읽는 메모(camera.move)는 뺀다."""
    d = {k: v for k, v in c.items() if k != "camera"}
    d["camera"] = {k: v for k, v in c.get("camera", {}).items() if k != "move"}
    return json.dumps(d, sort_keys=True)


def diff_specs(old, new, fps=24):
    res = {"added": [], "removed": [], "objects": {}, "cameras": [], "set": {}, "palette": {}, "render": {},
           "unchanged_objects": []}
    oo = {o["id"]: o for o in old.get("objects", [])}
    no = {o["id"]: o for o in new.get("objects", [])}
    res["added"] = [i for i in no if i not in oo]
    res["removed"] = [i for i in oo if i not in no]
    dur = max(_duration(old), _duration(new))
    n = int(round(dur * fps))
    times = [i / float(fps) for i in range(n + 1)]
    for oid in [i for i in no if i in oo]:
        a, b = oo[oid], no[oid]
        ka, kb = _keys(a), _keys(b)
        ch = {}
        for field, tol, unit in FIELDS + (("visible", 0.5, ""),):
            vals = [_dist(field, sample_keys(ka, t, field, DEFAULTS[field]), sample_keys(kb, t, field, DEFAULTS[field]))
                    for t in times]
            flags = [v > tol for v in vals]
            if any(flags):
                ch[field] = {"max": round(max(vals), 3), "unit": unit,
                             "windows": [[round(s, 3), round(e, 3)] for s, e in _windows(flags, times)]}
        for k in ("follow", "size", "shape", "height", "kind", "color", "pivot", "facing_marker", "child", "sides"):
            if json.dumps(a.get(k), sort_keys=True) != json.dumps(b.get(k), sort_keys=True):
                ch[k] = {"old": a.get(k), "new": b.get(k)}
        if ch:
            res["objects"][oid] = ch
        else:
            res["unchanged_objects"].append(oid)
    ca = {c["id"]: c for c in old.get("cuts", [])}
    cb = {c["id"]: c for c in new.get("cuts", [])}
    for cid in sorted(set(ca) | set(cb)):
        x, y = ca.get(cid), cb.get(cid)
        if x is None or y is None:
            res["cameras"].append({"cut": cid, "change": "더함" if x is None else "뺌"})
            continue
        if _cut_key(x) != _cut_key(y):
            res["cameras"].append({"cut": cid, "change": "카메라·시각 칸이 다름"})
    sa = {s.get("id", "set_%d" % i): s for i, s in enumerate(old.get("world", {}).get("set", []))}
    sb = {s.get("id", "set_%d" % i): s for i, s in enumerate(new.get("world", {}).get("set", []))}
    res["set"] = {"added": [i for i in sb if i not in sa], "removed": [i for i in sa if i not in sb],
                  "changed": [i for i in sb if i in sa and json.dumps(sa[i], sort_keys=True) != json.dumps(sb[i], sort_keys=True)]}
    pa, pb = old.get("palette", {}), new.get("palette", {})
    res["palette"] = {k: {"old": pa.get(k), "new": pb.get(k)} for k in sorted(set(pa) | set(pb)) if pa.get(k) != pb.get(k)}
    ra = {k: v for k, v in old.get("render", {}).items() if k != "scale_percent"}
    rb = {k: v for k, v in new.get("render", {}).items() if k != "scale_percent"}
    res["render"] = {k: {"old": ra.get(k), "new": rb.get(k)} for k in sorted(set(ra) | set(rb)) if ra.get(k) != rb.get(k)}
    return res


def format_lines(res):
    """사람이 읽는 줄(한국어). 사용자가 말한 것 말고 바뀐 줄이 있으면 되돌린다."""
    L = []
    for i in res["added"]:
        L.append("더한 물체: %s" % i)
    for i in res["removed"]:
        L.append("뺀 물체: %s" % i)
    for oid, ch in res["objects"].items():
        parts = []
        for k, v in ch.items():
            if "windows" in v:
                w = ", ".join("%.2f~%.2f초" % (s, e) for s, e in v["windows"])
                parts.append("%s %s(최대 %s%s)" % (k, w, v["max"], v["unit"]))
            else:
                parts.append("%s 칸 바뀜" % k)
        L.append("바뀐 물체 %s: %s" % (oid, " · ".join(parts)))
    for c in res["cameras"]:
        L.append("카메라 %s: %s" % (c["cut"], c["change"]))
    for k in ("added", "removed", "changed"):
        if res["set"].get(k):
            L.append("세트 %s: %s" % ({"added": "더함", "removed": "뺌", "changed": "바뀜"}[k], ", ".join(res["set"][k])))
    if res["palette"]:
        L.append("색 바뀜: " + ", ".join("%s %s→%s" % (k, v["old"], v["new"]) for k, v in res["palette"].items()))
    if res["render"]:
        L.append("렌더 칸 바뀜: " + ", ".join("%s %s→%s" % (k, v["old"], v["new"]) for k, v in res["render"].items()))
    if not L:
        L.append("바뀐 것 없음")
    if res["unchanged_objects"]:
        L.append("그대로인 물체 %d개" % len(res["unchanged_objects"]))
    return L


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--fps", type=int, default=0, help="비교 프레임 간격(기본 = 이번 판 render.fps)")
    ap.add_argument("--json", default="", help="결과를 JSON으로도 저장")
    args = ap.parse_args()
    with open(args.old, encoding="utf-8") as f:
        old = json.load(f)
    with open(args.new, encoding="utf-8") as f:
        new = json.load(f)
    fps = args.fps or int(new.get("render", {}).get("fps", 24))
    res = diff_specs(old, new, fps)
    for line in format_lines(res):
        print("[직전 판 대비] " + line)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    sys.exit(main())
