"""블렌더 안에서 도는 프리비즈 생성기(헤드리스). 직접 부르지 말고 previz.py로 부른다.

  blender -b --factory-startup --python-exit-code 1 -P build_previz.py -- <spec.json> <출력폴더>

자세한 근거는 references/rules.md.
  ① 피사체는 단순 도형(사람 = 하체·상체·머리 3부품 다면체 + 허리 힌지 1개, 팔·다리·목 없음)
  ② 바꿀 대상마다 한눈에 다른 색(순서표, SKILL.md 1절) — 이미지를 따로 받는 대상만 각자 색, 나머지 사람은 한 색
     + 같은 색 안에서 면 밝기 3단(앞 밝게·옆 중간·뒤 어둡게), 전부 무광
  ③ 배경·바닥은 R=G=B 회색, 카메라는 매 프레임 구워 컷은 한 영상 안 1프레임 도약(하드 컷)
  ④ 몸을 돌리는 사람은 앞면 표시(머리 앞 쐐기 + 가슴 앞 띠 — dirbox와 같은 방향 부호).
     사람마다 facing_marker: "auto"(기본 — rot 키 폭이 45° 이상이면 켬) · true/"both" · "chest" · "head" · false
     auto인데 얼굴 앞에 제품(kind: product — 선글라스 등)이 오는 구간이 있으면 쐐기를 빼고 "chest"로 내린다(쐐기가 제품 상자와 겹침).
  ⑤ 이름 있는 사람(관중 색이 아닌 사람·방향 표시가 켜진 사람)마다 렌즈 기준 몸 방향(0° 정면 · 90° 옆 · 180° 뒤)을
     0.5초마다 qc.json facing_to_lens에 적는다 — 넘기기 글의 몸 각도는 이 값을 따른다(prompt_canon §0-C).

하는 일: 장면 구성 → 매 프레임 굽기 → 렌더 전 숫자 점검(qc.json) → PNG 연속 프레임 렌더 → previz.blend 저장.
"""
import json
import math
import os
import sys

import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(argv) < 2:
    raise SystemExit("사용: blender -b -P build_previz.py -- spec.json outdir")
SPEC_PATH, OUT = argv[0], argv[1]
with open(SPEC_PATH, encoding="utf-8") as f:
    SPEC = json.load(f)
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- 색(선형 RGB = 블렌더 값)
# 색 이름표(정본 검증 + 추가 색). 고르는 순서·피할 색은 SKILL.md 1절 표시 — 대상별 색은 spec.palette(id 키)로 준다.
PALETTE = {
    "magenta": (0.85, 0.03, 0.55),      # ≈ #ED30C4 — 가장 확실한 치환 신호(콜라 7R 얼음 즉시 치환)
    "purple": (0.45, 0.10, 0.85),       # ≈ #B359ED
    "hotpink": (0.95, 0.15, 0.45),      # ≈ #F96CB3
    "violet": (0.28, 0.05, 0.45),       # ≈ #903FB3
    "deepcyan": (0.00, 0.62, 0.72),     # ≈ #00CEDD
    "palecyan": (0.55, 0.95, 1.00),     # ≈ #C4F9FF — 물·입자(명도 3단 안 씀)
    "yellow": (1.00, 0.65, 0.014),      # ≈ #FFD21F — ⚠ 정본 검증 밖(분홍·마젠타 계열을 못 쓸 장면용 추가)
    "lime": (0.27, 0.66, 0.0),          # ≈ #8FD400 — ⚠ 정본 검증 밖(분홍·라일락 장소용)
    "orange": (1.00, 0.195, 0.0),       # ≈ #FF7A00 — ⚠ 정본 검증 밖(분홍·라일락 장소용)
}
# 종류 → 기본 색 이름. 주인공 물건(제품)이 가장 확실한 신호(마젠타)를 갖는다.
# 순서표: 주인공 purple → 제품 magenta → 둘째 인물 yellow → 관중·나머지 사람 deepcyan(한 색) → 소품 lime → orange
# 사람은 spec.palette에 id(또는 person1·person2)로 색을 받은 사람만 따로 칠한다. 안 적으면 첫 사람만 purple, 나머지는 전부 관중 색.
KIND_COLOR = {"product": "magenta", "person": ["purple"], "crowd": "deepcyan",
              "prop": "lime", "effect": "orange", "animal": "orange", "vehicle": "orange"}
GRAYS = {"background": 0.62, "floor": 0.42, "set": 0.57, "landmark": 0.53}  # R=G=B (선형)
# 정본(EEVEE)은 균일한 회색 월드 빛(≈0.62~0.72) 아래 무광 재질이라 화면 밝기 ≈ 재질색 × 0.65였다.
# Workbench FLAT은 재질색을 그대로 찍으므로 같은 화면이 되게 물체·세트에 이 배율을 곱한다(배경은 그대로).
FLAT_EXPOSURE = 0.65
TONE_HI, TONE_LO, TONE_DOT = 0.30, 0.34, 0.35   # 정본 v17 tone_mats()/add_poly() 값 그대로
# 사람 앞면 표시(곧은 기둥 더미는 몸 돌리기가 결과로 잘 안 옮겨짐). 'auto'면 rot 키 폭이 이 각도 이상일 때만 켬.
MARKER_AUTO_DEG = 45.0

R = SPEC.get("render", {})
FPS = int(R.get("fps", 24))
W, H = int(R.get("width", 720)), int(R.get("height", 1280))
CUTS = SPEC["cuts"]
DURATION = float(R.get("duration") or CUTS[-1]["end"])
NFRAMES = int(round(DURATION * FPS))
USER_PAL = SPEC.get("palette", {})  # {"product": "#hex" 또는 색 이름, "model": ...(id별)}


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def parse_color(v):
    if isinstance(v, (list, tuple)):
        return tuple(float(x) for x in v[:3])
    if isinstance(v, str) and v in PALETTE:
        return PALETTE[v]
    if isinstance(v, str) and v.startswith("#"):
        h = v.lstrip("#")
        return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))
    raise SystemExit("색을 읽을 수 없음: %r" % (v,))


# ---------------------------------------------------------------- 장면 기본
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, NFRAMES
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.resolution_percentage = int(R.get("scale_percent", 100))
scene.render.use_motion_blur = False             # 정본: 프리비즈 렌더는 모션 블러 끔
try:
    scene.view_settings.view_transform = "Standard"  # 색 이름 = 화면 색이 되도록(AgX ✕)
    scene.view_settings.look = "None"
except Exception:
    pass
# 렌더러: Workbench + FLAT 조명 + 머티리얼 색 = 면 밝기 3단이 조명과 무관하게 '물체에 고정'된다.
# (정본 EEVEE도 균일한 월드 조명 + 무광이라 화면 결과는 같은 원리. 블렌더 5.2에서 Workbench 렌더 확인)
ENGINE = R.get("engine", "WORKBENCH").upper()
if ENGINE == "WORKBENCH":
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "FLAT"
    sh.color_type = "MATERIAL"
    sh.show_shadows = False
    try:
        sh.show_cavity = False
        sh.show_object_outline = False
        sh.show_specular_highlight = False
    except Exception:
        pass
    try:
        scene.display.render_aa = "8"
    except Exception:
        pass
else:
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = eng
            break
        except TypeError:
            continue
world = bpy.data.worlds.new("PrevizWorld")
scene.world = world
g = float(SPEC.get("world", {}).get("background_gray", GRAYS["background"]))
world.color = (g, g, g)
world.use_nodes = True
try:
    bgn = world.node_tree.nodes["Background"]
    bgn.inputs[0].default_value = (g, g, g, 1.0)  # EEVEE: 이 회색이 배경이자 균일한 빛(정본 방식)
except Exception:
    pass
ims = scene.render.image_settings
if hasattr(ims, "media_type"):
    ims.media_type = "IMAGE"                       # 5.x: media_type 먼저
ims.file_format = "PNG"
ims.color_mode = "RGB"

# ---------------------------------------------------------------- 머티리얼
_MATS = {}


def flat_mat(name, rgb):
    if ENGINE == "WORKBENCH":
        rgb = tuple(c * FLAT_EXPOSURE for c in rgb)
    key = (name, tuple(round(c, 4) for c in rgb))
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name)
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)   # Workbench MATERIAL 색
    m.roughness = 0.9
    m.metallic = 0.0
    m.specular_intensity = 0.0
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        bs.inputs["Roughness"].default_value = 0.9
        for k in ("Specular", "Specular IOR Level"):
            if k in bs.inputs:
                bs.inputs[k].default_value = 0.0
    _MATS[key] = m
    return m


def tone_mats(cname, rgb):
    r, g_, b = rgb
    hi = (min(1, r + (1 - r) * TONE_HI), min(1, g_ + (1 - g_) * TONE_HI), min(1, b + (1 - b) * TONE_HI))
    lo = (r * TONE_LO, g_ * TONE_LO, b * TONE_LO)
    return [flat_mat(cname + "_Hi", hi), flat_mat(cname + "_Mid", rgb), flat_mat(cname + "_Lo", lo)]


def apply_tones(obj, cname, rgb, front=(0.0, -1.0, 0.0), tone=True):
    """면 노멀·로컬 정면 내적으로 명도 3단 배정(정본 apply_tone_faces). 면은 각지게(use_smooth=False)."""
    me = obj.data
    me.materials.clear()
    if not tone:
        me.materials.append(flat_mat(cname, rgb))
        for p in me.polygons:
            p.use_smooth = False
        return
    for m in tone_mats(cname, rgb):
        me.materials.append(m)
    fw = Vector(front).normalized()
    for p in me.polygons:
        d = p.normal.dot(fw)
        p.material_index = 0 if d > TONE_DOT else (2 if d < -TONE_DOT else 1)
        p.use_smooth = False


def poly_mesh(name, verts, faces, parent=None, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.parent = parent
    o.location = loc
    return o


def add_empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    scene.collection.objects.link(e)
    e.empty_display_size = 0.1
    e.parent = parent
    e.location = loc
    return e


# ---------------------------------------------------------------- 도형
def box_verts(sx, sy, sz, z0=0.0):
    x, y = sx / 2.0, sy / 2.0
    v = [(-x, -y, z0), (x, -y, z0), (x, y, z0), (-x, y, z0),
         (-x, -y, z0 + sz), (x, -y, z0 + sz), (x, y, z0 + sz), (-x, y, z0 + sz)]
    f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return v, f


def dirbox_verts(sx, sy, sz):
    """방향 부호화 상자: +X 위 모서리만 깎아 좌우 비대칭(돌 때 어느 면인지 읽힘). 앞 = −Y."""
    x, y = sx / 2.0, sy / 2.0
    cz, cx = sz * 0.30, sx * 0.30
    v = [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0),          # 0-3 바닥
         (-x, -y, sz), (-x, y, sz),                                # 4-5 −X 위
         (x, -y, sz - cz), (x, y, sz - cz),                        # 6-7 +X 깎인 아래
         (x - cx, -y, sz), (x - cx, y, sz)]                        # 8-9 깎인 위
    f = [(0, 1, 2, 3), (0, 1, 6, 8, 4), (2, 3, 5, 9, 7), (1, 2, 7, 6), (3, 0, 4, 5), (6, 7, 9, 8), (4, 8, 9, 5)]
    return v, f


def prism_verts(n, sx, sy, sz):
    """n각 기둥(원기둥 대용 — 매끈한 원기둥은 방향 정보 0이라 면이 보이는 각기둥)."""
    v, f = [], []
    for z in (0.0, sz):
        for k in range(n):
            a = 2 * math.pi * k / n + math.pi / n
            v.append((math.cos(a) * sx / 2.0, math.sin(a) * sy / 2.0, z))
    f.append(tuple(range(n)))
    f.append(tuple(range(n, 2 * n)))
    for k in range(n):
        f.append((k, (k + 1) % n, n + (k + 1) % n, n + k))
    return v, f


def lump_verts(sx, sy, sz):
    """불규칙 덩어리(얼음·바위·음식 등 프라이어 강한 것 — 최소형 프록시)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.5)
    verts = []
    for i, vv in enumerate(bm.verts):
        j = 0.85 + 0.3 * ((i * 37 % 11) / 10.0)
        verts.append((vv.co.x * sx * j, vv.co.y * sy * j, vv.co.z * sz * j + sz / 2.0))
    faces = [tuple(v.index for v in fc.verts) for fc in bm.faces]
    bm.free()
    return verts, faces


def human_profile(part, Hh, hip_ratio=0.52):
    """정본 previz_engine.poly_profile 그대로(허리 너클 포함). 좌표: 정면 = −Y, 왼쪽 = +X, 발바닥 z≈0."""
    hip = Hh * hip_ratio
    zb, zm, zt = Hh * 0.008, hip, Hh * 0.845
    bx0, by0 = Hh * 0.070, Hh * 0.048
    bx1, by1 = Hh * 0.100, Hh * 0.062
    bx2, by2 = Hh * 0.128, Hh * 0.072
    if part == "lower":
        v = [(-bx0, -by0, zb), (bx0, -by0, zb), (bx0, by0, zb), (-bx0, by0, zb),
             (-bx1, -by1, zm), (bx1, -by1, zm), (bx1, by1, zm), (-bx1, by1, zm)]
        f = [(0, 1, 2, 3), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]
        return v, f
    if part == "upper":
        chz, chx = Hh * 0.10, Hh * 0.058
        zc, cx = zt - chz, bx2 - chx
        v = [(-bx1, -by1, zm), (bx1, -by1, zm), (bx1, by1, zm), (-bx1, by1, zm),
             (-bx2, -by2, zt), (-bx2, by2, zt), (bx2, -by2, zc), (bx2, by2, zc), (cx, -by2, zt), (cx, by2, zt)]
        f = [(0, 1, 6, 8, 4), (2, 3, 5, 9, 7), (1, 2, 7, 6), (3, 0, 4, 5), (6, 7, 9, 8), (4, 8, 9, 5)]
        # 허리 너클: 평평한 뚜껑 대신 힌지 축과 동심 원호(젖혀도 뚜껑 면이 화면에 안 나옴)
        Rr, n = by1, 8
        slope_x = (bx1 - bx0) / (zm - zb)
        ring = [(1, 0)]
        for k in range(1, n):
            phi = math.pi * k / n
            dep = Rr * math.sin(phi)
            yk, zk = -Rr * math.cos(phi), zm - dep
            xk = bx1 - slope_x * dep
            v.append((xk, yk, zk))
            v.append((-xk, yk, zk))
            ring.append((len(v) - 2, len(v) - 1))
        ring.append((2, 3))
        for k in range(n):
            (ap, am), (bp, bm_) = ring[k], ring[k + 1]
            f.append((ap, am, bm_, bp))
        f.append(tuple(p for p, _ in ring))
        f.append(tuple(m for _, m in ring))
        return v, f
    if part == "head":
        z0 = Hh * 0.925
        wF = Hh * 0.070
        dF, dB = Hh * 0.055, Hh * 0.078
        wB, sx = wF * 0.42, Hh * 0.015
        zTp, zBt = z0 + Hh * 0.065, z0 - Hh * 0.085
        zbT, zbB = z0 + Hh * 0.040, z0 - Hh * 0.045
        v = [(-wF, -dF, zBt), (wF, -dF, zBt), (wF, -dF, zTp), (-wF, -dF, zTp),
             (-wB + sx, dB, zbB), (wB + sx, dB, zbB), (wB + sx, dB, zbT), (-wB + sx, dB, zbT)]
        f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        return v, f
    raise SystemExit(part)


def facing_marker_parts(Hh, hip_ratio=0.52):
    """사람 앞면 표시(정면 = −Y). human_profile과 같은 좌표(발바닥 z≈0, 허리 힌지 아래위 같은 오프셋).
    head = 머리 앞면 가운데 아래쪽의 작은 쐐기(모양으로 방향 — dirbox 원리 · 옆에서 보면 튀어나옴)
    chest = 상체 앞면 가운데 세로 띠(살짝 돌출 — 옆에서 보면 능선)
    둘 다 같은 색의 어두운 단(Lo)으로 칠한다 — 밝은 앞면 위에서 또렷(rules.md '방향은 색이 말한다').
    팔·다리·얼굴 흉내가 아니라 방향 부호다(빼기 규칙의 예외는 이것뿐)."""
    hip = Hh * hip_ratio
    zm, zt = hip, Hh * 0.845
    by1, by2 = Hh * 0.062, Hh * 0.072
    # 머리 쐐기 — 머리 앞면(y = −dF) 가운데, 위는 얕고 아래는 깊게(콧날처럼 비스듬히)
    z0, dF = Hh * 0.925, Hh * 0.055
    zT, zB = z0 + Hh * 0.005, z0 - Hh * 0.050
    wn, yb = Hh * 0.022, -dF + Hh * 0.010          # 밑면은 머리 속으로 1cm쯤 묻음(틈 방지)
    yT, yB = -dF - Hh * 0.015, -dF - Hh * 0.035
    head_v = [(-wn, yb, zT), (wn, yb, zT), (wn, yb, zB), (-wn, yb, zB), (0.0, yT, zT), (0.0, yB, zB)]
    head_f = [(0, 3, 5, 4), (1, 4, 5, 2), (0, 4, 1), (3, 2, 5), (0, 1, 2, 3)]
    # 가슴 띠 — 상체 앞면(허리 y=−by1 → 어깨 y=−by2로 비스듬)을 따라 세로로, 앞으로 약 0.015H 돌출
    zA, zC = zm + (zt - zm) * 0.25, zt - Hh * 0.030
    wb, emb, pro = Hh * 0.020, Hh * 0.010, Hh * 0.022

    def yfront(z):
        return -(by1 + (by2 - by1) * (z - zm) / (zt - zm))
    chest_v = []
    for z in (zA, zC):
        yf = yfront(z)
        chest_v += [(-wb, yf + emb, z), (wb, yf + emb, z), (wb, yf - pro, z), (-wb, yf - pro, z)]
    chest_f = [(0, 1, 2, 3), (4, 7, 6, 5), (3, 2, 6, 7), (0, 4, 5, 1), (1, 5, 6, 2), (0, 3, 7, 4)]
    return {"head": (head_v, head_f), "chest": (chest_v, chest_f)}


def marker_mode(o):
    """사람 명세의 facing_marker → None | 'both' | 'chest' | 'head'."""
    v = o.get("facing_marker", "auto")
    if v in (False, None, "off", "none"):
        return None
    if v == "auto":
        rots = [float(k["rot"]) for k in o.get("keys", []) if "rot" in k]
        if len(rots) < 2 or (max(rots) - min(rots)) < MARKER_AUTO_DEG:
            return None
        return "both"
    if v is True:
        return "both"
    if v in ("both", "chest", "head"):
        return v
    raise SystemExit("facing_marker는 auto/true/false/both/chest/head 중 하나: %s=%r" % (o.get("id"), v))


# ---------------------------------------------------------------- 보간
def ease(p, mode="inout"):
    p = max(0.0, min(1.0, p))
    if mode == "linear":
        return p
    if mode == "in":
        return p * p * p
    if mode == "out":
        q = 1 - p
        return 1 - q * q * q
    return p * p * p * (p * (p * 6 - 15) + 10)   # 정본: quintic smootherstep(저크 최소)


def pchip(xs, ys, x):
    """단조 3차 보간(오버슛 없음 — 정본 카메라 표 보간)."""
    n = len(xs)
    if n == 1 or x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] if h[i] else 0.0 for i in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    for i in range(n - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / h[i] if h[i] else 0.0
            h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
            h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
            return h00 * ys[i] + h10 * h[i] * m[i] + h01 * ys[i + 1] + h11 * h[i] * m[i + 1]
    return ys[-1]


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


# ---------------------------------------------------------------- 장면 만들기
WS = SPEC.get("world", {})
if WS.get("floor", True):
    fg = float(WS.get("floor_gray", GRAYS["floor"]))
    fl = poly_mesh("floor", [(-40, -40, 0), (40, -40, 0), (40, 40, 0), (-40, 40, 0)], [(0, 1, 2, 3)])
    apply_tones(fl, "floor", (fg, fg, fg), tone=False)
for i, st in enumerate(WS.get("set", [])):
    # 세트(벽·가구·랜드마크): 회색(R=G=B). 회전 컷에는 비대칭 랜드마크가 꼭 필요(정본).
    gval = float(st.get("gray", GRAYS["set"] if st.get("type") != "landmark" else GRAYS["landmark"]))
    sv, sf = box_verts(*st.get("size", [1, 1, 1]))
    o = poly_mesh(st.get("id", "set_%d" % i), sv, sf)
    o.location = st.get("pos", [0, 0, 0])
    o.rotation_euler = (0, 0, math.radians(st.get("rot", 0)))
    apply_tones(o, "set_%d" % i, (gval, gval, gval), tone=bool(st.get("tone", False)))

OBJ = {}
person_n = 0
for o in SPEC.get("objects", []):
    kind = o.get("kind", "prop")
    if o["id"] in USER_PAL:
        col = parse_color(USER_PAL[o["id"]])
        cname = o["id"]
    elif "color" in o:
        col = parse_color(o["color"])
        cname = o["id"]
    elif kind == "person":
        names = KIND_COLOR["person"]
        cname = USER_PAL.get("person%d" % (person_n + 1)) or (names[person_n] if person_n < len(names) else (USER_PAL.get("crowd") or KIND_COLOR["crowd"]))
        col = parse_color(cname)
    else:
        cname = USER_PAL.get(kind) or KIND_COLOR.get(kind, "lime")
        col = parse_color(cname)
    root = add_empty(o["id"])
    entry = {"root": root, "spec": o, "kind": kind, "color": cname, "meshes": [], "hinge": None,
             "facing_marker": None, "mark_head": None, "height": None}
    if kind == "person":
        person_n += 1
        Hh = float(o.get("height", 1.70))
        hip_ratio = 0.50 if o.get("child") else 0.52
        v, f = human_profile("lower", Hh, hip_ratio)
        low = poly_mesh(o["id"] + ".lower", v, f, root)
        hinge = add_empty(o["id"] + ".waist", (0, 0, Hh * hip_ratio), root)
        v, f = human_profile("upper", Hh, hip_ratio)
        up = poly_mesh(o["id"] + ".upper", v, f, hinge, (0, 0, -Hh * hip_ratio))
        v, f = human_profile("head", Hh, hip_ratio)
        hd = poly_mesh(o["id"] + ".head", v, f, hinge, (0, 0, -Hh * hip_ratio))
        for m in (low, up, hd):
            apply_tones(m, cname, col)
        entry["meshes"] = [low, up, hd]
        entry["hinge"] = hinge
        entry["height"] = (Hh, hip_ratio)
        mk = marker_mode(o)
        entry["facing_marker"] = mk
        if mk:
            parts = facing_marker_parts(Hh, hip_ratio)
            if mk in ("both", "head"):
                v, f = parts["head"]
                nose = poly_mesh(o["id"] + ".mark_head", v, f, hinge, (0, 0, -Hh * hip_ratio))
                apply_tones(nose, cname, col)
                for p_ in nose.data.polygons:              # 같은 색의 어두운 단 — 밝은 얼굴 면 위에서 보임
                    p_.material_index = 2
                entry["meshes"].append(nose)
                entry["mark_head"] = nose
            if mk in ("both", "chest"):
                v, f = parts["chest"]
                band = poly_mesh(o["id"] + ".mark_chest", v, f, hinge, (0, 0, -Hh * hip_ratio))
                apply_tones(band, cname, col)
                for p_ in band.data.polygons:              # 띠 전체 = 같은 색의 어두운 단(앞면 밝은 단 위에서 또렷)
                    p_.material_index = 2
                entry["meshes"].append(band)
    else:
        shape = o.get("shape", "box")
        size = o.get("size", [0.3, 0.3, 0.3])
        if shape == "box":
            v, f = box_verts(*size)
        elif shape == "dirbox":
            v, f = dirbox_verts(*size)
        elif shape in ("prism", "cylinder"):
            v, f = prism_verts(int(o.get("sides", 8)), *size)
        elif shape == "lump":
            v, f = lump_verts(*size)
        elif shape == "plane":
            v, f = [(-size[0] / 2, -size[1] / 2, 0.002), (size[0] / 2, -size[1] / 2, 0.002),
                    (size[0] / 2, size[1] / 2, 0.002), (-size[0] / 2, size[1] / 2, 0.002)], [(0, 1, 2, 3)]
        else:
            raise SystemExit("모르는 shape: %s (box/dirbox/prism/lump/plane)" % shape)
        pv = o.get("pivot")  # 회전 중심(바닥 가운데 기준 로컬 m) — 예: 뚜껑의 뒤쪽 아래 모서리 = 경첩
        body = poly_mesh(o["id"] + ".body", v, f, root,
                         loc=(-pv[0], -pv[1], -pv[2]) if pv else (0, 0, 0))
        apply_tones(body, cname, col, tone=(kind != "effect"))
        entry["meshes"] = [body]
    OBJ[o["id"]] = entry


# ---------------------------------------------------------------- 굽기(물체·사람)
frames_t = [(f, (f - 1) / float(FPS)) for f in range(1, NFRAMES + 1)]


def obj_state(oid, t):
    sp = OBJ[oid]["spec"]
    keys = sorted(sp.get("keys", [{"t": 0, "pos": [0, 0, 0]}]), key=lambda k: k["t"])
    return (sample_keys(keys, t, "pos", [0, 0, 0]), sample_keys(keys, t, "rot", 0.0),
            sample_keys(keys, t, "rot_x", 0.0), sample_keys(keys, t, "bend", 0.0),
            sample_keys(keys, t, "scale", 1.0), sample_keys(keys, t, "visible", True))


for oid, e in OBJ.items():
    root = e["root"]
    keys = e["spec"].get("keys", [])
    has_vis = any("visible" in k for k in keys)
    for fr, t in frames_t:
        pos, yaw, tilt, bend, scale, vis = obj_state(oid, t)
        root.location = pos
        root.rotation_euler = Euler((math.radians(tilt), 0.0, math.radians(yaw)), "XYZ")
        s = scale if isinstance(scale, list) else [scale] * 3
        root.scale = s
        root.keyframe_insert("location", frame=fr)
        root.keyframe_insert("rotation_euler", frame=fr)
        root.keyframe_insert("scale", frame=fr)
        if e["hinge"] is not None:
            # 허리 힌지: + = 앞으로 숙임, − = 뒤로 젖힘(도). 대자세는 힌지(V) + 텍스트 병행(정본 C-α)
            e["hinge"].rotation_euler = Euler((math.radians(bend), 0, 0), "XYZ")
            e["hinge"].keyframe_insert("rotation_euler", frame=fr)
        if has_vis:
            for m in e["meshes"]:
                m.hide_render = not bool(vis)
                m.keyframe_insert("hide_render", frame=fr)

# 따라 붙는 물건(손에 든 제품 등): follow = {"to": id, "offset": [x,y,z](대상 로컬), "from": 초, "until": 초}
# 팔이 없는 정본 더미라 '손 위치'는 상체 앞 어딘가 — 위치·크기만 맞추고 손 동작은 텍스트로.
for oid, e in OBJ.items():
    fol = e["spec"].get("follow")
    if not fol:
        continue
    host = OBJ[fol["to"]]
    anchor = host["hinge"] if (host["hinge"] is not None and fol.get("upper", True)) else host["root"]
    off = Vector(fol.get("offset", [0.0, -0.25, 0.25]))
    for fr, t in frames_t:
        if fol.get("from", 0) <= t <= fol.get("until", 1e9):
            scene.frame_set(fr)
            mw = anchor.matrix_world @ Matrix.Translation(off)
            loc, rot, _ = mw.decompose()
            e["root"].location = loc
            e["root"].rotation_euler = (rot.to_euler("XYZ").x, rot.to_euler("XYZ").y,
                                        rot.to_euler("XYZ").z + math.radians(fol.get("rot", 0)))
            e["root"].keyframe_insert("location", frame=fr)
            e["root"].keyframe_insert("rotation_euler", frame=fr)

# 얼굴 앞 제품 검사: 머리 쐐기가 켜진 사람 얼굴 앞에 제품(kind: product — 선글라스 등)이
# 0.25초 넘게 이어서 오면 auto는 쐐기를 빼고 "chest"로 내리고, 직접 고른 both/head/true는 경고만 낸다.
MARKER_NOTES = []


def _face_hits(e, others, step_fr):
    Hh, hip_ratio = e["height"]
    z0 = Hh * 0.925 - Hh * 0.02
    hits = {}
    for fr, t in frames_t[::step_fr]:
        scene.frame_set(fr)
        inv = e["hinge"].matrix_world.inverted()
        for oid2, e2 in others:
            if any(m.hide_render for m in e2["meshes"]):
                continue
            sz = e2["spec"].get("size", [0.3, 0.3, 0.3])
            pv = e2["spec"].get("pivot") or [0, 0, 0]
            c = e2["root"].matrix_world @ Vector((-pv[0], -pv[1], sz[2] / 2.0 - pv[2]))
            q = inv @ c + Vector((0, 0, Hh * hip_ratio))     # 사람 메시 좌표(발바닥 z≈0, 정면 = −Y)
            if abs(q.x) <= 0.10 * Hh and abs(q.z - z0) <= 0.08 * Hh and -0.20 * Hh <= q.y <= 0.0:
                hits.setdefault(oid2, []).append(t)
    dt = step_fr / float(FPS)
    runs = {}
    for k, ts in hits.items():                               # 0.25초(표본 3개) 넘게 이어진 구간만
        seg = [ts[0], ts[0], 1]
        for t in ts[1:]:
            if t - seg[1] <= dt * 1.5:
                seg[1], seg[2] = t, seg[2] + 1
            else:
                if seg[2] >= 3:
                    runs.setdefault(k, []).append((seg[0], seg[1]))
                seg = [t, t, 1]
        if seg[2] >= 3:
            runs.setdefault(k, []).append((seg[0], seg[1]))
    return runs


_others = [(k, v) for k, v in OBJ.items() if v["kind"] == "product"]   # 얼굴에 쓰는 것 = 제품(공 같은 소품은 스쳐 지나감)
_step_fr = max(1, FPS // 8)
for oid, e in OBJ.items():
    if e["facing_marker"] not in ("both", "head") or not _others:
        continue
    hits = _face_hits(e, [x for x in _others if x[0] != oid], _step_fr)
    if not hits:
        continue
    span = " · ".join("%s %s" % (k, ", ".join("%.1f~%.1f초" % r for r in v)) for k, v in hits.items())
    if e["spec"].get("facing_marker", "auto") == "auto" and e["mark_head"] is not None:
        nose = e["mark_head"]
        e["meshes"].remove(nose)
        bpy.data.objects.remove(nose, do_unlink=True)
        e["mark_head"] = None
        e["facing_marker"] = "chest"
        MARKER_NOTES.append("%s: 얼굴 앞에 제품이 오는 구간(%s)이 있어 방향 표시를 auto → chest(가슴 띠만)로 내림 — "
                            "머리 쐐기가 제품 상자와 겹치지 않게" % (oid, span))
    else:
        MARKER_NOTES.append("%s: facing_marker=%r인데 얼굴 앞에 제품이 오는 구간(%s)이 있음 — 머리 쐐기가 제품과 겹치니 "
                            "\"chest\"로 바꾸기를 권함" % (oid, e["spec"].get("facing_marker"), span))

# ---------------------------------------------------------------- 카메라
cam_data = bpy.data.cameras.new("previz_cam")
cam_data.sensor_width = 36
cam_data.clip_start = 0.02
cam = bpy.data.objects.new("previz_cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam


def target_info(target, t, offset):
    """바라볼 점 + 그 대상의 정면 방위(yaw)."""
    if isinstance(target, str):
        if target not in OBJ:
            raise SystemExit("카메라 target '%s'가 objects에 없습니다" % target)
        scene.frame_set(int(round(t * FPS)) + 1)
        base = OBJ[target]["root"].matrix_world.translation.copy()
        yaw = sample_keys(OBJ[target]["spec"].get("keys", []), t, "rot", 0.0)
        return base + Vector(offset), yaw
    return Vector(target) + Vector(offset), 0.0


def cut_keys(cs, start, end):
    """카메라 표 → (상대 시각 목록, 키 목록). from/to는 두 줄짜리 표의 줄임."""
    if "keys" in cs:
        ks = sorted(cs["keys"], key=lambda k: k["t"])
        return ks
    a = dict(cs.get("from", {}))
    b = dict(a)
    b.update(cs.get("to", {}))
    hs, he = float(cs.get("hold_start", 0)), float(cs.get("hold_end", 0))
    a["t"], b["t"] = start + hs, end - he
    b["ease"] = cs.get("ease", "inout")
    return [a, b]


def cam_state(c, t):
    cs = c["camera"]
    ks = cut_keys(cs, c["start"], c["end"])
    target = cs.get("target", [0, 0, 0])
    offset = cs.get("look_offset", [0, 0, 1.2] if isinstance(target, str) else [0, 0, 0])
    follow = cs.get("follow", True)
    tp, tyaw = target_info(target, t if follow else c["start"], offset)
    rel = cs.get("relative_to_facing", True)
    vals = {}
    two_point = "keys" not in cs
    for fld, dflt in (("az", 0.0), ("h", 1.5), ("dist", 3.0), ("tilt", 0.0), ("pan", 0.0), ("roll", 0.0),
                      ("lens", 35.0)):
        pts = [(k["t"], k[fld]) for k in ks if fld in k]
        if not pts:
            vals[fld] = dflt
        elif two_point:
            # 두 줄 표: 출발·도착 사이를 ease로(기본 quintic). hold 구간은 정지.
            (t0, v0), (t1, v1) = pts[0], pts[-1]
            p = 0.0 if t1 <= t0 else ease((t - t0) / (t1 - t0), ks[-1].get("ease", "inout"))
            vals[fld] = v0 + (v1 - v0) * p
        else:
            vals[fld] = pchip([p[0] for p in pts], [p[1] for p in pts], t)
    pos_pts = [(k["t"], k["pos"]) for k in ks if "pos" in k]
    if pos_pts:
        if len(pos_pts) == 1:
            pos = Vector(pos_pts[0][1])
        else:
            pos = Vector([pchip([p[0] for p in pos_pts], [p[1][i] for p in pos_pts], t) for i in range(3)])
            if two_point:
                (t0, v0), (t1, v1) = pos_pts[0], pos_pts[-1]
                p = 0.0 if t1 <= t0 else ease((t - t0) / (t1 - t0), ks[-1].get("ease", "inout"))
                pos = Vector(v0).lerp(Vector(v1), p)
    else:
        # 방위 0 = 대상 정면, + = 대상의 오른쪽 면 쪽(정본 카메라 표 규약).
        # 대상 정면 벡터 f(ψ) = (sin ψ, −cos ψ) (yaw 0이면 −Y). 카메라 방향 = f(ψ − az).
        ang = math.radians(vals["az"] - (tyaw if rel else 0.0))
        d = vals["dist"]
        pos = Vector((tp.x - math.sin(ang) * d, tp.y - math.cos(ang) * d, vals["h"]))
    look_pts = [(k["t"], k["look"]) for k in ks if "look" in k]
    if look_pts:
        if len(look_pts) == 1:
            tp = Vector(look_pts[0][1])
        elif two_point:
            (t0, v0), (t1, v1) = look_pts[0], look_pts[-1]
            p = 0.0 if t1 <= t0 else ease((t - t0) / (t1 - t0), ks[-1].get("ease", "inout"))
            tp = Vector(v0).lerp(Vector(v1), p)
        else:
            tp = Vector([pchip([q[0] for q in look_pts], [q[1][i] for q in look_pts], t) for i in range(3)])
    return pos, tp, vals


CAMLOG = []
for fr, t in frames_t:
    c = next((c for c in CUTS if c["start"] <= t < c["end"]), CUTS[-1])
    pos, look, v = cam_state(c, t)
    q = (look - pos).to_track_quat("-Z", "Y")
    m = q.to_matrix().to_4x4()
    if v["pan"] or v["tilt"] or v["roll"]:
        m = m @ Matrix.Rotation(math.radians(v["pan"]), 4, "Y") @ \
            Matrix.Rotation(math.radians(v["tilt"]), 4, "X") @ Matrix.Rotation(math.radians(v["roll"]), 4, "Z")
    cam.location = pos
    cam.rotation_euler = m.to_euler("XYZ")
    cam_data.lens = v["lens"]
    cam.keyframe_insert("location", frame=fr)
    cam.keyframe_insert("rotation_euler", frame=fr)
    cam_data.keyframe_insert("lens", frame=fr)
    CAMLOG.append((fr, t, c["id"], tuple(pos), tuple(look), v["lens"]))


def all_fcurves(idblock):
    ad = getattr(idblock, "animation_data", None)
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and not hasattr(act, "layers"):
        return list(act.fcurves)
    out = []
    for layer in getattr(act, "layers", []):          # 5.x 층 구조
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    if not out and hasattr(act, "fcurves"):
        out = list(act.fcurves)
    return out


# 매 프레임 키를 '계단'으로 → 컷 경계가 1프레임 도약(하드 컷)으로 정확히 유지
for ob in [cam, cam_data] + [e["root"] for e in OBJ.values()] + [e["hinge"] for e in OBJ.values() if e["hinge"]]:
    for fc in all_fcurves(ob):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
for c in CUTS:
    mk = scene.timeline_markers.new(c["id"], frame=int(round(c["start"] * FPS)) + 1)
    mk.camera = cam

# ---------------------------------------------------------------- 렌더 전 숫자 점검(0원)
QC = {"cuts": {}, "objects": {}, "warnings": []}
deps = bpy.context.evaluated_depsgraph_get()


def screen_box(e):
    """화면 위 사각 범위 + 카메라에서 가장 가까운 꼭짓점 거리(m)."""
    xs, ys, zs, dmin = [], [], [], 1e9
    cpos = cam.matrix_world.translation
    for mobj in e["meshes"]:
        if mobj.hide_render:
            continue
        mw = mobj.matrix_world
        for vtx in mobj.data.vertices:
            wv = mw @ vtx.co
            p = world_to_camera_view(scene, cam, wv)
            xs.append(p.x)
            ys.append(p.y)
            zs.append(p.z)
            dmin = min(dmin, (wv - cpos).length)
    if not xs:
        return None
    return min(xs), max(xs), min(ys), max(ys), min(zs), dmin


step = max(1, FPS // 8)
for c in CUTS:
    QC["cuts"][c["id"]] = {"objects": {}}
for fr, t in frames_t[::step] + [frames_t[-1]]:
    scene.frame_set(fr)
    c = next((c for c in CUTS if c["start"] <= t < c["end"]), CUTS[-1])
    cq = QC["cuts"][c["id"]]["objects"]
    for oid, e in OBJ.items():
        sb = screen_box(e)
        if sb is None:
            continue
        x0, x1, y0, y1, zmin, near = sb
        in_front = zmin > 0
        cx0, cx1, cy0, cy1 = max(0, x0), min(1, x1), max(0, y0), min(1, y1)
        vis_area = max(0, cx1 - cx0) * max(0, cy1 - cy0) if in_front else 0.0
        clipped = in_front and vis_area > 0 and (x0 < 0 or x1 > 1 or y0 < 0 or y1 > 1)
        dist = near
        d = cq.setdefault(oid, {"max_screen_pct": 0.0, "visible_frames": 0, "clipped_frames": 0,
                                "checked": 0, "min_cam_dist_m": 1e9})
        d["checked"] += 1
        d["max_screen_pct"] = max(d["max_screen_pct"], round(vis_area * 100, 1))
        if vis_area > 0.0005:
            d["visible_frames"] += 1
        if clipped:
            d["clipped_frames"] += 1
        d["min_cam_dist_m"] = round(min(d["min_cam_dist_m"], dist), 2)
for cid, cq in QC["cuts"].items():
    for oid, d in cq["objects"].items():
        if d["max_screen_pct"] >= 75:
            QC["warnings"].append("%s: %s가 화면의 %.0f%%를 덮음(정본 한도 75%% — 넘으면 배경·라벨 붕괴 위험)" % (
                cid, oid, d["max_screen_pct"]))
        if OBJ[oid]["kind"] == "person" and d["min_cam_dist_m"] < 0.8 and d["visible_frames"]:
            QC["warnings"].append("%s: 카메라가 %s 몸 표면에 %.2fm까지 붙음(정본 마진 0.80m — 레퍼런스가 그렇게 붙는 컷이면 이유를 적고 진행)" % (
                cid, oid, d["min_cam_dist_m"]))
for oid, e in OBJ.items():
    QC["objects"][oid] = {"kind": e["kind"], "color": e["color"]}
    if e["facing_marker"]:
        QC["objects"][oid]["facing_marker"] = e["facing_marker"]
QC["facing_marker"] = [oid for oid, e in OBJ.items() if e["facing_marker"]]
QC["warnings"].extend(MARKER_NOTES)

# 렌즈 기준 몸 방향(글의 몸 각도는 프리비즈 rot과 같아야 한다, prompt_canon §0-C).
# 0° = 렌즈를 정면으로 봄 · 90° = 옆모습 · 180° = 등. side = 몸 앞이 화면 어느 쪽을 향하나(오른쪽/왼쪽).
_crowd_name = USER_PAL.get("crowd") or KIND_COLOR["crowd"]


def _named_person(oid, e):
    if e["kind"] != "person":
        return False
    if e["facing_marker"]:
        return True
    cn = USER_PAL.get(oid) or e["spec"].get("color") or e["color"]
    return cn != _crowd_name


FACING = {oid: [] for oid, e in OBJ.items() if _named_person(oid, e)}
if FACING:
    _half = max(1, int(round(FPS * 0.5)))
    for fr, t in frames_t[::_half]:
        scene.frame_set(fr)
        cmw = cam.matrix_world
        cinv = cmw.to_3x3().inverted()
        for oid in FACING:
            e = OBJ[oid]
            if any(m.hide_render for m in e["meshes"]):
                continue
            rmw = e["root"].matrix_world
            fwd = rmw.to_3x3() @ Vector((0.0, -1.0, 0.0))
            fwd.z = 0.0
            tocam = cmw.translation - rmw.translation
            tocam.z = 0.0
            if fwd.length < 1e-6 or tocam.length < 1e-6:
                continue
            ang = math.degrees(fwd.angle(tocam))
            sx = (cinv @ fwd).x
            side = "정면" if ang < 5 else ("오른쪽" if sx > 0 else "왼쪽")
            FACING[oid].append([round(t, 2), int(round(ang)), side])
QC["facing_to_lens"] = FACING
# 마지막 프레임 카메라가 멈춰 있는지(정본: 길이 메우기용 정지 금지, 의도한 정지는 hold_reason으로 선언)
if len(CAMLOG) > 3:
    p1, p2 = Vector(CAMLOG[-1][3]), Vector(CAMLOG[-3][3])
    l1, l2 = Vector(CAMLOG[-1][4]), Vector(CAMLOG[-3][4])
    if (p1 - p2).length < 1e-4 and (l1 - l2).length < 1e-4:
        last = CUTS[-1]["camera"]
        if not last.get("hold_reason"):
            QC["warnings"].append("마지막 프레임에서 카메라가 완전히 멈춤 — 의도한 정지면 마지막 컷 camera.hold_reason에 이유를 "
                                  "적고, 아니면 끝까지 조금이라도 움직이게(정본: 정지로 길이 메우기 금지)")
QC["engine"] = scene.render.engine
QC["frames"] = NFRAMES
with open(os.path.join(OUT, "qc.json"), "w", encoding="utf-8") as fqc:
    json.dump(QC, fqc, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- 저장·렌더
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "previz.blend"))
if not SPEC.get("_no_render"):
    frames_dir = os.path.join(OUT, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    scene.render.filepath = os.path.join(frames_dir, "f_")
    bpy.ops.render.render(animation=True)
print("PREVIZ_DONE frames=%d fps=%d size=%dx%d engine=%s" % (NFRAMES, FPS, W, H, scene.render.engine))
