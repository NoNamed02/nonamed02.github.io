## 구조

```
posts/                  글 원고 (글 하나 = 폴더 하나: index.md + 이미지)
templates/post.html     글 페이지 템플릿
templates/index.html    목록 페이지 템플릿
css/style.css           전체 스타일 (색·크기는 상단 :root 변수만 수정)
about.html              소개 페이지 (그대로 복사됨)
build.py                _site/로 사이트 생성 (글 목록도 자동 생성)
lib/markdown2.py        마크다운 변환 라이브러리 (저장소에 포함 — 설치 불필요)
.github/workflows/deploy.yml   푸시 시 빌드 + Pages 배포
_site/                  빌드 결과물 (git에 올라가지 않음)
```

## 새 글 쓰는 법

글 하나 = 폴더 하나. `posts/YYYY-MM-DD-제목/` 폴더를 만들고 그 안에
본문 `index.md`와 글에서 쓸 이미지를 함께 넣는다.
목록 페이지에는 빌드할 때 자동으로 들어간다 (date 내림차순 정렬).

```
posts/2026-07-10-여행기/
  index.md       본문
  바다.jpg        이미지 — 본문에서 ![설명](바다.jpg) 로 참조
```

index.md는 상단에 front matter를 채우고 마크다운으로 쓴다:

```markdown
---
title: 글 제목
date: 2026-07-10
description: 검색·미리보기에 쓰일 한 줄 요약 (생략 가능)
---

본문. 코드 블록, 표, 인용문 지원.
```

이미지 경로가 상대 경로라서 VSCode 마크다운 미리보기(Cmd+Shift+V)에서도
사진이 그대로 보인다. 이미지 없는 짧은 글은 폴더 없이
`posts/YYYY-MM-DD-제목.md` 한 파일로 써도 된다.

## 로컬에서 확인

별도 설치가 필요 없다 — 변환 라이브러리가 저장소에 포함돼 있어서 파이썬만 있으면 된다.

**VSCode Live Server로 보기 (추천)** — 저장하면 브라우저까지 자동 새로고침:

1. 폴더를 열면 "블로그 빌드 감시" 태스크가 자동 시작된다
   (VSCode가 자동 태스크 허용을 물으면 Allow. 수동 실행: Terminal → Run Task)
2. 상태바의 **Go Live** 클릭 → `_site/`가 서빙된다 (.vscode/settings.json에 설정됨)
3. md를 저장하면 감시 태스크가 재빌드하고, Live Server가 브라우저를 새로고침한다

**터미널만으로 보기**:

```sh
python3 build.py --serve
# http://localhost:8000 (저장 시 자동 재빌드, 새로고침은 수동)
```

한 번만 빌드하려면 `python3 build.py`.

## 배포 (최초 1회 설정)

1. GitHub에 저장소를 만들어 푸시
2. 저장소 → **Settings → Pages** → Source를 **GitHub Actions**로 설정
3. 이후에는 `main`에 푸시할 때마다 자동 배포

배포 상태는 저장소의 Actions 탭에서 확인할 수 있다.
