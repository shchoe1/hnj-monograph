#!/usr/bin/env python3
"""
verify_doi.py · 참고문헌 DOI 4단계 검증 스크립트
힘뇌장 모노그래프 프로젝트 · reference-validator Skill용

사용법:
    python scripts/verify_doi.py --file chapters/ch10-theanine.md \
        --output references/validation-log-ch10.csv --update-in-place

의존:
    pip install requests python-Levenshtein
"""

import argparse
import csv
import re
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests 라이브러리 필요. `pip install requests` 실행")
    sys.exit(1)

try:
    import Levenshtein
    def similarity(a, b):
        return Levenshtein.ratio(a.lower().strip(), b.lower().strip())
except ImportError:
    def similarity(a, b):
        # Fallback: simple 문자 매칭
        a, b = a.lower().strip(), b.lower().strip()
        if a == b: return 1.0
        matches = sum(1 for x, y in zip(a, b) if x == y)
        return matches / max(len(a), len(b))

CROSSREF_API = "https://api.crossref.org/works/"
PUBMED_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# Blacklist URLs (즉시 배제)
BLACKLIST_DOMAINS = [
    "blog.naver.com", "tistory.com", "wordpress.com",
    "webmd.com", "healthline.com", "health.chosun.com",
    "amazon.com/dp/", "coupang.com/vp/",
    "wikipedia.org", "namu.wiki",
    "youtube.com/watch", "podcasts.apple.com"
]

# Whitelist journals (Tier 1)
WHITELIST_JOURNALS = [
    "Nature", "Science", "Cell", "New England Journal of Medicine",
    "Lancet", "JAMA", "BMJ", "PNAS",
    "Physiological Reviews", "Nature Reviews", "Annual Review",
    "Gut", "Gastroenterology", "Molecular Psychiatry",
    "Brain Behavior and Immunity", "Nutrients", "American Journal of Clinical Nutrition"
]

CITATION_PATTERN = re.compile(
    r'\[(\d+)\]\s*(.+?)\s*doi:([^\s\.]+(?:\.[^\s\.]+)*)\s*(?:PMID:(\d+))?',
    re.DOTALL
)

def extract_doi(citation_text):
    """DOI 정규식 추출"""
    doi_match = re.search(r'10\.\d{4,}/[^\s]+', citation_text)
    return doi_match.group(0).rstrip('.,;)]') if doi_match else None

def check_blacklist(citation_text):
    """Blacklist URL 검사"""
    for domain in BLACKLIST_DOMAINS:
        if domain in citation_text.lower():
            return f"BLACKLISTED_SOURCE: {domain}"
    return None

def crossref_verify(doi):
    """CrossRef API로 DOI 존재 확인 · 논문 메타데이터 반환"""
    try:
        r = requests.get(CROSSREF_API + doi, timeout=10,
                         headers={"User-Agent": "HIMNOEJANG-Monograph/1.0 (mailto:choe.sunghwa@gmail.com)"})
        if r.status_code == 404:
            return None, "DOI_NOT_FOUND"
        elif r.status_code != 200:
            return None, f"CROSSREF_ERROR_{r.status_code}"
        return r.json().get("message"), None
    except Exception as e:
        return None, f"CROSSREF_EXCEPTION: {e}"

def pubmed_search(title):
    """PubMed E-utilities로 제목 검색 · PMID 반환"""
    try:
        params = {"db": "pubmed", "term": title, "retmode": "json", "retmax": 5}
        r = requests.get(PUBMED_API + "esearch.fcgi", params=params, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])
        return pmids[0] if pmids else None
    except Exception:
        return None

def verify_citation(citation_id, citation_text):
    """단일 인용 4단계 검증"""
    result = {
        "id": citation_id,
        "raw": citation_text[:200],
        "doi": None,
        "verified": False,
        "reason": None,
        "timestamp": datetime.now().isoformat()
    }

    # Stage 0: Blacklist 검사
    bl = check_blacklist(citation_text)
    if bl:
        result["reason"] = bl
        return result

    # DOI 추출
    doi = extract_doi(citation_text)
    if not doi:
        result["reason"] = "NO_DOI_FOUND"
        return result
    result["doi"] = doi

    # Stage 1: CrossRef DOI 존재 확인
    paper, err = crossref_verify(doi)
    if err:
        result["reason"] = err
        return result

    # Stage 2: 제목 일치 (★ Anti-Hallucination 핵심)
    cited_title = extract_title(citation_text)
    paper_title = paper.get("title", [""])[0] if paper.get("title") else ""
    sim = similarity(cited_title, paper_title)
    if sim < 0.85:  # 85% 미만 시 실패 (완화 기준)
        result["reason"] = f"TITLE_MISMATCH (sim={sim:.2f}): cited='{cited_title[:60]}' vs actual='{paper_title[:60]}'"
        return result
    result["title_sim"] = sim

    # Stage 3: 저자·저널·연도 (약식)
    journal = paper.get("container-title", [""])[0] if paper.get("container-title") else ""
    year = None
    if paper.get("issued", {}).get("date-parts"):
        year = paper["issued"]["date-parts"][0][0]

    # Stage 4: PubMed 교차 확인 (의학 논문)
    pmid = pubmed_search(paper_title)
    if pmid:
        result["pmid"] = pmid

    result["verified"] = True
    result["journal"] = journal
    result["year"] = year
    return result

def extract_title(citation_text):
    """인용 문자열에서 제목 추출 (약식)"""
    # 저자 뒤 첫 번째 마침표 이후, 저널 이름 앞까지
    # 예: "Cryan JF et al. The Microbiota-Gut-Brain Axis. Physiological Reviews..."
    parts = re.split(r'\.\s+', citation_text)
    if len(parts) >= 2:
        # 두 번째 파트가 대개 제목
        return parts[1].strip()
    return ""

def process_file(file_path, output_csv=None, update_in_place=False):
    """파일 내 모든 인용 검증"""
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    # PENDING-DOI-VERIFY 태그 인용 찾기
    pattern = re.compile(r'\[(\d+)\](.+?)\[PENDING-DOI-VERIFY\]', re.DOTALL)
    matches = pattern.findall(content)

    print(f"검증 대상: {len(matches)}개 인용")
    results = []

    for i, (cid, ctext) in enumerate(matches, 1):
        print(f"  [{i}/{len(matches)}] {cid}: 검증 중...", end=" ", flush=True)
        result = verify_citation(cid, ctext)

        if result["verified"]:
            print(f"✓ VERIFIED (sim={result.get('title_sim', 0):.2f})")
            # In-place 태그 교체
            if update_in_place:
                today = datetime.now().strftime("%Y-%m-%d")
                content = content.replace(
                    f"[PENDING-DOI-VERIFY]",
                    f"[DOI-VERIFIED {today} ✓]",
                    1
                )
        else:
            print(f"✗ FAILED: {result['reason']}")
            if update_in_place:
                content = content.replace(
                    f"[PENDING-DOI-VERIFY]",
                    f"[VERIFY-FAILED: {result['reason']}]",
                    1
                )

        results.append(result)
        time.sleep(0.5)  # API rate limit 준수

    # 파일 업데이트
    if update_in_place:
        path.write_text(content, encoding="utf-8")
        print(f"\n원고 업데이트: {path}")

    # CSV 리포트
    if output_csv:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id","doi","verified","reason","title_sim","journal","year","pmid","timestamp","raw"])
            writer.writeheader()
            for r in results:
                writer.writerow({k: r.get(k, "") for k in writer.fieldnames})
        print(f"검증 리포트: {output_csv}")

    # 요약
    verified = sum(1 for r in results if r["verified"])
    print(f"\n=== 검증 요약 ===")
    print(f"검증 완료: {verified}/{len(results)} ({100*verified/max(len(results),1):.1f}%)")
    print(f"검증 실패: {len(results)-verified}")

    return results

def main():
    parser = argparse.ArgumentParser(description="힘뇌장 모노그래프 · 참고문헌 DOI 검증")
    parser.add_argument("--file", required=True, help="검증할 원고 Markdown 파일")
    parser.add_argument("--output", help="검증 리포트 CSV 저장 경로")
    parser.add_argument("--update-in-place", action="store_true", help="원고 파일에 태그 자동 갱신")
    args = parser.parse_args()

    process_file(args.file, args.output, args.update_in_place)

if __name__ == "__main__":
    main()
