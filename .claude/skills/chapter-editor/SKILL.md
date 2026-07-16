---
name: chapter-editor
description: 챕터 원고의 최종 편집을 수행한다 · KFDA 표시광고법 준수 확인(치료/예방/완치 어사 배제) · 학술 용어 일관성 · 저자(최성화 교수) 톤 유지 · 인용 형식 표준화 · 챕터 헤더 필드 갱신 · 학술 편집자 시각의 스타일 통일. reference-validator와 historical-verifier 완료 후 마지막 단계로 실행한다. 사용자가 "Chapter X 편집" 또는 "chapter-editor 실행" 등을 요청할 때 발동한다.
---

# chapter-editor · 최종 편집 스킬

## 목적

챕터 원고를 학술 출판 수준으로 다듬는다. 규제 준수 · 톤 통일 · 인용 형식 · 챕터 간 일관성을 확보한다.

## 언제 발동하는가

- "Chapter 10 편집"
- "chapter-editor 실행"
- "최종 편집 · 스타일 통일"
- reference-validator + historical-verifier 완료 직후 자동 연쇄

## 입력 (Inputs)

- **file_path**: 편집할 원고 (예: `chapters/ch10-theanine.md`)
- **style_guide**: `prompts/style-guide.md` (참조)
- **glossary**: `references/glossary.md` (용어 사전)

## 산출물 (Outputs)

- **편집된 원고**: 원본 파일 in-place 수정 (또는 `.edited.md` 별도 저장)
- **편집 로그**: `references/edit-log-ch{N}-{YYYY-MM-DD}.md`
- **저자 검토 요청**: 주요 변경 사항 저자에게 보고

## 편집 프로세스 (6단계)

### Stage 1 · KFDA 표시광고 규제 준수

**금지 표현 자동 검색·대체:**

| 금지 (Ban) | 대체 (Replace) | 이유 |
|---|---|---|
| "치료한다" | "관련성이 보고되었다" | 의약품 효능 어사 |
| "예방한다" | "지원 가능성이 시사된다" | 질병 예방 표방 |
| "완치" | "개선 · 관련 근거" | 완치 주장 금지 |
| "특효" | "효과가 관찰되었다" | 과장 |
| "OO에 좋다" | "OO 관련 연구가 보고되었다" | 근거 수준 |
| "머리가 좋아진다" | "인지 기능 지원 가능성" | 소비자 오인 |
| "치매 예방" | "인지 기능 유지 관련 연구" | 질병 예방 금지 |
| "우울증 치료" | "스트레스 완화 관련 근거" | 의약품 표방 |
| "임상적으로 입증" | "임상 연구가 보고되었다" | 오인 방지 |

★ 특히 힘뇌장은 일반식품이므로 건강기능식품 오인 표현도 배제

### Stage 2 · 학술 용어 통일

**Glossary 참조 (예시):**
- gut-brain axis / 장-뇌축 / 腸-腦軸 (3중 표기 유지)
- microbiota / 미생물총 (microbiome과 구분)
- Cryan 2019 (Cryan et al. 2019 · Cryan JF et al. 2019 등 통일)
- 사군자탕 / 四君子湯 / Sagunjatang (3중 표기)
- SCFA / short-chain fatty acid / 단쇄지방산

### Stage 3 · 저자 톤 유지

**최성화 교수 서술 스타일 특징:**
- 학술적이면서도 서사적
- 서울대 학생 관찰 · 조선 사료 · 현대 논문 3중 결합
- 겸손한 표현 · 과장 배제
- 한국인 정체성 강조 (K-보약 · K-Wellness 서사)
- 인간적 관찰의 순간을 논리 시작점으로 활용

**AI가 개입할 수 있는 부분:**
- 문법 · 어색한 문장
- 반복 · 중복 표현
- 용어 통일
- 인용 형식

**AI가 개입해서는 안 되는 부분:**
- 저자의 논지 · 관점 · 서사
- 서울대 학생 에피소드 · 조선 일화 (원본 유지)
- 특허 청구항 · 배합 정당화 논리

### Stage 4 · 인용 형식 표준화

**본문 인용:** 
- Vancouver style (숫자 대괄호): "SCFA는 HPA 축을 정상화한다 [12]"
- APA 스타일 (저자·연도): "Cryan et al. (2019)에 따르면..."
- 한 챕터 내 스타일 통일 필수

**참고문헌 목록:**
```
[1] Cryan JF, O'Riordan KJ, Cowan CSM, et al. 
    The Microbiota-Gut-Brain Axis. 
    Physiological Reviews. 2019;99(4):1877-2013. 
    doi:10.1152/physrev.00018.2018. 
    PMID:31460832. 
    URL: https://doi.org/10.1152/physrev.00018.2018. 
    [DOI-VERIFIED 2026-07-16 ✓]
```

### Stage 5 · 챕터 헤더 필드 갱신

```
# Chapter {N} · {한글 원료명} ({학명})

저자: 최성화 (서울대학교 생명과학부)
공저자: {실제 공저자}
참고문헌: 총 {N}편 · 검증 완료 {N}편 · [PENDING] 0편
최종 검증 실행일: {YYYY-MM-DD}
사료 검증 완료: {YYYY-MM-DD}
AI 초안: Claude Sonnet 4.5 · chapter-drafter v1.0
편집: chapter-editor v1.0 · {YYYY-MM-DD}
저자 검토: [ ] 미완료 (편집 후 저자 최종 승인 필요)
```

### Stage 6 · 챕터 간 일관성 확인

- Cross-reference 확인: "Chapter 6의 5.2에서 언급한 바와 같이..."
- 용어 통일 (전 챕터 참조)
- 인용 번호 중복 확인
- 부록 · 인덱스 반영

## Edit Log 형식

```markdown
# Edit Log · Chapter 10 · L-Theanine · 2026-07-16

## KFDA 규제 준수 (12건 수정)
- Line 245: "치료한다" → "관련성이 보고되었다"
- Line 312: "머리가 좋아진다" → "인지 기능 지원 가능성"
- ...

## 용어 통일 (8건)
- Line 156: "장뇌축" → "장-뇌축"
- Line 234: "Cryan et al 2019" → "Cryan et al. (2019)"
- ...

## 인용 형식 표준화 (전체)
- 참고문헌 목록 정렬: 인용 순서
- 저자 형식 통일: LastName FirstInitial

## 저자 승인 필요 사항
- Line 89: 조선 사례 서술이 다소 감정적 → 톤 조정 제안
- Line 456: L-테아닌 250mg 근거 표현이 다소 강함 → 완화 제안

편집자: chapter-editor v1.0 · Claude Sonnet 4.5
검토 필요: 최성화 교수
```

## 실행 명령

```bash
python scripts/edit_chapter.py \
    --file chapters/ch10-theanine.md \
    --style-guide prompts/style-guide.md \
    --glossary references/glossary.md \
    --output-log references/edit-log-ch10.md
```

자연어:
```
"Chapter 10 편집 실행"
"chapter-editor로 ch10.md · 저자 톤 유지 · KFDA 준수"
```

## 저자 검토 게이트

편집 완료 후 반드시 저자(최성화 교수) 승인 필수. 다음 사항 저자 확인:
1. 서사 · 관점 · 논지 훼손 여부
2. 조선 사례 · 서울대 에피소드 원본 유지
3. 특허 · 배합 정당화 논리 정확성
4. 최종 서명 · Chapter Header 저자 검토 필드 갱신

## 예상 소요

- 챕터당 편집: 1-2일 (자동 반나절 + 저자 검토 1일)
- 저자 서명 후 Git commit

## 완료 시 알림

```
Chapter {N} 편집 완료 · 최종 승인 대기.

편집 요약:
- KFDA 규제 수정: {N}건
- 용어 통일: {N}건
- 인용 형식 표준화 완료
- 저자 승인 필요 사항: {N}건 (edit-log-ch{N}.md 참조)

저자(최성화 교수)의 최종 검토를 요청합니다.
승인 후 git commit 실행:
$ git add chapters/ch{N}-topic.md
$ git commit -m "Chapter {N} · {topic} · Final Approved"
```
