import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.vfs import VirtualFS


def test_vfs_write_read_remove(tmp_path):
    v = VirtualFS("testpack")
    # write
    v.write_text("foo/bar.txt", "hello world")
    assert "bar.txt" in v.listdir("foo")
    assert v.read_text("foo/bar.txt") == "hello world"
    # remove
    assert v.remove("foo/bar.txt")
    assert "bar.txt" not in v.listdir("foo")
