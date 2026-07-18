#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""md_to_latex.py · 힘뇌장 v1 통합본 -> 단행본 LaTeX(XeLaTeX)

기존 조판틀(latex/himnoejang-book.tex)의 전처리부(preamble)·표지·판권면을 재사용하고,
본문만 v1 윤문본(chapters/ch*-v1.md + appendices/*.md)에서 새로 변환해 조립한다.

변환 규칙(기존 .tex 관례와 일치):
  # Chapter N · 제목        -> \\chapter{제목}         ("Chapter N ·" 제거)
  # 서문 … (Preface)        -> \\chapter*{…}+목차등록  (첫 인용블록은 authnote 유지)
  # 부록 X · 제목           -> \\chapter*{…}+목차등록
  ## N · 제목 / ## 제목     -> \\section{제목}          (앞 번호 제거)
  ### N.N 제목              -> \\subsection{제목}
  ## 참고문헌 (References)  -> \\section*{참고문헌}+\\refstart … \\refend
  [n] 서지 … URL … [tag]    -> \\reff{n}{서지}          (URL·검증태그 제거)
  **굵게**                  -> \\textbf{…}
  *기울임*                  -> \\textit{…}
  `코드`                    -> \\texttt{…}
  | 표 |                    -> tabularx (첫 행 굵게)
  > 인용블록                -> authnote
  - 불릿 / 1. 번호          -> itemize / enumerate
  ---(수평선)               -> 삭제
  헤더 메타데이터           -> 삭제 (서문·부록의 안내 인용블록은 유지)

사용법:  python scripts/md_to_latex.py
출력:   latex/himnoejang-book-v1.tex
"""
import os, re, sys

BASE_TEX = "latex/himnoejang-book.tex"
OUT_TEX = "latex/himnoejang-book-v1.tex"

PREFACE = "chapters/ch00-preface-v1.md"
CHAPTERS = [
    "chapters/ch01-introduction-v1.md",
    "chapters/ch02-joseon-yi-sunsin-v1.md",
    "chapters/ch03-gut-brain-history-v1.md",
    "chapters/ch04-ginseng-v1.md",
    "chapters/ch05-atractylodes-v1.md",
    "chapters/ch06-poria-v1.md",
    "chapters/ch07-glycyrrhiza-v1.md",
    "chapters/ch08-hericium-v1.md",
    "chapters/ch09-polygala-v1.md",
    "chapters/ch10-theanine-v1.md",
    "chapters/ch11-tyrosine-v1.md",
    "chapters/ch12-glutamine-v1.md",
    "chapters/ch13-curcumin-v1.md",
    "chapters/ch14-fos-palatinose-v1.md",
    "chapters/ch15-epilogue-v1.md",
]
APPENDICES = [
    "appendices/appendix-A-historical-sources.md",
    "appendices/appendix-B-patent-claims.md",
]

META_LABEL = re.compile(
    r'^\s*(기획·감수|저자 검토|최종 검증 실행일|검증 로그|사료 검증|AI 초안 도구|'
    r'편집 로그|공저자|참고문헌|작성|문체|분량|저자|편집|대상|상태)\s*[:：]')

_SPECIAL = {'&': r'\&', '%': r'\%', '#': r'\#', '$': r'\$', '_': r'\_', '{': r'\{', '}': r'\}'}


def esc(t):
    t = re.sub(r'[&%#$_{}]', lambda m: _SPECIAL[m.group()], t)
    return t.replace('~', r'\textasciitilde{}').replace('^', r'\textasciicircum{}')


# 맨눈 호스트명(http 없이 쓴 도메인): 좁은 판폭·표 칸에서 줄바꿈되도록 \url 처리
BAREHOST = re.compile(
    r'(?<![\w./@-])((?:[A-Za-z0-9-]+\.)+(?:kr|com|org|net|gov|edu|int))(/[^\s)>\]]*)?')


def inline(t):
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)              # [text](url)->text
    # URL·코드·도메인을 먼저 치환·보관(escape/강조 처리에서 보호), 마지막에 복원
    stash = []

    def put(s):
        stash.append(s)
        return '\x00%d\x00' % (len(stash) - 1)

    t = re.sub(r'`([^`]+?)`', lambda m: put(r'\texttt{%s}' % esc(m.group(1))), t)   # `코드`
    t = re.sub(r'<((?:https?://|mailto:)[^>]+)>', lambda m: put(r'\url{%s}' % m.group(1)), t)
    t = re.sub(r'(?<![\w])(https?://[^\s<>()\[\]]+)', lambda m: put(r'\url{%s}' % m.group(1)), t)
    t = BAREHOST.sub(lambda m: put(r'\url{%s}' % m.group(0)), t)                    # 맨눈 도메인
    t = esc(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', t)
    t = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'\\textit{\1}', t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: stash[int(m.group(1))], t)
    return t


def ref_line(num, rest):
    rest = rest.split(' URL:')[0]
    rest = re.sub(r'\s*\[[^\]]*(VERIFIED|VERIFY|PENDING)[^\]]*\]\s*$', '', rest).strip()
    return r'\reff{%s}{%s}' % (num, esc(rest))


def is_trow(line):
    s = line.strip()
    return s.startswith('|') and s.count('|') >= 2


def is_sep(line):
    return bool(re.match(r'^\s*\|[\s:|-]+\|\s*$', line))


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def table(rows):
    ncol = max(len(r) for r in rows)
    spec = r'@{}*{%d}{>{\raggedright\arraybackslash}X}@{}' % ncol
    out = [r'\vspace{2pt}\noindent{\scriptsize\begin{tabularx}{\linewidth}{%s}' % spec, r'\toprule']
    for i, r in enumerate(rows):
        r = r + [''] * (ncol - len(r))
        conv = [inline(c) for c in r]
        if i == 0:
            conv = [r'\textbf{%s}' % c for c in conv]
        out.append(' & '.join(conv) + r' \\')
        if i == 0:
            out.append(r'\midrule')
    out.append(r'\bottomrule')
    out.append(r'\end{tabularx}}\vspace{3pt}')
    return '\n'.join(out)


def render_list(entries):
    # entries: [(indent, 'ol'|'ul', inline_text)] -> 중첩 enumerate/itemize
    out, stack = [], []

    def _open(kind):
        out.append(r'\begin{%s}[leftmargin=6mm,itemsep=1pt,topsep=2pt]'
                   % ('enumerate' if kind == 'ol' else 'itemize'))

    def _close(kind):
        out.append(r'\end{%s}' % ('enumerate' if kind == 'ol' else 'itemize'))

    for indent, kind, text in entries:
        while stack and indent < stack[-1][0]:
            _close(stack.pop()[1])
        if not stack or indent > stack[-1][0]:
            _open(kind)
            stack.append((indent, kind))
        elif kind != stack[-1][1]:
            _close(stack.pop()[1])
            _open(kind)
            stack.append((indent, kind))
        out.append(r'  \item %s' % text)
    while stack:
        _close(stack.pop()[1])
    return '\n'.join(out)


def chapter_head(title, kind):
    ti = inline(title)
    if kind == 'chapter':
        return r'\chapter{%s}' % ti
    # preface / appendix : 번호 없는 장 + 목차 등록
    return (r'\chapter*{%s}\addcontentsline{toc}{chapter}{%s}\markboth{%s}{}'
            % (ti, ti, ti))


def render(path, kind):
    raw = open(path, encoding='utf-8').read().split('\n')
    # --- 제목 ---
    title = raw[0].lstrip('#').strip()
    title = re.sub(r'^Chapter\s+\d+\s*·\s*', '', title)
    title = re.sub(r'\s*\(Preface\)\s*$', '', title)
    blocks = [chapter_head(title, kind)]

    # --- 본문 시작 지점 ---
    body = raw[1:]
    if kind == 'chapter':
        # 헤더 메타데이터 + 원고상태 인용블록: 첫 '---' 까지 통째로 제거
        cut = 0
        for i, ln in enumerate(body):
            if re.match(r'^\s*---+\s*$', ln):
                cut = i + 1
                break
        body = body[cut:]
    else:
        # 서문/부록: 선두의 메타데이터 라벨 줄만 제거(안내 인용블록은 유지)
        j = 0
        while j < len(body):
            s = body[j].strip()
            if not s:
                j += 1
                continue
            if META_LABEL.match(body[j]):
                j += 1
                continue
            break
        body = body[j:]

    i, n = 0, len(body)
    while i < n:
        line = body[i]
        s = line.strip()
        if not s:
            i += 1
            continue

        # 수평선 삭제
        if re.match(r'^\s*(---+|\*\*\*+)\s*$', line):
            i += 1
            continue

        # 참고문헌 섹션(파일 끝까지)
        if s.startswith('## 참고문헌') or s.startswith('## References'):
            blocks.append(r'\section*{참고문헌}\addcontentsline{toc}{section}{참고문헌}')
            blocks.append(r'\refstart')
            i += 1
            while i < n:
                t = body[i].strip()
                m = re.match(r'^\[(\d+)\]\s+(.*)$', t)
                if m:
                    blocks.append(ref_line(m.group(1), m.group(2)))
                i += 1
            blocks.append(r'\refend')
            break

        # 표
        if is_trow(line):
            blk = []
            while i < n and is_trow(body[i]):
                if not is_sep(body[i]):
                    blk.append(cells(body[i]))
                i += 1
            if blk:
                blocks.append(table(blk))
            continue

        # 제목
        m = re.match(r'^###\s+(?:\d+\.\d+\s+)?(.+)$', s)
        if m:
            blocks.append(r'\subsection{%s}' % inline(m.group(1)))
            i += 1
            continue
        m = re.match(r'^##\s+(?:\d+\s*·\s*)?(.+)$', s)
        if m:
            blocks.append(r'\section{%s}' % inline(m.group(1)))
            i += 1
            continue

        # 인용블록 -> authnote
        if s.startswith('>'):
            buf = []
            while i < n and body[i].strip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', body[i]).strip())
                i += 1
            txt = inline(' '.join(x for x in buf if x))
            blocks.append(r'\begin{authnote}%s\end{authnote}' % txt)
            continue

        # 목록(번호·불릿, 들여쓰기 중첩 지원)
        if re.match(r'^\s*(?:[-*]|\d+\.)\s+', line) and not is_trow(line):
            entries = []
            while i < n and re.match(r'^\s*(?:[-*]|\d+\.)\s+', body[i]) and not is_trow(body[i]):
                m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', body[i])
                kind = 'ol' if m.group(2).endswith('.') else 'ul'
                entries.append((len(m.group(1)), kind, inline(m.group(3).strip())))
                i += 1
            blocks.append(render_list(entries))
            continue

        # 일반 문단
        blocks.append(inline(s))
        i += 1

    return '\n\n'.join(blocks)


def transform_head(head):
    """기존 preamble/표지를 신국판(152×225mm)으로 바꾸고 오버플로 방지 설정을 주입."""
    # 1) 판형: 46배판(188×257) -> 신국판(152×225) + 여백 재계산
    head = re.sub(
        r'\\usepackage\[paperwidth=188mm,paperheight=257mm,.*?heightrounded\]\{geometry\}',
        (r'\\usepackage[paperwidth=152mm,paperheight=225mm,' + '\n'
         r'  top=20mm,bottom=20mm,inner=19mm,outer=15mm,headsep=6mm,footskip=11mm,' + '\n'
         r'  heightrounded]{geometry}'),
        head, flags=re.S)

    # 2) 오버플로 방지: URL 줄바꿈(xurl) + 라인브레이크 여유
    head = head.replace(
        r'\usepackage[unicode,hidelinks]{hyperref}',
        r'\usepackage[unicode,hidelinks]{hyperref}' + '\n'
        r'\usepackage{xurl}                 % 긴 URL 을 어디서든 줄바꿈(신국판 좁은 판폭)' + '\n'
        r'\tolerance=3000 \emergencystretch=4em \hbadness=10000  % 줄 넘침 방지 여유')

    # 2b) 주석(authnote) 우여백 축소 — 좁은 판폭에서 붙은 토큰 오버플로 방지
    head = head.replace(r'\leftskip=7mm\rightskip=5mm\small\color{muted}',
                        r'\leftskip=6mm\rightskip=3mm\small\color{muted}')

    # 3b) 가독성: 본문 폰트 확대(11→12pt) + 줄간격 확대(1.22→1.38)
    head = head.replace(r'\documentclass[11pt,oneside]{book}',
                        r'\documentclass[12pt,oneside]{book}')
    head = head.replace(r'\linespread{1.22}', r'\linespread{1.38}')

    # 3c) 참고문헌: 본문보다 더 작은 폰트 + 촘촘한 줄간격(footnotesize→8.5pt, 줄간격 tight)
    head = head.replace(
        r'\newcommand{\refstart}{\par\begingroup\footnotesize\setlength{\parskip}{2.5pt}\raggedright}',
        r'\newcommand{\refstart}{\par\begingroup\fontsize{8.5pt}{10.2pt}\selectfont'
        r'\setlength{\parskip}{1.4pt}\raggedright}')

    # 3) 표지 글자 크기 축소(좁아진 판폭에 맞춤)
    head = head.replace(r'\fontsize{86}{92}\selectfont 힘뇌장',
                        r'\fontsize{60}{66}\selectfont 힘뇌장')
    head = head.replace(r'{\sffamily\LARGE\color{celadondk}\addfontfeature{LetterSpace=26} HIMNOEJANG}',
                        r'{\sffamily\Large\color{celadondk}\addfontfeature{LetterSpace=14} HIMNOEJANG}')
    head = head.replace(r'{\large\color{ink} 전통과 현대를 잇는 장-뇌 설계 — 열두 원료, 하나의 계(系)}',
                        r'{\normalsize\color{ink} 전통과 현대를 잇는 장-뇌 설계 — 열두 원료, 하나의 계(系)}')
    head = head.replace(r'\addfontfeature{LetterSpace=18} GUT–BRAIN AXIS MONOGRAPH',
                        r'\addfontfeature{LetterSpace=10} GUT–BRAIN AXIS MONOGRAPH')
    return head


def main():
    tex = open(BASE_TEX, encoding='utf-8').read()
    head = transform_head(tex[:tex.index('%% ===== 서문 =====')])
    tail = tex[tex.index('\\backmatter'):]

    parts = [head.rstrip() + '\n\n', '%% ===== 서문 =====\n\n']
    parts.append(render(PREFACE, 'preface'))
    parts.append('\n\n\\clearpage\n\\tableofcontents\n\\clearpage\n\n\\mainmatter\n\\pagestyle{fancy}\n\n')
    for k, ch in enumerate(CHAPTERS, 1):
        parts.append('\n%%%%%% CH %d %%%%%%\n\n' % k)
        parts.append(render(ch, 'chapter'))
        parts.append('\n')
    parts.append('\n%% ===== 부록 (Appendices) =====\n\n')
    for ap in APPENDICES:
        parts.append(render(ap, 'appendix'))
        parts.append('\n')
    parts.append('\n' + tail)

    with open(OUT_TEX, 'w', encoding='utf-8') as f:
        f.write(''.join(parts))

    body = ''.join(parts)
    print("생성:", OUT_TEX)
    print("  \\chapter  :", body.count('\\chapter{') + body.count('\\chapter*{'))
    print("  \\section  :", body.count('\\section{') + body.count('\\section*{'))
    print("  \\subsection:", body.count('\\subsection{'))
    print("  \\reff     :", body.count('\\reff{'))
    print("  tabularx  :", body.count('\\begin{tabularx}'))
    print("  authnote  :", body.count('\\begin{authnote}'))


if __name__ == "__main__":
    main()
