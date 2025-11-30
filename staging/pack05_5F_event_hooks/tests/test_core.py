def test_info():
    from core.module import info
    r = info()
    assert r.get('pack') == 'pack05_5F_event_hooks'
