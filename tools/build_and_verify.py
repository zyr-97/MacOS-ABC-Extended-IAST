#!/usr/bin/env python3
"""Build and semantically verify the IAST 2.2 layout. Python 3.8+, stdlib only.

Run from any directory: python3 tools/build_and_verify.py
XML 1.1 control references are masked only in the in-memory inspection copy.
The actual layout preserves the original XML text and control references.
No installation, system modification, or network access is performed.
"""
import hashlib
import json
import plistlib
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import quoteattr

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'source' / 'ABC Extended - IAST.original.keylayout'
VERSION = '2.2'
LAYOUT_NAME = 'ABC Extended - IAST ' + VERSION
BUNDLE = ROOT / ('ABC-Extended-IAST-%s.bundle' % VERSION)
PREVIOUS = ROOT / 'source' / 'ABC Extended - IAST 2.1.keylayout'
OUTPUT = BUNDLE / 'Contents' / 'Resources' / (LAYOUT_NAME + '.keylayout')
BUNDLE_ID = 'local.iast.keyboardlayout.abcextended22'
INPUT_ID = 'local.iast.keylayout.abcextended22'
LAYOUT_ID = '-28682'  # Unique per version so releases can be installed side by side.

# macOS physical key codes. Letters follow the original US/ABC QWERTY map.
DIRECT = {4: 'ḥ', 46: 'ṃ', 13: 'ṁ', 17: 'ṭ', 16: 'r\u0325', 3: 'm\u0310'}
VOWELS = {0: 'ā', 34: 'ī', 32: 'ū', 15: 'ṛ', 37: 'ḷ', 16: 'r\u0325'}
ACCENTS = {'s10': '\u0301', 's1': '\u0300', 's23': '\u0302'}
MACRON_CODE = 24  # Option+Shift+=, not the minus key.
OPTION_SYMBOLS = {25: '\u23d1', 29: '\u23d3', 26: '\u00b0', 43: '<', 47: '>'}
# Keys changed since the previous release (PREVIOUS): {map index: {code: output}}.
# Option and Caps Lock+Option: comma/period give < > (Shift+comma/period stay ⟨ ⟩).
DELTA = {3: {43: '<', 47: '>'}, 7: {43: '<', 47: '>'}}
EXTRA_SYMBOLS = {43: '\u27ea', 47: '\u27eb', 28: '\u25ca', 23: '\u00b0'}


def parse_layout(text):
    """ElementTree is XML 1.0; mask forbidden control references losslessly."""
    def mask(match):
        token = match.group(1)
        value = int(token[1:], 16) if token.startswith('x') else int(token)
        if value < 32 and value not in (9, 10, 13):
            return chr(0xE000 + value)
        return match.group(0)
    return ET.fromstring(re.sub(r'&#(x[0-9A-Fa-f]+|[0-9]+);', mask, text))


def tables(root):
    actions = {a.get('id'): {w.get('state'): dict(w.attrib) for w in a}
               for a in root.find('actions')}
    terminators = {w.get('state'): w.get('output', '') for w in root.find('terminators')}
    modifiers = {m.get('id'): {frozenset(k.get('keys', '').split()): int(s.get('mapIndex'))
                              for s in m for k in s} for m in root.findall('modifierMap')}
    maps = {s.get('id'): {int(m.get('index')): {int(k.get('code')): dict(k.attrib)
                                             for k in m} for m in s}
            for s in root.findall('keyMapSet')}
    return actions, terminators, modifiers, maps


def target(index, code):
    lower = {18: '\u1e2b', 19: '\u1e96', 21: '\u0304', 12: '\u0308'}
    upper = {18: '\u1e2a', 19: 'H\u0331', 12: '\u00a8'}
    if index in (3, 7) and code in lower:
        return lower[code]
    if index in (5, 6) and code in upper:
        return upper[code]
    if index in (3, 7) and code in OPTION_SYMBOLS:
        return OPTION_SYMBOLS[code]
    if index == 1 and code in (43, 47):
        return {43: '\u27e8', 47: '\u27e9'}[code]
    if index in (5, 6) and code in EXTRA_SYMBOLS:
        # Symbols work with Caps Lock either off or on.
        return EXTRA_SYMBOLS[code]
    if index not in (3, 5):
        return None
    if index == 5 and code == MACRON_CODE:
        return '\u0304'
    value = DIRECT.get(code, VOWELS.get(code))
    return value.upper() if value is not None and index == 5 else value


def custom_transition(index, code, state, terminators):
    value = target(index, code)
    if value is None:
        return None
    if code in VOWELS and state in ACCENTS:
        # Keep the vowel's length and dot/ring when adding the accent.
        # Ring-below sequences deliberately retain an explicit base+ring order.
        return value + ACCENTS[state], 'none'
    return terminators.get(state, '') + value, 'none'


def resolve(actions, terminators, key, state):
    if 'output' in key:
        return terminators.get(state, '') + key['output'], 'none'
    rules = actions[key['action']]
    if state in rules:
        rule = rules[state]
        return rule.get('output', ''), rule.get('next', 'none')
    rule = rules['none']
    return terminators.get(state, '') + rule.get('output', ''), rule.get('next', 'none')


def build(original):
    root = parse_layout(original)
    actions, terminators, _, maps = tables(root)
    states = list(next(iter(actions.values())).keys())
    assert states[0] == 'none' and len(states) == 51
    assert all(set(a) == set(states) for a in actions.values())
    added = []
    for index in (1, 3, 5, 6, 7):
        for code in sorted(maps['maps0'][index]):
            if target(index, code) is None:
                continue
            aid = 'iast21_%d_%d' % (index, code)
            lines = ['    <action id="%s">' % aid]
            for state in states:
                out, nxt = custom_transition(index, code, state, terminators)
                assert nxt == 'none'
                lines.append('      <when state=%s output=%s/>' % (quoteattr(state), quoteattr(out)))
            lines.append('    </action>')
            added.append('\n'.join(lines))

    def change_set(match):
        def change_map(mm):
            index = int(mm.group(2))
            def change_key(km):
                code = int(km.group(1))
                if target(index, code) is None:
                    return km.group(0)
                return '<key code="%d" action="iast21_%d_%d"/>' % (code, index, code)
            body = re.sub(r'<key code="(\d+)"[^>]*/>', change_key, mm.group(3))
            return mm.group(1) + body + mm.group(4)
        body = re.sub(r'(<keyMap index="(\d+)">)(.*?)(</keyMap>)', change_map, match.group(2), flags=re.S)
        return match.group(1) + body + match.group(3)
    result = re.sub(r'(<keyMapSet id="maps[01]">)(.*?)(</keyMapSet>)', change_set, original, flags=re.S)
    result = result.replace('id="-28673" name="ABC Extended - IAST"',
                            'id="%s" name="%s"' % (LAYOUT_ID, LAYOUT_NAME), 1)
    result = re.sub(r'<!-- Derived from.*?-->',
                    '<!-- IAST 2.2: Option+comma/period give < >; keeps 2.1 combining macron and diaeresis, h variants, IAST and symbols. '
                    'Derived from the supplied ABC Extended - IAST layout. See README and tools/build_and_verify.py. -->',
                    result, count=1, flags=re.S)
    result = result.replace('  </actions>', '\n'.join(added) + '\n  </actions>', 1)
    assert result != original
    return result


def verify(original, revised):
    old, new = parse_layout(original), parse_layout(revised)
    oa, ot, om, ok = tables(old)
    na, nt, nm, nk = tables(new)
    assert ot == nt and om == nm
    assert old.find('layouts').attrib == new.find('layouts').attrib
    assert ET.tostring(old.find('layouts')) == ET.tostring(new.find('layouts'))
    assert all(na[aid] == rules for aid, rules in oa.items())
    assert new.get('id') != old.get('id')
    assert new.get('name') == LAYOUT_NAME
    states = list(next(iter(oa.values())))
    assert len(na) == len(set(na))
    for ms in nk.values():
        for km in ms.values():
            assert len(km) == 128
            for key in km.values():
                assert ('output' in key) != ('action' in key)
                if 'action' in key:
                    assert key['action'] in na
    max_units = max(len(w.get('output', '').encode('utf-16-le')) // 2
                    for rules in na.values() for w in rules.values())
    assert max_units <= int(new.get('maxout'))

    comparisons = changes = 0
    for ms, modid in [('maps0', 'mods0'), ('maps1', 'mods1')]:
        assert len(om[modid]) == 256
        for modifiers, index in om[modid].items():
            eligible = bool({'option', 'rightOption'} & modifiers) and not (
                {'command', 'control', 'rightControl', 'caps'} & modifiers)
            assert (index in (3, 5)) == eligible
            for code, oldkey in ok[ms][index].items():
                for state in states:
                    before = resolve(oa, ot, oldkey, state)
                    after = resolve(na, nt, nk[ms][index][code], state)
                    expected = custom_transition(index, code, state, ot)
                    assert after == (before if expected is None else expected), (ms, modifiers, code, state)
                    comparisons += 1
                    changes += before != after

    # Independently specified user-visible examples, tested on both map sets.
    seqcases = [
        ('\u1e96', [('option', 19)]),
        ('H\u0331', [('shift option', 19)]),
        ('\u0304', [('option', 21)]),
        ('\u0308', [('option', 12)]),
        ('\u00a8', [('shift option', 12)]),
        ('a\u0304', [('', 0), ('option', 21)]),
        ('e\u0304', [('', 14), ('option', 21)]),
        ('i\u0304', [('', 34), ('option', 21)]),
        ('o\u0304', [('', 31), ('option', 21)]),
        ('u\u0304', [('', 32), ('option', 21)]),
        ('A\u0304', [('shift', 0), ('option', 21)]),
        ('a\u0308', [('', 0), ('option', 12)]),
        ('o\u0308', [('', 31), ('option', 12)]),
        ('u\u0308', [('', 32), ('option', 12)]),
        ('e\u0308', [('', 14), ('option', 12)]),
        ('i\u0308', [('', 34), ('option', 12)]),
        ('A\u0308', [('shift', 0), ('option', 12)]),
        ('a\u00a8', [('', 0), ('shift option', 12)]),
        ('\u00a8a', [('shift option', 12), ('', 0)]),
        ('r\u0325\u0304', [('option', 16), ('option', 21)]),
        ('r\u0325\u0304\u0301', [('option', 16), ('option', 21), ('shift option', 14)]),
        ('\u2260', [('option', 24)]),
        ('\u203a', [('shift option', 21)]),
        ('\u00b4\u1e96', [('option', 14), ('option', 19)]),
        ('am\u0310\u1e2b\u1e96a', [('', 0), ('option', 3), ('option', 18), ('option', 19), ('', 0)]),
        ('m\u0310', [('option', 3)]),
        ('M\u0310', [('shift option', 3)]),
        ('\u1e2b', [('option', 18)]),
        ('\u1e2a', [('shift option', 18)]),
        ('\u23d1', [('option', 25)]),
        ('\u23d3', [('option', 29)]),
        ('\u00b0', [('option', 26)]),
        ('\u2013', [('option', 27)]),
        ('\u2014', [('shift option', 27)]),
        ('\u00a7', [('option', 23)]),
        ('m\u0310\u1e2b', [('rightOption', 3), ('rightOption', 18)]),
        ('M\u0310\u1e2a', [('rightShift rightOption', 3), ('rightShift rightOption', 18)]),
        ('\u23d1\u23d3\u00b0', [('rightOption', 25), ('rightOption', 29), ('rightOption', 26)]),
        ('\u23d1\u23d3\u00b0', [('caps option', 25), ('caps option', 29), ('caps option', 26)]),
        ('\u23d1\u23d3\u00b0', [('caps rightOption', 25), ('caps rightOption', 29), ('caps rightOption', 26)]),
        ('am\u0310a', [('', 0), ('option', 3), ('', 0)]),
        ('a\u1e2bka', [('', 0), ('option', 18), ('', 40), ('', 0)]),
        ('\u00b0k\u1e63ai\u1e25', [('option', 26), ('', 40), ('option', 1), ('', 0), ('', 34), ('option', 4)]),
        ('sva\u00b0', [('', 1), ('', 9), ('', 0), ('option', 26)]),
        ('\u23d1 \u2013 \u23d3', [('option', 25), ('', 49), ('option', 27), ('', 49), ('option', 29)]),
        ('m\u0310\u0301', [('option', 3), ('shift option', 14)]),
        ('\u00b4m\u0310', [('option', 14), ('option', 3)]),
        ('\u00b4\u1e2b', [('option', 14), ('option', 18)]),
        ('\u00b4\u23d1', [('option', 14), ('option', 25)]),
        ('\u00b4\u23d3', [('option', 14), ('option', 29)]),
        ('\u00b4\u00b0', [('option', 14), ('option', 26)]),
        ('\u27ea', [('shift option', 43)]),
        ('\u27eb', [('shift option', 47)]),
        ('\u25ca', [('shift option', 28)]),
        ('\u2022', [('option', 28)]),
        ('\u00b7', [('shift option', 25)]),
        ('\u00b0', [('shift option', 23)]),
        ('\u201a', [('shift option', 29)]),
        ('\u2021', [('shift option', 26)]),
        ('\u27eaabc\u27eb', [('shift option', 43), ('', 0), ('', 11), ('', 8), ('shift option', 47)]),
        ('\u27ea\u27eb\u25ca', [('rightShift rightOption', 43), ('rightShift rightOption', 47), ('rightShift rightOption', 28)]),
        ('\u27ea\u27eb\u25ca', [('shift option caps', 43), ('shift option caps', 47), ('shift option caps', 28)]),
        ('\u00b4\u27ea', [('option', 14), ('shift option', 43)]),
        ('\u00b0', [('shift option caps', 23)]),
        ('a\u030c', [('', 0), ('shift option', 9)]),
        ('\u27e8', [('shift', 43)]),
        ('\u27e9', [('shift', 47)]),
        ('\u27e8\u27e9', [('rightShift', 43), ('rightShift', 47)]),
        ('\u27e8\u27e9', [('shift caps', 43), ('shift caps', 47)]),
        ('\u27e8abc\u27e9', [('shift', 43), ('', 0), ('', 11), ('', 8), ('shift', 47)]),
        (',.', [('', 43), ('', 47)]),
        ('<>', [('option', 43), ('option', 47)]),
        ('<>', [('caps option', 43), ('caps rightOption', 47)]),
        ('<a>', [('option', 43), ('', 0), ('option', 47)]),
        ('\u00b4<', [('option', 14), ('option', 43)]),
        ('\u00b4\u27e8', [('option', 14), ('shift', 43)]),
        ('ḥ', [('option', 4)]), ('Ḥ', [('shift option', 4)]),
        ('ṃ', [('option', 46)]), ('Ṃ', [('shift option', 46)]),
        ('ṁ', [('option', 13)]), ('Ṁ', [('shift option', 13)]),
        ('ṭ', [('option', 17)]), ('Ṭ', [('shift option', 17)]),
        ('ṛ', [('option', 15)]), ('Ṛ', [('shift option', 15)]),
        ('r\u0325', [('option', 16)]), ('R\u0325', [('shift option', 16)]),
        ('ā\u0301', [('option', 0), ('shift option', 14)]),
        ('ā\u0301', [('option', 14), ('option', 0)]),
        ('ī\u0301', [('option', 14), ('option', 34)]),
        ('ū\u0301', [('option', 14), ('option', 32)]),
        ('ṛ\u0301', [('option', 14), ('option', 15)]),
        ('Ā\u0301', [('option', 14), ('shift option', 0)]),
        ('ā\u0300', [('option', 50), ('option', 0)]),
        ('ā\u0302', [('option', 22), ('option', 0)]),
        ('r\u0325\u0301', [('option', 14), ('option', 16)]),
        ('r\u0325\u0304\u0301', [('option', 16), ('shift option', 24), ('shift option', 14)]),
        ('R\u0325\u0304\u0300', [('shift option', 16), ('shift option', 24), ('shift option', 50)]),
        ('é', [('option', 14), ('', 14)]),
        ('ă', [('option', 11), ('', 0)]),
        ('ĭ', [('option', 11), ('', 34)]),
        ('ŭ', [('option', 11), ('', 32)]),
        ('Ă', [('option', 11), ('shift', 0)]),
        ('Ĭ', [('option', 11), ('shift', 34)]),
        ('Ŭ', [('option', 11), ('shift', 32)]),
        ('ă', [('', 0), ('shift option', 11)]),
        ('ĭ', [('', 34), ('shift option', 11)]),
        ('ŭ', [('', 32), ('shift option', 11)]),
        ('ā', [('', 0), ('shift option', 24)]),
        ('ḥ', [('option', 7), ('', 4)]),
        ('ṃ', [('option', 7), ('', 46)]),
        ('namaḥ', [('', 45), ('', 0), ('', 46), ('', 0), ('option', 4)]),
        ('saṃskṛtam', [('', 1), ('', 0), ('option', 46), ('', 1), ('', 40), ('option', 15), ('', 17), ('', 0), ('', 46)]),
        ('aṣṭa', [('', 0), ('option', 1), ('option', 17), ('', 0)]),
        ('r\u0325gvedá', [('option', 16), ('', 5), ('', 9), ('', 14), ('', 2), ('option', 14), ('', 0)]),
    ]
    tests = 0
    for ms, modid in [('maps0', 'mods0'), ('maps1', 'mods1')]:
        def type_sequence(seq):
            output, state = '', 'none'
            for modifiers, code in seq:
                index = nm[modid][frozenset(modifiers.split())]
                text, state = resolve(na, nt, nk[ms][index][code], state)
                output += text
            return output
        for expected, seq in seqcases:
            actual = type_sequence(seq)
            assert unicodedata.normalize('NFC', actual) == unicodedata.normalize('NFC', expected), (expected, actual)
            tests += 1
        # Exact code points and Shift/Caps/right-side modifier behavior are essential
        # for combining marks. NFC-only checks would hide some encoding mistakes.
        for option in ['option', 'rightOption']:
            for caps in ['', 'caps ']:
                mods = caps + option
                for code, expected in [(18, '\u1e2b'), (19, '\u1e96'), (21, '\u0304'), (12, '\u0308')]:
                    assert type_sequence([(mods, code)]) == expected
                    tests += 1
                for shift in ['shift ', 'rightShift ']:
                    for code, expected in [(18, '\u1e2a'), (19, 'H\u0331'), (12, '\u00a8')]:
                        assert type_sequence([(shift + mods, code)]) == expected
                        tests += 1
        for code, base in [(0, 'a'), (14, 'e'), (32, 'u')]:
            assert type_sequence([('', code), ('option', 21)]) == base + '\u0304'
            assert type_sequence([('', code), ('option', 12)]) == base + '\u0308'
            tests += 2
        for code, vowel in VOWELS.items():
            for shift in ('', 'shift '):
                for prefix, suffix, accent in [(14, 14, '\u0301'), (50, 50, '\u0300'), (22, 22, '\u0302')]:
                    before = type_sequence([('option', prefix), (shift + 'option', code)])
                    after = type_sequence([(shift + 'option', code), ('shift option', suffix)])
                    expected = (vowel.upper() if shift else vowel) + accent
                    assert before == after == expected
                    tests += 1
    return {'status': 'PASS', 'transition_comparisons': comparisons,
            'intentional_changed_transitions': changes, 'sequence_tests': tests,
            'hardware_map_sets': 2, 'modifier_combinations_per_set': 256,
            'states': len(states), 'maximum_utf16_output_units': max_units,
            'macOS_runtime_test': 'NOT PERFORMED: Linux build environment',
            'XML_inspection': 'Parsed a control-reference-masked in-memory copy; original XML 1.1 references preserved. No Apple DTD validation claimed.'}


def verify_delta(revised):
    """Independently restrict the changes since the previous release to DELTA."""
    old, new = parse_layout(PREVIOUS.read_text(encoding='utf-8')), parse_layout(revised)
    oa, ot, om, ok = tables(old)
    na, nt, nm, nk = tables(new)
    assert om == nm and ot == nt
    assert new.get('id') != old.get('id')
    comparisons = changes = 0
    states = list(next(iter(oa.values())))
    for ms in ok:
        for index in ok[ms]:
            for code, key in ok[ms][index].items():
                desired = DELTA.get(index, {}).get(code)
                for state in states:
                    before = resolve(oa, ot, key, state)
                    after = resolve(na, nt, nk[ms][index][code], state)
                    expected = before if desired is None else (ot.get(state, '') + desired, 'none')
                    assert after == expected, ('unexpected delta', ms, index, code, state)
                    comparisons += 1
                    changes += before != after
    return {'status': 'PASS', 'previous': PREVIOUS.name,
            'transition_comparisons': comparisons, 'changed_transitions': changes,
            'allowed_changes': ['Option , / Option . : U+003C < / U+003E > (was U+2264 / U+2265)',
                                'Same with Caps Lock on; Shift , / Shift . remain U+27E8 / U+27E9']}


def main():
    original = SOURCE.read_text(encoding='utf-8')
    revised = build(original)
    report = verify(original, revised)
    report['delta_from_previous'] = verify_delta(revised)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(revised, encoding='utf-8')
    info = {
        'CFBundleDevelopmentRegion': 'en',
        'CFBundleIdentifier': BUNDLE_ID,
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundleName': LAYOUT_NAME,
        'CFBundlePackageType': 'BNDL',
        'CFBundleShortVersionString': VERSION,
        'CFBundleVersion': VERSION,
        'KLInfo_' + LAYOUT_NAME: {
            'TISInputSourceID': INPUT_ID,
            'TISIntendedLanguage': 'en',
        },
    }
    plist_path = BUNDLE / 'Contents' / 'Info.plist'
    plist_path.write_bytes(plistlib.dumps(info, fmt=plistlib.FMT_XML, sort_keys=False))
    loaded_info = plistlib.loads(plist_path.read_bytes())
    assert loaded_info == info
    assert '.keyboardlayout.' in loaded_info['CFBundleIdentifier']
    assert 'KLInfo_' + OUTPUT.stem in loaded_info
    assert loaded_info['KLInfo_' + OUTPUT.stem]['TISIntendedLanguage'] == 'en'
    assert parse_layout(OUTPUT.read_text(encoding='utf-8')).get('name') == OUTPUT.stem
    report['bundle_structure'] = 'PASS: plist round-trip, layout name and KLInfo key match'
    report['input_source_language'] = 'en'
    report['press_and_hold_runtime_test'] = 'NOT PERFORMED: macOS user test required'
    report['word_language_and_font_runtime_test'] = 'NOT PERFORMED: metadata is a hint, not a Word formatting lock'
    report['source_sha256'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    report['output_sha256'] = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    (ROOT / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
