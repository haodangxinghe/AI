import re
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Sequence, Set


CHINESE_RE = re.compile(r"[\u4e00-\u9fff]+")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_chinese_segments(text: str) -> List[str]:
    return [match.group(0) for match in CHINESE_RE.finditer(text)]


def extract_chinese_tokens(text: str, max_len: int = 6) -> List[str]:
    tokens: List[str] = []
    for match in CHINESE_RE.finditer(text):
        token = match.group(0)
        if 1 <= len(token) <= max_len:
            tokens.append(token)
    return tokens


def load_prior_words(path: Path) -> List[str]:
    raw_text = load_text(path)
    tokens = extract_chinese_tokens(raw_text, max_len=6)
    return tokens


def generate_ngrams(segment: str, min_len: int = 1, max_len: int = 4) -> List[str]:
    tokens: List[str] = []
    length = len(segment)
    for size in range(min_len, max_len + 1):
        for i in range(length - size + 1):
            tokens.append(segment[i : i + size])
    return tokens


def tokenize_shijing(text: str) -> Counter:
    segments = extract_chinese_segments(text)
    counter: Counter[str] = Counter()
    for segment in segments:
        counter.update(generate_ngrams(segment))
    return counter


def filter_prior_by_presence(prior_words: Iterable[str], text: str) -> Set[str]:
    present = set()
    for word in prior_words:
        if word and word in text:
            present.add(word)
    return present


def discover_new_words(token_counts: Counter, known: Set[str], min_freq: int = 8) -> Set[str]:
    new_words = set()
    for tok, freq in token_counts.items():
        if tok in known:
            continue
        if len(tok) < 2:
            continue
        if freq >= min_freq:
            new_words.add(tok)
    return new_words


def extract_keywords(token_counts: Counter, top_k: int = 200) -> Set[str]:
    sorted_tokens = sorted(
        token_counts.items(), key=lambda item: (-item[1], -len(item[0]), item[0])
    )
    keywords: List[str] = []
    for tok, _ in sorted_tokens:
        if len(tok) == 1 and len(keywords) >= top_k:
            break
        keywords.append(tok)
        if len(keywords) >= top_k:
            break
    return set(keywords)


def write_sections(path: Path, sections: Sequence[tuple[str, List[str]]]) -> None:
    lines: List[str] = []
    for title, words in sections:
        lines.append(f"{title}（{len(words)}）")
        lines.append("、".join(words))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def sort_words(words: Iterable[str]) -> List[str]:
    return sorted(set(words), key=lambda w: (len(w), w))


def main():
    base_dir = Path(__file__).parent
    shijing_text = load_text(base_dir / "shijing_plain.txt")
    prior_words = load_prior_words(base_dir / "先验词表.txt")

    token_counts = tokenize_shijing(shijing_text)
    validated_prior = filter_prior_by_presence(prior_words, shijing_text)
    new_words = discover_new_words(token_counts, validated_prior, min_freq=8)
    keywords = extract_keywords(token_counts, top_k=200)

    merged = set().union(validated_prior, new_words, keywords)

    sections = [
        ("校验通过的先验词表", sort_words(validated_prior)),
        ("新词发现", sort_words(new_words)),
        ("关键词提取", sort_words(keywords)),
        ("合并词表", sort_words(merged)),
    ]

    write_sections(base_dir / "自动化词表输出.txt", sections)


if __name__ == "__main__":
    main()
