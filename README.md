# 힘뇌장 (HIMNOEJANG) Scientific Monograph Project

**저자:** 최성화 박사 (서울대 생명과학부 · ㈜지플러스생명과학 대표)
**저장소:** C:\hnj-mgf
**시작:** 2026-07-16
**목표 완간:** 2028-07 (24개월)

## 프로젝트 개요

힘뇌장(HIMNOEJANG)의 배합 설계 철학(Design Rationale)을 학술 모노그래프(Scientific Monograph)로 집대성한다.
- 서명: **「힘뇌장: 장-뇌축을 기반으로 설계된 한국형 기능성 포뮬러의 과학」**
- 벤치마크: Nature Reviews · Physiological Reviews · Annual Review 급
- 분량: 350-500 페이지 · 15 챕터 · 참고문헌 800-1,200편

## 폴더 구조

```
C:\hnj-mgf\
├── .claude/skills/           ← 4개 Custom Skills (chapter-drafter · reference-validator · historical-verifier · chapter-editor)
├── prompts/                  ← 마스터 프롬프트 v2.0
├── chapters/                 ← 원고 Markdown 15개 챕터
├── references/               ← BibTeX · 검증 로그 · Whitelist/Blacklist
├── figures/                  ← 도판 원본 · 최종
├── scripts/                  ← Python 자동화 (verify_doi.py 등)
├── output/                   ← PDF · DOCX · HTML 빌드
└── README.md                 ← 본 파일
```

## 4개 Skill 개요

| Skill | 목적 | 예상 소요 |
|---|---|---|
| **chapter-drafter** | 챕터 15섹션 초고 생성 (40-50p) | 3-5시간 |
| **reference-validator** | DOI 4단계 검증 · Anti-Hallucination | 1-2일 |
| **historical-verifier** | 조선 사료 원전 국가 DB 검증 | 반나절-1일 |
| **chapter-editor** | 최종 편집 · KFDA 준수 · 톤 통일 | 1-2일 |

## 챕터별 워크플로우 (5단계 · 4-6주)

```
1. 사전 리서치 (Deep Research Agent) · 1-2주
   ↓
2. chapter-drafter 실행 · 3-5일
   ↓
3. reference-validator 실행 · 1-2일
   ↓
4. historical-verifier 실행 (해당 시) · 1-2일
   ↓
5. chapter-editor + 저자 검토 · 1-2주
   ↓
Git commit · 다음 챕터
```

## Chapter 15개 목차

### Part I · 서장 (Prologue)
- Ch 1 · 총론 · 왜 이 책인가
- Ch 2 · 조선시대 · 이순신 장군 사례
- Ch 3 · 장-뇌축 재발견 · Cryan 2019까지

### Part II · 사군자탕 4원료 (Foundation)
- Ch 4 · 인삼 (Panax ginseng)
- Ch 5 · 백출 (Atractylodes)
- Ch 6 · 복령 (Poria)
- Ch 7 · 감초 (Glycyrrhiza)

### Part III · Gut-Brain 특화 (Gut & Brain)
- Ch 8 · 노루궁뎅이버섯 (Hericium erinaceus)
- Ch 9 · 법제 원지 (Polygala tenuifolia)
- Ch 10 · L-테아닌 (L-Theanine)

### Part IV · 기능성 보조 (Cognition & Resilience)
- Ch 11 · L-티로신
- Ch 12 · L-글루타민
- Ch 13 · 커큐민
- Ch 14 · FOS · 팔라티노스

### Part V · 종장 (Epilogue)
- Ch 15 · 힘뇌장 통합 · 시너지 · 미래

## 시작 명령 예시

```bash
$ cd C:\hnj-mgf
$ git init
$ git add .
$ git commit -m "Initial project structure with 4 skills"
$ claude

  > "Chapter 10 L-Theanine을 마스터 프롬프트 v2.0에 따라
    ① 사전 리서치 (100편)
    ② 초고 드래프팅 (15섹션 40-50p)
    ③ 참고문헌 DOI 검증
    ④ 사료 검증
    ⑤ 편집
    순서로 진행. 각 단계 저자 승인 후 다음."
```

## Anti-Hallucination · 필수 준수

1. Blacklist 원천 배제 (블로그·상품·유튜브·Wikipedia·AI 응답 등 10종)
2. DOI 4단계 검증 통과 인용만 `[DOI-VERIFIED ✓]` 태그
3. 조선 사료 국가 DB 확인 필수
4. KFDA 표시광고법 준수 (치료·예방·완치 어사 금지)

## Git 브랜치 전략

```
main                    ← 검증 완료된 챕터만
├── ch01-introduction
├── ch02-joseon-yi-sunsin
├── ch03-gut-brain-history
├── ch04-ginseng
└── ...
```

각 챕터는 별도 브랜치에서 진행 · 저자 승인 후 main 병합.

## 예산 · 팀 (기본 시나리오 · 2억 8천만원 · 24개월)

- 주 저자: 최성화 교수
- 공저자: 한의학사 전문가 + Gut-brain axis 학자
- 리서치 어시스턴트: 2-3명
- 편집자: 학술 + 대중 이중
- 의학 일러스트레이터: 1-2명

## 참고 문헌

- Cryan JF et al. (2019). The Microbiota-Gut-Brain Axis. Physiol Rev 99:1877-2013.
- 마스터 프롬프트 v2.0: `prompts/master-prompt-v2.0.md`
- 힘뇌장 8차 시제품 의뢰서 V4.0
- ㈜지플러스생명과학 특허 6개 청구항
