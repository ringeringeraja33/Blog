# Blog 写作与发布

文章统一放在 `posts/`，可复制 `posts/_template.md` 后开始写作。文件名建议使用 `YYYY-MM-DD-英文或中文短名.md`；`title` 和 `date` 必填，`draft: true` 不会发布，改为 `false` 后才会进入文章列表。

图片放在 `assets/`，正文使用标准 Markdown 路径，例如 `![说明](../assets/example.jpg)`。构建时图片会复制到发布目录。提交并推送到 `main` 后，GitHub Actions 会生成文章页面并发布到 GitHub Pages。发布前可在本地执行：

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build.py
```

生成结果位于 `docs/`。不要直接编辑 `docs/posts/*.html`，它们会在下次构建时重建。
