# 씨댄스 프롬프트 정본 발췌 — 6단계 넘기기에서 읽는다

- 넘기기의 완성 프롬프트는 이 정본의 **§3-B 「프리비즈 있는 리메이크」 틀**(= §3-A 기본 틀 + §3-B 바꿈)을 그대로 쓰고, §2 참조 표기 경로별·§6 오디오·§7 제출 전 점검·§8 수정 요청 규칙·§1 원칙을 따른다.
- **아래 본문은 원문 문장 그대로다**(각 덩어리 앞 `원문 N~M행` 표시 — 배포본은 원문 속 날짜·사람·내부 메모만 줄이고 규칙 문장은 그대로 두었다). 이 스킬에 필요한 절만 뽑았고, 뽑은 절 안에서 뺀 줄은 그 자리에 적어 두었다. 정본 문장을 우리 말로 바꾸거나 새 틀을 만들지 않고, 정본에 없는 규칙을 더하지 않는다.
- 본문 속 괄호 번호(상충목록 N번 · 07 #N)와 다른 문서 표시(01·03·04·06 §N, `prompt_check.py`, `inputs.json`)는 **원문의 출처 표시**다 — 이 스킬 폴더에는 그 문서·스크립트가 없다. §7의 `prompt_check.py` 점검 항목은 코덱스가 같은 항목을 직접 대조하고, 글자 수는 python으로 센다.
- 틀의 `{purple}`·`{magenta}`는 자리 표시다 — 실제 더미 색(이 스킬 순서표: 주인공 purple → 제품 magenta → 둘째 인물 yellow → 관중·나머지 사람 deepcyan → 소품 lime → orange, `previz_spec`의 `palette`)으로 바꿔 쓴다(아래 §3-B 쓰는 법 '색 이름 = 실제 더미 색').
- **§0은 원문이 아니다** — 이 스킬에서 원문 위에 덮어쓰는 것(실험으로 확인됨). 원문 본문의 규칙은 고치지 않았고, 바뀐 자리 옆에 `[§0-X]` 표시만 달았다. 원문과 §0이 다르면 §0을 따른다.

## 0. 이 스킬에서 원문 위에 덮어쓰는 것 (원문 아님)

아래 영어 문장 중 **§0-B 선언 구절 세 꼴 · §0-C 부정 구절 `never squared up to the lens` · §0-D 사람 유지 문장 꼴 · §0-E 장소 사진 줄 · §0-F 거리 문장과 '다큐판 + 뜨는 장면' 꼴 · §0-H 큰 동작 줄 두 꼴(RULES `{MOVE} POSE RULE` 한 줄 · KEEP 한 줄)**은 `handoff.md` '정본 문장을 고쳐도 되는 범위' 안이다(쓰기 전 확인 없이 쓴다 — 두 문서 같은 목록). §0-C의 비트 예문은 틀 빈칸(`{beat at {t}s}`·`{how she moves}`)을 채우는 보기일 뿐 그대로 옮기는 문장이 아니다.

### §0-B 방향 표시 선언 [추가]
렌더 출력에 `[방향 표시] <id>(쐐기+띠 | 띠만 | 쐐기만)…`(report.json `qc.facing_marker`·`qc.objects.<id>.facing_marker` = both·chest·head)가 있으면 `@previz` 줄 Colour key 문장의 끝 — 세트 선언 `{; the grey blocks are the {SET ITEMS}}` 뒤, 그 문장을 끝내는 마침표 앞(= `. Keep only …` 바로 앞) — 에 한 구절을 붙인다. 나온 종류로 고른다(없는 쐐기를 선언하지 않게):
- 쐐기가 한 명이라도 있으면(both·head가 섞여도): `; the dark wedge on the front of a figure's head and the dark stripe down its chest only show which way that person faces`
- 전부 띠만(chest): `; the dark stripe down a figure's chest only shows which way that person faces`
- 전부 쐐기만(head): `; the dark wedge on the front of a figure's head only shows which way that person faces`
— 선언 안 한 모양은 새 소품으로 발명된다(아래 §3-B 쓰는 법 '회색 세트도 무엇인지 선언')와 같은 이유. 색 이름을 쓰지 않는 구절이라 §0-D와 부딪히지 않는다. 얼굴 앞에 제품(kind: product — 선글라스 등)이 오는 사람은 스크립트가 auto를 띠만(chest)으로 내리고 `[점검]` 줄로 알린다(직접 both·head를 골랐는데 같은 경고가 나오면 `"chest"`로 고쳐 다시 렌더). 생성 효과는 시험 0회.

### §0-C 몸 언어 — 틀 빈칸을 채우는 법 [추가 · 새 줄 없음]
- **몸 전체가 향하는 쪽은 프리비즈가 정한다**(나누기): 명세 `rot`가 나르고, 글에 쓰는 몸 각도·향하는 대상은 그 시각 렌더 출력 `[몸 방향]`(report.json `qc.facing_to_lens` — 렌즈 기준 0° 정면·90° 옆·180° 등, 0.5초마다)과 같게 쓴다. 사용자가 각도를 바꾸라고 하면(「살짝 측면으로」) 글이 아니라 **명세 `rot`부터** 그 시간대만 고치고(`SKILL.md` 5단계 3 '말한 부위만' — `--prev`로 확인) 새 `[몸 방향]` 값으로 글을 쓴다 — 글과 프리비즈가 다른 각도를 주면 섞여 흔들리고, 결과는 프리비즈를 따른다(나누기 근거). **글만 나르는 것** = 하체와 어긋나는 상체·어깨 비틀기, 무게(어느 발), 무릎, 두 팔이 서로 다르게 하는 일, 시선, 표정·태도, 리듬.
- CHARACTER AND PRODUCT RULES `{NAME} — {2-3 trait words}; {how she moves}; …`의 `{how she moves}` = 원본에서 본 움직임(예 `loose and athletic, her weight low, her two arms never doing the same thing`).
- SHOTS `{beat at {t}s}` = 큐시트 `to_text`·`body_language`를 **빠짐없이**, 비트마다 시각과 함께 — 무게·다리 / 상체 비틀기 / 두 팔이 서로 다르게 하는 일 / 시선 / 표정·태도 / 리듬. 자리(손에 든 물건이 어디에)·향하는 쪽은 쓰기 전에 프리비즈 값(명세 키·`[몸 방향]`)을 확인하고 그대로 쓴다. 예(농구 예시 — 명세·원본과 대조한 꼴 — `[몸 방향]` 주인공 2~4.5초 약 6~16°, 6~7초 약 13~19°, 7.5~8.5초 약 32~42°):
  `1.83-2.6s, the leap at its fullest — her right leg (screen-left) folded tight with the knee pointing down and the lower leg tucked under her, her left leg (screen-right) reaching far and nearly level, almost straight, its foot just below hip height; torso tipped a little to her left, the ball beside her head in her left hand while her right hand holds the folded sunglasses up beside her head; head turned and tilted down toward the male defender, a cool defiant stare, lips pressed together.`
  (원본 해상도 프레임과 대조해 쓴 꼴 — 다리에 `split`·`wide`를 붙이지 않는다: §0-H 피할 말)
  `6.25-7.1s, she lands with her weight sinking onto one leg and her hips cocked to one side, and flicks her left shoulder exactly twice with only her right hand, quick and casual; head tilted, eyes half-lidded, a smug one-sided smirk.`
  `[몸 방향]`이 30° 근처인 구간이면 그 값을 쓴다(예 `7.5-8.5s, her body turned about 35° from the lens, …`). 프리비즈가 렌즈 쪽(0~20°)인데 '측면'을 쓰지 않는다.
- **차렷 ✕의 뜻**: 렌즈를 향한 구간이라도 대칭으로 똑바로 선 자세로 쓰지 않는다 — 무게를 한 발에, 골반·어깨를 어긋나게, 고개 기울기·시선을 쓴다(`weight on one leg` · `hips cocked to one side` · `head tilted`). 부정이 꼭 필요하면 한 구절(`never squared up to the lens`) — §1-7 '최소한'.
- **비트는 빈틈없이**: 사람이 화면에 있는 0초~끝을 비트 시간대가 끊김 없이 덮는다 — 빈 구간은 모델이 굳은 정면 자세로 채운다. 원본 동작을 바꿨으면(§0-G) 그 동작이 나오는 모든 시간대가 비트에 있어야 한다.
- **길이 우선순위**(§1-6 — 30초 9샷 약 9천 자 상한과 함께): 주인공 = 비트마다 빠짐없이 · 둘째 인물(색을 따로 받은 사람) = 비트마다 한 구절 · 관중·행인 = 영상 전체에 한 줄(예 `the spectators watch, a few shifting their weight or turning their heads`). 길이가 넘으면 §1-6 순서로 줄이되 큐시트 `to_text` 항목과 §0-H 큰 동작 줄(RULE·KEEP·정점 비트의 정도 말)은 줄이는 순서 맨 끝 — 넘치면 큰 동작 밖의 비트(예 착지 뒤)·둘째 인물·관중 구절과 앞부분(§1-6 ①②)부터 짧게 한다.
- 쓰지 않는 것: '더미 자세를 따르라'는 문장(`follow the figure's pose` 등 — 아래 §3-B 4번 CRITICAL 줄만 예외), 사진에 있는 생김새(§1-2), 사람을 `figure`·`block`·`mannequin`으로 부르기(§0-D).
- 원문과의 관계: §1-1(동작 세부·표정 = 글) · §3-B 4번(큰 자세 = 허리 힌지 + CRITICAL)과 같은 방향이고 Motion feel 문장은 그대로 둔다 — 대체하는 원문 없음.

### §0-D 색 이름은 정체를 정할 때만 [추가]
- 색 이름이 나와도 되는 곳: ① Colour key(이 색 = 이 실제 사람·물건, 한 번) ② 모양이 다른 더미 치환 줄(`Every {magenta} block is completely replaced …`) ③ CRITICAL 줄 ④ 끝 면 줄(`The side of the {magenta} block …`). ③④는 CHARACTER AND PRODUCT RULES 안에 있어도 된다. 그 밖(SHOTS·WHERE·**RULES의 나머지 줄**·KEEP CONSISTENT·카메라 꼬리·덧붙인 문장)에서는 사람·물건 이름으로 부른다(`the model` · `the male defender` · `the spectators` · `the sunglasses`).
- **더미 낱말도 같다**: SHOTS·WHERE·RULES에서 사람을 색 없이 `figure`·`block`·`mannequin`·`dummy`로 부르지 않는다(예 `the three low figures at the front of the left group …`도 블록을 붙잡는다). `figure`는 ①~④ 안에서만.
- 이미지 없이 글로 바꿀 인물의 정체는 Colour key에 실제 사람으로, 사용자가 지정한 말 그대로: `the yellow figure is a real man, {사용자가 지정한 말 — 예 a male defender in a navy sleeveless jersey}`.
- 화면에 머물게 할 때도 사람으로: `the male defender stays beside her from 1.0s to 5.0s` · `the spectators stay where they are for the whole clip`. **언제·어디에**: 원본에서 그 사람이 그 구간 화면에 있을 때만, 그 시간대를 덮는 SHOTS 줄의 비트(시각과 함께) 또는 KEEP CONSISTENT 한 줄로 — 둘 다 쓰지 않는다. 장소 사진을 올리는 생성(§0-E — 이제 기본)에서는 원본에서 끝까지 화면에 있는 둘째 인물·관중마다 한 번 넣는다(근거: 사진만 더한 07 → 1초 뒤 사라짐, 유지 문장을 넣은 09 → 관중 유지. 사람 이름 꼴의 유지 문장은 시험 0회).
- 근거(실험으로 확인됨, 원인은 추정): 색 이름으로 사람을 카메라 꼬리·SHOTS에서 여러 번 붙잡은 판(`the yellow defender`)에서 노랑·관중 블록 마네킹이 실사로 안 바뀌고 그대로 남았고, 색 이름 유지 문장이 한 줄뿐인 판은 안 남았다. 다만 그 판은 카메라 꼬리·더미 낱말도 함께 바뀌어 색 이름 횟수만으로는 설명되지 않는다.
- **드래프트에서 블록이 실사로 안 바뀌고 남으면** 의심 순서: ① 직전에 통과한 판과 바뀐 카메라 꼬리(그 꼴로 되돌린 판 1회) → ② SHOTS·RULES·KEEP의 색 이름·더미 낱말 → ③ 프리비즈(블록이 화면을 크게·오래 덮나). 한 번에 변수 하나(§8-4).

### §0-E 장소 사진 줄 [대체]
- **대체되는 원문**(표시 6곳): 아래 §1-2 '회색 세트가 정하는 장소의 겉모습만 글로' · 3-A 틀 장소 판 줄의 조건 `[no previz, or a previz whose background is removed — not with a grey previz set]` · §3-B 첫 문단 '장소 판 줄은 프리비즈 배경을 지운 경우(…)에만 넣는다 — 회색 세트 + 랜드마크 프리비즈가 공간을 정하면 판 없이 장소는 WHERE·BACKGROUND 글로' · 3-B 틀 REFERENCES 괄호 '장소 판 줄은 배경을 지운 프리비즈일 때만'(틀 아래 표시 줄) · §3-B 쓰는 법 REFERENCES '회색 세트 프리비즈면 판 없이' · §3-B 쓰는 법 '장소 판'의 예외 ②. **사라지는 것**: 회색 세트 프리비즈에서 장소 사진을 업로드 목록에서 빼고 장소 겉모습을 WHERE·BACKGROUND·LOOK 글로 쓰던 것 · 배경을 지운 프리비즈에서 장소 판 각도를 그 생성 첫 샷 시점에 맞추던 것(첫 장면은 이미지가 이긴다 — 이제 각도는 `ignore its camera angle` 글 한 줄로만 막는다. 장소 판 각도가 화면으로 복제된 실측이 약 5건 있으니 드래프트에서 첫 프레임이 장소 사진 각도를 따라갔는지 본다 — `handoff.md` 7절). **남는 것**: 장소당 생성 1번·장소 판 2장 이상 ✕·반대편 컷 규칙·시간대 덮어쓰기(`; override its daylight`).
- 업로드: 받은 장소 사진을 `loc_<장소>`로, **이미지 마지막 번호**(REFERENCES 순서 = 올리는 순서). 예외 — `@first_frame`을 레퍼런스로 쓰는 드문 경우(3-B 쓰는 법 '첫 프레임')는 3-A 틀 순서대로 장소 줄 다음이라 `first_frame`이 마지막, 장소는 그 앞 번호.
- REFERENCES 줄 — `Reference-sheet panels are not the scene.` 다음, `@previz` 줄 앞:
  `@loc_<장소> — {PLACE}: take only how the place looks — its surfaces, materials, colours and light; ignore its camera angle — layout and camera come only from @previz. This photo shows the empty place; every person in the scene comes only from @previz, never from this photo.`
- `{PLACE}`는 몇 낱말 이름(예 `a night outdoor basketball court`) — 사진 속 색·재질을 나열하지 않는다(사진이 나른다 — §1-2, 18번). WHERE EVERYTHING IS·`BACKGROUND:`는 무엇이 어디에(배치)만.
  기본은 '몇 낱말' 꼴이다(장소 색·재질은 사진이 나른다 — 정본 18번). 장소 겉모습을 짧게 늘어놓은 꼴(`the red court with white markings, the blue hoop post …`)보다 덜 시험된 꼴이니 드래프트에서 장소가 사진대로 나오는지 함께 본다.
- 3-A 틀의 장소 판 문장(`this plate is the first shot's viewpoint; take geometry, materials and props from it`)은 쓰지 않는다 — 프리비즈 카메라와 사진 각도가 다르고 배치는 프리비즈가 정한다.
- 근거(실험으로 확인됨): 장소 사진만 더한 판은 수비수·관중이 1초 뒤 사라졌고(빈 사진을 따라감 추정), '빈 장소 — 사람은 프리비즈에서만' 문장을 넣은 판은 관중이 유지됐다.

### §0-F 카메라 꼬리 = 원본 카메라 [대체 + 추가]
- **대체되는 원문**: §3-B 쓰는 법 '세기'의 장르 기준 '제품 커머셜·숏폼 광고 = 커머셜판'. 이제 큐시트 `camera.mount`로 고른다 — 핸드헬드 → 다큐판 꼬리(틀의 `[default — same, but daily/documentary cuts whose reference camera is handheld only …]` 줄, 장르 상관없이), 짐벌·고정·돌리 → 커머셜판. **사라지는 것**: 숏폼 광고라서 핸드헬드 원본에도 커머셜판(`no handheld sway or shake`)을 쓰던 것.
- **추가**: 꼬리 안, `Never gimbal-smooth, never digital jitter.`(다큐판) 또는 `no handheld sway or shake, never digital jitter.`(커머셜판) 바로 뒤에 한 문장:
  `Keep the previz framing distance: the camera never gets closer to the people than the previz camera does.`
  — 원문 '꼬리에 방향·거리·속도를 쓰지 않는다'(경로를 글로 다시 쓰지 말라는 뜻)의 예외: 새 경로가 아니라 프리비즈 거리를 지키라는 잠금이다. 원문 §1-3·§3-B '역할'·§7 점검의 '꼬리 안 카메라 움직임 단어 = 경고' 자리에도 이 예외 표시를 달았다 — 점검에서 이 한 문장은 지우지 않는다. Motion feel은 그대로 꼬리 바로 뒤.
- **다큐판 빈칸**: 틀의 선택 빈칸 `{, a small operator settle at each {impact | stop}}`은 기본으로 **뺀다**(괄호째 — 묻지 않음). 넣을 때는 카메라를 든 사람의 정착으로 `, a small operator settle at each stop`만 쓰고 `impact`는 쓰지 않는다(사람 착지·충돌로 읽힘 — §1-3, 커머셜판 `{stop | landing}`과 같은 원리).
- **다큐판 + 일부러 뜨거나 느린 장면**(원본이 시간 정지·슬로모션·공중에 떠서 머묾 — §3-B 쓰는 법 '예외'): 다큐판 마지막 문장 `Real-time speed throughout, natural live-action motion only; natural body weight through every move — nothing floats, nothing teleports.`을 `Natural live-action motion only; nothing teleports.`로 바꾼다 — `Real-time speed throughout`·`natural body weight through every move`(무게 구절도 떠 있는 몸을 끌어내림)·`nothing floats`를 뺀다. `nothing teleports`를 남길지는 정본대로 쓰기 전 사용자에게 확인(뺄 때는 `Natural live-action motion only.`).
- **컷마다 마운트가 다르면**: 꼬리는 생성 하나에 하나(`@previz` 줄 하나) — 화면 시간이 더 긴 쪽 마운트로 고르고 handoff 5절에 한 줄 남긴다. 마운트가 바뀌는 것이 원본의 핵심이면 그 컷에서 생성을 나눌지 사용자에게 묻는다.
- 근거(실험으로 확인됨): 원본이 폰 핸드헬드인데 커머셜판 꼬리를 쓰면 원본 카메라 느낌과 달라진다. 거리 문장이 없으면 시작 구도가 몸에 바짝 붙었고, 넣은 판은 프리비즈 거리를 지켰다(같은 판에서 꼬리도 바뀌어 추정). 위 정본 다큐판 꼬리·거리 문장 꼴 그대로는 아직 생성 시험 전이다.

### §0-G 바꾼 동작은 새 동작만 [추가]
큐시트 `meta.user_changes`가 있으면 원본 동작 이름은 프롬프트 어디에도 쓰지 않는다(`instead of …`·`never …` 포함 — §1-7 ③ '부정 1구절'보다 엄격, 그 자리에 표시). 새 동작만 긍정형으로, 그 비트의 나머지 몸 언어(§0-C)는 원본 그대로. 원본에 그 동작이 여러 번 나오면(예 7.5~8.25초에 같은 손 제스처 한 번 더) **모든 시간대**를 `user_changes.time`에 적고, 사용자가 정하지 않은 시간대의 새 동작은 프롬프트를 쓰기 전에 묻는다(0절 질문 규칙 — 기본값: 앞 시간대 새 동작의 이어짐, 예 선글라스를 쓴 채 그 손을 내림).

### §0-H 큰 동작은 글로 잠근다 + 생성 필터 안전 말 [추가]
- **언제**: 큐시트 `big_moves`에 적힌 큰 팔다리 동작(점프 자세·발차기·회전 중 다리·앉기·눕기·팔 크게 뻗기). 세 덩어리 더미는 이 모양을 못 나르므로(공중 구간 더미 = 곧은 기둥) 글이 유일한 그릇이다. 프리비즈 구조(세 덩어리·색·나누기·방향 표시)는 그대로 — 더미에 다리를 만들지 않는다.
- **같은 사실을 세 자리에**(큰 동작 하나당):
  ① CHARACTER AND PRODUCT RULES 한 줄 — `{MOVE} POSE RULE: from {t0}s to {t1}s she is {운동 동작 — 예 airborne in one big layup leap} like a real {종목} player — {그 사람 오른쪽 팔다리 (screen-…) + 구간 내내 안 바뀌는 모양}, and {왼쪽 팔다리 (screen-…) + 구간 내내 안 바뀌는 모양}. {풀리는 모습} only from {t1}s.`
  ② KEEP CONSISTENT 한 줄 — `In the air from {t0}s to {t1}s she keeps the same leg shape: {가장 잘 깨지는 두 가지 — 좌우·화면 쪽과 함께}.`(점프가 아니면 `In the air` 자리에 그 상황)
  ③ 그 구간 SHOTS 비트마다 정도 말 — 시작 `springs into` · 정점 `at its fullest` · 유지 `holding` · 풀림 말(`loosen`·`relax`·`come down`)은 `big_moves.end`부터만.
  — **RULE = 그 구간 내내 변하지 않는 모양만**(어느 팔다리가 접히고 어느 쪽이 곧은지·화면 쪽). 단계별 높이·기울기(발 높이·몸통 기울기·정강이가 늘어짐)는 그 시각 비트에 쓴다 — 정점 모양을 RULE에 걸면 발이 내려오는 뒤 비트와 한 프롬프트 안에서 부딪혀 정점 자세로 굳거나 흔들린다. RULE·KEEP은 짧게(아래 예 약 300자·150자).
  — 사람 이름으로(색 이름·`figure` ✕ — §0-D). '더미 자세를 따르라'는 문장이 아니다(CRITICAL 줄은 더미 허리 힌지가 나르는 숙임에만 — §3-B 4번).
  예(농구 1.5~4.25초, 원본 프레임 대조 — 틀 빈칸을 채우는 보기일 뿐 그대로 옮기지 않는다, 생성 시험 0회):
  `JUMP POSE RULE: from 1.5s to 4.25s she is airborne in one big layup leap like a real basketball player — her right leg (screen-left) stays sharply bent at the knee and her left leg (screen-right) stays long and almost straight, reaching far toward screen-right. Her feet come down under her only from 4.25s.`
  `In the air from 1.5s to 4.25s she keeps the same leg shape: right leg bent toward screen-left, left leg long and almost straight toward screen-right.`
- **좌우 = 그 사람 기준 + 괄호에 화면 쪽**: `her right leg (screen-left)` · `her left leg (screen-right)`. 괄호는 그 시각 렌더 `[몸 방향]` 값으로 정한다 — 약 60° 이하(렌즈 쪽)면 그 사람 오른쪽 = `screen-left`, 약 120° 이상(등짐)이면 같은 쪽(오른쪽 = `screen-right`), 그 사이(옆모습·도는 중)는 괄호를 쓰지 않거나 `near the lens`·`far side`로 쓴다. 깊이(`behind her`·`toward the lens`)는 원본에서 확실할 때만 덧붙이고, 화면에서 보이는 쪽을 먼저 쓴다 — 렌즈를 향한 몸에서 `behind her`만 쓰면 렌즈 반대쪽으로 숨는 다리로 읽힐 수 있다(뒤로 곧게 뻗은 다리가 안 나온 실험이 있다 — 원인 추정).
- **정도는 운동 말 + 정도 말로 세게, 숫자 각도 ✕**: 운동 말 `layup leap` · `trailing leg` · `long airborne stride` · `tuck` · `reach` · `folds tight` · `knee pointing down` · `lower leg tucked back under her` · `reaching far` (`knee driven high`는 원본이 무릎을 가슴 쪽으로 드는 동작일 때만 — 아니면 무릎을 가슴까지 든 흔한 레이업이 나온다) / 정도 말 `sharply bent` · `long and straight` · `almost straight` · `nearly level` · `foot near hip height` · `almost level with the court` · `at its fullest` · `held through the hang time`. 원본 프레임에서 본 높이 그대로 고른다(예 무릎이 그 다리의 가장 낮은 점이면 `knee pointing down`).
- **피할 말 — 2단 표**(주인공 다리·무릎·split에 붙을 때. 생성 필터 거절·통과 실험에서 고름 — 낱말이 거절 원인이라는 것은 추정, 거절 이유는 공개 안 됨):
  | 단 | 피할 말 | 대신 | 근거 |
  |---|---|---|---|
  | 1단 꼭 피함 | `open`·`opens`·`opening`(`thighs open`·`knee opens`·`split clearly open`·`wide open`) · `widest` · 다리 벌림 각도 숫자(`about 120 degrees`) | 정도 말(`at its fullest` · `reaching far` · `nearly level`) | 거절된 판에만 있던 말 — 통과한 판엔 0건 |
  | 2단 미리 피함 | `split(s)`·`scissor split`·`straddle`·`thigh(s)`·`inner thigh`·`crotch`·`groin`·`between her legs` · 다리에 붙은 `spread`·`apart`·`wide` | 운동 말(`layup leap` · `long airborne stride`) · `leg`·`knee`·`lower leg` | `splits her legs wide`·`thigh`가 있어도 통과한 판이 있음 → 단독 원인은 아님. 안 써도 손해 없음 |
  | 대상 아님 | 둘째 인물·수비수 `spread arms`·`feet apart for balance` · 몸 방향 `about N° from the lens`(`[몸 방향]` 값) · 선글라스 `open one temple` | — | 통과한 판에 있던 말, 다리 말 아님 |
  짧은 하의를 입은 인물이면 다리 사이·하의 안쪽을 가리키는 말은 전부 ✕. 점검 = `python3 <스킬>/scripts/pose_word_check.py 04_넘기기/handoff.md`(②·③ 코드 블록만 셈 — 1단 0건·2단 0건이면 통과, 걸린 말이 '대상 아님' 칸이면 그대로).
- 근거(실험으로 확인됨): 큐시트↔프롬프트 점검을 모두 통과해도 원본 프레임과 대조하지 않으면 공중 다리를 약하게(`knee bent`·`knee soft` — 원본은 거의 곧음) 쓰거나 원본보다 일찍 풀리게(`scissors loosen` — 원본은 끝까지 유지) 써서 다리를 모은 굳은 공중 자세가 나왔다. 다리에 `open`·`widest`·벌림 각도 숫자를 붙인 판은 생성 필터에 거절됐고, `knee driven high`는 원본과 달리 무릎을 가슴까지 든 흔한 레이업을 불렀다. 고친 다리 말(`folds tight, knee pointing down`)과 화면 쪽 괄호 꼴은 아직 생성 시험 전이다.

### §0-A 수정 요청 — 프롬프트 쪽 [확인 · 바뀐 원문 없음]
프리비즈 수정의 '말한 부위만'은 `SKILL.md` 5단계. 프롬프트 수정은 원문 §8 그대로(전체를 새로 · 이전 수정 유지) — 사용자가 한 부위만 바꾸라고 했으면 나머지 비트의 몸 언어·배치 문장은 그대로 둔다.

<!-- 원문 7~42행 -->
## 1. 원칙

1. **맥락을 가장 잘 나르는 채널 하나에 싣는다**. 생김새 = 이미지, 카메라·구도·컷 = 프리비즈, 나머지(치환 관계·동작 세부·표정·소리) = 글. 사람·물건의 동선·타이밍과 사람의 큰 자세도 프리비즈가 나른다 — 큰 자세는 허리 힌지 더미 + CRITICAL 글(§3-B 4번), 더미 모양·세부는 단순하게(04 §4) (97·98번). 인풋 이미지에 없는 것(생김새·모션)만 글로 묘사하고, 있는 것은 태그로 역할만 알린다(18번 — 원칙 2).
2. **넣는 것마다 REFERENCES 한 줄 = 핸들 + 이름 + 역할(가져올 것 + 무시할 것: 배경·조명·사람·카메라 각도)만** [힉스필드 §2 10/22판]. 사람 줄(얼굴 시트·착장 시트) 끝 `Matches the reference 100% at every distance.`는 정본 틀대로 둔다. 틀 문구는 §3-A.
   - **생김새는 글로 쓰지 않는다**(얼굴·머리·옷·제품 모양·색 — 인풋 이미지가 나른다). **대체(상충목록 18번)** — 옛 '식별점 한 줄(머리·눈에 띄는 표시·옷 대표 2개)'(07 #23)을 뺐다. 이미지 모델은 인풋 이미지에서 알 수 있는 정보를 프롬프트에 또 설명하면 그 글을 반영하려고 생김새를 바꾸는 경향이 있다 — 영상도 같다. 인풋 이미지에 없는 것의 생김새·모션을 묘사하고, 있는 것은 이미지 태그로 역할만 알린다. '외형 중복 금지'(외형이 이미지에 있으면 글로 다시 묘사하지 않는다)가 다시 기본이 됐다. KEEP CONSISTENT·RULES·SHOTS에서도 생김새 구절을 쓰지 않는다 — 인풋 이미지에 **없는** 것(참조 없는 행인·엑스트라의 옷, 회색 세트가 정하는 장소의 겉모습)만 글로 묘사한다. [§0-E: 이 스킬은 장소 사진을 올리므로 장소 겉모습도 사진이 나른다] [참고: 힉스필드 실제 제작 프롬프트 일부는 식별점 한 줄을 쓴다 — 이 정본은 쓰지 않는다]
   - 성격·행동 규칙은 REFERENCES가 아니라 CHARACTER AND PRODUCT RULES에만 쓴다.
   - **라벨·로고 글자는 영상 프롬프트에 쓰지 않는다** — 글자 내용, 'label'·'lettering' 낱말, 글자를 지키라는 문장(KEEP의 철자 줄·'다른 로고 금지' 줄)을 모두 넣지 않는다. **대체(상충목록 19번)** — 옛 '제품 줄에 무슨 글자가 어디에 + KEEP에 선명·철자 한 줄'(07 #22)을 뺐다. 라벨 글자를 꼭 지키라는 문장도 오히려 다른 문구를 불러올 수 있다. 글자는 디테일 클로즈업 이미지(태그로 역할만 — 03 §3-1)·1080p 접사 컷·후반(깨진 라벨은 라벨 수정·합성 — 06 §6)이 맡는다. 제품 면을 정할 때도 글자·로고 낱말 없이 쓴다(예 `the outer side of the temple`). [참고: 공식 가이드 8/13·higgsfield-seedance-prompt 7/10은 '작은 글씨·로고·핵심 색은 짧게 글로도'라고 한다 — 이 정본은 19번을 따른다]
   - 역할 줄 문형 `… exclusively for …`는 '가져올 것' 칸과 같은 일 — 그 줄 안에서 써도 된다(예 `Take her face and hair exclusively from this sheet`).
   - [관찰] 역할 줄을 빼면 요청 동작을 안 한 비율 0/4 → 3/4.
3. **프리비즈가 있으면 카메라 경로를 글로 다시 쓰지 않는다** — 프리비즈가 나른다. `@previz` 바인딩 줄만 필수, SHOTS는 `Camera as @previz.`로 시작하고 배치·BACKGROUND·비트·대사·END만 쓴다(§3-B). "the product stays perfectly still"처럼 쓰면 카메라까지 멈춘 사례가 있으니 정지는 물건이 아니라 카메라 기준으로 생각한다 [정본].
   - **CAMERA FEEL 꼬리 + `Motion feel` 문장(§3-B — 프리비즈를 넣는 모든 생성에 기본 · 114번 — 효과 미검증)은 이 원칙과 부딪히지 않는다**: 둘 다 방향·거리·속도를 쓰지 않는다 [§0-F 거리 문장 한 줄은 예외]. 카메라 꼬리 = 카메라를 든 사람의 몸 질감(관성·무게·정착)과 셔터 블러만 / Motion feel = 사람·물건이 **움직일 때의** 질감(실제 무게·관성·여운)만 — 범위를 `for people and objects`로 못 박아 `@previz` 줄의 'camera path, framing and cut timing only'와 'only'가 둘로 부딪히지 않게 한다. `@previz` 줄의 `match it 1:1`과는 **'경로·향하는 방향(facing)·시각·멈춤 자리는 1:1, 움직일 때의 질감만 자연, 프리비즈가 멈춰 둔 것은 그대로 멈춤'**으로 나눠 맡는다. 둘 다 `@previz` 줄 끝에 이어 붙이고(카메라 꼬리 → 바로 뒤 Motion feel) **`CAMERA —` 같은 머리 줄로 떼지 않는다** — REFERENCES는 '넣는 것마다 한 줄'이고, `prompt_check.py` ALIASES가 `CAMERA` 머리를 ⑦ SHOTS로 읽기 때문 [힉스필드 §2].
   - 프리비즈가 **없는** 생성(조각 컷·짧은 컷 — §3-A 기본 틀)은 SHOTS 줄마다 카메라를 숫자로: 위치·높이 m·거리 m·화각°(mm 병기 가능)·샷 전체를 도는 무브 하나 [힉스필드 §2 — 데이터: 화각° Princess 93.7%·Blackpine 89.6%]. 숫자만 믿지 말고 그 화각에서만 보이는 범위도 적는다 [그들 주장: CINEDANCE v4.4.2]. 무브는 대사 때문에 멈추지 않는다. 렌즈 표기 = 화각°+m 기본·mm 병기 — **유지(10/22 확인, 07 #25)**.
4. **모드 = 참조(omni_reference)**. 프리비즈를 편집(video_edit) 모드에 넣으면 배경 고정 턴테이블이 된다 [관찰 0/4]. 매그니픽엔 모드 칸이 없으니 프롬프트에 "Edit @Video1"·"editing master" 같은 편집 어휘를 쓰지 않는다. 영상 참조 모드는 **입력 종류로** 나눈다(상충목록 113번): 프리비즈 = 참조 모드·편집 어휘 ✕ / 내가 찍은 실사 원본의 카메라를 1:1로 옮기며 겉만 바꿀 때만 편집 모드(1회 실행으로 카메라 잠김 확인 — 06).
5. **길이 = 프리비즈 길이**(정수 초) [공식·관찰]. 짧게 뽑으면 잘리고, 길게 뽑으면 끝을 모델이 지어낸다. 길이는 **설정 칸(화면 UI·MCP 파라미터)에만** 넣고 글에 쓰지 않는다 — **대체(상충목록 112번)**: 옛 판은 한 줄 요약 첫머리에 길이를 적었다. 화면비·길이처럼 설정 칸에서 따로 정하는 것은 글에 중복으로 넣지 않는다. 샷 수·컷 시각은 내용이라 글에 쓴다. 설정 길이 = 마지막 샷 끝 — 화면이 이전 길이를 그대로 들고 있을 수 있어 제출 전 따로 확인한다(§7 `--duration`) [그들 주장: Higgos 10/07 · IYSL 브리프 '6초 계획에 15초를 두면 남는 시간을 모델이 지어냄'].
6. **글자 수 — 한도 때문에 줄이지 않는다, 길이 기준은 원본 틀 길이** [힉스필드 §2 10/22판]. **대체(상충목록 29·118번)** — 옛 '힉스필드 MCP 3,900자 상한(넘으면 실패)'은 지금 해당 없음.

   | 경로(`--route`) | 한도 | `prompt_check.py` 판정 | 근거 |
   |---|---|---|---|
   | 힉스필드 MCP(`higgsfield`) | 18,127자 전체판이 잘림 없이 들어감 — 한도 때문에 줄이지 않음 | 글자 수로는 실패·경고 없음([정보]만) | [관찰] 18,127자 통과(29번 — 옛 7,170자 422 오류·3,900자 상한 기록은 지금 해당 없음) |
   | 매그니픽 MCP·웹(`magnific`) | 10,000자(3,900자 이하 권장) | 10,000 넘으면 **실패** · 3,900 넘으면 경고 | 카탈로그 10/9 |
   | 힉스필드 웹(`web`) | 사실상 넉넉함 | 20,000 넘으면 [정보]만 — 실패·경고 없음(8/22 이후 2만 자 넘게 정상) | [데이터] 2.5 출시 직후 8/10~12에 20,000자에서 잘림(Trigger 15·Dusk 43건) → 8/22 이후 2만 자 넘게 정상(최대 43,155자, 8/27 Princess) |

   - 힉스필드 MCP로 긴 프롬프트를 냈으면 결과 기록(생성 기록의 프롬프트)에서 **전문이 들어갔는지 확인**한다(29번).
   - **길이 기준 = 원본 틀 길이**(118번 — 같은 장면에서 긴 글이 7점 낮았다, 각 1회): 앞부분(REFERENCES·LOOK·RULES·WHERE)은 짧게, 샷마다 카메라 무브 하나 + 3~4문장, 30초 9샷이면 약 9천 자가 상한. 생김새를 글로 쓰지 않으면(원칙 2) 앞부분은 저절로 짧아진다.
   - 매그니픽 10,000자에 걸릴 때 줄이는 순서: ① 프리비즈가 이미 말하는 문장 → ② LOOK. **KEEP CONSISTENT·개수·시간대별 상태·END 줄은 남긴다** [힉스필드 10/10판 §7 — 10/22판 §7은 순서만 적고 이 줄을 거두지 않음].
   - 그래도 넘으면 **꼬리 안에서**(프리비즈가 있으면 CAMERA FEEL 꼬리 + Motion feel은 기본 — §3-B) ③ Motion feel 문장을 짧은판(약 225자, §3-B 쓰는 법 '글자 수')으로 → ④ `Real-time …` 문장 → ⑤ 짐벌·jitter 구절 → ⑥ 셔터 문장 순으로 줄인다. Motion feel이 먼저인 이유: 짧은판도 '경로·방향·시각·멈춤은 프리비즈 그대로 + 움직일 때만 무게·관성·여운 + 프리비즈가 멈춰 둔 것은 멈춤'이라는 뜻을 다 남긴다(빼는 게 아니라 줄임). 셔터 문장이 마지막인 이유: 프리비즈 정본 §4-4 '프리비즈 렌더는 모션 블러 오프, 최종 블러는 텍스트로'. 꼬리(카메라 꼬리 + Motion feel 짧은판)를 통째로 빼야 할 만큼 넘으면 사용자에게 알리고 경로(힉스필드 웹·MCP)를 고르게 한다 [힉스필드 §2]. [관찰] 기본 꼬리(카메라 꼬리 + Motion feel)는 약 750~1,030자.
   - 텍스트만 나르는 문장(자세·치환·인원수)을 지우면 그 축이 무너진다 [정본: 45% 압축에 젖힘 88°→10°].
7. **부정문 — 꼭 필요한 최소한만, 독립 NEGATIVE 블록은 쓰지 않는다** [힉스필드 §2 10/22판 — 데이터: Soul Angel·Blackpine·Today·whimsy NEGATIVE 0% / 그들 주장: timed-prompts §3·CINEDANCE v4.4 NEGATIVE 칸 폐지]. **유지 + 보강(상충목록 16번)** — 이미지 생성에는 긍정문만, 영상에는 꼭 필요한 최소한의 부정문은 괜찮다.
   - 기본은 긍정형 — "하지 마" 대신 그 자리에 있어야 할 상태를 쓴다(`headless` + "목 위엔 하늘만"이 "머리가 없다"보다 성공).
   - **'최소한'의 예 넷**: ① 짧은 꼬리 부정(`no dissolve, no morph`) ② 프리비즈 컷 끝 고정 줄 — KEEP CONSISTENT 맨 끝 `No transformation, no morphing, no bgm.`(효과 A/B 없음, 관행) ③ 긍정으로 못 막는 축의 1구절 [원본에서 바꾼 동작 이름은 이 부정 1구절로도 쓰지 않는다 — §0-G] — 치환 대상마다 부정 1구절(`never beads, marbles or rods` 삭제 → 3/3 구슬화 [관찰·정본]) ④ 도구의 네거티브 전용 칸.
   - 쓰지 않는 것: 독립 NEGATIVE 블록·[AVOID] 블록·4~8개 금지 목록.
   - 빼야 할 것(배경 음악·자막·화면 글자)은 SOUND 블록 안 짧은 목록으로(`No background score.` · `No subtitles, no on-screen text.`) [그들 주장: 공식 가이드 8/13 'GLOBAL STYLE·AUDIO에 빼야 할 것을 명시하면 실패를 더 막는다'].
   - 맨 끝 KEEP CONSISTENT **6~14줄**로 잘 깨지는 것을 다시 잠근다(§3 ⑨).
8. 매 생성마다 **최신 프리비즈·이미지를 보고 새로** 쓴다. 이전 라운드 문장을 재사용하지 않는다 [정본]. 수정 요청 때도 전체 프롬프트를 새로 낸다(§8).
9. **실존 감독·촬영감독·작품·카메라 장비·브랜드 이름 금지** [그들 주장: Top Up 공식 스킬 6월·higgsfield-seedance-prompt 7/10]. 공식 데이터에 실명이 남은 문장(Red Flag·Trigger·Vengeance)은 인용하지 않는다. 가격·할인·날짜·혜택 문구는 생성하지 않고 편집에서 얹는다 [그들 주장: 공식 블로그 9/19·10/08].
10. **화면비**: 숏폼·커머셜 = 9:16 세로, 무드 필름 = 16:9. 리메이크는 레퍼런스가 이 둘 중 무엇인지 보고 맞춘다 — 레퍼런스 화면비가 둘 다 아니면(1:1·4:5 등) 사용자에게 한 줄 확인. 화면비는 **설정 칸(화면·파라미터)에만** 넣고 글에 쓰지 않는다(112번 — 원칙 5). 설정 화면비 = 프리비즈 렌더 = 장소 판 화면비(03 §4). 세로판이 따로 필요하면 06 §9.

<!-- 원문 44~70행 -->
## 2. 참조 표기 — 경로별

**대체**: 기본 표기를 번호식(`@Image1`)에서 **@요소이름**으로 바꿨다(힉스필드 정본 §7). 사라지는 것 없음 — 번호식은 번호를 쓸 수밖에 없는 경로의 예외로 그대로 남는다. '힉스필드에는 @ 태그가 없다'는 옛 답 — 지금은 힉스필드에도 '@' 참조가 있고 형식이 프리픽 이미지 태그(@로 고른 파란 글씨)와 다르다(상충목록 36번).

기본 = `@요소이름`(요소 이름 = 파일 이름 = `inputs.json`의 `handle`) [그들 주장: timed-prompts §0 '@파일 이름만, 번호식 금지' 10/06 · 데이터: Higgos 10/07 `@char_mika`·`@prop_phone`]. **역할 줄 내용은 경로가 달라도 같다** — 바뀌는 건 부르는 이름뿐.

**태그는 REFERENCES에서 한 번이 기본**(상충목록 90번 — '한 번만 태그' · 컷마다 태그한 판에서도 화면 글자 정확): SHOTS·RULES에서는 이름(the model·the glasses)으로 부르고, 그 컷에서 틀리면 안 되는 것(화면 글자가 읽혀야 하는 접사·닮은 두 제품·디테일 클로즈업 컷)만 그 컷 SHOTS 줄에서 핸들로 다시 태그한다. 다시 태그해도 생김새는 글로 쓰지 않는다(§1-2).

**자동 태그는 영상 쪽 확인 전**(정본 §8 K5 — '태그는 최대한 자동으로'는 이미지 프리비즈 쪽 규칙, 영상 규칙으로 정한 것 아님): 매그니픽 스페이스 프롬프트 노드가 영상 프롬프트에도 이미지 태그를 자동으로 거는지 모른다. 매그니픽 밖(아스트라 등)에서 줄 프롬프트는 `@` + 이미지 이름(= 핸들) 꼴로 태그 걸 자리를 표시한다 — 아래 기본 표기와 같은 꼴 (정본 §8 K5).

| 경로 | 프롬프트 표기 | 무엇과 맞추나 | 구분 |
|---|---|---|---|
| 힉스필드 웹 — 요소(Elements)로 등록 | `@face_hilite_model` | 요소 이름 = 파일 이름 = `handle` | **기본** |
| 힉스필드 웹 — 요소 없이 첨부 | `@Image1` 입력 → 칩 `<<<image_1>>>` | 첨부 순서 | 예외(번호) |
| 힉스필드 MCP `generate_video`(seedance_2_5) | `IMAGE 1`, `VIDEO 1` 평문 [관찰 T0929 통과 형식] | `medias` 배열 역할별(이미지끼리·영상끼리) 순서 = `tag` | 예외(번호) |
| 매그니픽 MCP `video_generate` · 매그니픽 웹 | `@Image1`, `@Video1` | `references[].modifier_key` = `Image1`·`Video1` | 예외(번호) — 웹 칩 표기·product 칸 1장 한도는 화면 확인 전(정본 §9) |

- `inputs.json` 항목마다 `handle`(@ 없이)과 `tag`(`IMAGE N`·`VIDEO N`, 올린 순서)를 **둘 다** 둔다(03 §9 준비표에서 만든다).
  - **핸들 꼴**(정본 §2 틀의 자리 이름을 실제 이름으로 옮긴 꼴, 스킬 전체 같은 꼴 · 12종 + 보완 4종): 얼굴 각도 시트 `face_<이름>` · 착장 시트 `outfit_<이름>`(옷이 바뀌면 `outfit_<이름>_look2`…) · 제품 각도 시트 `prod_<이름>` · 디테일 클로즈업 `prod_<이름>_detail` · 닫힘/열림 `prod_<이름>_states` · 포장 `pack_<이름>` · 장소 판 `loc_<장소>`(반대쪽 `loc_<장소>_reverse`) · 프리비즈 `previz`(파트면 `previz_partN`) · 첫 프레임·이음 시작 이미지 `first_frame`(파트면 `first_frame_partN`) · 자리 배치 `layout_<큐시트 컷 id>`(id는 큐시트 꼴 그대로 — `extract_frames.py`가 만드는 `C01`·`C03` 꼴, 예 `layout_C03`) · 엑스트라 `extras_<장소>` · 앞 영상 `prev_partN`(매끈 이음용 끝 3~4초는 `prev_partN_tail` — 앞 영상 `prev_partN`과 구분, 06 §6-1).
    - **보완 4종**: 소품 `prod_<이름>`(제품 시트 꼴 — `prop_` ✕) · 옷 디테일 클로즈업 `outfit_<이름>_detail`(03 §2) · 상태 꼬리 `_v2`·`_wet`·`_open` 등 허용(상태가 바뀐 판 — 예 `prod_<이름>_open`) · 끝 프레임 칸 `last_frame`(파트면 `last_frame_partN` — 06 §6-1).
  - 예: `face_hilite_model`·`outfit_hilite_model`·`prod_hilite_glasses`·`prod_hilite_glasses_detail`·`prod_hilite_case_states`·`prod_phone`(소품)·`loc_arcade`·`layout_C03`·`previz`. 옛 꼴(`char_hilite_model`·`char_hilite_model_face`·`char_hilite_model_look1`·`prod_hilite_sheet`·`prod_detail` 단독·`map_`·`prop_`)은 쓰지 않는다 (예·옛 꼴 보완).
- **번호 = 올린 순서.** 제출 전 `prompt_check.py --route …`가 프롬프트의 핸들·번호를 `inputs.json`과 대조한다(§7) [데이터: Blackpine 10/03 첨부 순서 어긋남 4건 → 1분 뒤 재생성 · Red Flag 8/12]. 실제 올린 순서가 `tag`와 같은지는 사람 눈으로 한 번 더.
- 아래 틀·예시는 기본 표기(`@핸들`)로 적었다. 번호 경로로 낼 때는 `@핸들`이 나오는 곳을 모두 그 항목의 `tag`로만 바꾼다:
  - 힉스필드 MCP: `@face_hilite_model — the model: …` → `IMAGE 1 — the model: …` · `@previz — …` → `VIDEO 1 — …`
  - 매그니픽: → `@Image1 — the model: …` · `@Video1 — …`
  - 다른 줄 안에서 부르는 핸들(예 착장 시트 줄의 `from @face_hilite_model`, KEEP CONSISTENT의 `as @prod_hilite_glasses`, SHOTS에서 다시 태그한 핸들)도 같이 바꾼다.
  - 사람·제품은 SHOTS·RULES에서 이름(the model·the glasses)으로 부르면 바꿀 곳이 줄어든다.

<!-- 원문 72행 + 79~95행 (73~77행 = 옛 6블록 골격 대체 기록, 뺌) -->
## 3. 기본 골격 — 정본 9블록 [힉스필드 §2]

**블록 순서** — 기하(참조·배치) → 샷 → 소리 → 잠금. 모델이 행동보다 기하를 먼저 읽고, 마지막 블록이 깨지기 쉬운 규칙을 반복하기 때문 [그들 주장: timed-prompts §2, 10/06].

| # | 블록 | 무엇을 |
|---|---|---|
| ① | 한 줄 요약 | 컷 수·하드컷 시각·무슨 일·컷 트릭. **길이·화면비는 쓰지 않는다** — 설정 칸에만(112번, §1-5·§1-10) |
| ② | Opens mid-situation | **이어지는 파트만** — 프레임 0의 상태를 숫자로(카메라 높이·거리, 화면 x%, 손에 든 것). 06 §6-1 '길게 만들기'(하드컷 있는 20~30초·30초 넘음·장소가 바뀜 — 24·88번) |
| ③ | REFERENCES | 넣는 것마다 한 줄 = 핸들 + 이름 + 역할(가져올 것·무시할 것)만(§1-2) — 생김새·라벨 글자 ✕. 시트를 넣으면 `Reference-sheet panels are not the scene.` 한 줄(86번). 옷이 바뀌면 `Outfit order`(03 §2) |
| ④ | LOOK | 렌즈 계열·색 의도·광원 하나(방향·약 몇 K). 모든 파트에 같은 문장 |
| ⑤ | CHARACTER AND PRODUCT RULES | 인물: 성격 2~3단어 + 움직임·말투 + 행동 규칙 하나 / 제품: 쥐는 법·렌즈를 향하는 면·시간대별 상태·개수 |
| ⑥ | WHERE EVERYTHING IS | 영상 내내 고정: 카메라 쪽 기준 화면 좌·중·우(또는 x%) + 각자 뒤에 무엇 |
| ⑦ | SHOTS | 샷마다 `t0–t1s — 카메라 / 배치 / BACKGROUND: / 비트 시각 / 대사 시각 / END: 끝 상태 / 컷 종류` |
| ⑧ | SOUND | 생성 오디오는 켜고 효과음·현장음만 · 배경 음악 없음(화면 안 음원만 예외) · 현장음 시각 · 대사 '정확히 한 번씩' · 자막·화면 글자 없음(§6) |
| ⑨ | KEEP CONSISTENT | **6~14줄**(라벨 두 줄이 빠진 기준 — 정본 §7·§9) — 잘 깨지는 것만 다시: 얼굴·옷·제품(시트 태그로만 — 생김새 글 ✕)·개수·시간대별 상태·컷 시각·첫 샷·빛 방향. 라벨·글자 줄 ✕(§1-2) |

- 힉스필드 팀 공용 틀 이름으로 읽어도 같다: SCENE CONTEXT = ① · ACTIVE REFERENCES = ③ · LOCATION MAP / FIRST FRAME AND SPATIAL BLOCKING = ⑥ · FORMAT MODE = ①의 컷 줄 · OPTICS / CAMERA / ACTION TIMING = ⑦ · LIGHTING = ④ · AUDIO = ⑧ · POSITIVE LOCKS = ⑨ [데이터: Today·Princess·Soul Angel·Blackpine]. 순서는 다르다(팀 틀은 LIGHTING이 ACTION 뒤 — '같은 방향으로 수렴'은 추정, 정본 §2). 이 스킬은 위 9블록 이름으로 통일한다.
- 독립 NEGATIVE 블록은 없다(§1-7). 컷은 글로 나누고 멀티샷 스위치는 켜지 않는다 [데이터: 씨댄스 생성 멀티샷 스위치 0].


<!-- 원문 96~147행 -->
### 3-A. 기본 틀 — 정본 §2 '그대로 쓰는 틀'(프리비즈 없이 글로 카메라를 줄 때)

조각 컷·짧은 컷처럼 프리비즈 없이 뽑을 때. 역할 줄 영어는 정본 10/22판 §2 틀 문구 그대로다. 정본 틀과 다른 곳:
- 정본 틀은 프리비즈 줄(`@{previz}` 줄·Camera feel 꼬리·Motion feel·CRITICAL 줄)까지 한 틀에 담았다 — 이 스킬은 그 줄들을 프리비즈 변형(3-B)으로 옮겼다. 그 밖은 정본 틀 그대로다.
- **대체** — 옛 판 틀에서 빠진 것: 캐릭터 시트 줄(식별점 + 초상 칸·몸 칸 두 개)과 옷 착용컷 `same face` 줄(10·11·12·18번) · 제품 줄의 모양·색 몇 단어와 라벨 글자 칸, KEEP의 라벨 철자 줄과 '다른 로고 금지' 줄(18·19번) · 한 줄 요약의 길이·화면비(112번) → 얼굴 각도 시트·착장 시트·제품 각도 시트·디테일 클로즈업 줄 + 시트 한 줄. 옛 판에서 제품 줄 끝에 더했던 `Matches the reference 100% …`도 정본 틀대로 사람 줄에만 둔다.
- 틀 안 대괄호 `[…]` = 넣는 조건(프롬프트에 옮기지 않음), 중괄호 `{…}` = 채울 자리.
- 틀의 `@{face_sheet}`·`@{outfit_sheet}`·`@{outfit_sheet_look2}`·`@{product_sheet}`·`@{product_detail}`·`@{product_states}`·`@{loc_plate}`·`@{first_frame}`(정본 틀의 `@{previz}`도)는 **정본 틀의 자리 이름**이다 — 실제로는 §2 핸들 꼴로 채운다: `@face_<이름>` · `@outfit_<이름>`(두 번째 옷 `@outfit_<이름>_look2`) · `@prod_<이름>` · `@prod_<이름>_detail` · `@prod_<이름>_states` · `@loc_<장소>` · `@first_frame`(파트면 `@first_frame_partN`) · `@previz`(파트면 `@previz_partN` — 3-B 틀은 이미 이 이름) (핸들 꼴 통일).
- [아래 틀의 장소 판 줄 조건 `[no previz, or a previz whose background is removed — not with a grey previz set]`과 그 문장(`this plate is the first shot's viewpoint …`)은 §0-E로 대체: 이 스킬은 회색 세트 프리비즈에도 §0-E 장소 사진 줄을 `Reference-sheet panels are not the scene.` 다음에 넣는다]

```
Live-action {product commercial | short-form ad | brand film}, {N} shots with hard cuts at {t1}s, {t2}s, ... — {one line: what happens, and the cut trick if any}.
[continuation parts only] Opens mid-situation: {who/what is where at frame 0 — camera {h} m high, {d} m away, {subject} at about x={x}%, what is in each hand — identical to the last frame of the previous part}.

REFERENCES
@{face_sheet} — {NAME}: her face and hair from every angle; take only her face and hair from this sheet; ignore the grey backdrop and the studio light. Matches the reference 100% at every distance.
@{outfit_sheet} — {NAME}: her outfit and body proportions from every angle; this sheet has no head — her face comes only from @{face_sheet}; ignore the grey backdrop and the studio light. Matches the reference 100% at every distance.
[outfit changes only] @{outfit_sheet_look2} — {NAME}'s second outfit; defines the outfit only. Outfit order: @{outfit_sheet} ({t}-{t}s) → @{outfit_sheet_look2} ({t}-{t}s).
@{product_sheet} — the {PRODUCT}, every angle: take its exact shape, colours, materials and hinge from this sheet whenever it appears ({in the case | in a hand | worn}); ignore the backdrop.
[products with small or complex detail] @{product_detail} — a close-up of the {PRODUCT}'s {part}: use it only for how that part looks up close.
[only if the clip shows both states] @{product_states} — the same {PRODUCT} {closed and open}: use only for how it looks in each state.
[always — the sheets are multi-panel] Reference-sheet panels are not the scene.
[no previz, or a previz whose background is removed — not with a grey previz set] @{loc_plate} — {PLACE}: this plate is the first shot's viewpoint; take geometry, materials and props from it; any people are ignored.
[with a previz, only when the opening composition must match — as a reference instead of the start-frame slot; or part continuation on a tool that cannot take a start image together with references] @{first_frame} — the very first frame of the clip is exactly this composition.

LOOK
{clean modern digital look | real phone-camera UGC look}, {lens family / field of view range}, {colour intent}, {one motivated light: direction, about {K} K}. {The PRODUCT is the most saturated colour in frame.}

CHARACTER AND PRODUCT RULES
{NAME} — {2-3 trait words}; {how she moves / speaks}; {one behaviour rule}.
{PRODUCT} RULE: {how it is held}; {which face points to the lens}; {state by time: closed until {t}s, open from {t}s; where it is in each shot}; one {PRODUCT} only.

WHERE EVERYTHING IS — fixed for the whole clip
From the camera side: {screen-left ...}, {centre ...}, {screen-right ...}; behind {NAME}: {landmark}.

SHOTS
0.0-{t1}s — {camera position, {h} m high, {d} m away, {FOV}° (about {mm} mm), one move that runs the whole shot}. {who/what is where in this frame}. BACKGROUND: {what is behind them from this angle}. {beat at {t}s}. {line '...' {t}-{t}s}. END: {who/what is where on the last frame, what is in each hand}. Hard cut.
{t1}-{t2}s — {...}. BACKGROUND: {...}. {...}. END: {...}. {Hard cut | Match cut: same lens, same angle, same subject size, the move continues at the same speed; only the world changes}.
{tN-1}-{end}s — {final shot: the PRODUCT reads first, one focus change only}; holds still for the last {0.5}s. END: {final state}.

SOUND
No background score{; the only music is {visible source} playing from {t}s to {t}s}. {ambience and product sounds with times}. {Lines, each spoken exactly once and nothing else: {t} {NAME} '...'}. No subtitles, no on-screen text.

KEEP CONSISTENT
{NAME}'s face, hair and outfit exactly as @{face_sheet} and @{outfit_sheet} in every shot{; outfits change only as the outfit order says}.
The {PRODUCT} exactly as @{product_sheet}; never redesigned.
{counts: one PRODUCT, one case}.
{state by time: closed until {t}s, open from {t}s; where the PRODUCT is in each shot}.
Exactly {N} shots, cuts at {t1}s, {t2}s ...; the clip opens on {first shot}, never on {wrong opening}.
{light rule: the sun stays screen-left in every shot}.
```

- 틀 KEEP은 6줄 — 10/22 기준 6~14줄(§3 ⑨) 안이다.
- 제품 면은 글자·로고 낱말 없이 고른다(정본 예 `in close-ups the outer side of the temple faces the lens`).

<!-- 원문 149~208행 + 210행 (209행 = 꼬리 효과의 한계 기록, 뺌) -->
### 3-B. 프리비즈 있는 리메이크 — 변형 (이 스킬의 기본)

[이 문단의 장소 판 조건은 §0-E로 대체(회색 세트 프리비즈도 장소 사진을 올림)] 3-A와 다른 곳만 바꾼다. 나머지 블록(한 줄 요약·REFERENCES의 얼굴·착장·제품·디테일·상태 줄과 시트 한 줄·WHERE·SOUND)은 3-A 그대로. **장소 판 줄은 프리비즈 배경을 지운 경우(카메라가 거의 고정·망원인 리메이크·숏폼)에만** 넣는다 — 회색 세트 + 랜드마크 프리비즈가 공간을 정하면 판 없이 장소는 WHERE·BACKGROUND 글로(상충목록 88·89번 — 03 §4). `@{first_frame}` 줄은 기본 없이(아래 쓰는 법 '첫 프레임').
1. **REFERENCES 맨 끝에 `@previz` 한 줄** = 힉스필드 틀 문장(정본 §2 틀 그대로, 끊지 않음) + 바인딩 영어판('구도·카메라 무빙·컷 전환 레퍼런스' — 옛 골격 ② 문장, §4) + 색 대응 + 프리비즈 정본 보존/폐기 문장. 정지 이미지와 각도가 다르면 영상이 우선 [그들 주장: 정본 §1].
2. **SHOTS는 `Camera as @previz.`로 시작**하고 카메라 위치·화각·무브를 다시 쓰지 않는다 — 배치·BACKGROUND·비트·대사·END·컷 종류만(§1-3).
3. **LOOK 첫 문장** `A real photographic scene with real materials everywhere.`(옛 골격 ⑤의 첫 문장 — 더미 질감이 화면에 남지 않게). 렌즈 계열은 프리비즈가 나르므로 생략해도 된다.
4. 사람 큰 자세(허리 힌지)가 있을 때만 CHARACTER AND PRODUCT RULES 첫 줄에 CRITICAL 문장. 끝 면이 중요하면 제품 규칙에 끝 면 문장.
5. KEEP CONSISTENT 맨 끝 줄 `No transformation, no morphing, no bgm.`(프리비즈 컷 예외 — §1-7).
6. **`@previz` 줄 끝에 CAMERA FEEL 꼬리 + 바로 뒤 `Motion feel` 문장 — 기본**(프리비즈를 넣는 모든 생성 · 114번 — 효과 미검증). 결과를 보고 붙이는 것이 아니라 처음부터 넣는다 — 아래 틀·쓰는 법.

```
REFERENCES
… (얼굴·착장·제품·디테일·상태 줄과 `Reference-sheet panels are not the scene.`은 3-A와 같음 · 장소 판 줄은 배경을 지운 프리비즈일 때만 · `@first_frame` 줄은 시작 구도가 꼭 맞아야 할 때만)
@previz — camera path, framing and cut timing only; nothing visual carries over. Use this previz video as the reference for composition, camera movement and cut transitions, and match it 1:1. Colour key: the {purple} figure is {NAME}; the {magenta} block is the {PRODUCT}{; the grey blocks are the {SET ITEMS}}. Keep only their place, facing, size and motion; discard the flat colours, facets and tone bands — the final pixels contain no guide colour, never coloured blocks or mannequins.
[default — every generation with @previz · product commercial / short-form ad: append to the end of the @previz line above] Camera feel: subtle physical operator settling — momentum and weight, a small settle at each {stop | landing}; no handheld sway or shake, never digital jitter. 180-degree shutter: natural directional motion blur only in proportion to the speed already visible, never changing the path, timing or stops, resolving into a sharp, readable {PRODUCT | PRODUCT and face} whenever the camera settles; no ghosting, no stutter, no strobing. Real-time speed throughout; nothing floats, nothing teleports.
[default — same, but daily/documentary cuts whose reference camera is handheld only — instead of the line above] Camera feel: a real handheld operator — subtle organic handheld sway, a small breath-drift in the frame and weight shifting gently, never changing the path, the framing or the cut timing; operator momentum and a slight overshoot on hard direction changes{, a small operator settle at each {impact | stop}}. Never gimbal-smooth, never digital jitter. 180-degree shutter: natural directional motion blur only in proportion to the speed already visible, never changing the path, timing or stops, resolving into sharp, readable poses and faces; no ghosting, no stutter, no strobing. Real-time speed throughout, natural live-action motion only; natural body weight through every move — nothing floats, nothing teleports.
[default — every generation with @previz: right after the Camera feel tail, on the same @previz line] Motion feel: for people and objects, the previz sets only where each goes, which way it faces and when it stops — keep these 1:1. Whenever a body or object moves, it has real weight, inertia and follow-through, never the stiff, evenly eased motion of the guide blocks; whatever the previz holds still stays still.
[a dummy that stands in for a different shape only] Every {magenta} block is completely replaced by the {PRODUCT} from @{product_sheet}; preserve only its centre and approximate size; discard its edges, flat colour and shading — never {wrong guess, e.g. beads, marbles or rods}.

LOOK
A real photographic scene with real materials everywhere. {colour intent}, {one motivated light: direction, about {K} K}. {The PRODUCT is the most saturated colour in frame.}

CHARACTER AND PRODUCT RULES
[big body pose only] CRITICAL: the {purple} figure's waist bend IS {NAME}'s pose: as the camera {passes her side}, she leans forward from the waist, only ever deeper, never snapping back, and ends still leaning.
{NAME} — {2-3 trait words}; {how she moves}; {one behaviour rule}.
{PRODUCT} RULE: {state by time and where it is}; one {PRODUCT} only.{ The side of the {magenta} block that faces the lens in the last frame is the front of the {PRODUCT}.}

SHOTS
0.0-{t1}s — Camera as @previz. {who/what is where}. BACKGROUND: {...}. {beat at {t}s}. END: {...}. {Hard cut | No cut — the take continues}.
…

KEEP CONSISTENT
… (3-A의 줄들)
No transformation, no morphing, no bgm.
```

[위 틀에서 이 스킬이 바꾸는 곳: REFERENCES 괄호의 '장소 판 줄은 배경을 지운 프리비즈일 때만' → 장소 사진 줄(§0-E) · 카메라 꼬리 고르기와 거리 문장, 다큐판 빈칸 `{, a small operator settle …}`은 기본으로 뺌, 다큐판 + 뜨는 장면 꼴(§0-F) · Colour key의 방향 표시 구절(§0-B) · 색 이름·더미 낱말이 나와도 되는 곳(§0-D) · 비트 채우는 법(§0-C·§0-G)]

**쓰는 법**
- **REFERENCES는 그 생성(구간)에 나오는 것만**, 요소·상태당 1장 — 모델 한 명 = 얼굴 시트 + 착장 시트(옷이 바뀌면 그 구간 착장 시트). 생성당 보통 4~6장, 대부분 8장 이하, 10장이 넘으면 구간을 나눠 생성(03 §9 #7) [데이터: 정본 §2]. 장소 판은 생성 1번에 1장, 회색 세트 프리비즈면 판 없이(아래 '장소 판'). [§0-E: 회색 세트 프리비즈도 장소 사진 1장(이미지 마지막 번호)]
- **색 이름 = 실제 더미 색**(`saturated magenta`처럼 채도까지 써도 됨). 틀의 `{purple}`·`{magenta}`는 프리비즈 정본 기본 팔레트(사람 보라·제품 마젠타 — 04 §5, 분홍 제품이면 다른 오프팔레트 색 — 상충목록 94번)를 자리에 둔 것이고 실제 더미 색으로 바꿔 쓴다(07 #2 — 10/10판 정본 틀의 '파랑 상자·주황 기둥' 예는 10/22에 대체). 프리비즈에 놓은 회색 세트도 무엇인지 선언 — 선언 안 한 상자는 새 소품으로 발명된다 [정본].
- **생김새는 어디에도 글로 쓰지 않는다**(§1-2). 태그는 REFERENCES에서 한 번이 기본 — 샷에서는 이름(the glasses)으로 부르고, 그 컷에서 틀리면 안 되는 것(디테일 접사·닮은 두 제품·화면 글자가 읽혀야 하는 컷)만 그 컷 SHOTS 줄에서 다시 태그한다(§2 — 상충목록 90번. 대체: 옛 'Higgos는 `@prop_phone`을 18초 안에서 6번 부름 — 샷에서 핸들로 불러도 됨'). 닫힘/열림 이미지(`@prod_<이름>_states` — 예 `@prod_hilite_case_states`)는 제품 줄·디테일 줄 바로 뒤 ['제품 태그 뒤에 이 이미지도 추가로 태그' · 정본 §1].
- **첫 프레임 — 용도별**(상충목록 14·40번): 프리비즈를 넣는 생성은 **기본 첫 프레임 없이**. 시작 구도가 꼭 맞아야 하면 시작 프레임 칸이 아니라 레퍼런스로 넣고 `@first_frame` 줄 + 첫 샷 문장 `The very first frame of the clip is exactly @first_frame.`(플랫폼 무관) [매그니픽은 첫 프레임 칸과 레퍼런스를 같이 못 씀 → 레퍼런스로 넣고 문장으로 지정 · 정본 §6 문장 통일]. 프리비즈 첫 프레임과 같은 구도여야 한다(03 §5). 파트를 나눠 이을 때는 시작 이미지(`first_frame_partN` 핸들 꼴) — 힉스필드 MCP = `start_image` 칸(참조·프리비즈와 함께 들어감), 매그니픽 = 같이 못 넣으므로 참조 + 위 문장(06 §6-1). 이미지 없이 WHERE·첫 샷 배치(누가 화면 x%·y%)만으로 써도 된다. 나머지 용도(이미지 한 장을 영상으로 만드는 한 컷 = 첫 프레임 칸 · 제품 커머셜 = 없이도 됨)는 03 §5 표.
- [아래 예외 ②(회색 세트면 판 없이)는 §0-E로 대체] **장소 판 — 장소당 생성 1번**(상충목록 88·89번 — 03 §4): 그 생성 첫 샷 시점의 사람 없는 3/4 한 장, 역할 줄은 3-A 틀(`this plate is the first shot's viewpoint …`). 장소가 바뀌면 생성을 나눠 편집에서 매치컷(06 §6-1). 예외 ① 10초 안팎 짧은 컷 + 가림 전환이면 장소 판 여러 장을 순서대로 한 생성에 — 장소마다 한 줄 + SHOTS에서 그 구간에 태그 ② 회색 세트 + 랜드마크 프리비즈가 공간을 정하면 판 없이 장소는 WHERE·BACKGROUND 글로 — 배경을 지운 프리비즈(카메라 거의 고정·망원)는 판과 함께. 시간대가 다르면 새 판 대신 장소 줄 끝에 `; override its daylight` + LOOK에 빛. 카메라가 돌아 반대편이 보이면 (가) 반대쪽 장소 판을 **그 컷(그 생성)에만** 넣거나 (나) WHERE + 샷마다 `BACKGROUND:`를 글로 쓰거나 (다) 앞 영상(`@prev_partN` 핸들 꼴)을 위치 기준으로 넣는다(03 §4).
- **자리 배치 그림**(03 §10)을 넣으면 `@layout_<컷 id> — positions only; colours identify people (orange = @face_<이름> …), not wardrobe; faces, clothes and light come from the photo references.` [그들 주장: Higgos·timed-prompts §7a] — 핸들 `layout_<큐시트 컷 id>`(예 `layout_C03` — §2), 사람은 그 사람의 `face_<이름>`으로 지목(옛 `map_`·`char_` 꼴 대체). **엑스트라 단체 사진**(03 §11, 핸들 `extras_<장소>`)은 '알아볼 수 있는 엑스트라는 이 사람들뿐' 한 줄 + 위치로 지목(왼쪽에서 N번째). 다인물은 인물마다 참조 따로 [그들 주장: 공식 가이드 8/13].
- ⑦ SHOTS 시간은 **초 구간이 기본**. 프리비즈 카메라가 길게 이어지는 한 동작(젖힘·상승) 안에서 ⑤ 몸 자세 단계를 맞출 때만 초 대신 **카메라 위상**에 건다("as the camera passes her side") — 보조 요령(상충목록 115번). 그런 동작에서 초에 걸었더니 1단계에서 얼어붙은 기록이 있다 [정본].
- 연기가 중요한 장면만 ⑤ 아래 `ACTING TASK`(동기·목표·장애·전술 + 시선 줄)를 더한다 [데이터: Princess MOTIVE 줄 92.3%·Today 4/4].
- ⑦ 컷 규약 = 한 줄 요약의 컷 수·시각 + 샷마다 초 구간(종료 샷 = 마지막 줄, 끝 = 설정 길이) + KEEP CONSISTENT의 'Exactly {N} shots … opens on …' [프리비즈 정본 '개수 + 시각 + 종료 샷' · 힉스필드]. 동작은 동사로, 순서가 중요하면 번호로(사용 과정 3/3 vs 0/3 [관찰]). 모양이 바뀌는 동작(닫기·접기)은 다음 컷으로 떼기 [관찰]. 2.5는 정수 초에 반응 [공식]. [관찰] 컷은 평균 0.35초 일찍 들어간다.
- 대사는 그 샷 줄에 시각과 함께, SOUND에 '정확히 한 번씩' 목록으로 한 번 더(§6). 숫자는 한글로 풀어서("두 번") [관찰]. 화면 자막은 넣지 않는다(후편집).
- **마지막 제품 컷**(약 4초): 제품이 먼저 읽히게, 초점 이동은 한 번, 마지막 행동은 눈에 보이는 동작으로, VO는 첫 프레임부터, 끝 0.5초 정지 [데이터·그들 주장: Higgos 패킹샷 10/06~07].
  - **끝 로고는 쓰임별**(123번): 제품 로고 면을 보여 주며 끝나는 컷 = 생성 한 줄 — 어느 면이 렌즈를 향하는지만, 글자·로고 낱말 없이(예 제품 규칙에 `in the last frame the outer side of the temple faces the lens` — 19번, 작은 글자 오류는 라벨 고치기 06 §6) / 브랜드 로고 아웃트로 = 편집 끝 카드(0원) / 장면에 찍힌 로고 = 트래킹 합성(06 §6).
- 끝 면: 마지막에 제품 정면이 보여야 하면 제품 규칙에 `The side of the {magenta} block that faces the lens in the last frame is the front of the {PRODUCT}.` [관찰 끝 면 5/6]. 면 이름에 글자·로고 낱말을 쓰지 않는다 — 10/22에 끝의 '라벨 면' 구절을 뺐다(19번 · 정본 예 `the outer side of the temple`).
- **속도 램프**(빠름 → 슬로 → 감속 정지): 프리비즈에 속도 곡선이 있으면 생성에서 램프가 된다(04 §6). 글만으로는(프리비즈 없는 조각 컷) 램프·'거의 멈춤'이 실패하니 편집에서 한다 (116번).
- **제품 회전**: 제품은 움직이지 않고 카메라가 움직인다(회전하면 AI가 뒷면을 지어냄). 회전이 꼭 필요하면 뒷면 정보를 주는 참조(제품 시트 뒤 칸)와 프리비즈 앞뒤 색 구분(04 §4)을 함께 넣는다. 착용물은 몸과 함께 회전해도 된다 (117번).
- **CAMERA FEEL 꼬리 + `Motion feel` 문장 — 기본(대체: 옛 '선택 — 딱딱할 때만' → 기본, + Motion feel 추가 · 114번 — 효과 미검증)** [피사체 움직임·카메라 무빙이 프리비즈를 너무 따라가 어색한 경우가 훨씬 많아서 · 힉스필드 §2]. 프리비즈를 넣는 **모든 생성**의 `@previz`(`VIDEO 1` · `@Video1`) 줄 끝에 카메라 꼬리 하나(커머셜판 또는 다큐판) + 바로 뒤 Motion feel 문장을 붙인다. 결과를 보고 붙이는 것이 아니라 처음 프롬프트부터 넣는다.
  - **없어진 것**(07 §5): '① 프리비즈 속도 곡선 먼저 ② 그래도 딱딱하면 꼬리' 순서 조건 · '꼬리 있는 판·없는 판을 비교해 정한다' 단계. **남는 것**: 가감속·도착 뒤 감속·정착을 프리비즈의 키 시간 배치와 `ease`로 주는 것은 프리비즈 규칙으로 그대로(04 §3·§7 ⑤, 통합규칙 §4-3 '손맛은 흔들림이 아니라 속도 곡선'), 흔들림은 프리비즈에 넣지 않는다(04 §6 유지).
  - **역할**: 프리비즈 = 카메라 경로·구도·컷 타이밍·속도 곡선 + 사람·물건이 어디로 가고 언제 멈추는지 + 큰 자세(허리 힌지 더미 + 4번 CRITICAL 글, 더미 모양·세부는 단순하게 — 98번) / 카메라 꼬리 = 카메라를 든 사람의 몸 질감(관성·무게·정착)과 셔터 블러만 / Motion feel = 사람·물건이 **움직일 때의** 질감(실제 무게·관성·여운 follow-through)만 — 더미 블록의 딱딱하고 고르게 이징된 움직임을 따라 하지 않게. `@previz` 줄의 `match it 1:1`과 부딪히지 않게 Motion feel 안에 '경로·방향·시각·멈춤은 1:1'을 먼저 적고 질감만 풀어 준다. 문장에 세 가지를 박았다(10/11 저녁 점검 보완 — 결정 내용은 그대로, 문구만 다듬음): ① **범위** `for people and objects` — `@previz` 줄의 'camera path, framing and cut timing only'와 '프리비즈 역할은 이것뿐'이 둘로 부딪히지 않게 ② **방향** `which way it faces`(짧은판 `facings`) — 색 대응 문장의 `place, facing, size and motion`과 맞춰, 안경이 도는 각도·케이스 뚜껑 각도·마지막 면 같은 방향이 '질감이니 자유'로 읽히지 않게 ③ **조건형** `Whenever a body or object moves …; whatever the previz holds still stays still` — 시간 정지로 얼어 있는 사람·슬로모션 정지·HERO 정면 정지처럼 멈춰 있어야 할 것까지 움직이게 하지 않게. 둘 다 방향·거리·속도를 쓰지 않는다(§1-3) [§0-F 거리 문장 한 줄은 예외] — `prompt_check.py`가 꼬리·Motion feel 안 카메라 움직임 단어와 Motion feel 안 속도 말(`real-time`·`speed`)을 경고한다. 끝맺음(마지막까지 진행 / 의도한 정지)은 프리비즈와 04 §6 그대로.
  - [장르 기준 고르기는 §0-F로 대체: 원본 카메라가 핸드헬드면 다큐판] **세기**(카메라 꼬리만 — Motion feel은 한 가지 문장): 제품 커머셜·숏폼 광고 = **커머셜판**(관성·무게·정착 + 셔터 블러만, 흔들림·오버슛·짐벌 금지 문구는 넣지 않음 — 연출결정 '고급스럽게' = 긴 감속·오버슛 억제·정착 0.6~1.2s, '라벨·HERO 구간은 정면·정지', 통합규칙 §4-2 단조 보간 = 오버슛 불능). **다큐판**은 레퍼런스 카메라가 핸드헬드일 때만(큐시트 v2 `camera`의 마운트 = 핸드헬드, 01 §3 — 통합규칙 §4-3 '손떨림·셰이크는 레퍼런스에서 실측되지 않는 한 금지'). UGC도 같은 조건.
  - **예외**: 시간 정지·슬로모션처럼 일부러 뜨거나 느린 장면이면 카메라 꼬리에서 `Real-time speed …`와 `nothing floats`를 뺀다 — 3-C 샘플1(시간이 멈추고 물건이 떠 있음)이 여기에 해당. **Motion feel은 그대로 둔다** — 속도·'실시간' 뜻이 없고(그런 말을 더하지 않는다), 조건형('움직일 때만' + '프리비즈가 멈춰 둔 것은 멈춤')이라 얼어 있는 사람·떠서 멈춘 물건과도 맞는다. 떠 있음·멈춤·느린 흐름은 RULES(예 3-C `TIME RULE`)와 프리비즈 시각이 정한다. `real weight`가 떠 있는 물건을 떨어뜨릴지는 모른다 — `holds still stays still`이 막아 주는지 드래프트에서 [관찰](07 §6 ③).
  - **넣지 않는 것**: ① `gate weave`(필름 흉내 단어 — 06 §8 '색이 바램') ② PASSPORT의 `grey blocks and low-poly look are NOT inherited — re-skin …` — 위 `@previz` 줄의 `nothing visual carries over`와 버리는 문장이 이미 같은 일을 하고, 회색 세트 자리까지 버리라고 읽힐 수 있다. 결과에 회색 면이 남을 때만 겉모습을 가리키는 `the previz's flat grey surfaces and low-poly shading are not inherited; the grey blocks keep their place as the set items`를 쓴다.
  - **그대로 두는 것**: `@previz` 줄의 `nothing visual carries over` · SHOTS `Camera as @previz.` · KEEP CONSISTENT 끝 줄 `No transformation, no morphing, no bgm.`(§1-7).
  - **글자 수**: 커머셜판 약 495자 + Motion feel 약 310자 = 약 810자, 다큐판 약 715자 + 310자 = 약 1,030자(시간 정지 예외 커머셜판은 약 430~450자 + 310자 = 약 750자). 힉스필드 MCP는 1.8만 자를 받으므로 꼬리 때문에 줄이지 않는다(29번). 매그니픽 10,000자에 걸리면 §1-6 순서(①② 뒤 꼬리 안 ③ Motion feel 짧은판 → ④ `Real-time …` → ⑤ 짐벌·jitter → ⑥ 셔터). Motion feel 짧은판(약 225자, 같은 자리에 바꿔 넣음 — 범위 'only'가 없어 부딪힘이 없고, 방향·조건형은 그대로): `Motion feel: paths, facings, times and stops exactly as the previz; any body or object that moves has real weight, inertia and follow-through, never stiff, evenly eased block motion; what the previz holds still stays still.`
  - **드래프트에서 볼 것**(따로 비교 단계 없음 — G7b에서 같이, SKILL.md 7.6·06 §5 '보는 것'에도 같은 줄): 움직임이 3D 프리비즈 느낌인지(덜 딱딱한지) + 프리비즈 경로·향하는 방향·컷 시각·끝 정지점(멈춤 자리)을 지켰는지 + 프리비즈가 멈춰 둔 것(얼어 있는 사람·HERO 정지)이 멈춰 있는지 + 거꾸로 제자리 블록의 글로 적은 작은 동작(통화·웃음·손짓)까지 굳지 않았는지(07 §6 ④) + 큰 자세가 있는 생성이면 CRITICAL 글과 Motion feel의 'the previz sets only where each goes…'가 겹쳐 읽히는지 [관찰](함께 쓴 기록 0 — 정본 §9). 효과 기록이 없어 [관찰]로 기록하고, 경로·시각이 흔들리면 사용자에게 보여 준다(06 §8).

<!-- 원문 212~271행 = 3-C 예시(시험 샘플1 — 20초 9:16 원테이크, 시간이 멈추고 안경·케이스·폰이 공중에 떠 있는 장면)는 이 발췌에 싣지 않았다. 위 §3-B 쓰는 법 '예외'의 '3-C 샘플1'·'3-C `TIME RULE`'은 그 예시를 가리킨다 — 그 줄 원문(239행): `TIME RULE: from 3.3s to 16.8s time is frozen for both people, and the three objects hang perfectly still in the air; time snaps back at 16.8s.` 정본 문장을 고쳐도 되는 범위(3-C가 한 복수형·관사 맞춤 등)는 `references/handoff.md` 맨 앞에 적어 두었다. -->
<!-- 원문 273~293행 -->
### 3-1. 큐시트 → SHOTS 대응 [힉스필드 §7] — 리메이크 대응, 유지(10/22 확인)

큐시트 v2의 **컷 하나 = SHOTS 한 줄**(정본 10/22판 §7 '리메이크 대응': 컷 시간 → `t0–t1s`, 카메라 칸 → 카메라 위치·높이 m·거리 m·화각°(mm 병기), 배경 칸 → `BACKGROUND:`, 동작·소리 칸 → 비트 시각·SOUND 목록, 컷 끝 모습 → `END:`, **'확인 불가' 칸은 쓰지 않는다**). 레퍼런스의 길이·화면비는 프롬프트 글이 아니라 설정 칸으로만 옮긴다(§1-5·§1-10, 112번). 칸이 옮겨 가는 곳(01 §3 표의 `→`와 같다):

| 큐시트 v2 칸 | 프롬프트 자리 | 메모 |
|---|---|---|
| 컷(`id`) | SHOTS 한 줄 | 원테이크를 비트로 나눈 큐시트(샘플1 C01a~g)는 비트 하나 = 한 줄, 줄 끝 `No cut — the take continues.` |
| `start`·`end` | `t0–t1s` | 앞 줄 끝 = 다음 줄 시작, 마지막 끝 = 설정 길이(정수 초). 프리비즈를 고쳐 시각이 바뀌었으면 최신 `previz_spec_vN.json` 기준(샘플1: 큐시트 v2 15초 → 프리비즈 v3 20초) |
| `camera`·`shot`·`angle`·`lens_feel` | 프리비즈 있으면 `Camera as @previz.`만 / 없으면 카메라 위치·높이 m·거리 m·화각°(mm 병기)·무브 하나 | `lens_feel`은 추정 — 숫자는 v2에서 정한 값만(01 §3, 07 #25) |
| `subjects.position`·`facing` | 그 줄의 배치(화면 좌·중·우 / x%). 영상 내내 같은 것은 WHERE EVERYTHING IS | |
| `subjects.action`(시각 붙임) | 비트 시각(`At 3.3s …`) | 순서가 중요하면 번호로 |
| `background.place` | `BACKGROUND:` | 이 각도에서 인물 뒤에 보이는 것 |
| `lighting` | LOOK의 광원 한 줄 | 모든 파트 같은 문장 |
| `product`(상태·시각·면) | CHARACTER AND PRODUCT RULES의 시간대별 상태 + `END:`의 제품 면 | |
| `sound`(들은 것만) | 그 줄의 대사 시각 + SOUND 목록 | 대사 '정확히 한 번씩'. 배경 음악은 생성 안 함(§6) |
| `on_screen_text` | 라벨 글자는 글로 쓰지 않음(§1-2 — 19번) / 자막·카피는 후편집 → SOUND 끝 `No subtitles, no on-screen text.` | 글자는 디테일 클로즈업 이미지·1080p 접사 컷·후반(06 §6)이 맡음 |
| `transition` | 줄 끝 컷 종류: `Hard cut` / `Match cut: …` / `No cut — the take continues.` | |
| 끝 모습(`evidence`의 끝 프레임 · position "시작 → 끝") | `END:` 누가 어디·손에 든 것·제품 면 | |
| `must_show` 1순위 | KEEP CONSISTENT 후보 | |
| `inputs`(handle) | 그 생성의 REFERENCES 줄 목록 | 그 구간에 나오는 것만 |
| 어느 칸이든 `확인 불가`(`sound`·`lens_feel`·`on_screen_text`·`observation` 등 — 01 §3 '빈칸 금지') | **쓰지 않는다** | 모르는 칸을 글로 채우면 모델이 그걸 만든다 |

<!-- 원문 324~333행 (295~322행 = §4 바인딩 원문 모음·§5 타임라인, 뺌) -->
## 6. 오디오 [힉스필드 §2·§4 — 07 #21 + 상충목록 15·124번]

- **생성 오디오는 켜고 효과음·현장음만 만든다. 배경 음악은 생성하지 않고 편집에서 깐다** — 유지 + 보강(상충목록 15번 B): 배경 음악 없이 효과음 등만 생성하고, 배경음은 나중에 편집으로 넣는다. 켜는 칸: 힉스필드 `generate_audio: true` · 매그니픽 `withSoundEffects: true`.
- SOUND 첫마디는 `No background score.` 화면 안에 음원이 보일 때만(연주·스피커·파티 음악) 그 소리를 현장음으로 시각과 함께 적는다(`; the only music is {visible source} playing from {t}s to {t}s`) — 유지(10/22 확인, 10/10 D1 — 07 #21) [그들 주장: timed-prompts §5 / 데이터: Princess no music 86.5%·Trigger 71.6%·Higgos SOUND 블록·Blackpine 파티 장면 현장 음악].
- SOUND에 현장음·제품 소리 시각 + 대사·VO '정확히 한 번씩' 목록(`Lines, each spoken exactly once and nothing else: {t} {NAME} '...'`) + `No subtitles, no on-screen text.` 대사 시각은 SHOTS 줄의 대사 시각과 같아야 한다(§7 점검).
- **배경 음악 출처**(편집에서 깔 때): 저작권 없는 음원이 기본, 생성 음악(매그니픽 등)은 길이·박자를 맞춰야 할 때의 대안 — 약관·생성 화면을 보관한다(상충목록 124번). 배경음 생성 품질은 아직 연구 과제다(15번).
- **소리가 필요 없는 생성만 끄고** 원본 소리(= 우리가 생성한 영상의 오디오 또는 편집에서 넣는 소리, 남의 레퍼런스 영상 소리 ✕ — 상충목록 22번·음악 저작권)·편집 소리를 쓴다(기존 그대로). 꺼도 SOUND 블록은 `No background score. No subtitles, no on-screen text.` 한 줄로 남긴다 — 화면 글자 금지는 소리와 상관없이 필요하다 [우리].
- 비용: 힉스필드는 소리를 켜도 값이 같다는 공식 주장 [그들 주장: 도움말 9/09]. 매그니픽은 공식 주장이 없으니 켠 값·끈 값 견적을 둘 다 받아 확인한다(06 §3·§4).
- 오류 컷 갈아끼우기(4초 다시 생성)는 소리를 끄고 원래 소리를 쓴다(06 §6). 원본 소리(= 우리가 생성한 영상의 오디오 또는 편집에서 넣는 소리, 남의 레퍼런스 영상 소리 ✕ — 상충목록 22번·음악 저작권) 다시 붙이기는 모델이 아니라 후처리(06 §6).
- 대체된 것: 옛 '소리는 온'으로 생성해 결과에 들어간 배경 음악 → 편집에서 까는 음악(07 #21). 이 스킬의 옛 기본('생성 오디오 기본 끔 + `Natural sound only, no music`')도 위 기준으로 바뀌었다. 옛 판의 '필요할 때만 켬'(대사·현장음이 필요하면 켜고 아니면 끔)도 '기본 켬 + 효과음·현장음만'으로 대체(상충목록 15번 B — 07 §5).

<!-- 원문 335~369행 -->
## 7. 제출 전 점검 (0원) [힉스필드 §2·§7 — 그들 주장: timed-prompts §1·§3 '제출 전 자동 점검']

```
python3 <스킬>/scripts/prompt_check.py 05_생성/prompt_v1.txt --route higgsfield \
    --inputs 03_인풋이미지/inputs.json --spec 04_프리비즈/previz_spec_vN.json \
    --duration 20 [--part 2] [--allow HILITE]
```
- `--route` = 낼 경로, 셋 중 하나: `higgsfield`(힉스필드 MCP — `IMAGE N`·`VIDEO N`) / `magnific`(매그니픽 — `@Image1`·`@Video1`) / `web`(힉스필드 웹 — `@handle`). 경로를 바꾸면 표기도 바꾸고(§2) 다시 돌린다.
- `--inputs`(03 §9 준비표에서 만든 inputs.json)는 7단계엔 **항상** 넣는다 — 빼면 핸들·번호 대조(§2)를 건너뛰고 `[정보]`로만 알린다.
- `--spec`(프리비즈 명세)은 프리비즈가 있으면 넣는다. 프리비즈 없는 조각 컷이면 빼고.
  - **하드컷 파트 조각을 점검할 때**: `--spec`은 전체 프리비즈 명세라 길이 실패가 뜬다 → 조각 점검은 `--spec`을 빼고 `--duration N`(N = 그 조각 길이), 색 이름 점검은 전체 명세로 한 번만 (코드 변경 없음).
- `--duration` = 화면·파라미터에 넣을 길이(정수 초). **10/22부터 늘 넣는다** — 한 줄 요약에 길이를 쓰지 않으므로(§1-5, 112번) 이 값으로 마지막 샷 끝·프리비즈 길이와 대조한다. 빼면 프리비즈 명세 길이로 대신 점검하고(`[정보]`), 프리비즈도 없으면 '길이를 알 수 없음' 실패.
- `--part N` = 파트로 나눠 생성할 때 몇 번째 파트인지 — 하드컷 있는 20~30초는 하드컷에서, 30초가 넘거나 장소가 바뀌면 파트로 나눈다(06 §6-1, 24·88번). 2 이상이면 `Opens mid-situation` 줄이 없을 때 실패 — **안 주면 이 점검을 하지 않는다**. 나누지 않고 한 번에 생성하면(원테이크 15초 안팎·하드컷 있는 20초 미만) 뺀다.
- `--allow` = 실존 이름 목록과 겹치는 우리 이름(쉼표로, 예 `HILITE`). inputs.json에 적힌 우리 이름·핸들은 저절로 허용된다.
- `--limit N` = 글자 수 실패 한도를 직접 정할 때만(보통 안 씀 — 경로별 한도 §1-6).

**스크립트가 보는 것**
- 글자 수 — 경로별(§1-6): `higgsfield` = 한도 때문에 실패·경고하지 않음([정보]만 — 18,127자 통과, 29번) / `magnific` 10,000자 초과 = 실패, 3,900자 초과 = 경고(3,900은 실패 아님) / `web` 20,000자 초과 = [정보]만(8/22 이후 2만 자 넘게 정상). 넘을 때 줄이는 순서 안내는 §1-6 번호 그대로(①② → 꼬리 안 ③④⑤⑥). 길이 기준은 원본 틀 길이(30초 9샷 ≈ 9천 자 — §1-6, 118번).
- 참조 대조 — `web`이면 `@핸들` = `inputs.json`의 `handle`, 번호 경로면 태그 번호 = `tag`(올린 순서). 없는 것을 부르거나, 넣고도 안 부르는 것 [데이터: Blackpine 10/03 순서 어긋남 4건].
- 프리비즈 — 더미 색 이름이 색 대응 문장에 있는지(명세 색이 RGB 목록 `[0.42, 0.42, 0.42]`이면 이름 없는 색 — 회색 세트 등 — 으로 보고 이 점검에서 빼고 [정보] 한 줄. 10/11까지는 여기서 오류로 멈췄다) · `@previz` 바인딩(카메라 경로·구도·컷 타이밍) · SHOTS에 카메라 움직임 단어(프리비즈가 나르는 경로를 글로 다시 썼나) · CAMERA FEEL 꼬리 + Motion feel(§3-B, 10/11 저녁부터 기본) — 프리비즈가 있는데 `Camera feel:`이 없음 · `Motion feel:`이 없음 = 경고(각각) · 꼬리·Motion feel 안 카메라 움직임 단어 [§0-F 거리 문장 한 줄은 예외] ·`gate weave`·`@previz` 줄이 아닌 곳·두 판 다(두 번)·Motion feel이 카메라 꼬리 앞·Motion feel 안 속도 말(`real-time`·`speed`)·프리비즈 없는 꼬리·Motion feel = 경고 · PASSPORT `low-poly look are NOT inherited — re-skin` 문장 = 경고.
- **틀 빈칸** — `{stop | landing}`·`{PRODUCT | PRODUCT and face}`·`{NAME}`처럼 중괄호 `{…}`가 남아 있으면 경고(채우지 않은 틀 자리 — 중괄호는 씨댄스에 글자 그대로 들어간다. 10/11 저녁부터 꼬리가 모든 프리비즈 프롬프트에 기본이라 커머셜판 빈칸 2곳을 특히 확인).
- 샷 구간 연속(앞 줄 끝 = 다음 줄 시작) · 마지막 끝 = 설정 길이(`--duration`, 정수 초) = 프리비즈 길이.
- 대사 시각 = SOUND 목록 · 샷마다 `BACKGROUND:`·`END:` 있음 · KEEP CONSISTENT 6~14줄(10/22 — 라벨 두 줄이 빠진 기준, 정본 ⑨).
- 라벨·글자 문장 — REFERENCES·KEEP CONSISTENT·CHARACTER AND PRODUCT RULES 줄에 글자 낱말·철자를 지키라는 문장·'다른 로고 금지' 줄(`lettering`·`label reads`·`correctly spelled`·`No logos other than`·`logo`)이 있으면 경고(§1-2, 19번 — 디테일 클로즈업 1장이 맡음). 'label' 낱말 하나만 써도 경고 — 단 REFERENCES 디테일 줄(`a close-up of …`·`_detail` 줄)의 부위 이름 `the label`·소유격(`the bottle's label`)은 뒤에 reads·reading·lettering·spelled가 없을 때 허용(19번·정본 §2 ③). SHOTS·LOOK·WHERE 블록은 스크립트가 보지 않으니 사람 눈 ⑧로. 이 경고는 정본 §7 목록 밖(07 §6).
- 시트 줄 — 시트 핸들(`face_`·`outfit_`·`prod_`·`pack_`(포장 시트) — 클로즈업 1장 `prod_<이름>_detail`·`outfit_<이름>_detail`은 시트로 세지 않음, `_states`는 셈)이 REFERENCES에 있는데 `Reference-sheet panels are not the scene.` 줄이 없으면 경고(86번). 번호 경로(`IMAGE N`·`@Image1`)는 `inputs.json` `tag`로 핸들을 찾는다. 시트 핸들을 못 찾아도(번호 경로에 `--inputs`가 없거나 핸들이 이 꼴이 아닐 때) REFERENCES 줄에 `sheet`·`every angle`이 있으면 같은 경고 · `outfit_` 핸들(옷 디테일 클로즈업 `outfit_<이름>_detail`은 뺌)이 2개 이상인데 `Outfit order` 줄이 없으면 경고(정본 §2 ③ · 03 §2).
- `as above`·`same as before`·앞 컷 요약 문장 없음(§8) · 실존 감독·브랜드·장비 이름 없음(§1-9, 경고) · 한글(대사 외).
- 9블록 — REFERENCES·LOOK·SHOTS·SOUND·KEEP CONSISTENT 필수(없으면 실패) · CHARACTER AND PRODUCT RULES·WHERE EVERYTHING IS 권장 · 블록 순서 · 독립 NEGATIVE 블록(경고, §1-7).
- 한 줄 요약 — 샷 수·컷 시각 = SHOTS. 요약에 길이·화면비가 없는 것이 정상(112번 — 화면비는 `[정보]`로 '설정 칸에서'만 알림). 옛 프롬프트처럼 길이가 적혀 있으면 `--duration`과 다를 때 실패, 화면비가 9:16·16:9가 아니면 경고(§1-10).
- 이어받기 — `--part 2` 이상이면 `Opens mid-situation` 줄 필수 · `Continue directly from the final frame of the attached video.`는 맨 첫 줄 · 옛 `Extend @video1 …` 문장은 경고(07 §5).
- SOUND — 배경 음악 없음 줄(`No background score.`)이 없으면 경고(§6).
- 인풋 — 장소 판(`loc_`) 2장 이상·환경 라이팅 시트(`env_`)·이미지 10장 초과면 경고(03 §4·§9 #7). 장소 판 여러 장은 예외 ①(10초 안팎 + 가림 전환 — §3-B '장소 판')일 때만 경고를 넘긴다.
- 출력 꼬리표는 `[실패]`·`[경고]`·`[정보]` 셋. **`[실패]`가 하나라도 있으면 고친 뒤 다시 돌린다** — 견적·생성으로 넘어가지 않는다. `[경고]`·`[정보]`는 눈으로 보고 넘길 수 있다(예: 실존 이름 목록과 겹치는 우리 이름 → `--allow` / 원테이크라 한 줄 요약에 '{N} shots'가 없음).

**사람 눈 대조** [정본 생성 전 정합 QC + 힉스필드]
① 색: 프리비즈 더미 = 프롬프트 색 이름 = 역할 줄 ② 개수: 더미 수 = 치환 선언 수 = 이미지 ③ 첫 프레임 이미지를 쓰면 프리비즈 첫 프레임과 나란히 놓고 구도·위치·크기 비교 ④ 이전 라운드 문장·지운 더미를 가리키는 문장이 없나 ⑤ 시작·끝 방위가 필요한 회전 컷이면 둘 다 썼나 ⑥ 번호 경로면 실제로 올리는 순서 = `tag` ⑦ 화면(UI)의 길이 = `--duration` = 마지막 샷 끝, 화면비 = 프리비즈 렌더·장소 판(§1-10) — 화면이 이전 값을 들고 있을 수 있다 [그들 주장: Higgos 10/07] ⑧ 생김새 구절·라벨 글자·글자를 지키라는 문장이 없나(§1-2 — 18·19번).

<!-- 원문 371~378행 -->
## 8. 수정 요청 규칙 [힉스필드 §2·§7 — 그들 주장: timed-prompts §0·CINEDANCE V4 9/17~18·Higgos 10/07] — 유지(10/22 확인)

1. 수정 요청이 오면 **항상 전체 프롬프트를 새로** 낸다. 바뀐 줄만·차이만 내지 않는다. `as above`·`same as before`·앞 컷 요약 금지 — 모델은 생성마다 백지다.
2. **이전 수정은 사용자가 지우라고 할 때까지 유지**한다. 새 수정 때문에 앞에서 고친 문장이 슬쩍 빠지지 않게, 수정마다 `작업기록.md`에 '이번에 바꾼 문장 / 계속 유지하는 수정'을 적는다(04 §8과 같은 목록).
3. 수정 요청마다(길이를 바꾸지 않았어도) **화면(UI)·파라미터의 길이를 마지막 샷 끝과 따로 확인하라고 사용자에게 한 줄** 알린다 — 길이는 글에 없고 설정 칸에만 있으며(§1-5), 화면이 이전 길이를 그대로 들고 있을 수 있다 [그들 주장: Higgos 10/07 · IYSL 브리프 '남는 시간을 모델이 지어냄'].
4. 다시 뽑을 때는 **한 번에 변수 하나만**(인물 또는 장소 또는 프롬프트 한 블록) — 06 §8.
5. 프리비즈를 고쳤으면 지운 더미를 가리키는 문장·더한 더미를 부정하던 문장을 같이 고친다(04 §8, 정본 F-7·F-12).
6. 고친 프롬프트도 §7 점검을 다시 통과시킨다. 다시 뽑기는 건마다 새 승인(06).
