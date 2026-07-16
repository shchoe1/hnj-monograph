# prompts/ 폴더

## 마스터 프롬프트 v2.0

메인 프롬프트는 워크스페이스 상위의 다음 파일을 참조:
`__Beaudrug 보드락/_모노그래프_서적프로젝트/힘뇌장_모노그래프_서적집필_마스터프롬프트_v2.0_260716.docx`

C:\hnj-mgf 로 프로젝트 이관 시:
`prompts/master-prompt-v2.0.docx` 로 복사
또는 Markdown 변환:
```bash
pandoc 힘뇌장_모노그래프_서적집필_마스터프롬프트_v2.0_260716.docx -t markdown -o prompts/master-prompt-v2.0.md
```

## 챕터별 커스텀 프롬프트

각 챕터 시작 시 아래 형식으로 커스텀 프롬프트 저장:
- `prompts/ch01-intro-prompt.md`
- `prompts/ch04-ginseng-prompt.md`
- `prompts/ch10-theanine-prompt.md`
- ... 등등
