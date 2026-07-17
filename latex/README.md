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
