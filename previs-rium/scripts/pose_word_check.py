#!/usr/bin/env python3
"""완성 프롬프트(②힉스필드 웹판·③매그니픽판)에서 생성 필터에 걸릴 수 있는 다리 말을 센다.

prompt_canon.md §0-H 피할 말 2단 표의 점검기. 주인공 다리·무릎·split에 붙은 말만 본다.
  1단 꼭 피함: 다리에 붙은 open·opens·opening·widest · 벌림 각도 숫자(about 120 degrees)
  2단 미리 피함: split(s)·straddle·thigh(s)·inner thigh·crotch·groin·between her legs
                · 다리에 붙은 spread·apart·wide
  대상 아님: 몸 방향 값(about 35° from the lens) — 정규식이 뺀다.
             수비수 팔·발(spread arms·feet apart)·선글라스(open one temple)는 걸려 나와도 대상 아님.

쓰는 법:
  python3 pose_word_check.py <파일> [<파일> ...]
  - .md 파일(04_넘기기/handoff.md)이면 ```text 코드 블록(②·③)만 따로 센다.
  - 그 밖의 파일(.txt 등)은 전체를 센다.
판정: 모든 블록이 1단 0건 · 2단 0건이면 '통과'(끝 코드 0). 걸린 말이 있으면 목록을 보여 주고
끝 코드 1 — 주인공 다리 말이면 §0-H '대신' 말로 바꾸고, 수비수 팔·발·소품 말이면 그대로 둔다.
"""
import re
import sys

LEG = r'(?:leg|legs|knee|knees|thigh|thighs|split|splits|scissor|scissors)'
T1 = [LEG + r'[^.;,]{0,25}\b(?:open|opens|opening|widest)\b',
      r'\b(?:open|opening)\b[^.;,]{0,15}' + LEG,
      r'\d+\s*(?:degrees|°)(?! from the lens)']
T2 = [r'\b(?:splits?|straddle|crotch|groin|inner thigh|between her legs|thighs?)\b',
      LEG + r'[^.;,]{0,25}\b(?:spread|apart|wide)\b(?!\s+(?:arms|hands|fingers))',
      r'\b(?:spread|wide)\b[^.;,]{0,15}' + LEG]


def hits(text, patterns):
    return [m.group(0) for p in patterns for m in re.finditer(p, text, re.I)]


def blocks(path):
    text = open(path, encoding='utf-8').read()
    if path.lower().endswith('.md'):
        found = re.findall(r'```text\n(.*?)```', text, re.S)
        if found:
            return [(f'코드 블록 {i + 1}', b) for i, b in enumerate(found)]
        print(f'[알림] {path}: ```text 코드 블록이 없어 파일 전체를 셉니다')
    return [('전체', text)]


def main(paths):
    if not paths:
        print(__doc__)
        return 2
    total = 0
    for path in paths:
        for label, text in blocks(path):
            h1, h2 = hits(text, T1), hits(text, T2)
            total += len(h1) + len(h2)
            name = path.split('/')[-1]
            print(f'{name} [{label}] | 1단 {len(h1)}건 {h1[:8]} | 2단 {len(h2)}건 {h2[:8]}')
    if total:
        print('확인 필요 — 주인공 다리 말이면 prompt_canon.md §0-H 대신 말로 바꾼다(수비수 팔·발·소품 말은 대상 아님)')
        return 1
    print('통과 — 1단 0건 · 2단 0건')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
