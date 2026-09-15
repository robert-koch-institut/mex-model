#!/usr/bin/env python3
"""
MEx UML Diagram Generator
=========================
Reads the JSON schema entity definitions from a local clone of
https://github.com/robert-koch-institut/mex-model and generates
a self-contained mex-uml-diagram.html file.

Usage:
    # 1. Clone or update the repo
    git clone https://github.com/robert-koch-institut/mex-model.git  # first time
    cd mex-model && git pull                                          # updates

    # 2. Run the generator (from wherever this script lives)
    python generate_uml_diagram.py --repo ./mex-model --out mex-uml-diagram.html

    # 3. Open the HTML or commit it to your project.

Requirements: Python 3.9+, no third-party packages.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# ── Configuration ────────────────────────────────────────────────────────────

# We only visualise the "merged-*" entities (the canonical merged view).
ENTITY_PREFIX = "merged-"

# Properties to skip (internal / not useful in the UML diagram)
SKIP_PROPERTIES = {"identifier", "$schema", "entityType", "stableTargetId"}

# ── Helpers ──────────────────────────────────────────────────────────────────


def kebab_to_pascal(name: str) -> str:
    """Convert 'access-platform' -> 'AccessPlatform'."""
    return "".join(word.capitalize() for word in name.split("-"))


def ref_to_entity_id(ref: str) -> str | None:
    """
    Extract the entity display-id from a $ref like
    '/mex/model/entities/merged-person#/identifier'
    Returns 'Person' or None if it's not an entity reference.
    """
    m = re.match(r"^/mex/model/entities/merged-([\w-]+)#/identifier$", ref)
    if m:
        return kebab_to_pascal(m.group(1))
    return None


def _field_ref_name(ref: str) -> str:
    """'/mex/model/fields/text' -> 'Text'"""
    return ref.rsplit("/", 1)[-1].capitalize()


def _comment_to_type(comment: str) -> str:
    """'year_month_day_time' -> 'YearMonthDayTime'"""
    return "".join(word.capitalize() for word in comment.split("_"))


def _resolve_items(items: dict[str, Any]) -> str:
    """Resolve the inner type of an array's 'items'."""
    if "$ref" in items:
        eid = ref_to_entity_id(items["$ref"])
        if eid:
            return f"Merged{eid}Identifier"
        return _field_ref_name(items["$ref"])

    if "anyOf" in items:
        parts = []
        for variant in items["anyOf"]:
            if variant.get("type") == "null":
                continue  # skip null inside list items
            if "$ref" in variant:
                eid = ref_to_entity_id(variant["$ref"])
                if eid:
                    parts.append(f"Merged{eid}Identifier")
                else:
                    parts.append(_field_ref_name(variant["$ref"]))
            elif "$comment" in variant:
                parts.append(_comment_to_type(variant["$comment"]))
            elif variant.get("type") == "string":
                parts.append("str")
            elif variant.get("type") == "integer":
                parts.append("int")
            else:
                parts.append(variant.get("type", "?"))
        return " | ".join(parts) if parts else "?"

    t = items.get("type", "?")
    type_map = {"string": "str", "integer": "int", "number": "float", "boolean": "bool"}
    return type_map.get(t, t)


def resolve_type_string(prop: dict[str, Any]) -> str:
    """
    Build a human-readable type string from a JSON-schema property definition,
    mirroring the style used in the original HTML's RAW data.
    """
    # Direct $ref at top level (single value, required)
    if "$ref" in prop and "anyOf" not in prop:
        eid = ref_to_entity_id(prop["$ref"])
        if eid:
            return f"Merged{eid}Identifier"
        return _field_ref_name(prop["$ref"])

    # anyOf (nullable single value or union)
    if "anyOf" in prop:
        parts: list[str] = []
        for variant in prop["anyOf"]:
            if variant.get("type") == "null":
                parts.append("None")
            elif "$ref" in variant:
                eid = ref_to_entity_id(variant["$ref"])
                if eid:
                    parts.append(f"Merged{eid}Identifier")
                else:
                    parts.append(_field_ref_name(variant["$ref"]))
            elif "$comment" in variant:
                parts.append(_comment_to_type(variant["$comment"]))
            elif variant.get("type") == "string":
                parts.append("str")
            elif variant.get("type") == "integer":
                parts.append("int")
            else:
                parts.append(variant.get("type", "?"))
        return " | ".join(parts)

    # array
    if prop.get("type") == "array":
        items = prop.get("items", {})
        inner = _resolve_items(items)
        return f"list[{inner}]"

    # simple scalars
    t = prop.get("type", "?")
    type_map = {"string": "str", "integer": "int", "number": "float", "boolean": "bool"}
    return type_map.get(t, t)


def collect_refs(type_str: str) -> list[str]:
    """
    Given a type string like 'list[MergedPersonIdentifier | MergedOrgIdentifier]',
    return the entity display-ids referenced: ['Person', 'Organization', ...].
    """
    refs = []
    for m in re.finditer(r"Merged(\w+?)Identifier", type_str):
        refs.append(m.group(1))
    return sorted(set(refs))


# ── Schema parsing ───────────────────────────────────────────────────────────


def parse_entity(filepath: Path) -> dict[str, Any] | None:
    """Parse one merged-*.json file into our internal representation."""
    with open(filepath, "r", encoding="utf-8") as f:
        schema = json.load(f)

    stem = filepath.stem  # e.g. 'merged-access-platform'
    if not stem.startswith(ENTITY_PREFIX):
        return None
    entity_name = kebab_to_pascal(stem[len(ENTITY_PREFIX) :])

    required_set = set(schema.get("required", []))
    properties = schema.get("properties", {})

    attrs = []
    for prop_name, prop_def in sorted(properties.items()):
        if prop_name in SKIP_PROPERTIES:
            continue
        type_str = resolve_type_string(prop_def)
        is_required = prop_name in required_set
        attrs.append(
            {
                "name": prop_name,
                "type": type_str,
                "required": is_required,
            }
        )

    return {"id": entity_name, "attrs": attrs}


def load_all_entities(entities_dir: Path) -> list[dict[str, Any]]:
    """Load all merged-*.json files from the entities directory."""
    entities = []
    for fp in sorted(entities_dir.glob(f"{ENTITY_PREFIX}*.json")):
        ent = parse_entity(fp)
        if ent:
            entities.append(ent)
    return entities


# ── ID_MAP generation ────────────────────────────────────────────────────────


def build_id_map(entities: list[dict[str, Any]]) -> dict[str, str]:
    """Build the MergedXIdentifier -> X mapping from discovered entities."""
    return {f"Merged{e['id']}Identifier": e["id"] for e in entities}


# ── Layout heuristic ─────────────────────────────────────────────────────────


def compute_layout(
    entities: list[dict[str, Any]],
) -> tuple[dict[str, int], dict[str, int]]:
    """
    Compute a reasonable GRID_COL / GRID_ROW assignment.

    Strategy: sort entities by outgoing-reference count (most connected in
    the center), then distribute across columns. The user can always drag
    cards interactively in the HTML.
    """
    entity_ids = [e["id"] for e in entities]

    # Count outgoing references per entity
    out_refs: dict[str, set[str]] = {eid: set() for eid in entity_ids}
    for ent in entities:
        for attr in ent["attrs"]:
            for ref in collect_refs(attr["type"]):
                if ref in out_refs:
                    out_refs[ent["id"]].add(ref)

    # Count incoming references
    in_refs: dict[str, set[str]] = {eid: set() for eid in entity_ids}
    for eid, targets in out_refs.items():
        for t in targets:
            if t in in_refs:
                in_refs[t].add(eid)

    # Score = outgoing + incoming (total connectivity)
    score = {eid: len(out_refs[eid]) + len(in_refs[eid]) for eid in entity_ids}

    # Sort by score descending
    ranked = sorted(entity_ids, key=lambda e: score[e], reverse=True)

    # Distribute into columns (max ~3 per column)
    max_per_col = 3
    grid_col: dict[str, int] = {}
    grid_row: dict[str, int] = {}
    col = 0
    row = 0
    for eid in ranked:
        grid_col[eid] = col
        grid_row[eid] = row
        row += 1
        if row >= max_per_col:
            row = 0
            col += 1

    return grid_col, grid_row


# ── JS code generation ──────────────────────────────────────────────────────


def entities_to_js(entities: list[dict[str, Any]]) -> str:
    """Generate the RAW array as JavaScript source."""
    lines = ["const RAW = ["]
    for ent in entities:
        lines.append(f'  {{ id:"{ent["id"]}", attrs:[')
        for attr in ent["attrs"]:
            fn = "r" if attr["required"] else "o"
            escaped_type = attr["type"].replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'    {fn}("{attr["name"]}", "{escaped_type}"),')
        lines.append("  ]},")
    lines.append("];")
    return "\n".join(lines)


def id_map_to_js(id_map: dict[str, str]) -> str:
    """Generate the ID_MAP object as JavaScript source."""
    lines = ["const ID_MAP = {"]
    for k, v in sorted(id_map.items()):
        lines.append(f'  "{k}": "{v}",')
    lines.append("};")
    return "\n".join(lines)


def grid_to_js(grid_col: dict[str, int], grid_row: dict[str, int]) -> str:
    """Generate GRID_COL and GRID_ROW as JavaScript source."""
    lines = ["const GRID_COL = {"]
    for k, v in sorted(grid_col.items(), key=lambda x: (x[1], x[0])):
        lines.append(f'  "{k}": {v},')
    lines.append("};")
    lines.append("")
    lines.append("const GRID_ROW = {")
    for k, v in sorted(grid_row.items(), key=lambda x: (grid_col[x[0]], x[1])):
        lines.append(f'  "{k}": {v},')
    lines.append("};")
    return "\n".join(lines)


# ── HTML assembly ────────────────────────────────────────────────────────────


def build_html(raw_js: str, id_map_js: str, grid_js: str) -> str:
    """Inject generated data into the full HTML template."""
    return (
        HTML_TEMPLATE.replace("/* __RAW_DATA__ */", raw_js)
        .replace("/* __ID_MAP__ */", id_map_js)
        .replace("/* __GRID_LAYOUT__ */", grid_js)
    )


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the MEx UML diagram HTML from mex-model JSON schemas."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path("mex-model"),
        help="Path to local mex-model repository clone (default: ./mex-model)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("mex-uml-diagram.html"),
        help="Output HTML file path (default: ./mex-uml-diagram.html)",
    )
    args = parser.parse_args()

    entities_dir = args.repo / "mex" / "model" / "entities"
    if not entities_dir.is_dir():
        print(f"ERROR: Entities directory not found: {entities_dir}", file=sys.stderr)
        print(
            f"       Make sure --repo points to your mex-model clone.", file=sys.stderr
        )
        sys.exit(1)

    print(f"Reading schemas from {entities_dir} ...")
    entities = load_all_entities(entities_dir)
    if not entities:
        print("ERROR: No merged-*.json entities found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(entities)} entities: {', '.join(e['id'] for e in entities)}")
    total_attrs = sum(len(e["attrs"]) for e in entities)
    print(f"Total attributes: {total_attrs}")

    id_map = build_id_map(entities)
    grid_col, grid_row = compute_layout(entities)

    raw_js = entities_to_js(entities)
    id_map_js = id_map_to_js(id_map)
    grid_js = grid_to_js(grid_col, grid_row)

    html = build_html(raw_js, id_map_js, grid_js)

    args.out.write_text(html, encoding="utf-8")
    print(f"\nWritten: {args.out}  ({len(html):,} bytes)")
    print("Open the file in a browser to verify the diagram.")


# ══════════════════════════════════════════════════════════════════════════════
# HTML Template
# ══════════════════════════════════════════════════════════════════════════════
# This is the full rendering + interaction code from the original diagram.
# Only the three data blocks (RAW, ID_MAP, GRID_*) are replaced at generation
# time. Everything else (CSS, layout engine, arrow routing, pan/zoom,
# highlighting) is static and unchanged.
# ══════════════════════════════════════════════════════════════════════════════

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MEx Common &mdash; UML Class Diagram</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@700;800&display=swap');
:root {
  --bg: #0c0e15; --surface: #12151f; --surface2: #181c28;
  --border: #222638; --border-hi: #35405c;
  --text: #c8d0e8; --text-dim: #5c6882; --text-muted:#333b55;
  --accent: #5b8af0; --required: #f0a050; --ref-clr: #4ecf9a;
  --hi-out: #5b8af0; --hi-in: #e05b8a;
  --arrow-def: #2e3650;
  --hdr-h: 46px;
}
* { box-sizing:border-box; margin:0; padding:0; }
body {
  background:var(--bg); color:var(--text);
  font-family:'JetBrains Mono',monospace; font-size:12px;
  overflow:hidden; width:100vw; height:100vh;
}

/* TOOLBAR */
#toolbar {
  position:fixed; top:0; left:0; right:0; height:var(--hdr-h);
  background:var(--surface); border-bottom:1px solid var(--border);
  display:flex; align-items:center; padding:0 16px; gap:16px;
  z-index:1000; user-select:none;
}
.logo { font-family:'Syne',sans-serif; font-weight:800; font-size:15px; color:var(--accent); letter-spacing:.04em; flex-shrink:0; }
.sep-v { width:1px; height:18px; background:var(--border); }
.legend { display:flex; align-items:center; gap:12px; font-size:10.5px; color:var(--text-dim); flex-shrink:0; }
.li { display:flex; align-items:center; gap:5px; }
.dot { width:7px; height:7px; border-radius:50%; }
.d-req { background:var(--required); }
.d-ref { background:var(--ref-clr); }
.d-out { background:var(--hi-out); }
.d-in  { background:var(--hi-in); }
.hint { margin-left:auto; font-size:10px; color:var(--text-muted); white-space:nowrap; }
#btn-reset {
  padding:4px 11px; background:var(--surface2); border:1px solid var(--border);
  border-radius:4px; color:var(--text-dim); font-family:'JetBrains Mono',monospace;
  font-size:10px; cursor:pointer; transition:all .15s; flex-shrink:0;
}
#btn-reset:hover { border-color:var(--accent); color:var(--accent); }

/* CANVAS */
#wrap {
  position:fixed; top:var(--hdr-h); left:0; right:0; bottom:0;
  overflow:hidden; cursor:grab;
}
#wrap.dragging { cursor:grabbing; }
#canvas { position:absolute; transform-origin:0 0; }
svg#svg-layer { position:absolute; top:0; left:0; pointer-events:none; overflow:visible; }

/* CARDS */
.cls-card {
  position:absolute; background:var(--surface);
  border:1.5px solid var(--border); border-radius:8px;
  box-shadow:0 4px 20px rgba(0,0,0,.5);
  transition:border-color .18s, box-shadow .18s, opacity .18s;
  overflow:hidden;
}
.cls-card:hover { border-color:var(--border-hi); }
.cls-card.hl-src  { border-color:var(--hi-out)!important; box-shadow:0 0 0 2px var(--hi-out),0 6px 30px rgba(91,138,240,.2)!important; }
.cls-card.hl-tgt  { border-color:var(--hi-in)!important;  box-shadow:0 0 0 2px var(--hi-in), 0 6px 30px rgba(224,91,138,.2)!important; }
.cls-card.hl-self { border-color:var(--ref-clr)!important; box-shadow:0 0 0 2px var(--ref-clr)!important; }
.cls-card.dimmed  { opacity:.15; }
.cls-header {
  padding:8px 12px 6px; border-bottom:1px solid var(--border);
  cursor:pointer; transition:background .13s;
}
.cls-header:hover { background:var(--surface2); }
.cls-name { font-family:'Syne',sans-serif; font-weight:700; font-size:13px; color:#e8eaf6; letter-spacing:.02em; }
.cls-sub  { font-size:9px; color:var(--text-muted); margin-top:2px; }

/* ATTR SECTIONS */
.attr-sect { padding:3px 0 4px; }
.attr-sect+.attr-sect { border-top:1px solid var(--border); }
.sect-label { font-size:8.5px; color:var(--text-muted); padding:2px 12px 1px; letter-spacing:.06em; text-transform:uppercase; }
.attr-row {
  display:grid; grid-template-columns: minmax(0,1fr) auto;
  align-items:center; padding:1px 10px 1px 12px; gap:4px;
  min-height:19px; transition:background .1s;
}
.attr-row:hover { background:var(--surface2); }
.attr-row.is-ref { cursor:pointer; }
.attr-row.is-ref:hover { background:rgba(78,207,154,.07); }
.attr-row.attr-hl { background:rgba(78,207,154,.13)!important; outline:1px solid rgba(78,207,154,.3); }
.attr-main { display:flex; align-items:baseline; gap:4px; min-width:0; overflow:hidden; }
.attr-name { font-size:11.5px; color:var(--text); flex-shrink:0; }
.attr-name.req { color:var(--required); font-weight:600; }
.attr-name.ref { color:var(--ref-clr); }
.attr-type { font-size:10px; color:var(--text-dim); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; min-width:0; }
.tag { font-size:8px; font-weight:700; letter-spacing:.05em; padding:1px 4px; border-radius:3px; flex-shrink:0; }
.tag-req { background:rgba(240,160,80,.1); color:var(--required); border:1px solid rgba(240,160,80,.3); }
.tag-ref { background:rgba(78,207,154,.1); color:var(--ref-clr); border:1px solid rgba(78,207,154,.3); }

/* ARROWS */
.arrow-path { fill:none; stroke:var(--arrow-def); stroke-width:1.4; marker-end:url(#mh-def); transition:stroke .15s, opacity .15s; }
.arrow-path.out { stroke:var(--hi-out); stroke-width:1.9; marker-end:url(#mh-out); }
.arrow-path.in  { stroke:var(--hi-in);  stroke-width:1.9; marker-end:url(#mh-in); }
.arrow-path.dimmed { opacity:.05; }
.arrow-lbl { font-family:'JetBrains Mono',monospace; font-size:9px; fill:var(--text-muted); transition:fill .15s, opacity .15s; }
.arrow-lbl.out { fill:var(--hi-out); opacity:.9; }
.arrow-lbl.in  { fill:var(--hi-in);  opacity:.9; }
.arrow-lbl.dimmed { opacity:.04; }

/* Route select */
#route-select {
  background:var(--surface2); border:1px solid var(--border); border-radius:4px;
  color:var(--text-dim); font-family:'JetBrains Mono',monospace; font-size:10px;
  padding:3px 7px; cursor:pointer; flex-shrink:0;
}
#route-select:hover { border-color:var(--accent); }
#route-select option { background:var(--surface2); }
</style>
</head>
<body>

<div id="toolbar">
  <div class="logo">MEx UML</div>
  <div class="sep-v"></div>
  <div class="legend">
    <div class="li"><span class="dot d-req"></span> required</div>
    <div class="li"><span class="dot d-ref"></span> reference (click)</div>
    <div class="li"><span class="dot d-out"></span> outgoing</div>
    <div class="li"><span class="dot d-in"></span>  incoming</div>
  </div>
  <select id="route-select">
    <option value="orthogonal" selected>Orthogonal (elbow)</option>
    <option value="curved">Curved (bezier)</option>
    <option value="straight">Straight</option>
    <option value="bus">Bus (shared spine)</option>
    <option value="metro">Metro (45&deg; diagonal)</option>
  </select>
  <button id="btn-reset">Reset View</button>
  <div class="hint">Scroll=zoom &middot; Drag=pan/move &middot; Click header: out&rarr;in&rarr;reset</div>
</div>

<div id="wrap">
  <div id="canvas">
    <svg id="svg-layer">
      <defs>
        <marker id="mh-def" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
          <path d="M0,0 L8,3 L0,6" fill="none" stroke="var(--arrow-def)" stroke-width="1.2"/>
        </marker>
        <marker id="mh-out" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
          <path d="M0,0 L8,3 L0,6" fill="none" stroke="var(--hi-out)" stroke-width="1.2"/>
        </marker>
        <marker id="mh-in" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
          <path d="M0,0 L8,3 L0,6" fill="none" stroke="var(--hi-in)" stroke-width="1.2"/>
        </marker>
      </defs>
    </svg>
  </div>
</div>

<script>
// =======================================================================
// 1. RAW DATA - auto-generated from mex-model JSON schemas
// =======================================================================
const r = (n,t) => ({name:n,type:t,required:true});
const o = (n,t) => ({name:n,type:t,required:false});

/* __RAW_DATA__ */

// =======================================================================
// 2. VIEW MODEL - resolve refs, sort attrs
// =======================================================================

/* __ID_MAP__ */

const CLASS_IDS = new Set(RAW.map(c=>c.id));

function resolveRefs(typeStr) {
  const found = new Set();
  for (const [k,v] of Object.entries(ID_MAP)) {
    if (typeStr.includes(k)) found.add(v);
  }
  return [...found].sort();
}

function attrGroup(a) {
  return (a.required ? 0 : 2) + (a.refs.length ? 0 : 1);
}

const CLASSES = RAW.map(cls => {
  const attrs = cls.attrs.map(a => ({ ...a, refs: resolveRefs(a.type) }));
  attrs.sort((a,b) => {
    const ga = attrGroup(a), gb = attrGroup(b);
    return ga !== gb ? ga-gb : a.name.localeCompare(b.name);
  });
  return { id:cls.id, attrs };
});

function buildEdges() {
  const map = {};
  CLASSES.forEach(cls => {
    cls.attrs.forEach(attr => {
      attr.refs.forEach(tgt => {
        const k = cls.id + '\u2192' + tgt;
        if (!map[k]) map[k] = { from:cls.id, to:tgt, labels:[] };
        if (!map[k].labels.includes(attr.name)) map[k].labels.push(attr.name);
      });
    });
  });
  return Object.values(map);
}
const EDGES = buildEdges();

// =======================================================================
// 3. LAYOUT - columns, stacked rows
// =======================================================================

/* __GRID_LAYOUT__ */

const CARD_W = 310;
const COL_GAP = 80;
const ROW_GAP = 60;
const PAD = 60;

const canvasEl = document.getElementById('canvas');
const svgEl    = document.getElementById('svg-layer');
const positions = {};
const cardEls   = {};
const arrowMeta = [];

// =======================================================================
// 4. RENDER CARDS
// =======================================================================
function fmtType(t) {
  return t
    .replace(/MergedOrganizationalUnitIdentifier \| MergedPersonIdentifier \| MergedContactPointIdentifier/g,
             'OrgUnit|Person|ContactPoint\u2026ID')
    .replace(/MergedOrganizationIdentifier \| MergedPersonIdentifier/g,
             'Organization|Person\u2026ID')
    .replace(/Merged(\w+?)Identifier/g, (_,n) => n+'\u2197')
    .replace(/YearMonthDayTime \| YearMonthDay \| YearMonth \| Year/g, 'Year\u2026DayTime')
    .replace(/YearMonthDay \| YearMonth \| Year/g, 'Year\u2026Day');
}

function buildCards() {
  CLASSES.forEach(cls => {
    positions[cls.id] = { x:0, y:0, w:CARD_W, h:0 };

    const card = document.createElement('div');
    card.className = 'cls-card';
    card.id = 'card-' + cls.id;
    card.style.cssText = 'width:'+CARD_W+'px;left:0;top:0;';

    const hdr = document.createElement('div');
    hdr.className = 'cls-header';
    hdr.innerHTML = '<div class="cls-name">'+cls.id+'</div><div class="cls-sub">click: outgoing \u2192 incoming \u2192 reset</div>';
    hdr.addEventListener('click', function(e) { e.stopPropagation(); cycleClass(cls.id); });
    card.appendChild(hdr);

    var secs = [
      { key:'req-ref',  label:'Required \xb7 Reference', items: cls.attrs.filter(function(a){return a.required && a.refs.length;}) },
      { key:'req-plain',label:'Required',                items: cls.attrs.filter(function(a){return a.required && !a.refs.length;}) },
      { key:'opt-ref',  label:'Optional \xb7 Reference', items: cls.attrs.filter(function(a){return !a.required && a.refs.length;}) },
      { key:'opt-plain',label:'Optional',                items: cls.attrs.filter(function(a){return !a.required && !a.refs.length;}) },
    ].filter(function(s){return s.items.length;});

    secs.forEach(function(sec) {
      var div = document.createElement('div');
      div.className = 'attr-sect';
      var lbl = document.createElement('div');
      lbl.className = 'sect-label';
      lbl.textContent = sec.label;
      div.appendChild(lbl);

      sec.items.forEach(function(attr) {
        var isRef = attr.refs.length > 0;
        var row = document.createElement('div');
        row.className = 'attr-row' + (isRef ? ' is-ref' : '');
        row.dataset.cls = cls.id;
        row.dataset.attr = attr.name;

        var main = document.createElement('div');
        main.className = 'attr-main';
        var nameEl = document.createElement('span');
        nameEl.className = 'attr-name' + (attr.required?' req':'') + (isRef?' ref':'');
        nameEl.textContent = attr.name;
        var typeEl = document.createElement('span');
        typeEl.className = 'attr-type';
        typeEl.textContent = ' : ' + fmtType(attr.type);
        main.appendChild(nameEl);
        main.appendChild(typeEl);
        row.appendChild(main);

        if (attr.required || isRef) {
          var tag = document.createElement('span');
          tag.className = 'tag ' + (attr.required ? 'tag-req' : 'tag-ref');
          tag.textContent = attr.required ? 'REQ' : 'REF';
          row.appendChild(tag);
        }

        if (isRef) {
          row.title = 'References: ' + attr.refs.join(', ');
          row.addEventListener('click', (function(fromId, attrName, refs) {
            return function(e) { e.stopPropagation(); highlightAttr(fromId, attrName, refs); };
          })(cls.id, attr.name, attr.refs));
        }
        div.appendChild(row);
      });
      card.appendChild(div);
    });

    canvasEl.appendChild(card);
    cardEls[cls.id] = card;
    makeDraggable(card, cls.id);
  });
}

// =======================================================================
// 5. COMPUTE POSITIONS
// =======================================================================
function computeLayout() {
  CLASSES.forEach(function(cls) {
    positions[cls.id].h = cardEls[cls.id].offsetHeight;
    positions[cls.id].w = CARD_W;
  });

  var cols = {};
  CLASSES.forEach(function(cls) {
    var col = GRID_COL[cls.id] != null ? GRID_COL[cls.id] : 0;
    var row = GRID_ROW[cls.id] != null ? GRID_ROW[cls.id] : 0;
    if (!cols[col]) cols[col] = [];
    cols[col].push({ id:cls.id, row:row });
  });
  Object.values(cols).forEach(function(arr) { arr.sort(function(a,b){return a.row-b.row;}); });

  var sortedCols = Object.keys(cols).map(Number).sort(function(a,b){return a-b;});
  var colX = {};
  var cx = PAD;
  sortedCols.forEach(function(col) { colX[col]=cx; cx+=CARD_W+COL_GAP; });

  Object.entries(cols).forEach(function(entry) {
    var col = entry[0], arr = entry[1];
    var yy = PAD;
    arr.forEach(function(item) {
      positions[item.id].x = colX[parseInt(col)];
      positions[item.id].y = yy;
      yy += positions[item.id].h + ROW_GAP;
    });
  });

  CLASSES.forEach(function(cls) {
    var el = cardEls[cls.id];
    el.style.left = positions[cls.id].x + 'px';
    el.style.top  = positions[cls.id].y + 'px';
  });
}

// =======================================================================
// 6. ARROW ROUTING - 5 strategies
// =======================================================================
var currentRoute = 'orthogonal';

function buildArrows() {
  while (svgEl.childNodes.length > 1) svgEl.removeChild(svgEl.lastChild);
  arrowMeta.length = 0;

  EDGES.forEach(function(edge) {
    var g = document.createElementNS('http://www.w3.org/2000/svg','g');
    g.dataset.from = edge.from;
    g.dataset.to   = edge.to;

    var path = document.createElementNS('http://www.w3.org/2000/svg','path');
    path.classList.add('arrow-path');

    var lbl = document.createElementNS('http://www.w3.org/2000/svg','text');
    lbl.classList.add('arrow-lbl');
    var ltxt = edge.labels.length<=2
      ? edge.labels.join(', ')
      : edge.labels[0]+' +'+(edge.labels.length-1);
    lbl.textContent = ltxt;

    g.appendChild(path);
    g.appendChild(lbl);
    svgEl.appendChild(g);
    arrowMeta.push({ edge:edge, path:path, lbl:lbl });
  });
  updateArrows();
}

function rectCenter(id) {
  var p = positions[id];
  return { x: p.x + p.w/2, y: p.y + p.h/2 };
}

function exitPoint(id, dx, dy, offset) {
  var p = positions[id];
  var adx=Math.abs(dx), ady=Math.abs(dy);
  if (adx >= ady) {
    return { x: dx>=0 ? p.x+p.w : p.x, y: p.y+p.h/2+offset, side: dx>=0?'R':'L' };
  } else {
    return { x: p.x+p.w/2+offset, y: dy>=0 ? p.y+p.h : p.y, side: dy>=0?'B':'T' };
  }
}

function entryPoint(id, fromSide, offset) {
  var p = positions[id];
  if (fromSide==='R') return { x:p.x,       y:p.y+p.h/2+offset };
  if (fromSide==='L') return { x:p.x+p.w,   y:p.y+p.h/2+offset };
  if (fromSide==='B') return { x:p.x+p.w/2+offset, y:p.y };
  if (fromSide==='T') return { x:p.x+p.w/2+offset, y:p.y+p.h };
}

function routeOrthogonal(edge, edgeOff) {
  var STEP=20, p1=positions[edge.from], p2=positions[edge.to];
  if (edge.from===edge.to) return selfLoop(p1, edgeOff);
  var fc=rectCenter(edge.from), tc=rectCenter(edge.to);
  var dx=tc.x-fc.x, dy=tc.y-fc.y;
  var ep=exitPoint(edge.from,dx,dy,edgeOff);
  var en=entryPoint(edge.to,ep.side,edgeOff);
  var sx=ep.x,sy=ep.y,ex=en.x,ey=en.y,side=ep.side;
  var d,lx,ly;
  if (side==='R'||side==='L') {
    var x1=sx+(side==='R'?STEP:-STEP), x2=ex+(side==='R'?-STEP:STEP), ym=(sy+ey)/2;
    if (Math.abs(sy-ey)<4) { d='M'+sx+' '+sy+'L'+ex+' '+ey; lx=(sx+ex)/2; ly=sy-6; }
    else if (Math.abs(x1-x2)<4) { d='M'+sx+' '+sy+'L'+x1+' '+sy+'L'+x1+' '+ey+'L'+ex+' '+ey; lx=x1+4; ly=(sy+ey)/2; }
    else { d='M'+sx+' '+sy+'L'+x1+' '+sy+'L'+x1+' '+ym+'L'+x2+' '+ym+'L'+x2+' '+ey+'L'+ex+' '+ey; lx=(x1+x2)/2; ly=ym-6; }
  } else {
    var y1=sy+(side==='B'?STEP:-STEP), y2=ey+(side==='B'?-STEP:STEP), xm=(sx+ex)/2;
    if (Math.abs(sx-ex)<4) { d='M'+sx+' '+sy+'L'+ex+' '+ey; lx=sx+5; ly=(sy+ey)/2; }
    else if (Math.abs(y1-y2)<4) { d='M'+sx+' '+sy+'L'+sx+' '+y1+'L'+ex+' '+y1+'L'+ex+' '+ey; lx=(sx+ex)/2; ly=y1-6; }
    else { d='M'+sx+' '+sy+'L'+sx+' '+y1+'L'+xm+' '+y1+'L'+xm+' '+y2+'L'+ex+' '+y2+'L'+ex+' '+ey; lx=xm; ly=(y1+y2)/2-6; }
  }
  return { d:d, lx:lx, ly:ly };
}

function routeCurved(edge, edgeOff) {
  if (edge.from===edge.to) return selfLoop(positions[edge.from], edgeOff);
  var fc=rectCenter(edge.from), tc=rectCenter(edge.to);
  var dx=tc.x-fc.x, dy=tc.y-fc.y;
  var ep=exitPoint(edge.from,dx,dy,edgeOff);
  var en=entryPoint(edge.to,ep.side,edgeOff);
  var sx=ep.x,sy=ep.y,ex=en.x,ey=en.y;
  var PULL=Math.min(120, Math.sqrt(dx*dx+dy*dy)*0.45);
  var c1x,c1y,c2x,c2y;
  if (ep.side==='R'||ep.side==='L') {
    var sign=ep.side==='R'?1:-1;
    c1x=sx+sign*PULL; c1y=sy; c2x=ex-sign*PULL; c2y=ey;
  } else {
    var sign2=ep.side==='B'?1:-1;
    c1x=sx; c1y=sy+sign2*PULL; c2x=ex; c2y=ey-sign2*PULL;
  }
  var d='M'+sx+' '+sy+'C'+c1x+' '+c1y+','+c2x+' '+c2y+','+ex+' '+ey;
  return { d:d, lx:(sx+ex)/2, ly:(sy+ey)/2-8 };
}

function routeStraight(edge, edgeOff) {
  if (edge.from===edge.to) return selfLoop(positions[edge.from], edgeOff);
  var fc=rectCenter(edge.from), tc=rectCenter(edge.to);
  var dx=tc.x-fc.x, dy=tc.y-fc.y;
  var ep=exitPoint(edge.from,dx,dy,edgeOff);
  var en=entryPoint(edge.to,ep.side,edgeOff);
  var d='M'+ep.x+' '+ep.y+'L'+en.x+' '+en.y;
  return { d:d, lx:(ep.x+en.x)/2, ly:(ep.y+en.y)/2-6 };
}

function routeBus(edge, edgeOff, allEdges) {
  if (edge.from===edge.to) return selfLoop(positions[edge.from], edgeOff);
  var SPINE_X = _busSpineX(allEdges);
  var p1=positions[edge.from], p2=positions[edge.to];
  var fc=rectCenter(edge.from), tc=rectCenter(edge.to);
  var sx=p1.x+p1.w, sy=fc.y+edgeOff;
  var ex=p2.x,       ey=tc.y+edgeOff;
  var bx=SPINE_X+edgeOff*0.3;
  var d='M'+sx+' '+sy+'L'+bx+' '+sy+'L'+bx+' '+ey+'L'+ex+' '+ey;
  return { d:d, lx:bx+4, ly:(sy+ey)/2 };
}

var _cachedSpineX=null;
function _busSpineX(allEdges) {
  if (_cachedSpineX!==null) return _cachedSpineX;
  var minX=Infinity, maxX=0;
  CLASSES.forEach(function(c){ minX=Math.min(minX,positions[c.id].x); maxX=Math.max(maxX,positions[c.id].x+positions[c.id].w); });
  _cachedSpineX = minX+(maxX-minX)*0.5;
  return _cachedSpineX;
}

function routeMetro(edge, edgeOff) {
  if (edge.from===edge.to) return selfLoop(positions[edge.from], edgeOff);
  var fc=rectCenter(edge.from), tc=rectCenter(edge.to);
  var dx=tc.x-fc.x, dy=tc.y-fc.y;
  var ep=exitPoint(edge.from,dx,dy,edgeOff);
  var en=entryPoint(edge.to,ep.side,edgeOff);
  var sx=ep.x,sy=ep.y,ex=en.x,ey=en.y;
  var adx=Math.abs(ex-sx), ady=Math.abs(ey-sy);
  var diag=Math.min(adx,ady);
  var signX=ex>sx?1:-1, signY=ey>sy?1:-1;
  var mx,my;
  if (adx>ady) { mx=sx+signX*diag; my=ey; }
  else         { mx=ex; my=sy+signY*diag; }
  var d='M'+sx+' '+sy+'L'+mx+' '+my+'L'+ex+' '+ey;
  return { d:d, lx:(sx+ex)/2, ly:(sy+ey)/2-6 };
}

function selfLoop(p, edgeOff) {
  var sx=p.x+p.w, sy=p.y+50+edgeOff, ey=p.y+80+edgeOff, lx=sx+38;
  var d='M'+sx+' '+sy+'L'+lx+' '+sy+'L'+lx+' '+ey+'L'+sx+' '+ey;
  return { d:d, lx:lx+4, ly:(sy+ey)/2+3 };
}

function updateArrows() {
  _cachedSpineX = null;
  var pairCnt={}, pairIdx={};
  arrowMeta.forEach(function(item){
    var k=[item.edge.from,item.edge.to].sort().join('\u2194');
    pairCnt[k]=(pairCnt[k]||0)+1;
  });
  var OFF=16;
  arrowMeta.forEach(function(item){
    var edge=item.edge, path=item.path, lbl=item.lbl;
    var pk=[edge.from,edge.to].sort().join('\u2194');
    if (!pairIdx[pk]) pairIdx[pk]=0;
    var idx=pairIdx[pk]++;
    var total=pairCnt[pk];
    var off=(idx-(total-1)/2)*OFF;
    var r;
    switch(currentRoute) {
      case 'curved':   r=routeCurved(edge,off);       break;
      case 'straight': r=routeStraight(edge,off);      break;
      case 'bus':      r=routeBus(edge,off,EDGES);     break;
      case 'metro':    r=routeMetro(edge,off);         break;
      default:         r=routeOrthogonal(edge,off);    break;
    }
    path.setAttribute('d', r.d);
    lbl.setAttribute('x', r.lx);
    lbl.setAttribute('y', r.ly);
    lbl.setAttribute('text-anchor','middle');
  });
  var mx=0,my=0;
  CLASSES.forEach(function(c){
    mx=Math.max(mx,positions[c.id].x+positions[c.id].w+200);
    my=Math.max(my,positions[c.id].y+positions[c.id].h+200);
  });
  svgEl.setAttribute('width',mx);
  svgEl.setAttribute('height',my);
}

// =======================================================================
// 7. HIGHLIGHT
// =======================================================================
var clickModes = {};

function clearAll() {
  Object.keys(clickModes).forEach(function(k){clickModes[k]=0;});
  CLASSES.forEach(function(c){
    cardEls[c.id].classList.remove('hl-src','hl-tgt','hl-self','dimmed');
  });
  document.querySelectorAll('.attr-row.attr-hl').forEach(function(r){r.classList.remove('attr-hl');});
  arrowMeta.forEach(function(item){
    item.path.classList.remove('out','in','dimmed');
    item.lbl.classList.remove('out','in','dimmed');
  });
}

function applyHighlight(sourceId, targetIds, mode, edgeFilter) {
  var tSet = new Set(targetIds);
  if (mode==='out') {
    cardEls[sourceId].classList.add('hl-src');
    targetIds.forEach(function(t) { if (!cardEls[t]) return; cardEls[t].classList.add(t===sourceId?'hl-self':'hl-tgt'); });
    CLASSES.forEach(function(c){ if(c.id!==sourceId && !tSet.has(c.id)) cardEls[c.id].classList.add('dimmed'); });
    arrowMeta.forEach(function(item){
      var match = item.edge.from===sourceId && tSet.has(item.edge.to) && (!edgeFilter || edgeFilter(item.edge));
      if (match) { item.path.classList.add('out'); item.lbl.classList.add('out'); }
      else       { item.path.classList.add('dimmed'); item.lbl.classList.add('dimmed'); }
    });
  } else {
    cardEls[sourceId].classList.add('hl-tgt');
    targetIds.forEach(function(s) { if (!cardEls[s]) return; cardEls[s].classList.add(s===sourceId?'hl-self':'hl-src'); });
    CLASSES.forEach(function(c){ if(c.id!==sourceId && !tSet.has(c.id)) cardEls[c.id].classList.add('dimmed'); });
    arrowMeta.forEach(function(item){
      var match = item.edge.to===sourceId && tSet.has(item.edge.from) && (!edgeFilter || edgeFilter(item.edge));
      if (match) { item.path.classList.add('in'); item.lbl.classList.add('in'); }
      else       { item.path.classList.add('dimmed'); item.lbl.classList.add('dimmed'); }
    });
  }
}

function cycleClass(id) {
  var cur = clickModes[id]||0;
  var next = (cur+1)%3;
  clearAll();
  if (!next) return;
  clickModes[id]=next;
  if (next===1) {
    var targets = [];
    EDGES.forEach(function(e){ if(e.from===id && targets.indexOf(e.to)===-1) targets.push(e.to); });
    applyHighlight(id, targets, 'out');
  } else {
    var sources = [];
    EDGES.forEach(function(e){ if(e.to===id && sources.indexOf(e.from)===-1) sources.push(e.from); });
    applyHighlight(id, sources, 'in');
  }
}

function highlightAttr(fromId, attrName, refIds) {
  clearAll();
  cardEls[fromId].querySelectorAll('.attr-row').forEach(function(r){
    if(r.dataset.attr===attrName) r.classList.add('attr-hl');
  });
  var tSet = new Set(refIds);
  applyHighlight(fromId, refIds, 'out', function(edge) {
    return edge.from===fromId && tSet.has(edge.to) && edge.labels.indexOf(attrName)!==-1;
  });
}

document.addEventListener('click', function(e){
  if(!e.target.closest('.cls-card')&&!e.target.closest('#toolbar')) clearAll();
});

// =======================================================================
// 8. PAN & ZOOM
// =======================================================================
var scale=0.58, panX=20, panY=20;
var isPan=false, px0, py0, ppx, ppy;
var wrap=document.getElementById('wrap');

function applyXform() {
  canvasEl.style.transform='translate('+panX+'px,'+panY+'px) scale('+scale+')';
}

wrap.addEventListener('mousedown',function(e){
  if(e.target.closest('.cls-card')) return;
  isPan=true; wrap.classList.add('dragging');
  px0=e.clientX; py0=e.clientY; ppx=panX; ppy=panY;
});
window.addEventListener('mousemove',function(e){
  if(!isPan) return;
  panX=ppx+(e.clientX-px0); panY=ppy+(e.clientY-py0); applyXform();
});
window.addEventListener('mouseup',function(){ isPan=false; wrap.classList.remove('dragging'); });
wrap.addEventListener('wheel',function(e){
  e.preventDefault();
  var rect=wrap.getBoundingClientRect();
  var mx=e.clientX-rect.left, my=e.clientY-rect.top;
  var f=e.deltaY<0?1.10:0.91;
  var ns=Math.min(3,Math.max(0.08,scale*f));
  panX=mx-(mx-panX)*(ns/scale);
  panY=my-(my-panY)*(ns/scale);
  scale=ns; applyXform();
},{passive:false});

document.getElementById('btn-reset').addEventListener('click',function(){
  scale=0.58; panX=20; panY=20; applyXform(); clearAll();
});
document.getElementById('route-select').addEventListener('change', function(e){
  currentRoute = e.target.value; _cachedSpineX = null; updateArrows();
});

// =======================================================================
// 9. CARD DRAGGING
// =======================================================================
function makeDraggable(card, id) {
  card.addEventListener('mousedown', function(e){
    if(e.target.closest('.attr-row')||e.button!==0) return;
    var x0=e.clientX, y0=e.clientY;
    var startX=positions[id].x, startY=positions[id].y;
    var moved=false;
    var onMove=function(me){
      var dx=(me.clientX-x0)/scale, dy=(me.clientY-y0)/scale;
      if(!moved&&Math.abs(dx)+Math.abs(dy)<3) return;
      moved=true;
      positions[id].x=startX+dx; positions[id].y=startY+dy;
      card.style.left=positions[id].x+'px'; card.style.top=positions[id].y+'px';
      updateArrows();
    };
    var onUp=function(){
      window.removeEventListener('mousemove',onMove);
      window.removeEventListener('mouseup',onUp);
    };
    window.addEventListener('mousemove',onMove);
    window.addEventListener('mouseup',onUp);
    e.stopPropagation();
  });
}

// =======================================================================
// BOOT
// =======================================================================
buildCards();
applyXform();
requestAnimationFrame(function(){requestAnimationFrame(function(){
  computeLayout();
  buildArrows();
});});
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()
