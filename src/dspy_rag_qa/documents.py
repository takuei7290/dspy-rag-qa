"""資料の読み込みとチャンク分割。"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    """検索の単位になる、テキストの一部分。"""

    text: str
    source: str


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """テキストを chunk_size 文字ずつ、overlap 文字ずつ重ねて分割する。"""
    if chunk_size <= 0:
        raise ValueError(f"chunk_size は1以上にしてください: {chunk_size}")
    if overlap < 0:
        raise ValueError(f"overlap は0以上にしてください: {overlap}")
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap は chunk_size より小さくしてください: overlap={overlap}, chunk_size={chunk_size}"
        )

    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunks.append(text[start : start + chunk_size])
        if start + chunk_size >= len(text):
            break
    return chunks


def load_documents(
    folder: str | Path, extensions: tuple[str, ...] = (".md", ".txt")
) -> list[tuple[str, str]]:
    """フォルダ配下の対象ファイルを読み、(ファイル名, 中身) のリストをファイル名順で返す。"""
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"フォルダが見つかりません: {folder}")

    paths = []
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix in extensions:
            paths.append(path)
    if not paths:
        raise FileNotFoundError(
            f"対象のファイル({', '.join(extensions)})がありません: {folder}"
        )

    documents = []
    for path in sorted(paths):
        name = path.relative_to(folder).as_posix()
        documents.append((name, path.read_text(encoding="utf-8")))
    return documents


def make_chunks(
    documents: list[tuple[str, str]], chunk_size: int, overlap: int
) -> list[Chunk]:
    """読み込んだ文書をそれぞれ分割し、出典付きの Chunk にする。"""
    chunks = []
    for source, text in documents:
        for piece in split_text(text, chunk_size, overlap):
            chunks.append(Chunk(text=piece, source=source))
    return chunks
