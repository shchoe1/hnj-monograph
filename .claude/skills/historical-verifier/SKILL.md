---
name: historical-verifier
description: 원고 내 조선시대 사료 인용(동의보감·향약집성방·본초강목·상한론·금궤요략·난중일기·조선왕조실록·승정원일기 등)의 원전 정확성을 국가 DB(국사편찬위원회·규장각·한국한의학연구원 KTKP·국립현충사)에서 크로스체크한다. 이순신 관련 인용은 소설·드라마 배제하고 원본 확인 필수. 사용자가 "Chapter 2 사료 검증" 또는 "historical-verifier 실행" 등을 요청할 때 발동한다.
---

# historical-verifier · 조선 사료 원전 검증 스킬

## 목적

원고 내 조선시대·전근대 한의학 사료 인용의 원전 정확성을 국가 DB에서 검증하여 역사 왜곡 · 소설/드라마 오인용 · 허구 창작을 원천 차단한다.

## 언제 발동하는가

- "Chapter 2 사료 검증"
- "이순신 인용 원전 확인"
- "동의보감 인용 검증"
- "historical-verifier 실행"
- chapter-drafter 완료 시 (Chapter 1-4 특히) 자동 연쇄 실행

## 입력 (Inputs)

- **file_path**: 검증할 원고 Markdown 파일
- **sources_db**: `references/historical-sources.bib`
- **approved_dbs**: 아래 5개 국가 DB URL 리스트

## 산출물 (Outputs)

- **검증 태그 부착 원고**: `[HISTORICAL-VERIFIED YYYY-MM-DD ✓]` 또는 `[VERIFY-FAILED - {reason}]`
- **원문 발췌 리포트**: `references/historical-verification-ch{N}-{YYYY-MM-DD}.md`
- **원전 URL 목록**: 각 인용마다 국가 DB URL 첨부

## 허용 원전 소스 (Whitelist)

### Tier 1 · 국가 공식 DB

| 사료 | DB · URL | 확인 필수 |
|---|---|---|
| **조선왕조실록** | 국사편찬위원회 · https://sillok.history.go.kr | 왕대·연월일·URL |
| **승정원일기** | 국사편찬위원회 · https://sjw.history.go.kr | 일자·URL |
| **한국사데이터베이스** | https://db.history.go.kr | URL |
| **규장각 원문검색** | https://kyudb.snu.ac.kr | 청구기호·URL |

### Tier 2 · 한의학 전문 DB

| 사료 | DB · URL |
|---|---|
| **동의보감** | 한국한의학연구원 KTKP · http://www.oasis.kiom.re.kr |
| **향약집성방** | KTKP · 국역본 (남산당·법인문화사) |
| **본초강목** | 국역본 · Cambridge University Press (Metailie 역주) |
| **의방유취 · 의림촬요** | KTKP · 규장각 |

### Tier 3 · 이순신 관련 특별 DB

| 사료 | DB · URL |
|---|---|
| **난중일기** | 국립현충사 · http://hcs.chungmugong.go.kr |
| **이충무공전서** | 규장각 · 한국고전번역원 https://db.itkc.or.kr |
| **선조실록** | 국사편찬위원회 (임진왜란 관련) |

### Tier 4 · 학술 번역·연구

- 한국고전번역원 · https://db.itkc.or.kr (원전+국역)
- 국역본 (남산당·법인문화사·한의문화사·명문당 등)
- Peer-review 한의사학 논문 (KJIM · Journal of Korean Medicine 등)

## 절대 배제 (Blacklist)

- ❌ 소설: 김훈 「칼의 노래」 · 최인훈 등 문학 작품
- ❌ 드라마: KBS '불멸의 이순신' · SBS · 각종 사극
- ❌ 영화: '명량' · '한산: 용의 출현' · '노량: 죽음의 바다'
- ❌ 유튜브 사학 채널 (개인 블로거 수준)
- ❌ 나무위키 · 위키피디아 (배경 확인 허용 · 인용 각주 금지)
- ❌ 개인 블로그 · 커뮤니티 게시글
- ❌ 「이야기 조선왕조사」 등 대중 역사 서적 (peer-review 아님)

## 4단계 검증 프로세스

### Stage 1 · 사료 인식
```
For each historical citation:
  1. Parse citation elements:
     - 사료명 (예: 난중일기)
     - 연월일 (예: 갑오년 7월 25일 = 1594.7.25)
     - 원문 (한자·한글)
     - 국역본 페이지 (있는 경우)
     - 인용된 소장처·URL
```

### Stage 2 · 소스 신뢰도 확인
```
  2. Verify source is in Tier 1-4 whitelist
  3. Reject if from Blacklist (소설·드라마·개인 블로그)
```

### Stage 3 · 국가 DB 크로스체크
```
  4. For 조선왕조실록: query sillok.history.go.kr
     verify 왕대·연월일 exists · fetch original text
  5. For 난중일기: check 국립현충사 or 한국고전번역원
     verify 정확한 일자 · 원문 발췌
  6. For 동의보감·향약집성방: check KTKP DB
     verify 편명·페이지 · original 한자 text
```

### Stage 4 · 원문·국역 일치 확인
```
  7. Compare quoted 한자 원문 with DB 원문
  8. Compare quoted 국역 with 공식 국역본
  9. If discrepancy: mark [VERIFY-FAILED - TEXT-MISMATCH]
  10. If verified: mark [HISTORICAL-VERIFIED YYYY-MM-DD ✓]
```

## 이순신 관련 특별 지침

**허용 인용:**
- 난중일기 원본 (국립현충사)
- 이충무공전서 (한국고전번역원)
- 선조실록 관련 부분
- Peer-review 학술 논문 (예: '이순신의 건강과 질환' 관련)

**금지 인용:**
- 소설 · 드라마 · 영화 (사료가 아님)
- 개인 블로그 · 유튜브
- 대중 역사 서적 (검증 어려움)

**필수 확인 예시:**
```
인용: "1594년 (갑오년) 7월 25일 이순신은 배가 답답하고 어지러워 종일 힘들었다"

검증 절차:
1. 난중일기 갑오년 7월 25일 조 확인
2. 국립현충사 원본 or 한국고전번역원 국역본에서 발췌
3. 원문 한자 + 국역 3중 표기
4. URL 병기: https://db.itkc.or.kr/[해당 URL]
```

## 원문 인용 표준 형식

```
[H1] 이순신. 난중일기. 갑오년 (1594) 7월 25일 조.
     국립현충사 소장 원본 · 한국고전번역원 국역.
     원문: 「今日腹脹眩暈 終日苦焉」
     국역: "오늘 배가 부풀어 오르고 어지러워 종일 괴로웠다."
     URL: https://db.itkc.or.kr/dir/pop/premodern?dataId=...
     [HISTORICAL-VERIFIED 2026-07-16 ✓]
```

```
[H2] 허준. 동의보감·내경편·비장(脾臟)문. 1610 (광해군2).
     한국한의학연구원 KTKP DB.
     원문: 「脾主思」
     국역: "비장은 생각을 주관한다."
     페이지: 국역본 (남산당 1994) 제2권, p. 234.
     URL: http://www.oasis.kiom.re.kr/...
     [HISTORICAL-VERIFIED 2026-07-16 ✓]
```

## 실행 명령

```bash
python scripts/verify_historical.py \
    --file chapters/ch02-joseon-yi-sunsin.md \
    --db-config references/historical-dbs.json \
    --output references/historical-verification-ch2.md
```

또는 자연어:
```
"Chapter 2 조선 사료 원전 검증"
"historical-verifier로 이순신 인용 확인"
```

## 실패 시 저자 보고

```
Chapter 2 조선 사료 검증 결과:

검증 완료: 18/22 사료 인용

실패 인용 목록:
[H3] 이순신 관련 인용
     - 출처: '불멸의 이순신' KBS 드라마 대사
     - 조치: Blacklist · 즉시 배제 · 난중일기 원문으로 대체 필요

[H7] 동의보감 인용
     - 페이지 인용이 KTKP DB와 불일치
     - 조치: KTKP 재확인 or 국역본 정확 페이지 확인

대체 원전 자동 검색 · 저자 승인 요청.
```

## 예상 소요

- 챕터당 사료 인용 10-30개 검증: 반나절-1일
- API 자동 확인 + 수작업 확인 병행
- 국립현충사·규장각 DB는 API 미지원 → 수동 확인

## 다음 스킬 연결

검증 완료 후 사용자에게 알림:
> "Chapter {N} 사료 검증 완료. 검증률 {N}%. 다음으로 chapter-editor 실행하시겠습니까?"
