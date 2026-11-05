"""Hand-rolled SVG exhibits in a restrained consulting style: navy text, one blue accent, greys. Every plotted value is passed in."""
NAVY, BLUE, MID, GREY, LIGHT, RULE = "#051C2C", "#2251FF", "#6B7B8C", "#B4BCC5", "#E3E7EB", "#C9D0D6"
FONT = "font-family:'Liberation Sans',Arial,sans-serif"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" style="{FONT}">{body}</svg>'


def text(x, y, s, size=11, fill=NAVY, anchor="start", weight="normal"):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'


def legend(items, x, y, size=11):
    out, cx = [], x
    for label, color in items:
        out.append(f'<rect x="{cx}" y="{y-9}" width="10" height="10" fill="{color}"/>')
        out.append(text(cx + 15, y, label, size, MID))
        cx += 15 + len(label) * size * 0.56 + 18
    return "".join(out)


def grouped_columns(cats, series, width=640, height=300, fmt=lambda v: f"{v/1000:.0f}k", labels_all=True, note=None, top=34, sub=None):
    """cats: list of labels; series: list of (name, color, values list aligned to cats; None = missing)."""
    left, right, base = 8, width - 8, height - (44 if sub else 28)
    vmax = max(v for _, _, vs in series for v in vs if v is not None)
    band = (right - left) / len(cats)
    k = len(series)
    bw = min(band * 0.78 / k, 34)
    h = lambda v: v / vmax * (base - top - 18)
    out = [legend([(n, c) for n, c, _ in series], left, 14)]
    out.append(f'<line x1="{left}" x2="{right}" y1="{base}" y2="{base}" stroke="{RULE}"/>')
    for i, c in enumerate(cats):
        gx = left + i * band + (band - k * bw - (k - 1) * 3) / 2
        for j, (_, color, vs) in enumerate(series):
            v = vs[i]
            if v is None:
                continue
            x = gx + j * (bw + 3)
            out.append(f'<rect x="{x:.1f}" y="{base-h(v):.1f}" width="{bw:.1f}" height="{h(v):.1f}" fill="{color}"/>')
            if labels_all:
                out.append(text(x + bw / 2, base - h(v) - 4, fmt(v), 10, NAVY, "middle"))
        out.append(text(left + i * band + band / 2, base + 16, c, 11, MID, "middle"))
        if sub:
            out.append(text(left + i * band + band / 2, base + 31, sub[i], 11, NAVY, "middle", "bold"))
    if note:
        out.append(note)
    return svg(width, height, "".join(out)), (left, band, base, h, bw)


def hbars(rows, width=640, row_h=24, label_w=120, fmt=lambda v: f"{v:.1f}", vmax=None, top=30, legend_items=None, ref=None):
    """rows: list of (label, value, color, bold)."""
    vmax = vmax or max(v for _, v, _, _ in rows)
    height = top + row_h * len(rows) + 10
    x0, x1 = label_w, width - 46
    out = []
    if legend_items:
        out.append(legend(legend_items, 0, 14))
    for i, (lab, v, color, bold) in enumerate(rows):
        y = top + i * row_h
        out.append(text(label_w - 8, y + row_h * 0.62, lab, 11.5, NAVY, "end", "bold" if bold else "normal"))
        out.append(f'<rect x="{x0}" y="{y+3}" width="{max(0,(v/vmax)*(x1-x0)):.1f}" height="{row_h-8}" fill="{color}"/>')
        out.append(text(x0 + (v / vmax) * (x1 - x0) + 5, y + row_h * 0.62, fmt(v), 11, NAVY, "start", "bold" if bold else "normal"))
    if ref:
        rx = x0 + ref[0] / vmax * (x1 - x0)
        out.append(f'<line x1="{rx:.1f}" x2="{rx:.1f}" y1="{top-4}" y2="{height-6}" stroke="{MID}" stroke-dasharray="3 3"/>')
        out.append(text(rx + 4, top - 8, ref[1], 10, MID))
    out.append(f'<line x1="{x0}" x2="{x0}" y1="{top-4}" y2="{height-6}" stroke="{RULE}"/>')
    return svg(width, height, "".join(out))


def scatter(points, width=640, height=330, xlab="", ylab="", label_set=(), xfmt=lambda v: f"{v:.0f}%", yfmt=lambda v: f"{v:.0f}", accent="West Bengal"):
    """points: list of (name, x, y)."""
    l, r, t, b = 52, width - 16, 12, height - 44
    xmax = max(p[1] for p in points) * 1.08
    ymax = max(p[2] for p in points) * 1.12
    X = lambda v: l + v / xmax * (r - l)
    Y = lambda v: b - v / ymax * (b - t)
    out = []
    for g in range(0, int(ymax) + 1, 2 if ymax > 8 else 1):
        out.append(f'<line x1="{l}" x2="{r}" y1="{Y(g):.1f}" y2="{Y(g):.1f}" stroke="{LIGHT}"/>')
        out.append(text(l - 6, Y(g) + 3.5, yfmt(g), 10, MID, "end"))
    for g in range(0, int(xmax) + 1, 5):
        out.append(text(X(g), b + 15, xfmt(g), 10, MID, "middle"))
    out.append(f'<line x1="{l}" x2="{r}" y1="{b}" y2="{b}" stroke="{RULE}"/>')
    out.append(text((l + r) / 2, height - 8, xlab, 11, MID, "middle"))
    out.append(f'<text transform="translate(12,{(t+b)/2:.0f}) rotate(-90)" font-size="11" fill="{MID}" text-anchor="middle">{esc(ylab)}</text>')
    offs = {"West Bengal": (-9, 16, "end"), "Kerala": (9, -7, "start"), "Maharashtra": (-9, -7, "end"), "Bihar": (9, -7, "start"), "Karnataka": (-9, 14, "end"), "Tamil Nadu": (9, 16, "start"), "Andhra Pradesh": (9, 16, "start"), "Telangana": (9, -7, "start")}
    for name, x, y in points:
        wb = name == accent
        out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{7 if wb else 5}" fill="{BLUE if wb else GREY}" stroke="#fff" stroke-width="1.5"/>')
        if name in label_set:
            dx, dy, a = offs.get(name, (9, -7, "start"))
            out.append(text(X(x) + dx, Y(y) + dy, name, 11, NAVY, a, "bold" if wb else "normal"))
    return svg(width, height, "".join(out))


def strip(values, highlights, width=640, height=260, fmt=lambda v: f"{v/1000:.0f}k", refs=()):
    """values: one dot per city; highlights: (label, value, color, label_y_offset, anchor); refs: (value, label)."""
    l, r = 20, width - 20
    lo, hi = 10000, max(values) * 1.04
    X = lambda v: l + (v - lo) / (hi - lo) * (r - l)
    base = height - 40
    out = [f'<line x1="{l}" x2="{r}" y1="{base}" y2="{base}" stroke="{RULE}"/>']
    for g in range(10000, int(hi), 10000):
        out.append(f'<line x1="{X(g):.1f}" x2="{X(g):.1f}" y1="{base}" y2="{base+5}" stroke="{RULE}"/>')
        out.append(text(X(g), base + 19, fmt(g), 10.5, MID, "middle"))
    stack = {}
    for v in sorted(values):
        key = round(X(v) / 11)
        n = stack.get(key, 0)
        stack[key] = n + 1
        out.append(f'<circle cx="{X(v):.1f}" cy="{base-9-n*11:.1f}" r="4.6" fill="{GREY}"/>')
    for val, label in refs:
        out.append(f'<line x1="{X(val):.1f}" x2="{X(val):.1f}" y1="{base-148}" y2="{base}" stroke="{MID}" stroke-dasharray="3 3"/>')
        out.append(text(X(val) + 5, base - 142, label, 10.5, MID, "start"))
    for label, v, color, dy, anchor in highlights:
        out.append(f'<circle cx="{X(v):.1f}" cy="{base-9:.1f}" r="6" fill="{color}" stroke="#fff" stroke-width="1.4"/>')
        ly = base - 96 + dy
        out.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{ly+4:.1f}" y2="{base-16:.1f}" stroke="{color}"/>')
        out.append(text(X(v), ly, label, 11.5, NAVY, anchor, "bold"))
    return svg(width, height, "".join(out))


def hbars_grouped(cats, series, width=620, row_h=44, label_w=170, fmt=lambda v: f"{v:.1f}%", vmax=None, top=30):
    """cats: labels; series: list of (name, color, values aligned to cats)."""
    vmax = vmax or max(v for _, _, vs in series for v in vs)
    k = len(series)
    height = top + row_h * len(cats) + 6
    x0, x1 = label_w, width - 48
    bh = (row_h - 10) / k
    out = [legend([(n, c) for n, c, _ in series], 0, 14)]
    for i, c in enumerate(cats):
        y = top + i * row_h
        out.append(text(label_w - 10, y + row_h / 2 + 3, c, 11.5, NAVY, "end"))
        for j, (_, color, vs) in enumerate(series):
            yy = y + 4 + j * bh
            out.append(f'<rect x="{x0}" y="{yy:.1f}" width="{vs[i]/vmax*(x1-x0):.1f}" height="{bh-2:.1f}" fill="{color}"/>')
            out.append(text(x0 + vs[i] / vmax * (x1 - x0) + 5, yy + bh - 5, fmt(vs[i]), 11, NAVY))
    out.append(f'<line x1="{x0}" x2="{x0}" y1="{top-2}" y2="{height-4}" stroke="{RULE}"/>')
    return svg(width, height, "".join(out))


def bridge(items, width=640, height=330, fmt=lambda v: f"{abs(v):.2f}", sign=True):
    """Vertical bridge. items: (label with \\n for line breaks, value, kind, color); kind 'total' | 'down' | 'ref' (a bar from zero, no connector)."""
    left, right, base, top = 8, width - 8, height - 46, 30
    vmax = max(v for _, v, k, _ in items if k != "down")
    h = lambda v: v / vmax * (base - top - 14)
    n = len(items)
    band = (right - left) / n
    bw = band * 0.62
    out = [f'<line x1="{left}" x2="{right}" y1="{base}" y2="{base}" stroke="{RULE}"/>']
    level, prev_x = 0.0, None
    for i, (label, v, kind, color) in enumerate(items):
        x = left + i * band + (band - bw) / 2
        if prev_x is not None and kind != "ref":
            out.append(f'<line x1="{prev_x:.1f}" x2="{x:.1f}" y1="{base-h(level):.1f}" y2="{base-h(level):.1f}" stroke="{GREY}" stroke-dasharray="2 2"/>')
        if kind == "down":
            y_top, y_bot = base - h(level), base - h(level - v)
            out.append(f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bw:.1f}" height="{y_bot-y_top:.1f}" fill="{color}"/>')
            out.append(text(x + bw / 2, y_bot + 13, ("\u2212" if sign else "") + fmt(v), 10.5, NAVY, "middle"))
            level -= v
        else:
            out.append(f'<rect x="{x:.1f}" y="{base-h(v):.1f}" width="{bw:.1f}" height="{h(v):.1f}" fill="{color}"/>')
            out.append(text(x + bw / 2, base - h(v) - 5, fmt(v), 10.5, NAVY, "middle", "bold"))
            if kind == "total":
                level = v
        prev_x = x + bw
        for j, ln in enumerate(label.split("\n")):
            out.append(text(x + bw / 2, base + 15 + j * 12.5, ln, 10.5, MID, "middle"))
    return svg(width, height, "".join(out))
