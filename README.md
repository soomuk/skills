<p align="center"><img src="assets/logo.jpg" width="120" alt="樹默 수묵학술문화연구소"></p>

# 樹默 스킬 서가 (soomuk/skills)

수묵학술문화연구소가 공개한 Claude 스킬을 한 페이지에 모은 안내 페이지입니다.

**페이지 주소: https://soomuk.github.io/skills/**

스킬을 고르면 Claude 채팅창에 붙여 넣을 설치 문장과 사용 예시 문장을 버튼 하나로 복사할 수 있습니다.

| 스킬 | 하는 일 | 저장소 |
|---|---|---|
| 미술품 판독 노트 | 미술품 사진을 세부까지 판독해 크롭을 붙인 HTML 노트로 정리 | [soomuk/art-analysis](https://github.com/soomuk/art-analysis) |
| 불교학 학술지 편집검토 | 불교학 학술지 29종 규정으로 원고를 점검해 편집점검보고서(.docx) 작성 | [soomuk/k-buddhist-journal](https://github.com/soomuk/k-buddhist-journal) |

---

## 관리자용: 새 스킬 추가하기

페이지는 `skills.json` 한 파일로 만들어집니다. **index.html은 직접 고치지 않습니다.**

1. 새 스킬을 자기 저장소(예: `soomuk/새-스킬`)에 올립니다.
2. 이 저장소의 `skills.json`을 GitHub에서 엽니다. 연필(Edit) 버튼을 누릅니다.
3. `"skills": [` 목록 끝에 기존 항목 하나를 복사해 붙이고 내용을 바꿉니다. 앞 항목의 닫는 `}` 뒤에 쉼표(`,`)를 꼭 넣습니다.
4. **Commit changes**를 누릅니다.
5. 1~2분 뒤 페이지가 저절로 새로 만들어집니다. 진행 상황은 **Actions** 탭에서 볼 수 있습니다.

Claude에게 "스킬 서가에 ○○ 스킬 추가해줘"라고 하고 바뀐 `skills.json`을 받아 올려도 됩니다.

### skills.json 항목 설명

| 항목 | 뜻 |
|---|---|
| `id` | 페이지 주소 끝에 붙는 영문 이름(예: `#art-analysis`). 다른 스킬과 겹치면 안 됩니다 |
| `name` | 메뉴와 카드 제목에 보이는 이름 |
| `skill_name` | 스킬의 실제 이름(SKILL.md의 `name`) |
| `tagline` | 한 줄 설명 |
| `flow` | 올릴 것 → 받는 것 (한 줄) |
| `repo` | 스킬 저장소 주소 |
| `install_prompt` | Claude 채팅에 붙여 넣을 설치 문장 |
| `zip` | 업로드용 zip 파일 주소 |
| `claude_code` | Claude Code 설치 명령(줄마다 하나). 없으면 `[]` |
| `examples` | 사용 예시 문장 목록(2개 권장) |
| `note` | 주의 한 줄 |
| `extra` | 접어 두는 추가 목록(예: 수록 학술지). 없으면 `null` |

### 페이지가 안 바뀔 때

- **Actions** 탭에서 빨간 X가 있으면 눌러 오류를 봅니다. 대부분 `skills.json`의 쉼표나 따옴표 하나가 빠진 경우입니다.
- 오류 내용을 Claude에게 보여 주면 고칠 곳을 알려 줍니다.

## 처음 한 번만 하는 설정

1. **Settings → Pages**로 갑니다.
2. **Source**를 **GitHub Actions**로 고릅니다.
3. **Actions** 탭 → "스킬 서가 페이지 만들기" → **Run workflow**를 한 번 누릅니다.

## 파일 구성

```
skills.json                   ← 스킬 목록(이 파일만 고칩니다)
build.py                      ← skills.json으로 index.html을 만드는 스크립트
index.html                    ← 만들어진 페이지(자동 갱신)
assets/logo.jpg               ← 연구소 로고
.github/workflows/pages.yml   ← 자동 빌드·배포 설정
```

`build.py`는 페이지에 쓰인 한글·한자만 골라 Noto Serif KR 글꼴을 페이지 안에 넣습니다. 그래서 iPhone·Android·PC에서 같은 글꼴로 보입니다.

## 라이선스

MIT License · 수묵학술문화연구소 (soomuk)
