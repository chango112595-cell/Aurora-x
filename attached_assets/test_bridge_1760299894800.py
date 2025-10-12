from aurora_x.synthesis.universal_engine import generate_project
def test_bridge_ucse(tmp_path):
    res = generate_project("tiny ui app", runs_dir=tmp_path)
    assert (res.run_dir / "project.zip").exists()
