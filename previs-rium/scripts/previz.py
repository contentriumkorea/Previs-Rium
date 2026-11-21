#!/usr/bin/env python3
"""프리비즈 명세(previz_spec.json) → 블렌더 헤드리스 렌더 → 영상·접촉 시트·비교 영상.

사용:
  python3 previz.py <작업폴더>/03_프리비즈/previz_spec_v1.json --out <작업폴더>/03_프리비즈/v1 \
      --ref <작업폴더>/00_입력/<원본 영상> [--quick]
  수정 판(v2부터)은 직전 판 폴더도 준다 — '말한 부위만 바뀌었나' 자가 검사:
  python3 previz.py .../previz_spec_v2.json --out .../v2 --ref .../<원본 영상> --prev .../v1 [--quick]

만드는 것(--out 아래):
  previz.mp4          씨댄스에 넣을 깨끗한 프리비즈(글자 없음)
  previz_review.mp4   사용자 확인용(왼쪽 위에 컷 번호·초)
  compare.mp4         --ref를 주면 [레퍼런스 | 프리비즈] 나란히(타이밍 비교용, 무음)
  compare_prev.mp4    --prev를 주면 [원본 | 직전 판 | 이번 판] 나란히(--ref 없으면 [직전 | 이번])
  sheet_compare_prev.jpg  위 영상에서 1초마다 한 장씩 뽑은 접촉 시트(이미지로 확인용)
  diff_prev.json      --prev 폴더의 _spec_used.json과 이번 명세의 숫자 비교(spec_diff.py) — [직전 판 대비] 줄로도 출력
  cut_frames/         컷마다 첫·가운데·끝 프레임 PNG(첫 프레임 실사화 재료)
  sheet_previz.jpg    컷별 접촉 시트
  previz.blend        블렌더 파일(직접 열어 카메라를 고칠 수 있음)
  report.json         검사 결과(씨댄스 입력 조건 통과 여부 포함). qc.facing_to_lens = 이름 있는 사람의 렌즈 기준
                      몸 방향(0.5초마다 [초, 도, 화면 쪽]) — [몸 방향] 줄로도 출력, 넘기기 글의 몸 각도는 이 값대로

--quick: 절반 해상도로 빨리 확인(씨댄스 입력용 아님).
"""
import argparse
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rr_util import contact_sheet, fmt_t, load_font, need, probe, read_json, run, write_json  # noqa: E402
from spec_diff import diff_specs, format_lines  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# 씨댄스 2.5 영상 레퍼런스 조건(매그니픽 카탈로그 2026-10-09: 2~30초, 24~60fps,
# 총 화소 409,600 이상, mp4/mov, h264/hevc, 200MB 이하). 힉스필드 조건은 references/handoff.md 참고.
SEEDANCE_VIDEO = {"min_s": 2.0, "max_s": 30.0, "min_fps": 24, "max_fps": 60, "min_pixels": 409600}


def check_spec(spec):
    errs, warns = [], []
    r = spec.get("render", {})
    w, h, fps = int(r.get("width", 720)), int(r.get("height", 1280)), int(r.get("fps", 24))
    cuts = spec.get("cuts", [])
    if not cuts:
        errs.append("cuts가 비어 있음")
    prev_end = 0.0
    ids = set()
    for c in cuts:
        if c["id"] in ids:
            errs.append("컷 id 중복: %s" % c["id"])
        ids.add(c["id"])
        if abs(c["start"] - prev_end) > 1e-3:
            errs.append("%s 시작(%.3f)이 앞 컷 끝(%.3f)과 이어지지 않음" % (c["id"], c["start"], prev_end))
        if c["end"] <= c["start"]:
            errs.append("%s 끝이 시작보다 빠름" % c["id"])
        if "camera" not in c:
            errs.append("%s에 camera 없음" % c["id"])
        prev_end = c["end"]
    dur = float(r.get("duration") or prev_end)
    obj_ids = {o["id"] for o in spec.get("objects", [])}
    for c in cuts:
        tgt = c.get("camera", {}).get("target")
        if isinstance(tgt, str) and tgt not in obj_ids:
            errs.append("%s 카메라 target '%s'가 objects에 없음" % (c["id"], tgt))
    for o in spec.get("objects", []):
        fol = o.get("follow")
        if fol and fol.get("to") not in obj_ids:
            errs.append("%s follow 대상 '%s' 없음" % (o["id"], fol.get("to")))
        if o.get("kind") == "person" and o.get("shape"):
            warns.append("%s: 사람은 shape를 무시하고 정본 3부품 더미로 만듭니다" % o["id"])
        fm = o.get("facing_marker", "auto")
        if fm not in (True, False, None, "auto", "both", "chest", "head", "off", "none"):
            errs.append("%s facing_marker=%r — auto/true/false/both/chest/head 중 하나" % (o["id"], fm))
        elif "facing_marker" in o and o.get("kind") != "person":
            warns.append("%s: facing_marker는 사람(kind: person)에만 붙습니다 — 물건은 shape: dirbox" % o["id"])
    if abs(dur - round(dur)) > 1e-6:
        errs.append("길이 %.3f초 — 정수 초로(씨댄스 길이는 정수 초, 정본 게이트 [17])" % dur)
    elif dur < 4:
        warns.append("길이 %.0f초 — 씨댄스 생성 최소 길이는 4초" % dur)
    last_cam = cuts[-1].get("camera", {}) if cuts else {}
    if last_cam.get("hold_end") and not last_cam.get("hold_reason"):
        warns.append("마지막 컷 hold_end에 hold_reason이 없음 — 정지로 길이를 메우면 결과도 정지로 끝남(정본 5/5)")
    if w * h < SEEDANCE_VIDEO["min_pixels"]:
        errs.append("해상도 %dx%d = %d화소 < 씨댄스 최소 409,600(예: 720x1280·1280x720)" % (w, h, w * h))
    if not SEEDANCE_VIDEO["min_fps"] <= fps <= SEEDANCE_VIDEO["max_fps"]:
        errs.append("fps %d는 씨댄스 범위(24~60) 밖" % fps)
    if dur < SEEDANCE_VIDEO["min_s"]:
        errs.append("길이 %.2f초 < 2초" % dur)
    if dur > SEEDANCE_VIDEO["max_s"]:
        warns.append("길이 %.2f초 > 30초 — 씨댄스 한 번에 못 넣음(나눠서 생성)" % dur)
    if dur > 15:
        warns.append("15초 초과 — 힉스필드 웹 등 일부 경로는 15초까지만 받음(나눠서 생성)")
    for c in cuts:
        if c["end"] - c["start"] < 0.5:
            warns.append("%s가 %.2f초로 매우 짧음 — 씨댄스가 놓칠 수 있음" % (c["id"], c["end"] - c["start"]))
    return errs, warns, dur, fps, w, h


def label_frames(frames_dir, out_dir, spec, fps):
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    files = sorted(f for f in os.listdir(frames_dir) if f.endswith(".png"))
    font = None
    for i, fn in enumerate(files):
        t = i / float(fps)
        c = next((c for c in spec["cuts"] if c["start"] <= t < c["end"]), spec["cuts"][-1])
        im = Image.open(os.path.join(frames_dir, fn)).convert("RGB")
        if font is None:
            font = load_font(max(18, im.width // 24))
        d = ImageDraw.Draw(im)
        txt = "%s  %s  (%s~%s)" % (c["id"], fmt_t(t), fmt_t(c["start"]), fmt_t(c["end"]))
        move = c.get("camera", {}).get("move")
        if move:
            txt += "  " + move
        d.rectangle([0, 0, im.width, font.size + 16], fill=(0, 0, 0))
        d.text((10, 6), txt, fill=(255, 230, 120), font=font)
        im.save(os.path.join(out_dir, fn))


def encode(frames_dir, fps, out_mp4):
    run([need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-framerate", str(fps), "-i",
         os.path.join(frames_dir, "f_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
         "-movflags", "+faststart", out_mp4])


def compare_with_prev(args, spec, clean, out, fps, dur):
    """수정 판 자가 검사: [원본 | 직전 판 | 이번 판] 영상·접촉 시트 + 명세 숫자 비교."""
    prev = os.path.abspath(args.prev)
    if os.path.isdir(prev):
        prev_mp4, prev_spec = os.path.join(prev, "previz.mp4"), os.path.join(prev, "_spec_used.json")
    else:
        prev_mp4, prev_spec = prev, os.path.join(os.path.dirname(prev), "_spec_used.json")
    if not os.path.exists(prev_mp4):
        print("[직전 판 대비] 직전 previz.mp4를 찾지 못함: %s" % prev_mp4)
        return None, None, []
    lines = []
    if os.path.exists(prev_spec):
        res = diff_specs(read_json(prev_spec), spec, fps)
        write_json(os.path.join(out, "diff_prev.json"), res)
        lines = format_lines(res)
        for x in lines:
            print("[직전 판 대비] " + x)
    else:
        print("[직전 판 대비] 직전 명세(_spec_used.json)가 없어 숫자 비교는 건너뜀 — spec_diff.py로 직접 비교")
    inputs = ([args.ref] if args.ref else []) + [prev_mp4, clean]
    lens = [probe(x)["duration"] for x in inputs]
    hh = 640
    chains = "".join("[%d:v]scale=-2:%d,setsar=1,fps=%d[v%d];" % (i, hh, fps, i) for i in range(len(inputs)))
    filt = chains + "".join("[v%d]" % i for i in range(len(inputs))) + "hstack=inputs=%d,format=yuv420p" % len(inputs)
    cmp_mp4 = os.path.join(out, "compare_prev.mp4")
    cmd = [need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y"]
    for x in inputs:
        cmd += ["-i", x]
    run(cmd + ["-filter_complex", filt, "-an", "-t", "%.3f" % min(lens + [dur]), "-c:v", "libx264", "-crf", "20",
               cmp_mp4])
    n = max(1, int(min(lens + [dur])))
    cols = 3 if len(inputs) == 3 else 4
    rows = (n + cols - 1) // cols
    sheet = os.path.join(out, "sheet_compare_prev.jpg")
    run([need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", cmp_mp4, "-vf",
         "fps=1,scale=-2:300,tile=%dx%d" % (cols, rows), "-frames:v", "1", sheet])
    return cmp_mp4, sheet, lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", default="", help="레퍼런스 영상(나란히 비교 영상 만들 때)")
    ap.add_argument("--blender", default="")
    ap.add_argument("--quick", action="store_true", help="절반 해상도 미리보기")
    ap.add_argument("--prev", default="", help="직전 판 렌더 폴더(previz.mp4·_spec_used.json) 또는 직전 previz.mp4 — "
                                              "수정 판 자가 검사용 [원본 | 직전 | 이번] 비교와 숫자 비교")
    args = ap.parse_args()

    spec = read_json(args.spec)
    errs, warns, dur, fps, w, h = check_spec(spec)
    for x in warns:
        print("[주의] " + x)
    if errs:
        for x in errs:
            print("[오류] " + x)
        sys.exit("명세 오류를 고친 뒤 다시 실행하세요.")

    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    run_spec = dict(spec)
    if args.quick:
        run_spec["render"] = dict(spec.get("render", {}), scale_percent=50)
    tmp_spec = os.path.join(out, "_spec_used.json")
    write_json(tmp_spec, run_spec)
    frames_dir = os.path.join(out, "frames")
    if os.path.isdir(frames_dir):
        shutil.rmtree(frames_dir)

    blender = args.blender or need("blender")
    print("블렌더 렌더 중… (%d프레임)" % int(round(dur * fps)))
    env_dir = os.path.join(tempfile.gettempdir(), "previs-rium-blender")  # 사용자 블렌더 설정과 분리
    os.makedirs(env_dir, exist_ok=True)
    os.environ["BLENDER_USER_CONFIG"] = os.path.join(env_dir, "config")
    os.environ["BLENDER_USER_SCRIPTS"] = os.path.join(env_dir, "scripts")
    proc = run([blender, "--background", "--factory-startup", "-noaudio", "--python-exit-code", "1",
                "-P", os.path.join(HERE, "build_previz.py"), "--", tmp_spec, out])
    if "PREVIZ_DONE" not in (proc.stdout or ""):
        print((proc.stdout or "")[-2000:])
        sys.exit("블렌더가 끝까지 돌지 않았습니다.")

    clean = os.path.join(out, "previz.mp4")
    encode(frames_dir, fps, clean)
    rev_dir = os.path.join(out, "_frames_review")
    label_frames(frames_dir, rev_dir, spec, fps)
    encode(rev_dir, fps, os.path.join(out, "previz_review.mp4"))
    shutil.rmtree(rev_dir)

    cf = os.path.join(out, "cut_frames")
    os.makedirs(cf, exist_ok=True)
    rows, labels = [], []
    nframes = len([f for f in os.listdir(frames_dir) if f.endswith(".png")])
    for c in spec["cuts"]:
        fa = int(round(c["start"] * fps)) + 1
        fz = min(nframes, int(round(c["end"] * fps)))
        fm = (fa + fz) // 2
        row = []
        for key, fr in (("first", fa), ("mid", fm), ("last", fz)):
            src = os.path.join(frames_dir, "f_%04d.png" % fr)
            dst = os.path.join(cf, "%s_%s.png" % (c["id"], key))
            if os.path.exists(src):
                shutil.copy(src, dst)
            row.append({"path": dst, "label": "%s %s" % (key, fmt_t((fr - 1) / float(fps)))})
        rows.append(row)
        labels.append("%s\n%s-%s\n%s" % (c["id"], fmt_t(c["start"]), fmt_t(c["end"]),
                                          c.get("camera", {}).get("move", "")))
    contact_sheet(rows, os.path.join(out, "sheet_previz.jpg"), thumb_w=300, row_labels=labels,
                  title="프리비즈 %s — 컷별 첫·가운데·끝" % spec.get("meta", {}).get("version", ""))

    compare = None
    if args.ref:
        compare = os.path.join(out, "compare.mp4")
        ref_info = probe(args.ref)
        hh = 640
        filt = ("[0:v]scale=-2:%d,setsar=1,fps=%d[a];[1:v]scale=-2:%d,setsar=1,fps=%d[b];"
                "[a][b]hstack=inputs=2,format=yuv420p" % (hh, fps, hh, fps))
        run([need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", args.ref, "-i", clean,
             "-filter_complex", filt, "-an", "-t", "%.3f" % min(ref_info["duration"], dur), "-c:v", "libx264",
             "-crf", "20", compare])

    prev_cmp, prev_sheet, diff_lines = None, None, []
    if args.prev:
        prev_cmp, prev_sheet, diff_lines = compare_with_prev(args, spec, clean, out, fps, dur)

    info = probe(clean)
    ok = (info["width"] * info["height"] >= SEEDANCE_VIDEO["min_pixels"]
          and SEEDANCE_VIDEO["min_fps"] <= info["fps"] <= SEEDANCE_VIDEO["max_fps"]
          and SEEDANCE_VIDEO["min_s"] <= info["duration"] <= SEEDANCE_VIDEO["max_s"])
    shutil.rmtree(frames_dir)  # PNG 연속 프레임은 지움(영상·cut_frames·blend가 남음)
    qc = read_json(os.path.join(out, "qc.json")) if os.path.exists(os.path.join(out, "qc.json")) else {}
    for x in qc.get("warnings", []):
        print("[점검] " + x)
    if qc.get("facing_marker"):
        kinds = {"both": "쐐기+띠", "chest": "띠만", "head": "쐐기만"}
        objs = qc.get("objects", {})
        print("[방향 표시] %s — 넘기기 Colour key에 한 구절로 선언(prompt_canon §0-B — 쐐기+띠/띠만/쐐기만 구절이 다름)" % ", ".join(
            "%s(%s)" % (oid, kinds.get(objs.get(oid, {}).get("facing_marker"), "?")) for oid in qc["facing_marker"]))
    step_s = 0.5 if dur <= 12 else 1.0
    for oid, rows in (qc.get("facing_to_lens") or {}).items():
        pts = [r for r in rows if abs((r[0] / step_s) - round(r[0] / step_s)) < 1e-3]
        if pts:
            print("[몸 방향] %s(렌즈 기준 0°=정면·90°=옆·180°=등, 몸 앞이 향하는 화면 쪽): %s" % (oid, " · ".join(
                "%gs %d°%s" % (r[0], r[1], "" if r[2] == "정면" else ("오" if r[2] == "오른쪽" else "왼")) for r in pts)))
    report = {"spec": os.path.abspath(args.spec), "out": out, "video": clean, "info": info, "qc": qc,
              "seedance_video_ok": ok and not args.quick, "quick": args.quick, "warnings": warns,
              "compare": compare, "blend": os.path.join(out, "previz.blend"),
              "compare_prev": prev_cmp, "sheet_compare_prev": prev_sheet, "diff_prev": diff_lines}
    write_json(os.path.join(out, "report.json"), report)
    print("완료: %s (%dx%d, %.2f초, %.0ffps) 씨댄스 입력 조건=%s" % (
        clean, info["width"], info["height"], info["duration"], info["fps"],
        "통과" if report["seedance_video_ok"] else "미통과(quick 또는 조건 확인)"))
    print("확인용: previz_review.mp4 · sheet_previz.jpg" + (" · compare.mp4" if compare else "")
          + (" · compare_prev.mp4 · sheet_compare_prev.jpg" if prev_cmp else ""))


if __name__ == "__main__":
    main()
