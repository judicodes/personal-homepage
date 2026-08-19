"""
Build the hero font: add an 'odieresis' to Linea and compress to woff2.

Upstream Linea has no dieresis at all (no ö ä ü Ö Ä Ü ß), so "Böhlert" rendered
its ö from a fallback serif mid-word. This adds U+00F6 built from the font's
own outlines, then emits the woff2 the site actually serves.

Linea draws every glyph as a bundle of ~5 parallel hairlines, and it has two
distinct dot idioms: the period is five tall bars (103 units), while the i's
tittle is five tiny marks (11 units). The period is the wrong one, even though
the colon proves the designer duplicates that cluster verbatim for two dots:
at display size it renders an umlaut far heavier than anything else in the
face. The tittle is the font's *diacritic* dot, so that is what is reused here,
twice, at native size. Nothing is scaled, so stroke weight stays native.

Usage:  python3 tools/fonts/add-umlaut.py
        python3 tools/fonts/add-umlaut.py --gap 80 --keep-otf

Needs:  pip install fonttools brotli
"""
import argparse
import os
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

p = argparse.ArgumentParser()
p.add_argument("--src", default=os.path.join(HERE, "Linea-original.otf"))
p.add_argument("--dst", default=os.path.join(ROOT, "public/fonts/Linea-umlaut.woff2"))
# Gap between the two dot clusters, in font units. 65 puts the dieresis at 59%
# of the bowl's width: narrower reads as one dashed line, wider drifts past
# the o's shoulders.
p.add_argument("--gap", type=float, default=65.0)
# Baseline of the dots. 651 matches the i's own tittle height exactly.
p.add_argument("--base-y", type=float, default=651.0)
p.add_argument("--keep-otf", action="store_true", help="also write the uncompressed .otf")
args = p.parse_args()

font = TTFont(args.src)
gs = font.getGlyphSet()
cmap = font.getBestCmap()


def contours(glyph_name):
    rp = RecordingPen()
    gs[glyph_name].draw(rp)
    out, cur = [], []
    for op, a in rp.value:
        cur.append((op, a))
        if op in ("closePath", "endPath"):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def bounds_of(cs):
    bp = BoundsPen(gs)
    for c in cs:
        for op, a in c:
            getattr(bp, op)(*a)
    return bp.bounds


def shift(cs, dx, dy):
    return [[(op, tuple((x + dx, y + dy) for (x, y) in a)) for op, a in c] for c in cs]


o_contours = contours(cmap[ord("o")])
o_bounds = bounds_of(o_contours)
o_width = font["hmtx"][cmap[ord("o")]][0]

# The i's tittle: the marks sitting above its stem bundle.
tittle = [c for c in contours(cmap[ord("i")]) if bounds_of([c])[1] > 500]
bt = bounds_of(tittle)
dot_w = bt[2] - bt[0]

total_w = 2 * dot_w + args.gap
x0 = (o_bounds[0] + o_bounds[2]) / 2 - total_w / 2

# The font's accents rise slightly to the right and its colon offsets its two
# dots by ~3 units; keeping a small offset preserves that hand-drawn
# irregularity instead of producing a mechanical mirror pair.
left = shift(tittle, x0 - bt[0], args.base_y - bt[1])
right = shift(tittle, x0 + dot_w + args.gap - bt[0], args.base_y + 3.0 - bt[1])
glyph = o_contours + left + right

pen = T2CharStringPen(o_width, gs)
for c in glyph:
    for op, a in c:
        getattr(pen, op)(*a)

cff = font["CFF "].cff
top = cff.topDictIndex[0]
charstring = pen.getCharString(private=top.Private)

NAME = "odieresis"
charstring.private = top.Private
charstring.globalSubrs = cff.GlobalSubrs

# CharStrings.__setitem__ only rewrites existing glyphs, so a new one has to be
# appended to the backing INDEX and registered in the name->index map by hand.
cs_table = top.CharStrings
if cs_table.charStringsAreIndexed:
    cs_table.charStringsIndex.items.append(charstring)
    cs_table.charStrings[NAME] = len(cs_table.charStringsIndex.items) - 1
else:
    cs_table.charStrings[NAME] = charstring

if NAME not in top.charset:
    top.charset.append(NAME)

font["hmtx"][NAME] = (int(round(o_width)), int(round(o_bounds[0])))
order = font.getGlyphOrder()
if NAME not in order:
    font.setGlyphOrder(list(order) + [NAME])
font["maxp"].numGlyphs = len(font.getGlyphOrder())

for table in font["cmap"].tables:
    table.cmap[0x00F6] = NAME

# The GPL requires a modified version to carry notice of the change. The
# original copyright (name ID 0) is left untouched and the family name stays
# "Linea", which the GPL permits (it has no reserved-name clause).
NOTE = (
    "Modified version of Linea: adds odieresis (U+00F6), composed from the "
    "font's own i-tittle outlines without rescaling. No existing glyph is "
    "altered. Original by Marie Lescalier and Marine Sanchez, ESA le 75, 2019."
)
font["name"].setName(NOTE, 10, 3, 1, 0x409)
font["name"].setName(NOTE, 10, 1, 0, 0)
for rec in font["name"].names:
    if rec.nameID == 5:
        rec.string = "Version 001.000; odieresis added"

if args.keep_otf:
    otf = os.path.splitext(args.dst)[0] + ".otf"
    font.save(otf)
    print(f"wrote {otf} ({os.path.getsize(otf):,} bytes)")

font.flavor = "woff2"
font.save(args.dst)

span = f"{100 * total_w / (o_bounds[2] - o_bounds[0]):.0f}%"
print(f"dieresis: gap={args.gap:g} y={args.base_y:g} span={span} of bowl")
print(f"wrote {args.dst} ({os.path.getsize(args.dst):,} bytes, "
      f"from {os.path.getsize(args.src):,})")
