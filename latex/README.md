# 힘뇌장 · 표지 + 서문 (LaTeX)

`himnoejang-cover-preface.tex` — 힘뇌장 모노그래프의 **표지(Cover) + 서문(Preface)** 조판.

- **판형:** 신국판 **152 × 225 mm** (`geometry`로 지정)
- **엔진:** **XeLaTeX 필수** (한글 조판 · `kotex`/`fontspec`). pdfLaTeX로는 컴파일되지 않음.
- **구성:** 1면 표지(청자색 좌측 띠 + 낙관 印) → 서문 2~3면
- **디자인:** 청자(靑瓷) 정체성 — 청자 녹색 `#2F6F5E` · 먹빛 `#1B2320` · 낙관 주사 `#B23A2E`

## 컴파일 방법

### A) Overleaf (권장 · 설치 불필요, 기본값으로 바로 됨)
1. Overleaf에 `himnoejang-cover-preface.tex` 업로드
2. **Menu → Compiler → XeLaTeX** 로 설정
3. Recompile — 기본 폰트(나눔명조/나눔고딕 + TeX Gyre)로 바로 출력됨

### B) 로컬 (Windows · MiKTeX 또는 TeX Live)
1. `.tex` 상단 **폰트 블록**에서 "기본(Overleaf)" 4줄을 주석 처리하고, "윈도우 로컬용" 4줄(바탕·맑은 고딕·Times New Roman·Arial)의 주석을 해제
2. 명령:
   ```
   xelatex himnoejang-cover-preface.tex
   xelatex himnoejang-cover-preface.tex
   ```
   (배경/버전 참조 안정화를 위해 2회 실행 권장)

## 폰트 교체 지점
`.tex` 파일 상단 `폰트` 섹션의 `\setmainhangulfont`/`\setsanshangulfont`/`\setmainfont`/`\setsansfont`만 바꾸면 됨.
- 본문 한글: 명조 계열(나눔명조 / 바탕) · 제목·표지: 고딕 계열(나눔고딕 / 맑은 고딕)

## 산출물
`himnoejang-cover-preface.pdf` — 표지 1면 + 서문 2~3면 (신국판)

---

# 단행본 전체 (46배판 188 × 257 mm)

`himnoejang-book.tex` — **표지 + 서문 + 목차 + 15장 전체**를 담은 단행본 조판.

- **판형:** 46배판 **188 × 257 mm**
- **엔진:** **XeLaTeX 필수** (book class · kotex)
- **구성:** 표지 → 서문 → **목차(자동 · 장·절 시작 쪽번호 포함)** → 제1~15장(각 참고문헌 포함)
- **목차 쪽번호:** `\tableofcontents`로 자동 생성 — latexmk가 여러 번 컴파일하며 쪽번호를 확정(Overleaf는 자동)

## Overleaf 업로드용 zip
`himnoejang-book-overleaf.zip` (himnoejang-book.tex + latexmkrc)
1. Overleaf → **New Project → Upload Project** → 이 zip 선택
2. **Menu → Compiler → XeLaTeX** (새 프로젝트는 기본 pdfLaTeX이므로 반드시 변경)
3. **Recompile** — 목차 쪽번호가 자동으로 채워짐(2~3회 자동 재실행)

## 참고
- 폰트 기본값은 Nanum(+한자). 한자·기호(→ ★ ① 등)가 비면 `.tex` 상단 폰트 블록을 **Noto CJK**(주석 제공)로 교체.
- 양면 인쇄용 판짜기를 원하면 `\documentclass[11pt,oneside]{book}` 의 `oneside`를 `twoside`로 변경.

---

# 단행본 전체 · 윤문본 v1 (신국판 152 × 225 mm)

`himnoejang-book-v1.tex` — 최성화 스타일(sunghwa-scistyle)로 윤문한 **v1 원고** 전체(서문 + 15장 + 부록 A·B)를 담은 단행본 조판. `scripts/md_to_latex.py`가 v1 마크다운에서 자동 생성한다.

- **판형:** 신국판 **152 × 225 mm** (46배판 대비 소형 단행본)
- **엔진:** **XeLaTeX 필수** (book class · kotex)
- **구성:** 표지 → 서문 → 목차 → 제1~15장(각 참고문헌 826편) → 부록 A·B
- **가독성 타이포그래피:** 본문 **12pt · 줄간격 1.38** / 참고문헌 **8.5pt · 줄간격 10.2pt**(본문보다 작고 촘촘) / 표 `scriptsize`(컴팩트)
- **오버플로 점검 완료:** tectonic(XeTeX) 컴파일 결과 Overfull \hbox **0건** — 좁은 판폭에 맞춰 여백 재계산, 긴 URL·맨눈 도메인 `\url` 줄바꿈, 표지 글자 크기 축소, `emergencystretch` 여유 적용.

## Overleaf 업로드용 zip
`himnoejang-book-v1-overleaf.zip` (himnoejang-book-v1.tex + latexmkrc)
1. Overleaf → **New Project → Upload Project** → 이 zip 선택
2. **Menu → Compiler → XeLaTeX** (반드시 변경)
3. **Recompile** — 목차 쪽번호 자동 확정

## 재생성
```
python scripts/md_to_latex.py     # chapters/ch*-v1.md + appendices → latex/himnoejang-book-v1.tex
```
