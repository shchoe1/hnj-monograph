#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate_chapter.py · 참고문헌 DOI/PMID 4단계 검증 (self-contained · stdlib only)
힘뇌장(HIMNOEJANG) 모노그래프 · reference-validator Skill 단계 ③ 구현

master-prompt v2.0 §5.3의 4단계 검증:
  Stage1 DOI 존재(CrossRef 200 또는 PubMed 확인)
  Stage2 제목 일치(정규화 유사도 >= 0.90 · substring 보정)  ← Anti-hallucination 핵심
  Stage3 저자/연도 교차 확인
  Stage4 PubMed PMID 교차 확인(efetch · 권위 소스) + DOI-PMID 일치

통과 → 본문 [PENDING-DOI-VERIFY] 를 [DOI-VERIFIED YYYY-MM-DD ✓] 로 치환
실패 → [VERIFY-FAILED - reason] 로 치환하고 로그에 기록

의존: 없음 (Python 3.8+ 표준 라이브러리만 사용)

사용법:
  python scripts/validate_chapter.py --file chapters/ch11-tyrosine.md
  python scripts/validate_chapter.py --file chapters/ch11-tyrosine.md \
      --log references/validation-log-ch11-2026-07-17.csv --date 2026-07-17
  python scripts/validate_chapter.py --file chapters/ch11-tyrosine.md --dry-run
"""
import re, sys, io, os, time, json, csv, argparse, datetime
import urllib.request, urllib.parse, urllib.error, difflib
import xml.etree.ElementTree as ET

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
except Exception:
    pass

CROSSREF = "https://api.crossref.org/works/"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EMAIL = os.environ.get("HNJ_EMAIL", "choe.sunghwa@gmail.com")
UA = f"HIMNOEJANG-Monograph/1.0 (mailto:{EMAIL})"


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for a in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, b""
            time.sleep(1.2 * (a + 1))
        except Exception:
            time.sleep(1.2 * (a + 1))
    return None, b""


def norm(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    s = s.replace("’", "'").replace("–", "-").replace("—", "-")
    s = re.sub(r"[^0-9a-zA-Z]+", " ", s.lower()).strip()
    return re.sub(r"\s+", " ", s)


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def crossref(doi):
    st, body = get(CROSSREF + urllib.parse.quote(doi))
    if st != 200 or not body:
        return None
    try:
        m = json.loads(body)["message"]
    except Exception:
        return None
    title = (m.get("title") or [""])[0]
    journal = (m.get("container-title") or [""])[0]
    year = None
    dp = m.get("issued", {}).get("date-parts") or m.get("published", {}).get("date-parts")
    if dp and dp[0]:
        year = dp[0][0]
    auth = m["author"][0].get("family", "") if m.get("author") else ""
    return {"title": title, "journal": journal, "year": year, "author": auth}


def pubmed_by_pmid(pmid):
    if not pmid:
        return None
    st, body = get(EUTILS + "efetch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "retmode": "xml", "tool": "hnj", "email": EMAIL}))
    if not body:
        return None
    try:
        root = ET.fromstring(body)
    except Exception:
        return None
    art = root.find(".//PubmedArticle")
    if art is None:
        return None

    def t(el):
        return "".join(el.itertext()).strip() if el is not None else ""

    title = t(art.find(".//ArticleTitle")).rstrip(".")
    journal = t(art.find(".//Journal/Title"))
    year = t(art.find(".//JournalIssue/PubDate/Year"))
    if not year:
        md = t(art.find(".//JournalIssue/PubDate/MedlineDate"))
        mm = re.search(r"(\d{4})", md)
        year = mm.group(1) if mm else ""
    doi = ""
    for el in art.findall(".//Article/ELocationID"):
        if el.get("EIdType") == "doi" and t(el):
            doi = t(el).strip()
            break
    if not doi:
        for aid in art.findall("./PubmedData/ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi":
                doi = t(aid).strip()
                break
    author = t(art.find(".//AuthorList/Author/LastName"))
    got_pmid = t(art.find(".//PMID"))
    return {"title": title, "journal": journal, "year": year, "doi": doi,
            "author": author, "pmid": got_pmid}


def parse_entry(txt):
    m = re.search(r'doi:(10\.\d{4,}/[^\s]+?)\.?\s+PMID', txt) or re.search(r'doi:(10\.\d{4,}/\S+)', txt)
    doi = m.group(1).rstrip('.,;') if m else None
    mp = re.search(r'PMID:(\d+)', txt)
    pmid = mp.group(1) if mp else None
    body = txt.split(' doi:')[0]
    parts = body.split('. ')
    title = parts[1].strip() if len(parts) >= 2 else ""
    return doi, pmid, title


def main():
    ap = argparse.ArgumentParser(description="힘뇌장 챕터 참고문헌 DOI 4단계 검증")
    ap.add_argument("--file", required=True, help="검증할 챕터 Markdown 경로")
    ap.add_argument("--log", default=None, help="검증 로그 CSV 경로(기본: references/validation-log-<chap>-<date>.csv)")
    ap.add_argument("--date", default=None, help="검증일 YYYY-MM-DD (기본: 오늘)")
    ap.add_argument("--min-sim", type=float, default=0.90, help="제목 일치 최소 유사도(기본 0.90)")
    ap.add_argument("--dry-run", action="store_true", help="파일 미수정·검증만 수행")
    args = ap.parse_args()

    today = args.date or datetime.date.today().isoformat()
    ch_path = args.file
    stem = os.path.splitext(os.path.basename(ch_path))[0]
    log_path = args.log or os.path.join("references", f"validation-log-{stem}-{today}.csv")

    content = open(ch_path, encoding="utf-8").read()
    lines = content.split("\n")
    entry_re = re.compile(r'^\[([0-9A-Za-z]+)\]\s+(.*)\[PENDING-DOI-VERIFY\]\s*$')

    results = []
    for i, ln in enumerate(lines):
        m = entry_re.match(ln)
        if not m:
            continue
        cid, txt = m.group(1), m.group(2)
        doi, pmid, cited_title = parse_entry(txt)
        r = {"id": cid, "doi": doi or "", "pmid": pmid or "", "cited_title": cited_title,
             "verified": False, "reason": "", "title_sim": "", "src": "", "line": i}
        if not doi:
            r["reason"] = "NO-DOI"
            results.append(r)
            continue

        cr = crossref(doi); time.sleep(0.25)
        pm = pubmed_by_pmid(pmid); time.sleep(0.30)

        doi_exists = cr is not None or (pm and pm.get("doi", "").lower() == doi.lower())
        if not doi_exists:
            r["reason"] = "DOI-NOT-FOUND"
            results.append(r)
            continue
        r["src"] = "crossref+pubmed" if cr and pm else ("crossref" if cr else "pubmed")

        ref_title = (cr or {}).get("title") or (pm or {}).get("title") or ""
        pm_title = (pm or {}).get("title", "")
        substr = (norm(ref_title) and norm(ref_title) in norm(txt)) or \
                 (norm(pm_title) and norm(pm_title) in norm(txt))
        s = max(sim(cited_title, ref_title), sim(cited_title, pm_title) if pm else 0)
        if substr:
            s = max(s, 1.0)
        r["title_sim"] = f"{s:.3f}"
        if s < args.min_sim:
            r["reason"] = f"TITLE-MISMATCH(sim={s:.2f})"
            results.append(r)
            continue

        def yr_ok(src):
            y = str((src or {}).get("year") or "")
            return (not y) or (txt.find(y) >= 0)

        def auth_ok(src):
            fam = norm((src or {}).get("author") or "")
            return (not fam) or (fam.split(" ")[0] in norm(txt))

        meta_src = pm or cr
        if not (yr_ok(meta_src) and auth_ok(meta_src)):
            other = cr if meta_src is pm else pm
            if not (yr_ok(other) and auth_ok(other)):
                r["reason"] = "METADATA-MISMATCH"
                results.append(r)
                continue

        if pmid:
            if not pm:
                r["reason"] = "PMID-NOT-FOUND"
                results.append(r)
                continue
            if pm.get("pmid") != pmid:
                r["reason"] = "PMID-MISMATCH"
                results.append(r)
                continue
            if pm.get("doi") and pm["doi"].lower() != doi.lower():
                r["reason"] = f"DOI-PMID-MISMATCH(pm={pm['doi']})"
                results.append(r)
                continue

        r["verified"] = True
        results.append(r)
        print(f"[{cid:>4}] {'OK ' if r['verified'] else 'XX '} sim={r['title_sim']} "
              f"src={r['src']} doi={doi}", file=sys.stderr)

    ok = 0
    for r in results:
        ln = lines[r["line"]]
        if r["verified"]:
            lines[r["line"]] = ln.replace("[PENDING-DOI-VERIFY]", f"[DOI-VERIFIED {today} ✓]")
            ok += 1
        else:
            lines[r["line"]] = ln.replace("[PENDING-DOI-VERIFY]", f"[VERIFY-FAILED - {r['reason']}]")

    if not args.dry_run:
        open(ch_path, "w", encoding="utf-8").write("\n".join(lines))
        with open(log_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["id", "doi", "pmid", "verified", "reason",
                                              "title_sim", "src", "cited_title"])
            w.writeheader()
            for r in results:
                w.writerow({k: r.get(k, "") for k in w.fieldnames})

    print("\n=== 검증 요약 ===", file=sys.stderr)
    print(f"검증 대상: {len(results)}", file=sys.stderr)
    print(f"검증 완료: {ok}", file=sys.stderr)
    print(f"검증 실패: {len(results) - ok}", file=sys.stderr)
    for r in results:
        if not r["verified"]:
            print(f"  FAIL [{r['id']}] {r['reason']}  doi={r['doi']}", file=sys.stderr)
    if args.dry_run:
        print("\n(dry-run: 파일 미수정)", file=sys.stderr)
    else:
        print(f"\nLOG: {log_path}", file=sys.stderr)
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
