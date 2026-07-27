from ragbot.ingest import chunk_text


def test_chunk_text_respects_size_and_overlap():
    text = " ".join(str(i) for i in range(100))
    chunks = chunk_text(text, chunk_size=40, overlap=10)

    assert len(chunks) > 1
    assert all(len(c.split()) <= 40 for c in chunks)


def test_chunk_text_empty_input():
    assert chunk_text("", chunk_size=40, overlap=10) == []
