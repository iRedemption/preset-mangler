"""Library statistics for the Stats page; per-file records are cached by path, size and mtime."""

import collections
import datetime as dt
import hashlib
import json
from pathlib import Path

from backend import settings
from backend.container import unpack_in_memory
from backend.generator.constants import PATCH_WORDS
from backend.generator.selection import patch_families, source_labels
from backend.settings import ASSETS, library_paths

OSC_WRAPPERS = ("Oscillator0", "Oscillator1", "Oscillator2")
FILTERS = ("VoiceFilter0", "VoiceFilter1")
FX_RACKS = ("FXRack0", "FXRack1", "FXRack2")
MOD_SLOTS = [f"ModSlot{index}" for index in range(64)]
UNCLASSIFIED = "Unclassified"
CACHE_VERSION = 2  # bump whenever extract() output changes so stale cache entries are dropped


def _params(node):
    params = node.get("plainParams") if isinstance(node, dict) else None
    return params if isinstance(params, dict) else {}


def _engine(wrapper):
    if not isinstance(wrapper, dict):
        return None
    # Only the selected engine stores data beyond plainParams; the others hold defaults alone.
    active = [
        key for key, value in wrapper.items()
        if key != "plainParams" and isinstance(value, dict) and set(value) - {"plainParams"}
    ]
    return active[0].rstrip("0123456789") if active else None


def _route_label(labels, source):
    key = tuple(source) if isinstance(source, list) and len(source) == 2 else None
    if key is None:
        return "Unknown"
    return labels.get(key) or f"[{key[0]}, {key[1]}]"


def extract(path, labels):
    """Return a JSON-serialisable record describing one preset."""
    raw = path.read_bytes()
    preset = unpack_in_memory(raw)
    data, meta = preset["data"], preset["metadata"]
    categories = sorted(patch_families(path)) or [UNCLASSIFIED]
    engines = [_engine(data.get(key)) for key in OSC_WRAPPERS]
    filters = []
    for key in FILTERS:
        kind = _params(data.get(key)).get("kParamType")
        if isinstance(kind, str):
            filters.append(kind)
    fx = []
    for key in FX_RACKS:
        rack = data.get(key)
        for slot in (rack.get("FX") if isinstance(rack, dict) else None) or []:
            if isinstance(slot, dict):
                fx.extend(name for name in slot if name.startswith("FX"))
    routes = []
    for key in MOD_SLOTS:
        params = _params(data.get(key))
        if not params:
            continue
        slot = data[key]
        dest = slot.get("destModuleTypeString") or "Unknown"
        param = slot.get("destModuleParamName") or slot.get("destModuleParamID") or "?"
        routes.append([_route_label(labels, slot.get("source")), f"{dest}: {param}"])
    unison = _params(data.get("Oscillator0")).get("kParamUnison")
    return {
        "name": path.stem, "size": len(raw), "mtime": path.stat().st_mtime,
        "sha256": hashlib.sha256(raw).hexdigest(), "categories": categories,
        "engines": [engine for engine in engines if engine], "filters": filters, "fx": fx,
        "routes": routes, "unison": unison if isinstance(unison, int) else None,
        "tags": [tag for tag in meta.get("tags", []) if isinstance(tag, str)],
        "author": meta.get("presetAuthor") or "Unknown",
    }


def _cache():
    return settings.CONFIG.with_name("stats-cache.json")


def _load_cache():
    try:
        payload = json.loads(_cache().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload.get("files", {}) if payload.get("version") == CACHE_VERSION else {}


def _records(library):
    cache, fresh, labels = _load_cache(), {}, source_labels(ASSETS)
    records = []
    for path in library_paths(library):
        stat = path.stat()
        key = str(path.resolve())
        cached = cache.get(key)
        if cached and cached["size"] == stat.st_size and cached["mtime"] == stat.st_mtime:
            record = cached["record"]
        else:
            record = extract(path, labels)
        fresh[key] = {"size": stat.st_size, "mtime": stat.st_mtime, "record": record}
        records.append(record)
    _cache().write_text(json.dumps({"version": CACHE_VERSION, "files": fresh}), encoding="utf-8")
    return records


def _top(counter, limit=None):
    items = counter.most_common(limit)
    return [[name, count] for name, count in items]


def build(library):
    """Aggregate every library preset into one payload for the Stats page."""
    records = _records(library)
    count = len(records)
    if count == 0:
        return {"count": 0}
    hashes = collections.Counter(record["sha256"] for record in records)
    categories = collections.Counter(c for r in records for c in r["categories"])
    engines = collections.Counter(e for r in records for e in r["engines"])
    filters = collections.Counter(f for r in records for f in r["filters"])
    fx = collections.Counter(f for r in records for f in r["fx"])
    sources = collections.Counter(route[0] for r in records for route in r["routes"])
    destinations = collections.Counter(route[1] for r in records for route in r["routes"])
    top_sources = [name for name, _ in sources.most_common(12)]
    top_dests = [name for name, _ in destinations.most_common(12)]
    cells = collections.Counter((route[0], route[1]) for r in records for route in r["routes"])
    heatmap = [[top_dests.index(d), top_sources.index(s), cells[(s, d)]]
               for s in top_sources for d in top_dests if cells[(s, d)]]
    buckets = ["0", "1-4", "5-10", "11-20", "21+"]
    route_hist = collections.Counter()
    for record in records:
        n = len(record["routes"])
        route_hist[buckets[0] if n == 0 else buckets[1] if n <= 4 else buckets[2] if n <= 10
                   else buckets[3] if n <= 20 else buckets[4]] += 1
    primary = lambda r: r["categories"][0]
    links = collections.Counter()
    for r in records:
        engine = r["engines"][0] if r["engines"] else "None"
        filt = r["filters"][0] if r["filters"] else "None"
        links[(primary(r), f"Engine: {engine}")] += 1
        links[(f"Engine: {engine}", f"Filter: {filt}")] += 1
    nodes = sorted({n for pair in links for n in pair})
    months = collections.defaultdict(collections.Counter)
    days = collections.Counter()
    for r in records:
        stamp = dt.datetime.fromtimestamp(r["mtime"])
        months[stamp.strftime("%Y-%m")][primary(r)] += 1
        days[stamp.strftime("%Y-%m-%d")] += 1
    month_keys = sorted(months)
    series_names = [name for name, _ in categories.most_common()]
    unison = collections.Counter(r["unison"] for r in records if r["unison"] is not None)
    return {
        "count": count,
        "total_bytes": sum(r["size"] for r in records),
        "duplicates": sum(n - 1 for n in hashes.values() if n > 1),
        "with_mods": sum(1 for r in records if r["routes"]),
        "with_fx": sum(1 for r in records if r["fx"]),
        "avg_routes": round(sum(len(r["routes"]) for r in records) / count, 1),
        "unclassified": categories.get(UNCLASSIFIED, 0),
        "families": sorted(PATCH_WORDS),
        "categories": _top(categories),
        "engines": _top(engines),
        "filters": _top(filters),
        "fx": _top(fx),
        "sources": _top(sources, 15),
        "heatmap": {"sources": top_sources, "destinations": top_dests, "cells": heatmap},
        "route_hist": [[bucket, route_hist.get(bucket, 0)] for bucket in buckets],
        "sankey": {"nodes": nodes, "links": [[a, b, n] for (a, b), n in links.items()]},
        "monthly": {"months": month_keys, "series": {
            name: [months[m].get(name, 0) for m in month_keys] for name in series_names}},
        "calendar": sorted(([day, n] for day, n in days.items())),
        "tags": _top(collections.Counter(t for r in records for t in r["tags"]), 15),
        "authors": _top(collections.Counter(r["author"] for r in records), 15),
        "unison": sorted([[k, v] for k, v in unison.items()]),
    }
