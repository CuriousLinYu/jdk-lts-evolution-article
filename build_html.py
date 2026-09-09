# -*- coding: utf-8 -*-
"""JDK 演进文章 HTML 单页构建脚本：md -> 精美单页 HTML"""
import os
import re

import markdown

BASE = os.path.dirname(os.path.abspath(__file__))
MD_FILE = r'c:/Users/lintyu/IdeaProjects/mba/blog/2026-09-09-JDK版本演进四代LTS关键跃迁.md'
OUT_FILE = os.path.join(BASE, 'index.html')

# 配图插入点：{章节标题锚文本: (图片文件, 图注)}
IMAGE_SPOTS = [
    ('## 二、版本全景：定位、节奏与许可证', 'timeline.png', 'JDK 四大 LTS 发布时间线'),
    ('## 三、语言特性演进', 'stream-pipeline.png', 'Stream 管道：惰性中间操作 + 终端操作触发执行'),
    ('### 4.5 选型速查', 'gc-choice.png', 'GC 选型速览：按延迟与吞吐诉求分流'),
    ('## 六、JIT 与启动性能', 'jit-tiers.png', 'JIT 分层编译：解释器 → C1 → C2 逐级优化'),
]


def main():
    with open(MD_FILE, encoding='utf-8') as f:
        text = f.read()

    # 去 front matter
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)

    # 插入配图
    for anchor, img, caption in IMAGE_SPOTS:
        img_block = f'\n\n![{caption}](assets/{img})\n\n*{caption}*\n'
        if anchor in text:
            text = text.replace(anchor, anchor + img_block, 1)
            print(f'[img] inserted at {anchor}')
        else:
            print(f'[warn] anchor not found: {anchor}')

    # 生成 TOC（h2/h3）
    toc_items = []
    for line in text.splitlines():
        m = re.match(r'^(#{2,3})\s+(.+)$', line)
        if m:
            level = len(m.group(1)) - 1  # h2->1, h3->2
            title = m.group(2).strip()
            anchor = slugify(title)
            toc_items.append((level, title, anchor))
    toc_html = build_toc(toc_items)

    body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'sane_lists'])

    # 给正文标题补 id，与 TOC 锚点对齐
    for level, title, anchor in toc_items:
        tag = f'h{level + 1}'
        body = body.replace(f'<{tag}>{title}</{tag}>', f'<{tag} id="{anchor}">{title}</{tag}>', 1)

    # 标题与元信息
    title = 'JDK 8 → 17 → 21 → 25：四代 LTS 的关键跃迁与升级实战'

    html = render_template(title=title, toc=toc_html, body=body)

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'[done] {OUT_FILE} ({len(html)} bytes, {len(toc_items)} toc items)')


def slugify(title):
    """中文标题生成锚点：保留中英文数字，其余转横线"""
    s = re.sub(r'[^\w\u4e00-\u9fff]+', '-', title).strip('-')
    return s or 'sec'


def build_toc(items):
    """按层级生成嵌套 TOC"""
    if not items:
        return ''
    parts = []
    cur = 0
    for level, title, anchor in items:
        if level > cur:
            parts.append('<ul class="toc-sub">' * (level - cur))
        elif level < cur:
            parts.append('</ul>' * (cur - level))
        cur = level
        parts.append(f'<li><a href="#{anchor}">{title}</a></li>')
    parts.append('</ul>' * cur)
    return '\n'.join(parts)


def render_template(title, toc, body):
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css">
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
<style>
:root {{
  --bg: #0d1117;
  --bg-soft: #161b22;
  --border: #30363d;
  --text: #e6edf3;
  --text-dim: #8b949e;
  --accent: #ff7a45;
  --accent-2: #58a6ff;
  --code-bg: #0b0f14;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  line-height: 1.75;
}}
#progress {{
  position: fixed; top: 0; left: 0; height: 3px; width: 0;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  z-index: 100;
}}
.hero {{
  position: relative; overflow: hidden;
  text-align: center; padding: 96px 24px 72px;
  border-bottom: 1px solid var(--border);
}}
.hero img.bg {{
  position: absolute; inset: 0; width: 100%; height: 100%;
  object-fit: cover; opacity: .28; filter: blur(2px);
}}
.hero h1 {{
  position: relative; font-size: clamp(1.6rem, 4vw, 2.6rem);
  max-width: 900px; margin: 0 auto 16px; letter-spacing: .5px;
}}
.hero .meta {{
  position: relative; color: var(--text-dim); font-size: .92rem;
}}
.hero .meta a {{ color: var(--accent-2); text-decoration: none; }}
.layout {{ display: flex; max-width: 1280px; margin: 0 auto; gap: 40px; padding: 0 24px; }}
nav.toc {{
  flex: 0 0 260px; position: sticky; top: 24px; align-self: flex-start;
  max-height: calc(100vh - 48px); overflow-y: auto;
  padding: 20px 16px; background: var(--bg-soft);
  border: 1px solid var(--border); border-radius: 12px;
  font-size: .88rem;
}}
nav.toc h2 {{ font-size: .8rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }}
nav.toc ul {{ list-style: none; }}
nav.toc li {{ margin: 4px 0; }}
nav.toc a {{
  color: var(--text-dim); text-decoration: none; display: block;
  padding: 3px 8px; border-radius: 6px; transition: all .15s;
}}
nav.toc a:hover {{ color: var(--text); background: rgba(255,122,69,.12); }}
.toc-sub {{ padding-left: 14px !important; border-left: 1px solid var(--border); margin-left: 6px; }}
main {{
  flex: 1; min-width: 0; padding: 40px 0 80px;
  font-size: 1rem;
}}
main h1 {{ font-size: 1.7rem; margin: 48px 0 16px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }}
main h2 {{ font-size: 1.45rem; margin: 44px 0 14px; }}
main h3 {{ font-size: 1.2rem; margin: 32px 0 12px; color: var(--accent-2); }}
main p {{ margin: 14px 0; }}
main a {{ color: var(--accent-2); }}
main ul, main ol {{ margin: 12px 0 12px 24px; }}
main li {{ margin: 6px 0; }}
main blockquote {{
  margin: 18px 0; padding: 12px 18px;
  background: rgba(255,122,69,.07);
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0; color: var(--text-dim);
}}
main code {{
  font-family: 'JetBrains Mono', Consolas, 'Courier New', monospace;
  font-size: .88em; background: var(--code-bg);
  padding: 2px 6px; border-radius: 5px; color: #ffab70;
}}
main pre {{
  margin: 18px 0; padding: 18px; overflow-x: auto;
  background: var(--code-bg); border: 1px solid var(--border);
  border-radius: 10px; font-size: .86rem; line-height: 1.6;
}}
main pre code {{ background: none; padding: 0; color: inherit; }}
main table {{
  width: 100%; border-collapse: collapse; margin: 18px 0;
  font-size: .92rem; display: block; overflow-x: auto;
}}
main th, main td {{
  border: 1px solid var(--border); padding: 9px 14px; text-align: left;
}}
main th {{ background: var(--bg-soft); color: var(--accent-2); white-space: nowrap; }}
main img {{
  display: block; max-width: 100%; margin: 24px auto;
  border-radius: 12px; border: 1px solid var(--border);
  box-shadow: 0 8px 32px rgba(0,0,0,.4);
}}
main em {{ color: var(--text-dim); }}
main img + em {{ display: block; text-align: center; margin-top: -16px; font-size: .85rem; }}
#top-btn {{
  position: fixed; right: 28px; bottom: 28px; width: 44px; height: 44px;
  border-radius: 50%; border: 1px solid var(--border); background: var(--bg-soft);
  color: var(--text-dim); font-size: 1.2rem; cursor: pointer; display: none;
  align-items: center; justify-content: center; z-index: 99;
}}
#top-btn:hover {{ color: var(--accent); border-color: var(--accent); }}
footer {{
  text-align: center; padding: 32px 24px; border-top: 1px solid var(--border);
  color: var(--text-dim); font-size: .85rem;
}}
@media (max-width: 960px) {{
  .layout {{ flex-direction: column; }}
  nav.toc {{ position: static; flex: none; max-height: none; }}
}}
</style>
</head>
<body>
<div id="progress"></div>

<header class="hero">
  <img class="bg" src="assets/cover.png" alt="cover">
  <h1>{title}</h1>
  <div class="meta">2026-09-09 · 30 分钟阅读 · 参考自 <a href="https://juejin.cn/post/7625237255017299987" target="_blank" rel="noopener">掘金《JDK 8 → 17 → 21 → 25》</a> 重述改写</div>
</header>

<div class="layout">
  <nav class="toc">
    <h2>目录</h2>
    <ul>
{toc}
    </ul>
  </nav>
  <main>
{body}
  </main>
</div>

<button id="top-btn" title="回到顶部">↑</button>

<footer>
  本文为原创重述，参考来源：<a href="https://juejin.cn/post/7625237255017299987" target="_blank" rel="noopener">juejin.cn/post/7625237255017299987</a>
</footer>

<script>
hljs.highlightAll();
// 阅读进度条
const bar = document.getElementById('progress');
addEventListener('scroll', () => {{
  const h = document.documentElement;
  bar.style.width = (h.scrollTop / (h.scrollHeight - h.clientHeight) * 100) + '%';
}});
// 回到顶部按钮
const topBtn = document.getElementById('top-btn');
addEventListener('scroll', () => {{
  topBtn.style.display = scrollY > 600 ? 'flex' : 'none';
}});
topBtn.onclick = () => scrollTo({{ top: 0, behavior: 'smooth' }});
</script>
</body>
</html>'''


if __name__ == '__main__':
    main()
