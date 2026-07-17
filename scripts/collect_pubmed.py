#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
collect_pubmed.py · PubMed E-utilities 논문 수집 (self-contained · stdlib only)
힘뇌장(HIMNOEJANG) 모노그래프 · 챕터 파이프라인 단계 ① (사전 리서치)

각 챕터 원료의 PubMed 쿼리(여러 개)를 실행해 실측 논문 레코드를
raw JSON(제목·저널·연도·권/호/페이지·DOI·저자·PublicationType)으로 저장한다.
DOI 추출은 reference-list DOI 오염을 피하기 위해
  Article/ELocationID[@EIdType="doi"] + PubmedData/ArticleIdList/ArticleId[@IdType="doi"]
만 사용한다(.//ArticleId 사용 금지).

의존: 없음 (Python 3.8+ 표준 라이브러리만)

사용법:
  # queries.txt: 한 줄에 PubMed 쿼리 하나 (빈 줄/#주석 무시)
  python scripts/collect_pubmed.py --queries queries_ch12.txt \
      --out references/ch12_raw.json --mindate 2013 --maxdate 2026
"""
import urllib.request, urllib.parse, json, time, re, sys, io, argparse
import xml.etree.ElementTree as ET
from collections import Counter

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
except Exception:
    pass

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def eutil(ep, params, email):
    params = dict(params)
    params.setdefault("tool", "hnj")
    params.setdefault("email", email)
    url = EUTILS + ep + "?" + urllib.parse.urlencode(params)
    for a in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read()
        except Exception:
            time.sleep(1.3 * (a + 1))
    raise RuntimeError("fail " + url)


def esearch(term, retmax, mindate, maxdate, email):
    d = json.loads(eutil("esearch.fcgi", {
        "db": "pubmed", "term": term, "retmax": str(retmax), "retmode": "json",
        "datetype": "pdat", "mindate": mindate, "maxdate": maxdate, "sort": "relevance"}, email))
    return d["esearchresult"].get("idlist", [])


def t(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def main():
    ap = argparse.ArgumentParser(description="힘뇌장 챕터 PubMed 수집")
    ap.add_argument("--queries", required=True, help="쿼리 파일(한 줄에 쿼리 하나)")
    ap.add_argument("--out", required=True, help="출력 raw JSON 경로")
    ap.add_argument("--mindate", default="2013")
    ap.add_argument("--maxdate", default="2026")
    ap.add_argument("--retmax", type=int, default=55, help="쿼리당 최대 수집(기본 55)")
    ap.add_argument("--email", default="choe.sunghwa@gmail.com")
    args = ap.parse_args()

    queries = [ln.strip() for ln in open(args.queries, encoding="utf-8")
               if ln.strip() and not ln.strip().startswith("#")]
    print(f"쿼리 {len(queries)}개 · {args.mindate}-{args.maxdate}", file=sys.stderr)

    pmids, seen = [], set()
    for q in queries:
        ids = esearch(q, args.retmax, args.mindate, args.maxdate, args.email)
        for i in ids:
            if i not in seen:
                seen.add(i); pmids.append(i)
        time.sleep(0.35)
        print(f"[q] {q[:46]:46s} -> {len(ids):3d} (tot {len(pmids)})", file=sys.stderr)
    print(f"unique PMIDs: {len(pmids)}", file=sys.stderr)

    recs = []
    for k in range(0, len(pmids), 40):
        root = ET.fromstring(eutil("efetch.fcgi", {
            "db": "pubmed", "id": ",".join(pmids[k:k + 40]), "retmode": "xml"}, args.email))
        for art in root.findall(".//PubmedArticle"):
            pmid = t(art.find(".//PMID"))
            title = t(art.find(".//ArticleTitle")).rstrip(".")
            journal = t(art.find(".//Journal/Title"))
            year = t(art.find(".//JournalIssue/PubDate/Year"))
            if not year:
                md = t(art.find(".//JournalIssue/PubDate/MedlineDate"))
                mm = re.search(r"(\d{4})", md)
                year = mm.group(1) if mm else ""
            vol = t(art.find(".//JournalIssue/Volume"))
            iss = t(art.find(".//JournalIssue/Issue"))
            pages = t(art.find(".//Pagination/MedlinePgn"))
            doi = ""
            for el in art.findall(".//Article/ELocationID"):
                if el.get("EIdType") == "doi" and t(el):
                    doi = t(el).strip(); break
            if not doi:
                for aid in art.findall("./PubmedData/ArticleIdList/ArticleId"):
                    if aid.get("IdType") == "doi":
                        doi = t(aid).strip(); break
            authors = [f"{t(a.find('LastName'))} {t(a.find('Initials'))}".strip()
                       for a in art.findall(".//AuthorList/Author") if t(a.find('LastName'))]
            ptypes = [t(p) for p in art.findall(".//PublicationType")]
            recs.append(dict(pmid=pmid, title=title, journal=journal, year=year, volume=vol,
                             issue=iss, pages=pages, doi=doi, authors=authors, ptypes=ptypes))
        time.sleep(0.35)
        print(f"[fetch] {min(k + 40, len(pmids))}/{len(pmids)}", file=sys.stderr)

    bad = {"Retraction of Publication", "Retracted Publication", "Published Erratum"}
    mind = int(args.mindate)
    recs = [r for r in recs if r["doi"] and r["year"] and int(r["year"]) >= mind
            and not (set(r["ptypes"]) & bad)]
    json.dump(recs, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nvalid records: {len(recs)}  ->  {args.out}", file=sys.stderr)
    for j, n in Counter(r["journal"] for r in recs).most_common(12):
        print(f"  {n:2d} {j}", file=sys.stderr)


if __name__ == "__main__":
    main()
