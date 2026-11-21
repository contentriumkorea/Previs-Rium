"""Previs Rium 공용 도구: ffprobe 정보, 명령 실행, 글꼴, 접촉 시트.

다른 스크립트가 `from rr_util import ...`로 쓴다(같은 폴더에서 실행).
파이썬 3.9 기준(시스템 python3), 필요한 외부 모듈 = Pillow 하나.
"""
import json
import os
import shutil
import subprocess
import sys

FONT_CANDIDATES = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # 한글 포함
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNS.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

HDR_TRANSFERS = {"arib-std-b67", "smpte2084"}


def which(name, extra=()):
    for cand in list(extra) + [shutil.which(name)]:
        if cand and os.path.exists(cand):
            return cand
    for cand in ("/opt/homebrew/bin/" + name, "/usr/local/bin/" + name):
        if os.path.exists(cand):
            return cand
    return None


def need(name):
    path = which(name)
    if not path:
        sys.exit("[멈춤] '%s'를 찾을 수 없습니다. 설치가 필요합니다(사용자 동의 후 설치)." % name)
    return path


def run(cmd, capture=True):
    """명령 실행. 실패하면 stderr 끝부분을 보여 주고 멈춘다."""
    proc = subprocess.run(cmd, stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or "")[-1500:]
        raise RuntimeError("명령 실패: %s\n%s" % (" ".join(cmd[:6]), tail))
    return proc


def probe(path):
    """영상 정보(길이·크기·fps·코덱·HDR·오디오·회전)를 dict로."""
    ffprobe = need("ffprobe")
    out = run([ffprobe, "-v", "error", "-print_format", "json", "-show_format",
               "-show_streams", path]).stdout
    data = json.loads(out)
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    if v is None:
        sys.exit("[멈춤] 영상 트랙이 없습니다: %s" % path)
    num, den = (v.get("avg_frame_rate") or v.get("r_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0.0
    rotation = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rotation = int(sd["rotation"])
    if "rotate" in (v.get("tags") or {}):
        rotation = int(v["tags"]["rotate"])
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    if abs(rotation) in (90, 270):
        w, h = h, w  # 화면에 보이는 크기
    duration = float(data.get("format", {}).get("duration") or v.get("duration") or 0)
    transfer = v.get("color_transfer", "")
    return {
        "file": os.path.abspath(path),
        "duration": round(duration, 3),
        "width": w,
        "height": h,
        "fps": round(fps, 3),
        "codec": v.get("codec_name"),
        "pix_fmt": v.get("pix_fmt"),
        "color_transfer": transfer,
        "color_primaries": v.get("color_primaries", ""),
        "hdr": transfer in HDR_TRANSFERS,
        "rotation": rotation,
        "has_audio": a is not None,
        "audio_codec": a.get("codec_name") if a else None,
        "size_bytes": int(data.get("format", {}).get("size") or 0),
    }


def sdr_filter(info):
    """HDR(HLG/PQ) 영상이면 bt709로 바꾸는 ffmpeg 필터(로컬 ffmpeg엔 zscale이 없음)."""
    if not info.get("hdr"):
        return None
    itrc = "bt2020-10"
    return "colorspace=iall=bt2020:itrc=%s:all=bt709:format=yuv420p" % itrc


def load_font(size):
    from PIL import ImageFont
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def fmt_t(t):
    return "%.2fs" % t


def contact_sheet(items, out_path, cols=6, thumb_w=300, title=None, row_labels=None,
                  pad=8, bg=(24, 24, 24)):
    """items: [{'path':..., 'label':...}] 또는 행 단위 [[...], [...]].

    행 단위로 주면(row_labels와 함께) 컷마다 한 줄씩 그린다.
    """
    from PIL import Image, ImageDraw

    rows = items if items and isinstance(items[0], list) else None
    if rows is None:
        rows = [items[i:i + cols] for i in range(0, len(items), cols)]
    else:
        cols = max(len(r) for r in rows)

    first = None
    for r in rows:
        for it in r:
            if os.path.exists(it["path"]):
                first = Image.open(it["path"])
                break
        if first:
            break
    if first is None:
        raise RuntimeError("접촉 시트에 넣을 프레임이 없습니다")
    aspect = first.height / float(first.width)
    th = int(thumb_w * aspect)
    font = load_font(max(14, thumb_w // 16))
    title_font = load_font(max(18, thumb_w // 12))
    label_h = font.size + 10
    left = 0
    if row_labels:
        left = max(110, thumb_w // 2)
    top = (title_font.size + 20) if title else 0
    W = left + cols * (thumb_w + pad) + pad
    H = top + len(rows) * (th + label_h + pad) + pad
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((pad, 8), title, fill=(240, 240, 240), font=title_font)
    for ri, r in enumerate(rows):
        y = top + pad + ri * (th + label_h + pad)
        if row_labels:
            d.text((pad, y + th // 2 - font.size), row_labels[ri], fill=(255, 220, 120), font=font)
        for ci, it in enumerate(r):
            x = left + pad + ci * (thumb_w + pad)
            if os.path.exists(it["path"]):
                im = Image.open(it["path"]).convert("RGB")
                im = im.resize((thumb_w, th))
                sheet.paste(im, (x, y))
            d.text((x + 2, y + th + 3), it.get("label", ""), fill=(230, 230, 230), font=font)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    sheet.save(out_path, quality=88)
    return out_path


def write_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
