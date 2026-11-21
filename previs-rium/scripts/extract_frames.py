#!/usr/bin/env python3
"""레퍼런스 영상 → 컷 나누기 + 프레임 추출 + 접촉 시트 + 카메라 움직임 힌트.

AI는 영상을 직접 못 본다. 이 스크립트가 만든 접촉 시트(이미지)를 보고 큐시트를 쓴다.

사용:
  python3 extract_frames.py <영상> --out <작업폴더>/01_프레임 [--interval 0.5] [--scene 0.30]

만드는 것(--out 아래):
  info.json            영상 정보(길이·크기·fps·HDR·오디오)
  frames.json          컷 목록(시작·끝·프레임 경로·움직임 힌트) + 일정 간격 프레임 목록
  cuts/C01_a.jpg …     컷마다 첫(a)·가운데(m)·끝(z) 프레임
  every/t0000.00.jpg … 일정 간격 프레임
  sheet_cuts.jpg       컷 한 줄씩(첫·가운데·끝) 접촉 시트
  sheet_every_01.jpg … 일정 간격 접촉 시트(시간 라벨)
  audio.m4a            원본 오디오(있을 때만 — 나중에 리먹스용)

컷 경계는 '자동 추정'이다. 페이드·디졸브·빠른 휙 팬은 놓치거나 잘못 잡을 수 있으니
sheet_every로 다시 확인하고, 틀리면 --cuts "0,2.4,5.1"로 직접 준다.
"""
import argparse
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rr_util import (contact_sheet, fmt_t, need, probe, run, sdr_filter,  # noqa: E402
                     write_json)


def detect_scenes(video, threshold, info, low=0.12):
    """장면 전환 점수를 한 번에 잰다. threshold 이상 = 확정 컷, low~threshold = 후보(눈으로 확인)."""
    ffmpeg = need("ffmpeg")
    vf = "scale=320:-2,select='gt(scene\\,%s)',metadata=print" % min(low, threshold)
    pre = sdr_filter(info)
    if pre:
        vf = pre + "," + vf
    proc = run([ffmpeg, "-hide_banner", "-nostats", "-i", video, "-an", "-vf", vf, "-f", "null", "-"])
    hits, cur = [], None
    for line in proc.stderr.splitlines():
        m = re.search(r"pts_time:([0-9.]+)", line)
        if m:
            cur = float(m.group(1))
        m = re.search(r"lavfi\.scene_score=([0-9.]+)", line)
        if m and cur is not None:
            hits.append((round(cur, 3), float(m.group(1))))
            cur = None
    confirmed = sorted(set(t for t, sc in hits if sc >= threshold))
    candidates = [{"t": t, "score": round(sc, 3)} for t, sc in hits if sc < threshold]
    return confirmed, candidates


def build_cuts(times, duration, min_len):
    bounds = [0.0]
    for t in times:
        if t - bounds[-1] >= min_len and duration - t >= min_len:
            bounds.append(t)
    bounds.append(duration)
    cuts = []
    for i in range(len(bounds) - 1):
        cuts.append({"id": "C%02d" % (i + 1), "start": round(bounds[i], 3),
                     "end": round(bounds[i + 1], 3),
                     "dur": round(bounds[i + 1] - bounds[i], 3)})
    return cuts


def grab(video, t, out, width, info):
    ffmpeg = need("ffmpeg")
    vf = "scale=%d:-2,format=yuvj420p" % width
    pre = sdr_filter(info)
    if pre:
        vf = pre + "," + vf
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.3f" % max(0.0, t),
         "-i", video, "-frames:v", "1", "-vf", vf, "-q:v", "3", out])
    return out


def motion_hint(video, start, end, info, workdir):
    """컷 안의 화면 전체 움직임을 대충 잰다(카메라 무빙 판단의 참고용).

    위상 상관으로 좌우·상하 이동, 크기 비교로 확대·축소를 추정한다.
    피사체가 크게 움직이면 카메라 움직임과 섞인다 → 반드시 '추정'으로만 쓴다.
    """
    try:
        import numpy as np
        from PIL import Image
    except Exception:
        return None
    dur = end - start
    if dur < 0.3:
        return None
    n = int(min(24, max(4, dur * 6)))
    ffmpeg = need("ffmpeg")
    tmpdir = os.path.join(workdir, "_motion")
    os.makedirs(tmpdir, exist_ok=True)
    for f in os.listdir(tmpdir):
        os.remove(os.path.join(tmpdir, f))
    vf = "fps=%f,scale=192:-2,format=gray" % (n / dur)
    pre = sdr_filter(info)
    if pre:
        vf = pre + "," + vf
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.3f" % start, "-t",
         "%.3f" % dur, "-i", video, "-vf", vf, os.path.join(tmpdir, "m%03d.png")])
    files = sorted(os.listdir(tmpdir))
    frames = [np.asarray(Image.open(os.path.join(tmpdir, f)), dtype=np.float32) for f in files]
    if len(frames) < 3:
        return None
    h, w = frames[0].shape
    win = np.outer(np.hanning(h), np.hanning(w)).astype(np.float32)

    def shift(a, b):
        fa = np.fft.fft2((a - a.mean()) * win)
        fb = np.fft.fft2((b - b.mean()) * win)
        r = fa * np.conj(fb)
        r /= np.abs(r) + 1e-6
        c = np.abs(np.fft.ifft2(r))
        y, x = np.unravel_index(np.argmax(c), c.shape)
        if y > h // 2:
            y -= h
        if x > w // 2:
            x -= w
        return float(x), float(y)

    def scale_change(a, b, sx, sy):
        """b를 (sx,sy)만큼 되돌려 맞춘 뒤 크기 비율을 찾는다. 1보다 작으면 b가 커진 것(확대)."""
        b = np.roll(np.roll(b, -int(round(sy)), axis=0), -int(round(sx)), axis=1)
        ca = a[h // 5:h - h // 5, w // 5:w - w // 5]
        ca = (ca - ca.mean()) / (ca.std() + 1e-6)
        img_b = Image.fromarray(b)
        scores = {}
        for s in (0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03):
            bw, bh = int(round(w * s)), int(round(h * s))
            bb = np.asarray(img_b.resize((bw, bh)), dtype=np.float32)
            oy, ox = (bh - h) // 2, (bw - w) // 2
            if oy < 0 or ox < 0:
                pad = np.zeros((max(h, bh), max(w, bw)), dtype=np.float32)
                py, px = (pad.shape[0] - bh) // 2, (pad.shape[1] - bw) // 2
                pad[py:py + bh, px:px + bw] = bb
                bb = pad
                oy, ox = (bb.shape[0] - h) // 2, (bb.shape[1] - w) // 2
            cb = bb[oy:oy + h, ox:ox + w][h // 5:h - h // 5, w // 5:w - w // 5]
            cb = (cb - cb.mean()) / (cb.std() + 1e-6)
            scores[s] = float((ca * cb).mean())
        best_s = max(scores, key=scores.get)
        if scores[best_s] - scores[1.0] < 0.01:  # 차이가 작으면 크기 변화 없음으로 본다
            return 1.0
        return best_s

    dx, dy, zs = [], [], []
    for i in range(len(frames) - 1):
        x, y = shift(frames[i + 1], frames[i])
        dx.append(x)
        dy.append(y)
        zs.append(scale_change(frames[i], frames[i + 1], x, y))
    tot_x = sum(dx) / w * 100.0  # 화면 폭 대비 %
    tot_y = sum(dy) / h * 100.0
    zoom = 1.0
    for z in zs:
        zoom /= z  # z<1 = 다음 프레임 내용이 커짐 = 확대
    jitter = 0.0
    if len(dx) > 2:
        mx, my = sum(dx) / len(dx), sum(dy) / len(dy)
        jitter = math.sqrt(sum((a - mx) ** 2 + (b - my) ** 2 for a, b in zip(dx, dy)) / len(dx))
        jitter = jitter / w * 100.0
    words = []
    if zoom > 1.06:
        words.append("확대(푸시인/줌인) 약 %.2f배" % zoom)
    elif zoom < 0.94:
        words.append("축소(풀아웃/줌아웃) 약 %.2f배" % zoom)
    # 화면 내용이 왼쪽으로 흐르면(음수 x) 카메라는 오른쪽으로 간 것
    if abs(tot_x) > 8:
        words.append("내용이 %s으로 %.0f%% 흐름(카메라 %s)" % (
            "왼쪽" if tot_x < 0 else "오른쪽", abs(tot_x), "오른쪽 팬/트럭" if tot_x < 0 else "왼쪽 팬/트럭"))
    if abs(tot_y) > 8:
        words.append("내용이 %s로 %.0f%% 흐름(카메라 %s)" % (
            "위" if tot_y < 0 else "아래", abs(tot_y), "아래로 틸트/하강" if tot_y < 0 else "위로 틸트/상승"))
    if jitter > 1.2:
        words.append("흔들림 있음(핸드헬드 느낌, 지터 %.1f%%)" % jitter)
    if not words:
        words.append("거의 고정(스태틱) 또는 피사체만 움직임")
    return {"pan_x_pct": round(tot_x, 1), "tilt_y_pct": round(tot_y, 1),
            "zoom": round(zoom, 3), "jitter_pct": round(jitter, 2),
            "hint": " · ".join(words) + " — 자동 추정(피사체 움직임과 섞임), 프레임으로 확인할 것"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--interval", type=float, default=0.0,
                    help="일정 간격 초(0=길이에 맞춰 자동: 15초 이하 0.25s, 30초 이하 0.5s, 그 이상 1s)")
    ap.add_argument("--scene", type=float, default=0.30, help="장면 전환 감도(낮을수록 많이 자름)")
    ap.add_argument("--min-cut", type=float, default=0.30, help="이보다 짧은 컷은 앞 컷에 합침(초)")
    ap.add_argument("--cuts", default="", help="자동 대신 직접 컷 경계(초) 예: 0,2.4,5.1")
    ap.add_argument("--width", type=int, default=480, help="추출 프레임 폭(px)")
    ap.add_argument("--per-sheet", type=int, default=24)
    ap.add_argument("--no-motion", action="store_true")
    args = ap.parse_args()

    video = os.path.abspath(args.video)
    out = os.path.abspath(args.out)
    for sub in ("cuts", "every", "cuts_full"):
        d = os.path.join(out, sub)
        if os.path.isdir(d):
            for fn in os.listdir(d):  # 이전 실행의 프레임이 섞이지 않게
                os.remove(os.path.join(d, fn))
        os.makedirs(d, exist_ok=True)

    info = probe(video)
    write_json(os.path.join(out, "info.json"), info)
    dur = info["duration"]
    print("영상: %dx%d · %.2f초 · %.2ffps · HDR=%s · 오디오=%s" % (
        info["width"], info["height"], dur, info["fps"], info["hdr"], info["has_audio"]))

    if args.cuts:
        bounds = sorted(float(x) for x in args.cuts.split(",") if x.strip())
        times = [b for b in bounds if 0 < b < dur]
        cuts = build_cuts(times, dur, 0.0)
        candidates = []
        source = "manual"
    else:
        times, candidates = detect_scenes(video, args.scene, info)
        cuts = build_cuts(times, dur, args.min_cut)
        source = "auto(확정 scene>=%.2f, 후보 0.12~%.2f)" % (args.scene, args.scene)
    print("컷 %d개 (%s) · 후보 %d곳" % (len(cuts), source, len(candidates)))
    os.makedirs(os.path.join(out, "cuts_full"), exist_ok=True)

    interval = args.interval or (0.25 if dur <= 15 else 0.5 if dur <= 30 else 1.0)
    rows, labels = [], []
    for c in cuts:
        eps = min(0.05, c["dur"] / 4)
        points = [("a", c["start"] + eps), ("m", (c["start"] + c["end"]) / 2), ("z", c["end"] - eps)]
        c["frames"] = {}
        row = []
        for key, t in points:
            p = os.path.join(out, "cuts", "%s_%s.jpg" % (c["id"], key))
            grab(video, t, p, args.width, info)
            c["frames"][key] = {"t": round(t, 3), "path": p}
            row.append({"path": p, "label": "%s %s" % (key, fmt_t(t))})
        full = os.path.join(out, "cuts_full", "%s_a.png" % c["id"])
        grab(video, c["start"] + eps, full, info["width"], info)  # 원본 해상도 — 글자·라벨·손 읽기용
        c["frames"]["full"] = {"t": round(c["start"] + eps, 3), "path": full}
        if not args.no_motion:
            c["motion"] = motion_hint(video, c["start"], c["end"], info, out)
        rows.append(row)
        labels.append("%s\n%s-%s\n(%.2fs)" % (c["id"], fmt_t(c["start"]), fmt_t(c["end"]), c["dur"]))
    contact_sheet(rows, os.path.join(out, "sheet_cuts.jpg"), thumb_w=320, row_labels=labels,
                  title="컷별 첫(a)·가운데(m)·끝(z) — %s" % os.path.basename(video))

    every = []
    times_list = []
    hook = min(3.0, dur)
    k = 0
    while k / 6.0 < hook - 0.02:  # 첫 3초(훅)는 1/6초 간격 — 짧은 사건을 놓치지 않게
        times_list.append(k / 6.0)
        k += 1
    t = hook
    while t < dur - 0.02:
        times_list.append(t)
        t += interval
    cand_t = [c["t"] for c in candidates]
    for t in times_list:
        p = os.path.join(out, "every", "t%07.2f.jpg" % t)
        grab(video, t, p, args.width, info)
        cut_id = next((c["id"] for c in cuts if c["start"] <= t < c["end"]), cuts[-1]["id"])
        is_cut = any(abs(c["start"] - t) < 0.5 / max(info["fps"], 1) + 0.01 for c in cuts[1:])
        near_cand = any(0 <= t - ct < interval for ct in cand_t)
        every.append({"t": round(t, 3), "path": p, "cut": cut_id, "cut_start": is_cut, "candidate": near_cand})
    sheets = []
    for i in range(0, len(every), args.per_sheet):
        chunk = every[i:i + args.per_sheet]
        sp = os.path.join(out, "sheet_every_%02d.jpg" % (i // args.per_sheet + 1))
        contact_sheet([{"path": e["path"], "label": "%s %s%s" % (e["cut"], fmt_t(e["t"]),
                                                             " 후보컷?" if e.get("candidate") else "")}
                       for e in chunk],
                      sp, cols=6, thumb_w=260,
                      title="첫 3초 1/6초 · 이후 %.2fs 간격 %s~%s" % (interval, fmt_t(chunk[0]["t"]),
                                                                  fmt_t(chunk[-1]["t"])))
        sheets.append(sp)

    audio = None
    if info["has_audio"]:
        audio = os.path.join(out, "audio.m4a")
        try:
            run([need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", video, "-vn",
                 "-c:a", "aac", "-b:a", "192k", audio])
        except RuntimeError:
            audio = None

    mdir = os.path.join(out, "_motion")
    if os.path.isdir(mdir):
        for f in os.listdir(mdir):
            os.remove(os.path.join(mdir, f))
        os.rmdir(mdir)

    write_json(os.path.join(out, "frames.json"), {
        "video": video, "info": info, "cut_source": source, "interval": interval,
        "candidates": candidates,
        "cuts": cuts, "every": every, "sheets": {"cuts": os.path.join(out, "sheet_cuts.jpg"),
                                                  "every": sheets},
        "audio": audio,
    })
    print("접촉 시트: sheet_cuts.jpg + sheet_every_*.jpg %d장 → %s" % (len(sheets), out))
    for c in cuts:
        hint = (c.get("motion") or {}).get("hint", "")
        print("  %s %s~%s (%.2fs) %s" % (c["id"], fmt_t(c["start"]), fmt_t(c["end"]), c["dur"], hint))
    for cd in candidates:
        print("  후보 컷? %s (점수 %.2f) — 접촉 시트에서 눈으로 확인, 진짜면 --cuts로 다시" % (fmt_t(cd["t"]), cd["score"]))


if __name__ == "__main__":
    main()
