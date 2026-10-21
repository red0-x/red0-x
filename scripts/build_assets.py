#!/usr/bin/env python3
"""Builds assets/*.svg for the profile README in the red0xx v2 sticker style.

Tokens come from red0xx-web app/globals.css (v2-site). Fonts are subset and
embedded as base64 because GitHub serves SVGs through <img>, which can't load
external fonts. Needs: fonttools. Run: python3 scripts/build_assets.py
"""
import base64, io, pathlib, urllib.request
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
CACHE = pathlib.Path.home() / ".cache" / "red0x-profile"
AVATAR = pathlib.Path.home() / "Documents/GitHub/red0xx-web/public/stickers/avatar.png"

RED900, RED700, RED600, RED500, RED300 = "#6E0B0F", "#B3141C", "#C4161F", "#E01E2C", "#F26B74"
LOGO_RED, PAPER, INK, SHADOW, MANGO = "#E64949", "#FAF7F2", "#111111", "#190306", "#FFB000"
INK_DIM = "#3A3A3A"

FONTS = {
    "mona": "https://github.com/google/fonts/raw/main/ofl/monasans/MonaSans%5Bwdth,wght%5D.ttf",
    "hand": "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat%5Bwght%5D.ttf",
}
# simpleicons slugs, recoloured red. Ableton isn't on simpleicons, drawn by hand below.
STACK = [
    ["typescript", "javascript", "react", "nextdotjs", "tailwindcss", "nodedotjs", "bun", "electron", "html5", "css"],
    ["python", "cplusplus", "go", "redis", "docker", "linux", "archlinux", "git", "vercel", "ableton"],
]
ABLETON = '<path d="M2 4h2v16H2zM6 4h2v16H6zM10 4h2v16h-2zM14 4h2v16h-2zM18 6h4v2h-4zM18 10h4v2h-4zM18 14h4v2h-4zM18 18h4v2h-4z"/>'
ROLES = ["dev", "homelabber", "music producer", "chart watcher", "linguist"]
SECTIONS = {"about": "about me", "stack": "stack", "stats": "stats", "commits": "commits", "projects": "projects"}


def font(name, text, axes=None):
    """Return (base64 woff, TTFont) subset to `text`."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{name}.ttf"
    if not path.exists():
        urllib.request.urlretrieve(FONTS[name], path)
    f = TTFont(path)
    if axes:
        f = instantiateVariableFont(f, axes)
    opts = Options()
    opts.flavor = "woff"
    sub = Subsetter(opts)
    sub.populate(text=text)
    sub.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff"
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode(), f


def width(f, text, size):
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    return sum(hmtx[cmap[ord(c)]][0] for c in text) * size / f["head"].unitsPerEm


def face(family, b64):
    return f"@font-face{{font-family:{family};src:url(data:font/woff;base64,{b64}) format('woff')}}"


def extrude(text_el, depth, color):
    """Stepped 1px hard offset, same trick as .rail-name__handle on the site."""
    return "".join(f'<g transform="translate({i} {i})" fill="{color}">{text_el}</g>' for i in range(depth, 0, -1))


def sticker(x, y, w, h, rot, body, r=22, cut=8, fill=PAPER, shadow=8):
    cx, cy = x + w / 2, y + h / 2
    return (
        f'<g transform="rotate({rot} {cx} {cy})">'
        f'<rect x="{x - cut + shadow}" y="{y - cut + shadow}" width="{w + 2 * cut}" height="{h + 2 * cut}" rx="{r + cut}" fill="{SHADOW}"/>'
        f'<rect x="{x - cut}" y="{y - cut}" width="{w + 2 * cut}" height="{h + 2 * cut}" rx="{r + cut}" fill="#fff"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>{body}</g>'
    )


def banner():
    """Avatar + wordmark + typing role. Nothing else."""
    handle = "red0-x"
    mona_text = handle + "@.·" + "".join(ROLES) + "> _"
    mona_b64, mona = font("mona", mona_text, {"wght": 900, "wdth": 112.5})
    mono_b64, mono = font("mona", mona_text, {"wght": 600, "wdth": 75})

    av = base64.b64encode(AVATAR.read_bytes()).decode()
    big, hx, hy = 118, 268, 158
    handle_el = f'<text x="{hx}" y="{hy}" font-family="M" font-size="{big}" letter-spacing="-3">{handle}</text>'
    H = 270

    # typing roles: each word gets a 3s slot in a 15s loop, revealed by a stepped clip
    n, slot = len(ROLES), 3
    role_size, role_x, role_y = 30, 290, 214
    role_css, role_els = [], []
    for i, role in enumerate(ROLES):
        rw = width(mono, role, role_size) + 6
        a0 = i / n * 100
        a1 = a0 + 0.30 / n * 100  # typed by 30% of the slot
        a2 = a0 + 0.80 / n * 100
        a3 = a0 + 0.95 / n * 100
        role_css.append(
            f"@keyframes t{i}{{0%,{a0:.2f}%{{transform:scaleX(0)}}{a1:.2f}%,{a2:.2f}%{{transform:scaleX(1)}}{a3:.2f}%,100%{{transform:scaleX(0)}}}}"
            f"#c{i} rect{{transform-box:fill-box;transform-origin:left;animation:t{i} {n * slot}s steps({len(role)}) infinite}}"
        )
        role_els.append(
            f'<clipPath id="c{i}"><rect x="{role_x + 34}" y="{role_y - 30}" width="{rw:.0f}" height="42"/></clipPath>'
            f'<text clip-path="url(#c{i})" x="{role_x + 34}" y="{role_y}" font-family="S" font-size="{role_size}" fill="#fff">{role}</text>'
        )
    pill_w = 26 + max(width(mono, r, role_size) for r in ROLES) + 30
    W = max(hx + width(mona, handle, big), role_x + pill_w) + 44

    css = (
        face("M", mona_b64) + face("S", mono_b64)
        + "@keyframes pop{0%,70%,100%{transform:translate(0,0)}78%,92%{transform:translate(-5px,-5px)}}"
        + "@keyframes deep{0%,70%,100%{opacity:0}78%,92%{opacity:1}}"
        + ".face{animation:pop 4s cubic-bezier(.3,1.6,.5,1) infinite}.deep{animation:deep 4s cubic-bezier(.3,1.6,.5,1) infinite}"
        + "@media (prefers-reduced-motion:reduce){*{animation:none!important}"
        + ",".join(f"#c{i} rect" for i in range(1, len(ROLES))) + "{transform:scaleX(0)}}"
        + "".join(role_css)
    )

    dots = '<pattern id="d" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.6" fill="#fff" opacity=".09"/></pattern>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="red0-x: {", ".join(ROLES)}">
<title>red0-x</title><style>{css}</style>
<defs>{dots}<clipPath id="av"><rect x="44" y="56" width="160" height="160" rx="16"/></clipPath></defs>
<rect width="{W}" height="{H}" rx="26" fill="{RED600}"/><rect width="{W}" height="{H}" rx="26" fill="url(#d)"/>
{sticker(44, 56, 160, 160, -3, f'<image href="data:image/png;base64,{av}" x="44" y="56" width="160" height="160" clip-path="url(#av)"/>', r=16, cut=8)}
<g class="deep">{extrude(handle_el, 6, SHADOW)}</g>
{extrude(handle_el, 1, SHADOW)}
<g class="face" fill="#fff">{handle_el}</g>
<rect x="{role_x}" y="{role_y - 32}" width="{pill_w:.0f}" height="48" rx="12" fill="{RED900}"/>
<text x="{role_x + 14}" y="{role_y}" font-family="S" font-size="{role_size}" fill="{RED300}">&gt;</text>
{"".join(role_els)}
</svg>'''


def label(key, text):
    size = 40
    b64, f = font("mona", text, {"wght": 900, "wdth": 112.5})
    tw = width(f, text, size)
    pad, cut, sh = 24, 6, 6
    w, h = tw + pad * 2, 60
    W, H = w + 2 * cut + sh + 28, h + 2 * cut + sh + 28
    x, y = cut + 12, cut + 12
    t = f'<text x="{x + pad}" y="{y + 43}" font-family="M" font-size="{size}" letter-spacing="-1">{text}</text>'
    body = f'<g fill="{SHADOW}" transform="translate(3 3)">{t}</g><g fill="{RED600}">{t}</g>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="{text}">'
           f'<title>{text}</title><style>{face("M", b64)}</style>'
           + sticker(x, y, w, h, -1.5 if len(key) % 2 else 1.2, body, r=14, cut=cut, shadow=sh) + "</svg>")
    return svg


def icon(slug):
    if slug == "ableton":
        return ABLETON
    req = urllib.request.Request(f"https://cdn.simpleicons.org/{slug}", headers={"User-Agent": "curl/8"})
    svg = urllib.request.urlopen(req).read().decode()
    return svg[svg.index("<path"):svg.rindex("</svg>")]


def stack():
    tile, gap, pad = 64, 22, 18
    cols = max(len(r) for r in STACK)
    W = pad * 2 + cols * tile + (cols - 1) * gap + 6
    H = pad * 2 + len(STACK) * tile + (len(STACK) - 1) * gap + 6
    rots = [-3, 2, -1.5, 4, -2, 1]
    out = []
    for ri, row in enumerate(STACK):
        x0 = (W - (len(row) * tile + (len(row) - 1) * gap)) / 2
        for ci, slug in enumerate(row):
            x, y = x0 + ci * (tile + gap), pad + ri * (tile + gap)
            s = (tile - 28) / 24
            glyph = f'<g transform="translate({x + 14} {y + 14}) scale({s:.3f})" fill="{RED600}">{icon(slug)}</g>'
            out.append(sticker(x, y, tile, tile, rots[(ri * 3 + ci) % len(rots)], glyph, r=14, cut=4, shadow=5))
    names = ", ".join(s for r in STACK for s in r)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="{names}">'
            f'<title>{names}</title>{"".join(out)}</svg>')


def contributions():
    """Contribution heatmap, same data the snake used. Actions is locked on this
    account (billing), so this is generated locally instead of nightly."""
    import json, subprocess
    q = ('query{user(login:"red0-x"){contributionsCollection{contributionCalendar'
         '{totalContributions weeks{contributionDays{date contributionCount weekday}}}}}}')
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"],
                         capture_output=True, text=True, check=True).stdout
    cal = json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks, total = cal["weeks"], cal["totalContributions"]
    ramp = ["#F1ECE4", "#FBE7E8", "#F26B74", "#E01E2C", "#B3141C", "#6E0B0F"]
    cell, gap, pad, top = 12, 3, 20, 62
    cols = len(weeks)
    w = pad * 2 + cols * (cell + gap) - gap
    h = pad + top + 7 * (cell + gap) - gap
    f_b64, f = font("mona", "contributions in the last yearJanFebMarAprMayJunJulAugSepOctNovDec0123456789", {"wght": 700, "wdth": 100})
    out_el = [f'<text x="{pad}" y="32" font-family="M" font-size="18" fill="{INK}">{total} contributions in the last year</text>']
    seen = set()
    for ci, wk in enumerate(weeks):
        days = wk["contributionDays"]
        for d in days:
            x = pad + ci * (cell + gap)
            y = top + d["weekday"] * (cell + gap)
            n = d["contributionCount"]
            lvl = 0 if n == 0 else min(5, 1 + (n > 1) + (n > 3) + (n > 6) + (n > 11))
            out_el.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{ramp[lvl]}"/>')
        m = days[0]["date"][5:7]
        mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(m) - 1]
        if mon not in seen and days[0]["date"][8:10] <= "07":
            seen.add(mon)
            out_el.append(f'<text x="{pad + ci * (cell + gap)}" y="{top - 8}" font-family="M" font-size="11" fill="{INK_DIM}">{mon}</text>')
    W, H = w + 12, h + 12
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="contribution graph, {total} contributions in the last year">'
            f'<title>contributions</title><style>{face("M", f_b64)}</style>'
            f'<rect x="6" y="6" width="{w}" height="{h}" rx="16" fill="{SHADOW}"/>'
            f'<rect width="{w}" height="{h}" rx="16" fill="#FFF"/>'
            f'<rect x="6" y="6" width="{w - 12}" height="{h - 12}" rx="12" fill="{PAPER}"/>'
            f'{"".join(out_el)}</svg>')


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "banner.svg").write_text(banner())
    (OUT / "stack-icons.svg").write_text(stack())
    (OUT / "commits-graph.svg").write_text(contributions())
    for k, v in SECTIONS.items():
        (OUT / f"{k}.svg").write_text(label(k, v))
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.stat().st_size:>8}  {p.name}")
