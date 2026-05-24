from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings
from app.services.diagnostic_domains import analyze_clinical_domains

DEFAULT_DIGEST_PATH = Path(__file__).resolve().parents[1] / "knowledge" / (
    "clinical_orientation.md"
)
WORD_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁ0-9]{4,}")
HEADING_RE = re.compile(r"(?m)^(#{1,4}\s+.+)$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<meta>.*?)\n---\s*\n", re.DOTALL)
STOPWORDS = {
    "если",
    "когда",
    "чтобы",
    "можно",
    "нужно",
    "очень",
    "сейчас",
    "котор",
    "пользователь",
    "человек",
    "состояние",
    "проблема",
    "this",
    "that",
    "with",
    "from",
}


@dataclass
class KnowledgeChunk:
    source: str
    tags: tuple[str, ...]
    text: str
    priority: int = 0


@dataclass
class _KnowledgeCache:
    path: Path | None = None
    mtime_ns: int | None = None
    directory_signature: tuple[tuple[str, int], ...] | None = None
    chunks: list[KnowledgeChunk] | None = None


_cache = _KnowledgeCache()


def _resolve_digest_path() -> Path:
    configured = Path(settings.clinical_knowledge_path).expanduser()
    if configured.is_absolute():
        return configured
    cwd_path = Path.cwd() / configured
    if cwd_path.exists() or configured != Path(settings.clinical_knowledge_path):
        return cwd_path
    return DEFAULT_DIGEST_PATH


def _knowledge_dir() -> Path:
    return DEFAULT_DIGEST_PATH.parent


def _parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta_text = match.group("meta")
    rest = text[match.end():]
    meta: dict[str, object] = {}
    current_list: str | None = None
    for raw_line in meta_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if current_list and line.startswith("- "):
            value = line[2:].strip().strip("\"'")
            items = meta.setdefault(current_list, [])
            if isinstance(items, list):
                items.append(value)
            continue
        current_list = None
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            current_list = key
            meta[key] = []
        elif value.startswith("[") and value.endswith("]"):
            meta[key] = [
                item.strip().strip("\"'")
                for item in value[1:-1].split(",")
                if item.strip()
            ]
        elif value.isdigit():
            meta[key] = int(value)
        else:
            meta[key] = value.strip("\"'")
    return meta, rest


def _meta_tags(meta: dict[str, object], path: Path) -> tuple[str, ...]:
    tags = meta.get("tags")
    result: list[str] = []
    if isinstance(tags, list):
        result.extend(str(item).strip().lower() for item in tags if str(item).strip())
    domain = meta.get("domain")
    if domain:
        result.append(str(domain).strip().lower())
    result.extend(part.lower() for part in path.with_suffix("").parts[-3:])
    return tuple(dict.fromkeys(result))


def _keywords(text: str) -> set[str]:
    return {
        word.lower()
        for word in WORD_RE.findall(text or "")
        if word.lower() not in STOPWORDS
    }


def _split_digest(text: str) -> list[str]:
    clean = text.strip()
    if not clean:
        return []

    marked = HEADING_RE.sub(r"\n\n\1", clean)
    parts = [part.strip() for part in re.split(r"\n{2,}", marked) if part.strip()]
    chunks: list[str] = []
    current = ""
    for part in parts:
        candidate = f"{current}\n\n{part}".strip() if current else part
        if len(candidate) <= 1400:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = part[:1400].strip()
    if current:
        chunks.append(current)
    return chunks


def _source_files(path: Path) -> list[Path]:
    files = [path] if path.exists() else []
    knowledge_dir = _knowledge_dir()
    if knowledge_dir.exists():
        files.extend(
            file
            for file in sorted(knowledge_dir.rglob("*.md"))
            if file != path and file.name != "psychiatry_literature_digest.md"
        )
    return list(dict.fromkeys(files))


def _directory_signature(files: list[Path]) -> tuple[tuple[str, int], ...]:
    signature: list[tuple[str, int]] = []
    for file in files:
        try:
            signature.append((str(file), file.stat().st_mtime_ns))
        except FileNotFoundError:
            continue
    return tuple(signature)


def _load_chunks() -> list[KnowledgeChunk]:
    path = _resolve_digest_path()
    files = _source_files(path)
    signature = _directory_signature(files)
    try:
        stat = path.stat()
    except FileNotFoundError:
        _cache.path = path
        _cache.mtime_ns = None
        _cache.directory_signature = signature
        _cache.chunks = []
        return []

    if (
        _cache.path == path
        and _cache.mtime_ns == stat.st_mtime_ns
        and _cache.directory_signature == signature
        and _cache.chunks is not None
    ):
        return _cache.chunks

    _cache.path = path
    _cache.mtime_ns = stat.st_mtime_ns
    _cache.directory_signature = signature
    loaded: list[KnowledgeChunk] = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        if "Пока он содержит только заглушку" in text:
            continue
        meta, body = _parse_frontmatter(text)
        tags = _meta_tags(meta, file)
        priority = int(meta.get("priority", 0) or 0)
        if file.is_relative_to(_knowledge_dir()):
            source = str(file.relative_to(_knowledge_dir()))
        else:
            source = str(file)
        for chunk in _split_digest(body):
            loaded.append(KnowledgeChunk(source=source, tags=tags, text=chunk, priority=priority))
    _cache.chunks = loaded
    return _cache.chunks


def get_clinical_knowledge_context(query_text: str) -> str:
    chunks = _load_chunks()
    if not chunks:
        return ""

    keywords = _keywords(query_text)
    domains = analyze_clinical_domains(query_text)
    domain_tags = {
        str(tag)
        for domain in domains
        for tag in domain.get("tags", ())
    }

    def score_chunk(chunk: KnowledgeChunk) -> int:
        text = chunk.text.lower()
        tag_score = sum(8 for tag in domain_tags if tag in chunk.tags)
        keyword_score = sum(1 for word in keywords if word in text)
        priority_score = min(chunk.priority, 10)
        return priority_score + tag_score + keyword_score

    if keywords:
        ranked = sorted(
            chunks,
            key=score_chunk,
            reverse=True,
        )
        selected = [chunk for chunk in ranked if score_chunk(chunk) > min(chunk.priority, 10)]
    else:
        selected = []
    if not selected:
        selected = chunks[:2]

    limit = max(600, int(settings.clinical_knowledge_max_chars or 2600))
    result: list[str] = []
    total = 0
    for chunk in selected:
        if total >= limit:
            break
        remaining = limit - total
        heading = f"[Источник: {chunk.source}]"
        body = chunk.text
        text = f"{heading}\n{body}"
        piece = text if len(text) <= remaining else text[:remaining].rsplit(" ", 1)[0].strip()
        if piece:
            result.append(piece)
            total += len(piece) + 2
    return "\n\n".join(result).strip()
