"""Container helpers reused from preset-generator/generator_app/container.py."""

import json
import struct

import cbor2
import zstandard as zstd

MAGIC = b"XferJson\x00"


def unpack_in_memory(buf: bytes) -> dict:
    if not buf.startswith(MAGIC):
        raise ValueError("Not a Serum preset: invalid container signature.")
    off = len(MAGIC)
    jlen, _ = struct.unpack_from("<II", buf, off)
    off += 8
    metadata = json.loads(buf[off:off + jlen])
    off += jlen
    clen, _ = struct.unpack_from("<II", buf, off)
    off += 8
    cbor = zstd.ZstdDecompressor().decompress(buf[off:])
    if len(cbor) != clen:
        raise ValueError(f"CBOR length mismatch: expected {clen}, got {len(cbor)}")
    data = cbor2.loads(cbor)
    if not isinstance(data, dict):
        raise ValueError("Preset data must be a module dictionary.")
    return {"metadata": metadata, "data": data}


def pack_in_memory(obj: dict) -> bytes:
    metadata = json.dumps(obj["metadata"], separators=(",", ":")).encode()
    cbor = cbor2.dumps(obj["data"])
    compressed = zstd.ZstdCompressor(level=3).compress(cbor)
    return (MAGIC + struct.pack("<II", len(metadata), 0) + metadata
            + struct.pack("<II", len(cbor), 2) + compressed)
