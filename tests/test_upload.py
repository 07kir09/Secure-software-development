from pathlib import Path

from app.upload import secure_save


def test_rejects_big_file(tmp_path: Path):
    payload = b"\x89PNG\r\n\x1a\n" + b"0" * (5_000_001)
    ok, reason = secure_save(tmp_path, "x.png", payload)

    assert not ok
    assert reason == "too_big"


def test_sniffs_bad_type(tmp_path: Path):
    ok, reason = secure_save(tmp_path, "x.png", b"not_an_image")

    assert not ok
    assert reason == "bad_type"


def test_secure_save_writes_uuid(tmp_path: Path):
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
    ok, path_str = secure_save(tmp_path, "photo.png", png)

    assert ok
    saved = Path(path_str)
    assert saved.exists()
    assert saved.suffix == ".png"
    assert saved.read_bytes() == png
    assert saved.parent == tmp_path


def test_rejects_symlink_parent(tmp_path: Path):
    target_dir = tmp_path / "real"
    target_dir.mkdir()
    link_dir = tmp_path / "link"
    link_dir.symlink_to(target_dir)

    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
    ok, reason = secure_save(link_dir, "photo.png", png)

    assert not ok
    assert reason == "symlink_parent"
