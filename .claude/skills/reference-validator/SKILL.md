---
name: reference-validator
description: 원고 파일(Markdown)의 모든 학술 논문 인용을 CrossRef API와 PubMed E-utilities API로 4단계 검증한다. DOI 존재 · 제목 완전 일치 · 저자·저널·연도 교차 확인 · 원문 내용 확인의 4단계를 통과한 인용에만 [DOI-VERIFIED YYYY-MM-DD ✓] 태그를 부착하고, 실패한 인용은 [VERIFY-FAILED] 태그와 실패 이유를 표기한다. Hallucination(존재하지 않는 논문) 원천 차단. 사용자가 "Chapter X 참고문헌 검증" 또는 "reference-validator 실행" 등을 요청할 때 발동한다.
---

# reference-validator · 참고문헌 DOI 검증 스킬

## 목적

원고 파일 내 모든 학술 논문 인용을 CrossRef · PubMed API로 4단계 검증하여 hallucination을 원천 차단하고 신뢰성을 확립한다.

## 언제 발동하는가

- "Chapter 10 참고문헌 검증"
- "reference-validator로 ch10.md 검증"
- "DOI 검증 실행"
- "인용 문헌 실체 확인"
- chapter-drafter 완료 직후 자동 연쇄 실행

## 입력 (Inputs)

- **file_path**: 검증할 원고 Markdown 파일 (예: `chapters/ch10-theanine.md`)
- **whitelist** (선택): `references/whitelist-journals.txt` 참조
- **blacklist** (선택): `references/blacklist-sources.txt` 참조

## 산출물 (Outputs)

- **검증 태그 부착 원고**: 각 인용에 `[DOI-VERIFIED YYYY-MM-DD ✓]` 또는 `[VERIFY-FAILED - {reason}]`
- **검증 리포트**: `references/validation-log-ch{N}-{YYYY-MM-DD}.csv`
- **실패 목록**: 저자에게 별도 보고 (대체 논문 제안 요청)

## 4단계 검증 프로세스

### Stage 1 · DOI 존재 확인
```
For each citation:
  1. Extract DOI from citation (regex: 10\.\d{4,}/[\S]+)
  2. HTTP GET https://api.crossref.org/works/{DOI}
  3. If response != 200: mark [VERIFY-FAILED - DOI-NOT-FOUND]
```

### Stage 2 · 제목 완전 일치 검증 (★ Anti-Hallucination 핵심)
```
  4. Get returned paper.title from CrossRef response
  5. Compute string similarity with cited title (fuzzy match, e.g. Levenshtein)
  6. If similarity < 0.95: mark [VERIFY-FAILED - TITLE-MISMATCH]
     ★ This is the strongest anti-hallucination signal.
     If AI generated a fake paper, DOI likely won't match title.
```

### Stage 3 · 저자·저널·연도 교차 확인
```
  7. Compare paper.author[0].family with citation.author.family
  8. Compare paper['container-title'][0] with citation.journal
  9. Compare paper.issued.date-parts[0][0] with citation.year
  10. If any mismatch: mark [VERIFY-FAILED - METADATA-MISMATCH]
```

### Stage 4 · PubMed 교차 확인 (의학·생물학 논문 필수)
```
  11. Query PubMed E-utilities esearch with paper title
  12. Retrieve PMID
  13. Verify PMID matches citation.pmid
  14. If categorical mismatch: mark [VERIFY-FAILED - PMID-MISMATCH]
```

### 최종 · 검증 통과 처리
```
  15. If all 4 stages pass:
      Replace [PENDING-DOI-VERIFY] with [DOI-VERIFIED YYYY-MM-DD ✓]
  16. Log to references/validation-log-ch{N}.csv
```

## Whitelist · 허용 저널 (Tier 1-5)

**Tier 1 · 최상위:**
Nature (all subseries) · Science · Cell · NEJM · Lancet · JAMA · BMJ · PNAS · Physiological Reviews

**Tier 2 · 분야 최상위:**
Gut · Gastroenterology · Molecular Psychiatry · Brain Behavior Immunity · Nutrients · American Journal of Clinical Nutrition · Journal of Neuroscience

**Tier 3 · Peer-review 확립:**
Elsevier · Springer Nature · Wiley · ACS · Cell Press · PLOS · MDPI (peer-reviewed) · Frontiers · Taylor & Francis · SAGE

**Tier 4 · 국내 학술:**
KJIM · Journal of Ginseng Research · Korean J Physiol Pharmacol · 대한한의학회지 · 한국식품과학회지 · Journal of Korean Medical Science

**Tier 5 · 시스템 리뷰:**
Cochrane Library · Campbell Collaboration · JBI Reviews · PROSPERO 등록

## Blacklist · 절대 배제 (즉시 [VERIFY-FAILED])

1. 개인 블로그 · Naver blog · Tistory · WordPress
2. 브랜드 상품 페이지 · 쿠팡 · Amazon
3. WebMD · Healthline · 헬스조선 · 코메디닷컴
4. Wikipedia (배경 확인은 허용하되 인용 각주 금지)
5. 기업 백서 · 마케팅 자료
6. 유튜브 · Podcast (본인 학자 강연 제외)
7. 뉴스 기사 (원 논문 인용)
8. ChatGPT · Perplexity 등 AI 응답
9. Predatory Journals (Beall's List 등재)
10. 미출판 원고 (Preprint는 명시 하에 제한 허용)

## 실행 명령 (Python 스크립트 호출)

```bash
python scripts/verify_doi.py \
    --file chapters/ch10-theanine.md \
    --output references/validation-log-ch10.csv \
    --update-in-place
```

또는 자연어:
```
"Chapter 10 참고문헌 검증"
"reference-validator로 ch10.md 검증하고 실패 목록 알려줘"
```

## 검증 리포트 형식 (validation-log-ch{N}.csv)

```csv
citation_id,doi,title,verified,failure_reason,timestamp
[1],10.1152/physrev.00018.2018,"The Microbiota-Gut-Brain Axis",TRUE,,2026-07-16T14:30
[2],10.1234/fake.2019,"Fake Paper Title",FALSE,TITLE-MISMATCH,2026-07-16T14:30
[3],10.1038/s41586-2020-xxx,"Author Real Title",TRUE,,2026-07-16T14:30
```

## Preprint 특별 처리

- bioRxiv · medRxiv · ChemRxiv 등 preprint는 다음 조건에 한해 허용:
  1. `[PREPRINT]` 태그 명시 부착
  2. 명확한 경고 문구 병기
  3. 정식 출판 확인 시 자동 정식 인용으로 대체
  4. Chapter당 최대 5편 이하

## Blacklist URL 자동 검출

인용에 다음 URL 패턴이 포함되면 즉시 [VERIFY-FAILED]:
- `blog.naver.com` · `.tistory.com` · `wordpress.com`
- `webmd.com` · `healthline.com` · `health.chosun.com`
- `amazon.com/*/dp/*` · `coupang.com/*/products/*`
- `wikipedia.org` (직접 인용만)
- `youtube.com/watch` · `podcasts.apple.com`

## 저자 대응 · 실패 시

검증 실패 인용 목록을 저자(최성화 교수)에게 다음 형식으로 보고:

```
Chapter 10 참고문헌 검증 결과:

검증 완료: 62/68
검증 실패: 6

실패 인용 목록:
[1] "Fake Study on L-Theanine Miracle Effects" 
    - DOI 존재하지 않음 · Hallucination 의심
    - 조치: 대체 논문 필요
    
[2] "Kim JH et al. 2019 · Naver 블로그"
    - Blacklist 소스 (블로그)
    - 조치: 학술 논문으로 대체

대체 논문 자동 제안하겠습니까? (y/n)
```

## 예상 소요

- 챕터당 60-100편 인용 검증: 1-2일
- API 호출: 인용당 3-5초 · 총 5-10분 (자동)
- 대체 논문 재검색·확인: 저자 승인 필요

## 다음 스킬 연결

검증 완료 후 사용자에게 알림:
> "Chapter {N} 참고문헌 검증 완료. 검증률 {N}%. 다음으로 historical-verifier 실행하시겠습니까?"
