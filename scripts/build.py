#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
ASSETS_DIR = ROOT / "assets"
DOCS_DIR = ROOT / "docs"
OUTPUT_DIR = DOCS_DIR / "posts"
OUTPUT_ASSETS_DIR = DOCS_DIR / "assets"
INDEX_PATH = DOCS_DIR / "index.html"
POSTS_BLOCK = re.compile(r"(?s)<!-- POSTS:START -->.*?<!-- POSTS:END -->")


@dataclass
class Post:
    source: Path
    slug: str
    title: str
    published: date
    description: str
    tags: list[str]
    body: str


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.relative_to(ROOT)} 缺少 YAML 头部")
    try:
        raw_meta, body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise ValueError(f"{path.relative_to(ROOT)} 的 YAML 头部没有结束标记") from exc
    meta: dict[str, str] = {}
    for line in raw_meta.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{path.relative_to(ROOT)} 的头部格式错误：{line}")
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body.strip()


def make_slug(path: Path) -> str:
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem.lower())
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff-]+", "-", slug).strip("-")
    if not slug:
        raise ValueError(f"{path.relative_to(ROOT)} 无法生成文章网址")
    return slug


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        meta, body = parse_frontmatter(path)
        if meta.get("draft", "false").lower() in {"true", "yes", "1"}:
            continue
        title = meta.get("title", "").strip()
        published_text = meta.get("date", "").strip()
        if not title or not published_text:
            raise ValueError(f"{path.relative_to(ROOT)} 必须填写 title 和 date")
        try:
            published = date.fromisoformat(published_text)
        except ValueError as exc:
            raise ValueError(f"{path.relative_to(ROOT)} 的 date 必须是 YYYY-MM-DD") from exc
        tags_text = meta.get("tags", "").strip().strip("[]")
        tags = [item.strip().strip('"').strip("'") for item in tags_text.split(",") if item.strip()]
        posts.append(
            Post(
                source=path,
                slug=make_slug(path),
                title=title,
                published=published,
                description=meta.get("description", "").strip(),
                tags=tags,
                body=body,
            )
        )
    slugs = [post.slug for post in posts]
    if len(slugs) != len(set(slugs)):
        raise ValueError("存在重复的文章网址，请调整文件名")
    return sorted(posts, key=lambda post: post.published, reverse=True)


def render_tags(tags: list[str]) -> str:
    if not tags:
        return ""
    items = "".join(f"<li>{html.escape(tag)}</li>" for tag in tags)
    return f'<ul class="post-tags" aria-label="标签">{items}</ul>'


def render_index(posts: list[Post]) -> None:
    source = INDEX_PATH.read_text(encoding="utf-8")
    if not POSTS_BLOCK.search(source):
        raise ValueError("docs/index.html 缺少文章列表标记")
    if posts:
        items = []
        for post in posts:
            summary = f'<p class="post-summary">{html.escape(post.description)}</p>' if post.description else ""
            items.append(
                "\n".join(
                    [
                        '<article class="post-item">',
                        '  <header class="post-head">',
                        f'    <h2 class="post-title"><a href="./posts/{post.slug}.html">{html.escape(post.title)}</a></h2>',
                        f'    <time class="post-date" datetime="{post.published.isoformat()}">{post.published.isoformat()}</time>',
                        "  </header>",
                        f"  {summary}" if summary else "",
                        f"  {render_tags(post.tags)}" if post.tags else "",
                        f'  <a class="read-link" href="./posts/{post.slug}.html">阅读全文 →</a>',
                        "</article>",
                    ]
                )
            )
        content = '<div class="post-list">\n' + "\n".join(items) + "\n</div>"
    else:
        content = '<div class="empty-posts"><p>文章稍后整理。</p></div>'
    replacement = f"<!-- POSTS:START -->\n        {content}\n        <!-- POSTS:END -->"
    INDEX_PATH.write_text(POSTS_BLOCK.sub(replacement, source), encoding="utf-8")


def render_article(post: Post) -> str:
    body = markdown.markdown(
        post.body,
        extensions=["extra", "footnotes", "sane_lists", "smarty"],
        output_format="html5",
    )
    description_meta = html.escape(post.description, quote=True)
    description = f'<p class="article-description">{html.escape(post.description)}</p>' if post.description else ""
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{description_meta}">
    <title>{html.escape(post.title)} · Ævum</title>
    <link rel="stylesheet" href="../style.css">
  </head>
  <body>
    <header class="site-header">
      <div class="header-inner">
        <div class="site-identity">
          <h1 class="site-title"><a href="../index.html">Ævum</a></h1>
          <p class="site-tagline">軌跡</p>
        </div>
        <nav class="header-nav" aria-label="主要导航"><a href="../index.html">posts</a></nav>
      </div>
    </header>
    <main class="article-shell">
      <a class="article-back" href="../index.html">← 返回文章列表</a>
      <article>
        <header class="article-header">
          <h1 class="article-title">{html.escape(post.title)}</h1>
          <time class="post-date" datetime="{post.published.isoformat()}">{post.published.isoformat()}</time>
          {description}
          {render_tags(post.tags)}
        </header>
        <div class="article-body">{body}</div>
      </article>
    </main>
  </body>
</html>
"""


def build() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for old_page in OUTPUT_DIR.glob("*.html"):
        old_page.unlink()
    posts = load_posts()
    render_index(posts)
    for post in posts:
        (OUTPUT_DIR / f"{post.slug}.html").write_text(render_article(post), encoding="utf-8")
    OUTPUT_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for old_asset in OUTPUT_ASSETS_DIR.iterdir():
        if old_asset.name != ".gitkeep":
            if old_asset.is_dir():
                shutil.rmtree(old_asset)
            else:
                old_asset.unlink()
    for asset in ASSETS_DIR.iterdir():
        if asset.name == ".gitkeep":
            continue
        target = OUTPUT_ASSETS_DIR / asset.name
        if asset.is_dir():
            shutil.copytree(asset, target)
        else:
            shutil.copy2(asset, target)
    print(f"已生成 {len(posts)} 篇文章")


if __name__ == "__main__":
    build()
