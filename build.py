#!/usr/bin/env python3
"""posts/*.md를 HTML로 변환해 _site/에 사이트 전체를 생성한다.

별도 설치가 필요 없다 — 변환 라이브러리(lib/markdown2.py)가 저장소에 포함돼 있다.

사용법:
    python3 build.py          한 번 빌드
    python3 build.py --serve  빌드 + 미리보기 서버 + 저장할 때마다 자동 재빌드
    python3 build.py --watch  서버 없이 자동 재빌드만 (VSCode Live Server와 함께 사용)
"""
import html
import re
import shutil
import sys
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

ROOT = Path(__file__).parent

# 저장소에 포함된 lib/ 폴더에서 변환 라이브러리를 불러온다
sys.path.insert(0, str(ROOT / "lib"))
try:
    import markdown2
except ImportError:
    sys.exit("lib/markdown2.py가 없습니다. 저장소의 lib 폴더를 복원하세요.")

# 태스크 창 등 터미널이 아닌 곳에서도 로그가 즉시 보이도록
sys.stdout.reconfigure(line_buffering=True)

SITE = ROOT / "_site"
STATIC_FILES = ["about.html"]  # 그대로 복사할 최상위 파일들
WATCH_TARGETS = ["posts", "templates", "css", "images"] + STATIC_FILES
PORT = 8000


class BuildError(Exception):
    """글 원고의 문제(front matter 누락 등)로 빌드할 수 없을 때"""


def parse_post(path):
    """front matter(---로 감싼 머리말)와 마크다운 본문을 분리해 반환."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        raise BuildError(f"{path.name} 상단에 front matter(--- ... ---)가 없습니다")

    # "key: value" 줄들을 딕셔너리로
    meta = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        if key.strip():
            meta[key.strip()] = value.strip()

    for required in ("title", "date"):
        if required not in meta:
            raise BuildError(f"{path.name}의 front matter에 '{required}'가 없습니다")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["date"]):
        raise BuildError(f"{path.name}의 date는 YYYY-MM-DD 형식이어야 합니다")

    body = markdown2.markdown(
        m.group(2), extras=["fenced-code-blocks", "tables", "break-on-newline"]
    )
    body = body.replace("=&gt;", "→")
    return meta, str(body)


def render(template, **variables):
    """템플릿의 {{이름}} 자리에 값을 끼워 넣는다."""
    for key, value in variables.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def korean_date(iso):
    """'2026-07-03' → '2026년 7월 3일'"""
    y, m, d = iso.split("-")
    return f"{y}년 {int(m)}월 {int(d)}일"


def find_post_md(folder):
    """글 폴더 안에서 본문 md 파일을 찾는다."""
    md_files = sorted(folder.glob("*.md"))
    if len(md_files) == 1:
        return md_files[0]
    if (folder / "index.md").exists():
        return folder / "index.md"
    if not md_files:
        raise BuildError(f"posts/{folder.name}/ 안에 md 파일이 없습니다")
    raise BuildError(
        f"posts/{folder.name}/ 안에 md 파일이 여러 개입니다 — 본문 파일 이름을 index.md로 하세요"
    )


def build():
    # 결과물 폴더를 비우고 새로 만든다
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "posts").mkdir(parents=True)

    post_tpl = (ROOT / "templates" / "post.html").read_text(encoding="utf-8")
    index_tpl = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    # 1. 글 페이지 생성
    #    - 폴더 글:   posts/이름/ (index.md + 이미지들) → _site/posts/이름/index.html
    #    - 파일 글:   posts/이름.md                    → _site/posts/이름.html
    posts = []
    for entry in sorted((ROOT / "posts").iterdir()):
        if entry.is_dir():
            md_file = find_post_md(entry)
            out_dir = SITE / "posts" / entry.name
            # 이미지 등 본문 외의 파일을 통째로 복사 (md와 숨김 파일 제외)
            shutil.copytree(entry, out_dir, ignore=shutil.ignore_patterns("*.md", ".*"))
            out_file = out_dir / "index.html"
            url = f"posts/{entry.name}/"
            root = "../../"  # 이 페이지에서 사이트 최상위까지의 상대 경로
        elif entry.suffix == ".md":
            md_file = entry
            out_file = SITE / "posts" / (entry.stem + ".html")
            url = f"posts/{entry.stem}.html"
            root = "../"
        else:
            continue

        meta, body = parse_post(md_file)
        page = render(
            post_tpl,
            root=root,
            title=html.escape(meta["title"]),
            description=html.escape(meta.get("description", meta["title"])),
            date=meta["date"],
            date_kr=korean_date(meta["date"]),
            content=body,
        )
        out_file.write_text(page, encoding="utf-8")
        posts.append({**meta, "url": url})

    # 2. 목록 페이지 생성: 날짜 내림차순으로 index.html에 끼워 넣는다
    posts.sort(key=lambda p: p["date"], reverse=True)
    items = "\n".join(
        f'      <article class="post-item">\n'
        f'        <time datetime="{p["date"]}">{p["date"]}</time>\n'
        f'        <a href="{p["url"]}">{html.escape(p["title"])}</a>\n'
        f"      </article>"
        for p in posts
    )
    (SITE / "index.html").write_text(
        render(index_tpl, post_list=items), encoding="utf-8"
    )

    # 3. 나머지는 그대로 복사
    shutil.copytree(ROOT / "css", SITE / "css")
    if (ROOT / "images").exists():
        shutil.copytree(ROOT / "images", SITE / "images")
    for name in STATIC_FILES:
        shutil.copy(ROOT / name, SITE / name)

    print(f"빌드 완료: 글 {len(posts)}개 → _site/")


def snapshot():
    """감시 대상 파일들의 수정 시각 목록 — 달라지면 재빌드한다."""
    mtimes = {}
    for target in WATCH_TARGETS:
        path = ROOT / target
        if path.is_dir():
            for f in path.rglob("*"):
                if f.is_file():
                    mtimes[str(f)] = f.stat().st_mtime
        elif path.exists():
            mtimes[str(path)] = path.stat().st_mtime
    return mtimes


def watch():
    print("파일 변경 감시 중... (중지: Ctrl+C)")
    state = snapshot()
    try:
        while True:
            time.sleep(0.5)
            current = snapshot()
            if current != state:
                state = current
                try:
                    build()
                except BuildError as e:
                    print(f"오류: {e} — 고치고 저장하면 다시 빌드합니다")
    except KeyboardInterrupt:
        print("\n감시를 종료합니다")


def serve():
    handler = partial(SimpleHTTPRequestHandler, directory=str(SITE))
    server = ThreadingHTTPServer(("localhost", PORT), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    print(f"미리보기: http://localhost:{PORT}")
    watch()


def main():
    try:
        build()
    except BuildError as e:
        sys.exit(f"오류: {e}")
    if "--serve" in sys.argv:
        serve()
    elif "--watch" in sys.argv:
        watch()


if __name__ == "__main__":
    main()
