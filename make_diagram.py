#!/usr/bin/env python3
"""Generate the README diagrams, one SVG per colour scheme.

Two files per diagram rather than one self-switching file: GitHub strips
<style> blocks from inline SVG, so a `prefers-color-scheme` media query inside
the document is silently dropped. The README pairs them with <picture>, which
GitHub does honour.

  architecture-{light,dark}.svg  — both MCP clients, the router, Cognito, the
                                   OAuth state table and the cost Lambdas
  http-surface-{light,dark}.svg  — the six public routes and what guards each

Run:  python make_diagram.py
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

FONT = "-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

THEMES = {
    "dark": {
        "bg": "#0d1117", "panel": "#161b22", "text": "#e6edf3",
        "muted": "#8b949e", "line": "#58a6ff", "rule": "#30363d",
        "purple": "#c39be8", "green": "#3fb950", "blue": "#58a6ff",
        "amber": "#f2c163", "red": "#ff7b72", "navy": "#c8d6e8",
        "pink": "#f778ba",
        "get_bg": "#12261a", "post_bg": "#0c2d4d", "pill_bg": "#21262d",
        "lock_bg": "#3a2c0c",
    },
    "light": {
        "bg": "#ffffff", "panel": "#f6f8fa", "text": "#1f2328",
        "muted": "#59636e", "line": "#0969da", "rule": "#d1d9e0",
        "purple": "#8250df", "green": "#1a7f37", "blue": "#0969da",
        "amber": "#9a6700", "red": "#cf222e", "navy": "#475467",
        "pink": "#bf3989",
        "get_bg": "#dafbe1", "post_bg": "#ddf4ff", "pill_bg": "#eaeef2",
        "lock_bg": "#fff8c5",
    },
}

# Lucide icon paths, on a 24-unit grid.
ICONS = {
    "bot": ['<path d="M12 8V4H8"/>',
            '<rect width="16" height="12" x="4" y="8" rx="2"/>',
            '<path d="M2 14h2"/>', '<path d="M20 14h2"/>',
            '<path d="M15 13v2"/>', '<path d="M9 13v2"/>'],
    "message": ['<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 '
                '2 0 0 1 2 2z"/>'],
    "route": ['<circle cx="6" cy="19" r="3"/>', '<circle cx="18" cy="5" r="3"/>',
              '<path d="M12 19h4.5a3.5 3.5 0 0 0 0-7h-8a3.5 3.5 0 0 1 0-7H12"/>'],
    "zap": ['<path d="M4 14h7l-1 8 10-12h-7l1-8z"/>'],
    "shield": ['<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 '
               '20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 '
               '1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
               '<path d="m9 12 2 2 4-4"/>'],
    "database": ['<ellipse cx="12" cy="5" rx="9" ry="3"/>',
                 '<path d="M3 5V19A9 3 0 0 0 21 19V5"/>',
                 '<path d="M3 12A9 3 0 0 0 21 12"/>'],
    "chart": ['<path d="M3 3v16a2 2 0 0 0 2 2h16"/>',
              '<path d="m19 9-5 5-4-4-3 3"/>'],
}


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ================================================================================
# Architecture diagram
# ================================================================================

AW, AH = 1860, 720
NH = 96                                    # node height
TITLE_PX, SUB_PX, EDGE_PX = 24, 16, 16

# The two clients share a container: everything they do — the browser sign-in
# and the MCP calls — is identical, which is the point of V2.
CLIENTS = (40, 215, 340, 310)              # x, y, w, h
AWS_BOX = (460, 30, 1370, 660)

# id: (x, y, width, colour key, icon, title, subtitle)
NODES = {
    "claude":  (60, 262, 300, "purple", "bot", "Claude", "custom connector"),
    "chatgpt": (60, 392, 300, "green", "message", "ChatGPT",
                "developer-mode app"),
    "api":     (500, 322, 320, "blue", "route", "API Gateway",
                "HTTP API, public routes"),
    "router":  (920, 322, 360, "amber", "zap", "Router Lambda",
                "oauth.py + mcp.py"),
    "cognito": (920, 80, 360, "red", "shield", "Cognito",
                "user pool + Hosted UI"),
    "dynamo":  (920, 560, 360, "navy", "database", "DynamoDB",
                "OAuth state + PKCE, 5-min TTL"),
    "costs":   (1420, 322, 380, "amber", "zap", "Cost Lambdas",
                "6 tools, scoped CE roles"),
    "ce":      (1420, 560, 380, "pink", "chart", "Cost Explorer",
                "us-east-1 endpoint"),
}


def _r(nid):
    """Return (left, top, right, bottom, centre-x, centre-y) for a node."""
    x, y, w = NODES[nid][0], NODES[nid][1], NODES[nid][2]
    return x, y, x + w, y + NH, x + w / 2, y + NH / 2


def _h(a, b):
    """Horizontal hop, right edge of a to left edge of b."""
    return f"M{_r(a)[2]},{_r(a)[5]} L{_r(b)[0] - 5},{_r(b)[5]}"


def _v(a, b, x=None):
    """Vertical hop, downward from a to b."""
    x = _r(a)[4] if x is None else x
    return f"M{x},{_r(a)[3]} L{x},{_r(b)[1] - 5}"


_CX, _CY, _CW, _CH = CLIENTS
_CMID = _CY + _CH / 2

# id: (path, colour key, label, label_x, label_y, anchor, dashed, two_way)
EDGES = {
    "e_mcp":    (f"M{_CX + _CW},{_CMID} L{_r('api')[0] - 5},{_CMID}", "line",
                 "OAuth + MCP", (_CX + _CW + _r("api")[0]) / 2, _CMID - 14,
                 "middle", False, False),
    "e_signin": (f"M{_CX + _CW / 2},{_CY} V{_r('cognito')[5]} "
                 f"H{_r('cognito')[0] - 5}", "red",
                 "browser sign-in (Hosted UI)", 480, _r("cognito")[5] - 14,
                 "start", True, False),
    "e_gw":     (_h("api", "router"), "line", "", 0, 0, "start", False, False),
    "e_auth":   (f"M{_r('router')[4]},{_r('router')[1] - 5} "
                 f"L{_r('router')[4]},{_r('cognito')[3] + 5}", "red",
                 "code exchange · /oauth2/userInfo", _r("router")[4] + 16,
                 (_r("cognito")[3] + _r("router")[1]) / 2 + 6, "start",
                 True, True),
    "e_state":  (_v("router", "dynamo"), "navy",
                 "PENDINGAUTH / AUTHCODE",
                 _r("router")[4] + 16,
                 (_r("router")[3] + _r("dynamo")[1]) / 2 + 6, "start",
                 False, False),
    "e_invoke": (_h("router", "costs"), "amber", "lambda:Invoke",
                 (_r("router")[2] + _r("costs")[0]) / 2, _r("router")[5] - 14,
                 "middle", False, False),
    "e_ce":     (_v("costs", "ce"), "pink", "GetCostAndUsage / Forecast",
                 _r("costs")[4] - 16,
                 (_r("costs")[3] + _r("ce")[1]) / 2 + 6, "end",
                 False, False),
}


def node_svg(nid, t):
    """Render one service box: rounded panel, icon, title, subtitle."""
    x, y, w, key, icon, title, sub = NODES[nid]
    colour = t[key]
    scale = 1.25
    isz = 24 * scale
    ix, iy = x + 20, y + (NH - isz) / 2
    tx = x + 20 + isz + 14
    return "".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{NH}" rx="10" ry="10" '
        f'fill="{t["panel"]}" stroke="{colour}" stroke-width="2"/>',
        f'<g transform="translate({ix},{iy}) scale({scale})" fill="none" '
        f'stroke="{colour}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">' + "".join(ICONS[icon]) + "</g>",
        f'<text x="{tx}" y="{y + NH/2 - 4}" font-family="{FONT}" '
        f'font-size="{TITLE_PX}" font-weight="600" fill="{t["text"]}">{title}</text>',
        f'<text x="{tx}" y="{y + NH/2 + 22}" font-family="{FONT}" '
        f'font-size="{SUB_PX}" fill="{t["muted"]}">{sub}</text>',
    ])


def edge_svg(eid, t):
    """Render one arrow plus its label."""
    d, key, label, lx, ly, anchor, dashed, two_way = EDGES[eid]
    colour = t[key]
    dash = ' stroke-dasharray="7 6"' if dashed else ""
    start = f' marker-start="url(#a_{eid})"' if two_way else ""
    out = (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="2"'
           f'{dash}{start} marker-end="url(#a_{eid})"/>')
    if label:
        out += (f'<text x="{lx}" y="{ly}" text-anchor="{anchor}" '
                f'font-family="{FONT}" font-size="{EDGE_PX}" font-weight="600" '
                f'fill="{colour}">{_esc(label)}</text>')
    return out


def build_architecture(t):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{AW}" height="{AH}" '
           f'viewBox="0 0 {AW} {AH}" role="img" '
           f'aria-label="Claude and ChatGPT sign in through Cognito and call one '
           f'API Gateway and router Lambda, which invokes six Cost Explorer '
           f'Lambdas">', "<defs>"]
    # One marker per edge: a shared marker cannot carry per-edge colour.
    for eid, spec in EDGES.items():
        out.append(
            f'<marker id="a_{eid}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{t[spec[1]]}"/></marker>')
    out.append("</defs>")
    out.append(f'<rect width="{AW}" height="{AH}" fill="{t["bg"]}"/>')

    bx, by, bw, bh = AWS_BOX
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="14" '
               f'fill="none" stroke="{t["rule"]}" stroke-width="2" '
               f'stroke-dasharray="10 8"/>')
    out.append(f'<text x="{bx + 20}" y="{by + 30}" font-family="{FONT}" '
               f'font-size="18" font-weight="600" fill="{t["muted"]}">'
               f'AWS · us-east-1</text>')

    out.append(f'<rect x="{_CX}" y="{_CY}" width="{_CW}" height="{_CH}" rx="14" '
               f'fill="none" stroke="{t["rule"]}" stroke-width="2"/>')
    out.append(f'<text x="{_CX + 20}" y="{_CY + 32}" font-family="{FONT}" '
               f'font-size="18" font-weight="600" fill="{t["muted"]}">'
               f'MCP clients — same URL</text>')

    for eid in EDGES:
        out.append(edge_svg(eid, t))
    for nid in NODES:
        out.append(node_svg(nid, t))
    out.append("</svg>")
    return "".join(out)


# ================================================================================
# HTTP surface diagram
# ================================================================================

SW = 1500
ROW_H = 64
COL_EP, COL_METHOD, COL_AUTH, COL_PURPOSE = 70, 700, 840, 1020

# (path, method, purpose)
PUBLIC_ROUTES = [
    ("/.well-known/oauth-authorization-server", "GET",
     "RFC 8414 metadata — advertises PKCE S256"),
    ("/oauth/register", "POST", "RFC 7591 dynamic client registration"),
    ("/authorize", "GET", "Start Cognito login, store PKCE challenge"),
    ("/oauth/callback", "GET", "Cognito redirect target"),
    ("/oauth/token", "POST", "Verify PKCE, mac_ code → Cognito token"),
]


def _pill(x, cy, w, label, fill, stroke, colour, bold=True):
    return (f'<rect x="{x}" y="{cy - 18}" width="{w}" height="36" rx="18" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            f'<text x="{x + w / 2}" y="{cy + 6}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="17" '
            f'font-weight="{700 if bold else 400}" fill="{colour}">{label}</text>')


def _method_pill(method, cy, t):
    if method == "GET":
        return _pill(COL_METHOD, cy, 96, "GET", t["get_bg"], t["green"], t["green"])
    return _pill(COL_METHOD, cy, 96, "POST", t["post_bg"], t["blue"], t["blue"])


def _header_row(y, t):
    out = []
    for x, label in ((COL_EP, "ENDPOINT"), (COL_METHOD, "METHOD"),
                     (COL_AUTH, "AUTH"), (COL_PURPOSE, "PURPOSE")):
        out.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="15" '
                   f'font-weight="700" letter-spacing="1" fill="{t["muted"]}">'
                   f'{label}</text>')
    return "".join(out)


def build_surface(t):
    pub_top = 130
    pub_h = 70 + 40 + ROW_H * len(PUBLIC_ROUTES) + 10
    prot_top = pub_top + pub_h + 30
    prot_h = 120
    sh = prot_top + prot_h + 70

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SW}" height="{sh}" '
           f'viewBox="0 0 {SW} {sh}" role="img" '
           f'aria-label="Five public OAuth routes and one protected /mcp route">',
           f'<rect width="{SW}" height="{sh}" fill="{t["bg"]}"/>',
           f'<text x="40" y="60" font-family="{FONT}" font-size="32" '
           f'font-weight="700" fill="{t["text"]}">HTTP surface</text>',
           f'<text x="40" y="96" font-family="{FONT}" font-size="18" '
           f'fill="{t["muted"]}">The OAuth routes are public — they ARE the '
           f'login. /mcp is the only route that checks a token.</text>']

    # Public OAuth routes.
    out.append(f'<rect x="30" y="{pub_top}" width="{SW - 60}" height="{pub_h}" '
               f'rx="14" fill="{t["panel"]}" stroke="{t["blue"]}" '
               f'stroke-width="1.5"/>')
    out.append(f'<text x="{COL_EP}" y="{pub_top + 42}" font-family="{FONT}" '
               f'font-size="21" font-weight="700" fill="{t["blue"]}">'
               f'OAuth — public authorization endpoints</text>')
    out.append(_header_row(pub_top + 88, t))
    y = pub_top + 110
    for i, (path, method, purpose) in enumerate(PUBLIC_ROUTES):
        cy = y + ROW_H / 2
        if i:
            out.append(f'<line x1="{COL_EP - 10}" x2="{SW - 70}" y1="{y}" '
                       f'y2="{y}" stroke="{t["rule"]}" stroke-width="1"/>')
        out.append(f'<text x="{COL_EP}" y="{cy + 6}" font-family="{MONO}" '
                   f'font-size="18" fill="{t["text"]}">{path}</text>')
        out.append(_method_pill(method, cy, t))
        out.append(_pill(COL_AUTH, cy, 130, "public", t["pill_bg"], t["rule"],
                         t["muted"], bold=False))
        out.append(f'<text x="{COL_PURPOSE}" y="{cy + 6}" font-family="{FONT}" '
                   f'font-size="17" fill="{t["text"]}">{_esc(purpose)}</text>')
        y += ROW_H

    # The one protected route.
    out.append(f'<rect x="30" y="{prot_top}" width="{SW - 60}" '
               f'height="{prot_h}" rx="14" fill="{t["panel"]}" '
               f'stroke="{t["amber"]}" stroke-width="2.5"/>')
    out.append(f'<text x="{COL_EP}" y="{prot_top + 40}" font-family="{FONT}" '
               f'font-size="21" font-weight="700" fill="{t["amber"]}">'
               f'Protected — the one route that checks a token</text>')
    cy = prot_top + 84
    out.append(f'<text x="{COL_EP}" y="{cy + 7}" font-family="{MONO}" '
               f'font-size="22" font-weight="700" fill="{t["text"]}">/mcp</text>')
    out.append(_method_pill("POST", cy, t))
    out.append(_pill(COL_AUTH, cy, 160, "Bearer (Cognito)", t["lock_bg"],
                     t["amber"], t["amber"]))
    out.append(f'<text x="{COL_PURPOSE + 10}" y="{cy + 6}" font-family="{FONT}" '
               f'font-size="17" fill="{t["text"]}">MCP JSON-RPC — runs the six '
               f'cost tools</text>')

    out.append(f'<text x="40" y="{sh - 28}" font-family="{FONT}" '
               f'font-size="16" font-style="italic" fill="{t["muted"]}">'
               f'PKCE is enforced when the client sends a challenge (ChatGPT) '
               f'and skipped when it does not (Claude).</text>')
    out.append("</svg>")
    return "".join(out)


def main():
    for name, theme in THEMES.items():
        for stem, builder in (("architecture", build_architecture),
                              ("http-surface", build_surface)):
            path = os.path.join(HERE, f"{stem}-{name}.svg")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(builder(theme))
            print(f"  {stem}-{name}.svg")


if __name__ == "__main__":
    main()
