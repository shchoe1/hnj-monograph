---
name: chapter-drafter
description: 힘뇌장 모노그래프의 한 챕터(원료 리뷰) 초고를 마스터 프롬프트 v2.0의 15섹션 표준 템플릿에 따라 40-50페이지 분량으로 드래프팅한다. Chapter 4~14의 각 원료(인삼·백출·복령·감초·노루궁뎅이·원지·L-테아닌·L-티로신·L-글루타민·커큐민·FOS·팔라티노스)에 사용한다. 사용자가 "Chapter [X] [원료명] 초고 작성해줘" 또는 "chapter-drafter로 [원료] 챕터 드래프팅" 등을 요청할 때 발동한다.
---

# chapter-drafter · 챕터 드래프팅 스킬

## 목적

힘뇌장(HIMNOEJANG) 모노그래프의 한 챕터(약재/첨가물 리뷰)를 마스터 프롬프트 v2.0의 **15섹션 표준 템플릿**에 따라 40-50페이지 분량 초고로 생성한다.

## 언제 발동하는가

- "Chapter 4 인삼 초고 작성해줘"
- "chapter-drafter로 L-테아닌 챕터 드래프팅"
- "Chapter 8 노루궁뎅이버섯을 마스터 프롬프트로 만들어줘"
- "Ch 9 · 원지 · 40-50 페이지"

## 입력 (Inputs)

- **chapter_num**: 챕터 번호 (예: 10)
- **topic**: 원료명 (예: "L-Theanine" · "인삼" · "노루궁뎅이버섯")
- **master_prompt**: `prompts/master-prompt-v2.0.md` (참조)
- **research_bib** (선택): 사전 리서치된 참고문헌 파일 (`references/ch{N}.bib`)

## 산출물 (Outputs)

- **초고 파일**: `chapters/ch{NN}-{topic-slug}.md` (Markdown · 40-50p 상당)
- **인용 리스트**: 원고 하단에 모든 인용을 8개 필드 표준 형식으로 나열
- **초기 검증 태그**: 각 인용에 `[PENDING-DOI-VERIFY]` 태그 부착 (reference-validator가 이후 검증)

## 15섹션 표준 템플릿 (반드시 순서 준수)

각 섹션 목적·분량·필수 인용 요건은 아래와 같이 준수한다.

1. **내러티브 프롤로그** (1-2p) — 스토리 도입 · 조선/이순신/서울대 학생 에피소드
2. **역사적 배경** (3-5p) — 동의보감·향약집성방·본초강목·상한론·금궤요략 인용 [historical-verifier 검증 대상]
3. **힘뇌장 포함 이유 (Design Rationale)** (2-3p) — 가장 중요한 섹션 · 저자 논증 중심
4. **전통의학적 의미** (3-4p) — 기미·귀경·효능·주치·비위·간·심·신·GBA 연결
5. **현대 약리 기전** (5-7p) — 세포·분자·수용체·Signal pathway · 모든 인용 Tier 1-3 저널만
6. **장-뇌축(Gut-Brain Axis) 관점 · Cryan 2019 매핑** (4-6p) — Cryan 페이지 인용 필수
7. **동물실험** (3-4p) — 최신 연구 · PMID 필수
8. **인체 임상** (4-6p) — RCT · Meta · Cochrane 우선 · 검증 최엄격
9. **안전성** (2-3p) — NOAEL · 상호작용 · FDA/MFDS URL 필수
10. **힘뇌장 역할** (2-3p) — Core/Supporting/Synergistic 분류
11. **시너지** (2-3p) — 8종 원료 상호작용
12. **한국인의 지혜** (1-2p) — 자생·전통·문화
13. **근거 수준 (GRADE)** (1p) — ★☆~★★★★★ 등급화
14. **미래 관점** (1-2p) — 임상시험·Biomarker·Omics·AI nutrition
15. **핵심 요약** (1p · 10줄 이내) — "힘뇌장 설계 철학 관점의 존재 이유"

## 챕터 헤더 필수 필드

```
# Chapter {N} · {한글 원료명} ({학명})

저자: 최성화 (서울대학교 생명과학부)
공저자: [해당 시]
참고문헌: {N}편 · 검증 완료 {N}편 · [PENDING] {N}편
최종 검증 실행일: [reference-validator 실행 후 자동 갱신]
AI 초안 도구: Claude Sonnet 4.5 · chapter-drafter Skill v1.0
저자 검토: [ ] 미완료
```

## 인용 형식 (8개 필드 표준)

```
[1] Author FirstAuthor et al. Full Title Exactly As Published. 
    Journal Name (not abbreviated). Year;Vol(Issue):StartPage-EndPage. 
    doi:10.xxxx/xxxxx. PMID:xxxxxxxx. 
    URL: https://doi.org/10.xxxx/xxxxx. 
    [PENDING-DOI-VERIFY]
```

조선 사료 인용:
```
[H1] 저자. 서명. 편명·권명. 연도. 페이지(국역본 기준). 
     소장처: 국립현충사/규장각/KTKP DB. 
     URL: https://sillok.history.go.kr/... 
     [PENDING-HISTORICAL-VERIFY]
```

## 실행 프로세스 (5단계)

### 단계 1 · 사전 리서치 (선택)
`references/ch{N}.bib`가 없으면 Task 도구로 Deep Research 서브에이전트를 발동:
- Tier 1-3 저널 최근 10년 논문 100-150편 수집
- 조선 사료 원전 5-20편 발췌
- `references/ch{N}.bib` 저장

### 단계 2 · 섹션별 순차 드래프팅
15개 섹션을 순서대로 작성. 각 섹션마다:
1. 마스터 프롬프트 v2.0 해당 사양 준수
2. Tier 1-3 저널만 인용 (Blacklist 절대 금지)
3. 8개 필드 표준 형식
4. `[PENDING-DOI-VERIFY]` 태그 부착

### 단계 3 · 챕터 헤더 자동 생성

### 단계 4 · 참고문헌 목록 통합
학술 논문 · 조선 사료 두 섹션 나누어 정리

### 단계 5 · 파일 저장
`chapters/ch{NN}-{topic-slug}.md`

## Anti-Hallucination · 필수 준수

- ❌ 존재 확인 안 된 논문·저자·DOI 절대 생성 금지
- ❌ 블로그·상품 광고·WebMD·Wikipedia 직접 인용 금지
- ❌ 소설·드라마 (예: KBS '불멸의 이순신') 인용 금지
- ❌ "치료"·"예방"·"완치" 등 의약품 효능 어사 금지
- ✅ 확신 없는 인용 `[UNCERTAIN]` 태그 · 저자 알림
- ✅ 각 챕터 말미 "힘뇌장 설계 철학" 한 문단 정리
- ✅ 근거 수준 표현: "관련성이 보고되었다" · "지원할 가능성"

## 예시 명령

```bash
# 자연어 요청
"Chapter 10 L-Theanine을 마스터 프롬프트 v2.0에 따라 초고 작성해줘"

# 사전 리서치 지정
"chapter-drafter로 Chapter 8 노루궁뎅이 · references/ch8.bib 사용"
```

## 예상 소요

- 사전 리서치 있을 때: 3-5시간
- 사전 리서치 필요 시: 5-8시간 (Deep Research 포함)

## 다음 스킬 연결

초고 완성 후 사용자에게 알림:
> "Chapter {N} 초고 완성. 다음으로 reference-validator를 실행하시겠습니까?"
