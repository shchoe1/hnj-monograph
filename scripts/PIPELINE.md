# 챕터 제작 파이프라인 (4단계) · 스크립트 사용법

힘뇌장(HIMNOEJANG) 모노그래프의 원료 챕터(Ch4~14)는 아래 **4단계**로 제작한다.
모든 스크립트는 **Python 3.8+ 표준 라이브러리만** 사용하므로 별도 패키지 설치가 필요 없다
(외부 의존 `requests`/`Levenshtein` 등은 보조 도구 `verify_doi.py` 전용이며, 정본 파이프라인은 불필요).
> 검증 정본은 `validate_chapter.py`(stdlib 전용). `verify_doi.py`는 requests 기반 교차확인용 보조 도구로,
> 2026-07-17 라인 단위 파싱으로 오정렬 버그를 수정했다(상세: 파일 헤더 주석).

> 다른 PC로 이동 시: 이 저장소를 clone 한 뒤, 시스템 Python 3.8+ 만 있으면 바로 실행된다.
> `venv`는 저장소에 포함되지 않으므로(용량·이식성) 필요 시 새로 만든다: `python -m venv venv`.

---

## 단계 ① 사전 리서치 (수집 → 큐레이션)

### 1-a. PubMed 수집 → raw JSON

원료별 PubMed 쿼리를 한 줄에 하나씩 담은 텍스트 파일을 만든다(예: `queries_ch12.txt`).
`config/` 아래에 챕터별 예시가 있다(`queries_ch11_tyrosine.txt` 참고).

```bash
python scripts/collect_pubmed.py \
    --queries config/queries_ch12.txt \
    --out references/ch12_raw.json \
    --mindate 2013 --maxdate 2026
```

- DOI는 `Article/ELocationID` + `PubmedData/ArticleIdList/ArticleId` 에서만 추출한다
  (`.//ArticleId` 는 참고문헌 목록 DOI를 오염 수집하므로 사용 금지 — 과거 버그).
- 철회/오류정정 논문은 자동 제외.

### 1-b. 큐레이션 → chN.bib

버킷(관련성 키워드)·저널 티어·쿼터·배제어를 담은 config JSON을 만든다
(예시: `config/curate_ch11_tyrosine.json`). `title_gate` 를 주면 "제목에 해당 단어 필수"
게이트가 걸린다(예: `["tyrosine"]` — 무관한 tyrosine kinase/조영제/항암제 논문 배제에 사용).

```bash
python scripts/curate_refs.py \
    --raw references/ch12_raw.json \
    --out references/ch12.bib \
    --config config/curate_ch12.json
```

출력 후 stderr에 선별 제목 목록이 찍히므로 **off-topic이 섞였는지 눈으로 확인**하고,
필요하면 config의 `exclude_soft`/`title_gate`/`target`을 조정해 재실행한다.

---

## 단계 ② 초고 드래프팅

`chapters/chNN-slug.md` 를 **15섹션 표준 템플릿**으로 작성(수작업/AI).
- `references/chN.bib` 의 실존 문헌만 인용. 각 인용에 `[PENDING-DOI-VERIFY]` 태그.
- 본문 [n] ↔ 참고문헌 목록 [n] 1:1 대응(dangling 0 / orphan 0), 번호 연속.
- 정합성 자가점검:
  ```bash
  python - <<'PY'
  import re
  s=open('chapters/ch12-xxx.md',encoding='utf-8').read()
  body,ref=s.split('## 참고문헌 (References)')
  c=set(int(x) for x in re.findall(r'\[(\d{1,3})\]',body))
  l=set(int(x) for x in re.findall(r'^\[(\d{1,3})\]',ref,re.M))
  print('dangling',sorted(c-l),'orphan',sorted(l-c))
  PY
  ```

---

## 단계 ③ 참고문헌 DOI 검증 (reference-validator)

```bash
python scripts/validate_chapter.py --file chapters/ch12-xxx.md
# 검증만(파일 미수정) 먼저 확인하려면:
python scripts/validate_chapter.py --file chapters/ch12-xxx.md --dry-run
```

- CrossRef + PubMed 4단계(DOI 존재 → 제목 일치≥0.90 → 저자/연도 → PMID/DOI 교차).
- 통과 시 본문 태그가 `[DOI-VERIFIED YYYY-MM-DD ✓]` 로 치환되고
  `references/validation-log-<chap>-<date>.csv` 로그가 생성된다.
- 실패 항목은 `[VERIFY-FAILED - 사유]` 로 표시되고 요약에 나열된다 → 실존 여부 재조사/대체.

---

## 단계 ④ 편집 (chapter-editor)

- KFDA 표시광고 준수(힘뇌장에 대한 치료·예방·완치·특효 주장 0건).
- 용어 통일 · 저자 톤 유지 · 헤더 필드 갱신 · orphan/off-topic 정리.
- 편집 로그 `references/edit-log-<chap>-<date>.md` 작성.
- 자세한 규칙은 `.claude/skills/chapter-editor/SKILL.md` 참조.

---

## 커밋 규약

각 챕터 완료 시:
```bash
git add chapters/chNN-slug.md references/chN.bib references/chN_raw.json \
        references/validation-log-*.csv references/edit-log-*.md
git commit -m "Chapter N · 원료명 · ..."
git push origin main
```

## 진행 현황(2026-07-17 기준)

- 완료(①~④): Ch1~3(서장), Ch4~12 (Ch11 L-티로신 32/32·Ch12 L-글루타민 38/38 DOI-VERIFIED·편집 완료·저자 승인 대기)
- **드래프트(①②만 · ③④ 대기): Ch13 · 커큐민(울금)** (39편 큐레이션·15섹션 초고·본문↔목록 1:1·사료 최소화) ← 다음은 여기서 ③(reference-validator)부터
- 예정: Ch14(FOS·팔라티노스) · Ch15(종장)
