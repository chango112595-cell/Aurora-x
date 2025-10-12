from pathlib import Path
import json

def test_manifest_has_core_fields():
    p = Path('frontend/pwa/manifest.webmanifest')
    assert p.exists(), "manifest missing"
    m = json.loads(p.read_text(encoding='utf-8'))
    assert m['name'] and m['short_name']
    assert m['display'] in ('standalone','minimal-ui','fullscreen')
    assert 'icons' in m and len(m['icons']) >= 1