#!/usr/bin/env python3
"""
Aurora Phase-1 Production Manifest Generator
Generates module manifests for batch module generation.
"""

import argparse
import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

CATEGORIES = [
    "connector",
    "processor",
    "analyzer",
    "validator",
    "transformer",
    "optimizer",
    "monitor",
    "generator",
    "formatter",
    "integrator",
]

DRIVERS = {
    "connector": ["http", "grpc", "websocket", "mqtt", "amqp"],
    "processor": ["batch", "stream", "parallel", "sequential"],
    "analyzer": ["pattern", "statistical", "ml", "rule-based"],
    "validator": ["schema", "semantic", "syntax", "constraint"],
    "transformer": ["json", "xml", "csv", "binary", "protobuf"],
    "optimizer": ["cache", "compression", "dedup", "index"],
    "monitor": ["metrics", "logs", "traces", "alerts"],
    "generator": ["template", "procedural", "ml", "rule"],
    "formatter": ["text", "html", "markdown", "pdf"],
    "integrator": ["api", "database", "filesystem", "message-queue"],
}

CAPABILITIES = {
    "connector": ["connect", "disconnect", "send", "receive", "ping"],
    "processor": ["process", "batch", "filter", "aggregate", "transform"],
    "analyzer": ["analyze", "detect", "classify", "score", "report"],
    "validator": ["validate", "check", "verify", "assert", "sanitize"],
    "transformer": ["encode", "decode", "convert", "serialize", "deserialize"],
    "optimizer": ["optimize", "cache", "compress", "dedupe", "index"],
    "monitor": ["collect", "aggregate", "alert", "report", "trace"],
    "generator": ["generate", "create", "synthesize", "produce", "emit"],
    "formatter": ["format", "render", "template", "stringify", "prettify"],
    "integrator": ["integrate", "sync", "bridge", "adapt", "proxy"],
}


def generate_module_id(index: int) -> str:
    return f"{index:04d}"


def generate_checksum(data: dict) -> str:
    content = json.dumps(data, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def create_module_entry(index: int, category: str = None) -> dict:
    if category is None:
        category = CATEGORIES[index % len(CATEGORIES)]

    module_id = generate_module_id(index)
    drivers = DRIVERS.get(category, ["default"])
    capabilities = CAPABILITIES.get(category, ["execute"])

    driver = drivers[index % len(drivers)]

    entry = {
        "id": module_id,
        "uuid": str(uuid.uuid4()),
        "category": category,
        "name": f"{category}_{module_id}",
        "driver": driver,
        "capabilities": capabilities,
        "version": "1.0.0",
        "priority": (index % 10) + 1,
        "dependencies": [],
        "config": {
            "timeout_ms": 30000,
            "retry_count": 3,
            "buffer_size": 8192,
            "driver_options": {},
        },
        "metadata": {
            "created": datetime.now(UTC).isoformat(),
            "author": "aurora-generator",
            "tags": [category, driver, f"priority-{(index % 10) + 1}"],
        },
    }

    entry["checksum"] = generate_checksum(entry)
    return entry


def generate_manifest(count: int, categories: list = None) -> dict:
    if categories is None:
        categories = CATEGORIES

    modules = []
    for i in range(1, count + 1):
        category = categories[(i - 1) % len(categories)]
        modules.append(create_module_entry(i, category))

    manifest = {
        "version": "1.0.0",
        "generated": datetime.now(UTC).isoformat(),
        "generator": "aurora-phase1-manifest-generator",
        "total_modules": count,
        "categories": list(set(m["category"] for m in modules)),
        "modules": modules,
    }

    manifest["manifest_checksum"] = generate_checksum(manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate Aurora module manifest")
    parser.add_argument(
        "--out", "-o", type=str, default="modules.manifest.json", help="Output manifest file path"
    )
    parser.add_argument(
        "--count", "-c", type=int, default=550, help="Number of modules to generate (default: 550)"
    )
    parser.add_argument(
        "--categories", type=str, nargs="+", choices=CATEGORIES, help="Limit to specific categories"
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")

    args = parser.parse_args()

    print(f"[MANIFEST] Generating {args.count} module entries...")

    manifest = generate_manifest(args.count, args.categories)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        if args.pretty:
            json.dump(manifest, f, indent=2)
        else:
            json.dump(manifest, f)

    print(f"[MANIFEST] Generated manifest with {manifest['total_modules']} modules")
    print(f"[MANIFEST] Categories: {', '.join(manifest['categories'])}")
    print(f"[MANIFEST] Output: {out_path}")
    print(f"[MANIFEST] Checksum: {manifest['manifest_checksum']}")

    return manifest


if __name__ == "__main__":
    main()
