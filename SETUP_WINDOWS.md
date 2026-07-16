# C:\hnj-mgf · Windows 초기 설정

**저장소 이관 상태: ✅ 완료 (17개 파일 이미 배치됨)**
**Git 초기화: ⚠ Windows에서 재실행 필요 (아래 참조)**

---

## Step 0 · Git 저장소 재초기화 (필수)

Cowork 세션의 Linux sandbox에서 .git 폴더가 부분 초기화된 상태입니다. Windows에서 다음을 실행:

```powershell
# PowerShell 관리자 권한
cd C:\hnj-mgf

# 부분 초기화된 .git 완전 제거
Remove-Item -Recurse -Force .git

# 새로 초기화
git init -b main
git config user.email "choe.sunghwa@gmail.com"
git config user.name "Choe Sunghwa"
git add -A
git commit -m "Initial · 4 skills + scripts + master prompt v2.0"
```

## Step 1 · Python 환경 (verify_doi.py 실행용)

```powershell
cd C:\hnj-mgf
python -m venv venv
.\venv\Scripts\activate
pip install -r scripts\requirements.txt
```

## Step 2 · Claude Code 실행

```powershell
cd C:\hnj-mgf
claude
```

Claude Code가 시작되면 자동으로 `.claude/skills/` 내 4개 Skill을 인식합니다:
- chapter-drafter
- reference-validator
- historical-verifier
- chapter-editor

## Step 3 · 첫 챕터 시험

Claude 프롬프트에서:

```
Chapter 10 L-Theanine을 마스터 프롬프트 v2.0(prompts/master-prompt-v2.0.md)에 따라 
다음 순서로 진행해줘:

① 사전 리서치: Tier 1-3 저널 최근 10년 논문 100편 수집 · references/ch10.bib 저장
② 초고 드래프팅: 15섹션 표준 템플릿 · 40-50p · chapters/ch10-theanine.md 저장
③ 참고문헌 DOI 검증: reference-validator Skill 실행 · [DOI-VERIFIED ✓] 태그 부착
④ 편집: chapter-editor Skill 실행 · KFDA 준수 · 톤 통일

각 단계 결과 요약해서 보고하고 저자 승인 후 다음 단계로 진행.
```

## Step 4 · GitHub 원격 저장소 (선택)

```powershell
cd C:\hnj-mgf
git remote add origin https://github.com/[USERNAME]/hnj-monograph.git
git push -u origin main
```

## Step 5 · verify_doi.py 실측 테스트

Cryan 2019 (실제 존재 논문)로 검증:

```powershell
# 테스트용 임시 파일
'[1] Cryan JF et al. The Microbiota-Gut-Brain Axis. Physiological Reviews. 2019;99(4):1877-2013. doi:10.1152/physrev.00018.2018. PMID:31460832. URL: https://doi.org/10.1152/physrev.00018.2018. [PENDING-DOI-VERIFY]' | Out-File chapters\test.md

python scripts\verify_doi.py --file chapters\test.md --update-in-place
```

→ `[DOI-VERIFIED 2026-07-16 ✓]` 태그로 자동 갱신되면 정상

---

## 완료 확인 체크리스트

- [ ] `C:\hnj-mgf\` 폴더 접근 가능
- [ ] `.claude/skills/` 4개 Skill 파일 존재
- [ ] `prompts/master-prompt-v2.0.md` 존재
- [ ] `.git` 폴더 재초기화 완료
- [ ] Python venv + requirements.txt 설치
- [ ] Claude Code 실행 및 4개 Skill 인식
- [ ] verify_doi.py 실측 통과
- [ ] Chapter 10 첫 시험 실행

## 문제 발생 시

**Q: Skill이 인식되지 않는다**
A: Claude Code에서 `/skills` 명령으로 목록 확인. 없으면 `.claude/skills/` 폴더 위치 확인.

**Q: verify_doi.py 실행 오류**
A: `pip install requests python-Levenshtein` 재설치.

**Q: git config 오류**
A: 위 Step 0 재실행 (전체 .git 제거 후 다시 init).
