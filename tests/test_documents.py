import pytest

from dspy_rag_qa.documents import Chunk, load_documents, make_chunks, split_text


def test_split_text_exact_size_gives_one_chunk():
    assert split_text("abcd", 4, 1) == ["abcd"]


def test_split_text_one_over_size_gives_two_chunks():
    assert split_text("abcde", 4, 1) == ["abcd", "de"]


def test_split_text_overlaps_chunks():
    assert split_text("abcdefghij", 4, 1) == ["abcd", "defg", "ghij"]


def test_split_text_without_overlap():
    assert split_text("abcdefgh", 4, 0) == ["abcd", "efgh"]


def test_split_text_empty_text_gives_no_chunks():
    assert split_text("", 4, 1) == []


def test_split_text_rejects_zero_chunk_size():
    with pytest.raises(ValueError, match="chunk_size は1以上"):
        split_text("abc", 0, 0)


def test_split_text_rejects_negative_overlap():
    with pytest.raises(ValueError, match="overlap は0以上"):
        split_text("abc", 4, -1)


def test_split_text_rejects_overlap_equal_to_size():
    with pytest.raises(ValueError, match="chunk_size より小さく"):
        split_text("abc", 4, 4)


def test_split_text_rejects_overlap_larger_than_size():
    with pytest.raises(ValueError, match="chunk_size より小さく"):
        split_text("abc", 4, 5)


def test_load_documents_reads_japanese_file(tmp_path):
    (tmp_path / "rules.md").write_text("第1条(目的)\n有給休暇", encoding="utf-8")
    assert load_documents(tmp_path) == [("rules.md", "第1条(目的)\n有給休暇")]


def test_load_documents_reads_txt_file(tmp_path):
    (tmp_path / "memo.txt").write_text("メモ", encoding="utf-8")
    assert load_documents(tmp_path) == [("memo.txt", "メモ")]


def test_load_documents_skips_other_extensions(tmp_path):
    (tmp_path / "rules.md").write_text("規則", encoding="utf-8")
    (tmp_path / "data.csv").write_text("a,b", encoding="utf-8")
    assert load_documents(tmp_path) == [("rules.md", "規則")]


def test_load_documents_reads_empty_file(tmp_path):
    (tmp_path / "empty.md").write_text("", encoding="utf-8")
    assert load_documents(tmp_path) == [("empty.md", "")]


def test_load_documents_sorts_and_includes_subfolders(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.md").write_text("c", encoding="utf-8")
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    (tmp_path / "a.md").write_text("a", encoding="utf-8")
    names = [name for name, _ in load_documents(tmp_path)]
    assert names == ["a.md", "b.md", "sub/c.md"]


def test_load_documents_missing_folder_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="フォルダが見つかりません"):
        load_documents(tmp_path / "nothing")


def test_load_documents_no_target_files_raises(tmp_path):
    (tmp_path / "data.csv").write_text("a,b", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="対象のファイル"):
        load_documents(tmp_path)


def test_make_chunks_keeps_source_for_each_chunk():
    documents = [("a.md", "abcde"), ("b.md", "xy")]
    assert make_chunks(documents, 4, 1) == [
        Chunk(text="abcd", source="a.md"),
        Chunk(text="de", source="a.md"),
        Chunk(text="xy", source="b.md"),
    ]


def test_make_chunks_skips_empty_document():
    documents = [("empty.md", ""), ("a.md", "ab")]
    assert make_chunks(documents, 4, 1) == [Chunk(text="ab", source="a.md")]
