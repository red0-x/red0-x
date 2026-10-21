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

FONTS = {
    "mona": "https://github.com/google/fonts/raw/main/ofl/monasans/MonaSans%5Bwdth,wght%5D.ttf",
    "marker": "https://github.com/google/fonts/raw/main/apache/permanentmarker/PermanentMarker-Regular.ttf",
}
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
    W, H = 1200, 420
    handle = "red0-x"
    mona_text = handle + "HELLOmynameis@.·" + "".join(ROLES) + "> _" + "projects I will never touch again" + "redox.cool"
    mona_b64, mona = font("mona", mona_text, {"wght": 900, "wdth": 112.5})
    mono_b64, mono = font("mona", mona_text, {"wght": 600, "wdth": 75})
    marker_b64, _ = font("marker", "red0xx")

    av = base64.b64encode(AVATAR.read_bytes()).decode()
    big = 132
    hx, hy = 330, 210
    handle_el = f'<text x="{hx}" y="{hy}" font-family="M" font-size="{big}" letter-spacing="-4">{handle}</text>'

    # typing roles: each word gets a 3s slot in a 15s loop, revealed by a stepped clip
    n, slot = len(ROLES), 3
    role_size = 34
    role_css, role_els = [], []
    for i, role in enumerate(ROLES):
        rw = width(mono, role, role_size) + 4
        a0 = i / n * 100
        a1 = a0 + 0.30 / n * 100  # typed by 30% of the slot
        a2 = a0 + 0.80 / n * 100
        a3 = a0 + 0.95 / n * 100
        role_css.append(
            f"@keyframes t{i}{{0%,{a0:.2f}%{{transform:scaleX(0)}}{a1:.2f}%,{a2:.2f}%{{transform:scaleX(1)}}{a3:.2f}%,100%{{transform:scaleX(0)}}}}"
            f"#c{i} rect{{transform-box:fill-box;transform-origin:left;animation:t{i} {n * slot}s steps({len(role)}) infinite}}"
        )
        role_els.append(
            f'<clipPath id="c{i}"><rect x="402" y="232" width="{rw:.0f}" height="48"/></clipPath>'
            f'<text clip-path="url(#c{i})" x="402" y="268" font-family="S" font-size="{role_size}" fill="#fff">{role}</text>'
        )
    pill_w = 402 - 352 + max(width(mono, r, role_size) for r in ROLES) + 44

    css = (
        face("M", mona_b64) + face("S", mono_b64) + face("PM", marker_b64)
        + "@keyframes pop{0%,70%,100%{transform:translate(0,0)}78%,92%{transform:translate(-5px,-5px)}}"
        + "@keyframes deep{0%,70%,100%{opacity:0}78%,92%{opacity:1}}"
        + ".face{animation:pop 4s cubic-bezier(.3,1.6,.5,1) infinite}.deep{animation:deep 4s cubic-bezier(.3,1.6,.5,1) infinite}"
        + "@keyframes wob{0%,100%{transform:rotate(4deg)}50%{transform:rotate(1.5deg)}}"
        + ".tag{transform-box:fill-box;transform-origin:50% 0;animation:wob 5s ease-in-out infinite}"
        + "@keyframes draw{0%{stroke-dashoffset:900;fill-opacity:0}55%{stroke-dashoffset:0;fill-opacity:0}70%,90%{fill-opacity:1;stroke-dashoffset:0}100%{fill-opacity:1}}"
        + f".sig{{stroke:{INK};stroke-width:1.6;stroke-dasharray:900;animation:draw 6s ease-in-out infinite}}"
        + "@keyframes bob{0%,100%{transform:rotate(-7deg) translateY(0)}50%{transform:rotate(-5deg) translateY(-4px)}}"
        + ".mango{transform-box:fill-box;transform-origin:center;animation:bob 3.2s ease-in-out infinite}"
        + "@media (prefers-reduced-motion:reduce){*{animation:none!important}"
        + ",".join(f"#c{i} rect" for i in range(1, len(ROLES))) + "{transform:scaleX(0)}}"
        + "".join(role_css)
    )

    tag_x, tag_y, tag_w, tag_h = 905, 70, 240, 170
    nametag = (
        f'<g class="tag">' + sticker(tag_x, tag_y, tag_w, tag_h, 0,
            f'<path d="M{tag_x} {tag_y + 22}a22 22 0 0 1 22-22h{tag_w - 44}a22 22 0 0 1 22 22v40h-{tag_w}z" fill="{RED500}"/>'
            f'<text x="{tag_x + tag_w / 2}" y="{tag_y + 38}" text-anchor="middle" font-family="M" font-size="30" fill="#fff" letter-spacing="2">HELLO</text>'
            f'<text x="{tag_x + tag_w / 2}" y="{tag_y + 56}" text-anchor="middle" font-family="S" font-size="15" fill="#fff">my name is</text>'
            f'<text class="sig" x="{tag_x + tag_w / 2}" y="{tag_y + 135}" text-anchor="middle" font-family="PM" font-size="52" fill="{INK}">red0xx</text>',
            r=18) + "</g>"
    )

    mango_txt = "projects I will never touch again"
    mango_w = width(mono, mango_txt, 20) + 36
    mango = (
        f'<g class="mango">' + sticker(820, 318, mango_w, 44, 0,
            f'<text x="{820 + 18}" y="{318 + 29}" font-family="S" font-size="20" fill="{INK}">{mango_txt}</text>',
            r=22, cut=6, fill=MANGO, shadow=6) + "</g>"
    )

    dots = f'<pattern id="d" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.6" fill="#fff" opacity=".09"/></pattern>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="red0-x: {', '.join(ROLES)}">
<title>red0-x</title><style>{css}</style>
<defs>{dots}<clipPath id="av"><rect x="70" y="80" width="200" height="200" rx="18"/></clipPath></defs>
<rect width="{W}" height="{H}" rx="28" fill="{RED600}"/><rect width="{W}" height="{H}" rx="28" fill="url(#d)"/>
<path d="M0 {H - 34}H{W}V{H - 28}a28 28 0 0 1-28 28H28a28 28 0 0 1-28-28z" fill="{RED900}"/>
<text x="40" y="{H - 11}" font-family="S" font-size="16" fill="#fff" opacity=".72">security research · embedded · occasional web</text>
<text x="{W - 40}" y="{H - 11}" text-anchor="end" font-family="S" font-size="16" fill="#fff" opacity=".72">redox.cool</text>
{sticker(70, 80, 200, 200, -3, f'<image href="data:image/png;base64,{av}" x="70" y="80" width="200" height="200" clip-path="url(#av)"/>', r=18, cut=10)}
<g class="deep">{extrude(handle_el, 6, SHADOW)}</g>
{extrude(handle_el, 1, SHADOW)}
<g class="face" fill="#fff">{handle_el}</g>
<rect x="352" y="{hy + 24}" width="{pill_w:.0f}" height="50" rx="12" fill="{RED900}"/>
<text x="372" y="268" font-family="S" font-size="{role_size}" fill="{RED300}">&gt;</text>
{"".join(role_els)}
{nametag}
{mango}
</svg>'''
    return svg


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


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "banner.svg").write_text(banner())
    for k, v in SECTIONS.items():
        (OUT / f"{k}.svg").write_text(label(k, v))
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.stat().st_size:>8}  {p.name}")
