def test_info():
    from core.module import info
    r = info()
    assert r.get('pack') == 'pack05_5J_state_persistence'
