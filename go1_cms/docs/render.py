"""Markdown → the HTML a docs article is served with.

An article is written in Markdown and rendered once, when it is saved
(Doc Article.validate), so the public /docs route only reads stored HTML and
never parses Markdown on a visitor's request. `render(md, space)` returns:

    html     sanitised HTML with stable heading ids and highlighted code
    text     plain text of the body, for search
    outline  [{"id", "text", "level"}] for every h2 and h3, for "On this page"

What the Markdown may contain beyond the basics:

* fenced code blocks with a language (```python) → highlighted by Pygments
  (the stylesheet comes from `code_css()`);
* tables, ~~strike~~, task lists and footnotes;
* callouts, GitHub style — a blockquote whose first line is [!NOTE], [!TIP],
  [!WARNING] or [!IMPORTANT];
* links between articles written relative to the article: `[x](../slug)` or
  `[x](./slug)` point at another article of the same space and are rewritten
  to `/docs/<space>/<slug>`, so moving a whole space keeps its links working.

The output is cleaned with bleach against an explicit allowlist: an editor's
Markdown can carry raw HTML, and a script in it must never reach a visitor.
"""

import html as _html
import re

import bleach
import markdown2

EXTRAS = {
	"fenced-code-blocks": {"cssclass": "codehilite"},
	"tables": None,
	"header-ids": None,
	"strike": None,
	"task_list": None,
	"footnotes": None,
	"markdown-in-html": None,
	"cuddled-lists": None,
}

ALLOWED_TAGS = {
	"a", "abbr", "b", "blockquote", "br", "code", "dd", "del", "details", "div", "dl", "dt", "em",
	"figcaption", "figure", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "input", "kbd", "li",
	"mark", "ol", "p", "pre", "s", "span", "strong", "sub", "summary", "sup", "table", "tbody", "td",
	"tfoot", "th", "thead", "tr", "u", "ul", "video", "source", "iframe",
}
ALLOWED_ATTRS = {
	"*": ["class", "id", "title"],
	"a": ["href", "title", "target", "rel"],
	"img": ["src", "alt", "title", "width", "height", "loading"],
	"input": ["type", "checked", "disabled"],
	"video": ["src", "controls", "poster", "width", "height", "muted", "loop", "playsinline"],
	"source": ["src", "type"],
	"iframe": ["src", "width", "height", "allow", "allowfullscreen", "frameborder", "loading"],
	"ol": ["start"],
	"td": ["colspan", "rowspan"],
	"th": ["colspan", "rowspan"],
}
ALLOWED_PROTOCOLS = ["http", "https", "mailto", "tel"]
# Embeds are limited to the video hosts people actually paste.
IFRAME_HOSTS = ("https://www.youtube.com/embed/", "https://www.youtube-nocookie.com/embed/",
                "https://player.vimeo.com/video/", "https://www.loom.com/embed/")

CALLOUT_KINDS = {"NOTE": "Note", "TIP": "Tip", "WARNING": "Warning", "IMPORTANT": "Important", "CAUTION": "Caution"}
_CALLOUT_START = re.compile(r"^>\s*\[!(%s)\]\s*$" % "|".join(CALLOUT_KINDS), re.I)
_HEADING = re.compile(r"<h([23])\s+id=\"([^\"]+)\"[^>]*>(.*?)</h\1>", re.S)
_TAGS = re.compile(r"<[^>]+>")
_ALIGN_STYLE = re.compile(r"\sstyle=\"text-align:\s*(left|right|center);?\"")
_RELATIVE_HREF = re.compile(r"href=\"\.{1,2}/([a-z0-9-]+)(#[^\"]*)?\"")
_IFRAME = re.compile(r"<iframe\b[^>]*\bsrc=\"([^\"]*)\"[^>]*>(?:</iframe>)?", re.I)
# bleach strips a disallowed tag but keeps its text; a script's text is never content.
_DROP_BLOCKS = re.compile(r"<(script|style|noscript|template)\b.*?</\1\s*>", re.I | re.S)


def _callouts(md):
	"""`> [!NOTE]` blockquotes → a div the stylesheet draws as a callout box."""
	lines = md.split("\n")
	out, i = [], 0
	while i < len(lines):
		m = _CALLOUT_START.match(lines[i].strip())
		if not m:
			out.append(lines[i])
			i += 1
			continue
		kind = m.group(1).upper()
		body = []
		i += 1
		while i < len(lines) and lines[i].lstrip().startswith(">"):
			body.append(re.sub(r"^\s*>\s?", "", lines[i]))
			i += 1
		out.append('<div class="callout callout-%s" markdown="1">' % kind.lower())
		out.append("")
		out.append('<p class="callout-title">%s</p>' % CALLOUT_KINDS[kind])
		out.append("")
		out.extend(body)
		out.append("")
		out.append("</div>")
		out.append("")
	return "\n".join(out)


def _keep_safe_iframes(html):
	"""Drop any iframe that does not point at an allowed video host."""
	def check(m):
		return m.group(0) if m.group(1).startswith(IFRAME_HOSTS) else ""
	return _IFRAME.sub(check, html)


def _plain(fragment):
	return _html.unescape(_TAGS.sub("", fragment or "")).strip()


def article_route(space, slug):
	return "/docs/%s/%s" % (space, slug) if space else "/docs/%s" % slug


def render(md, space=None):
	"""Render one article body. Never raises on odd input: the worst case is an
	empty article, not a save that fails."""
	source = (md or "").replace("\r\n", "\n")
	if not source.strip():
		return {"html": "", "text": "", "outline": []}

	raw = markdown2.markdown(_callouts(source), extras=EXTRAS)
	raw = str(raw)
	# Table alignment arrives as an inline style; a class keeps style attributes off the allowlist.
	raw = _ALIGN_STYLE.sub(lambda m: ' class="ta-%s"' % m.group(1), raw)
	if space:
		raw = _RELATIVE_HREF.sub(lambda m: 'href="%s%s"' % (article_route(space, m.group(1)), m.group(2) or ""), raw)
	raw = _keep_safe_iframes(_DROP_BLOCKS.sub("", raw))

	clean = bleach.clean(raw, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, protocols=ALLOWED_PROTOCOLS, strip=True)
	clean = clean.replace("<img ", '<img loading="lazy" ')
	# External links open in a new tab; links inside the site do not.
	clean = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', clean)

	outline = [{"level": int(level), "id": hid, "text": _plain(inner)} for level, hid, inner in _HEADING.findall(clean)]
	return {"html": clean, "text": re.sub(r"\s+", " ", _plain(clean)), "outline": outline}


def code_css(style="default"):
	"""Pygments rules for highlighted code, scoped to .codehilite."""
	from pygments.formatters import HtmlFormatter

	return HtmlFormatter(style=style).get_style_defs(".codehilite")


SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def slugify(text):
	"""A URL slug from a title: lower-case words joined by dashes."""
	s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
	return s[:80].strip("-")


def is_slug(value):
	return bool(value) and bool(SLUG.match(value)) and len(value) <= 80
