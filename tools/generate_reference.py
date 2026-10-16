#!/usr/bin/env python3
"""Generate docs/輸出對照.txt and docs/符號速查.txt from the delivered 2.1 keylayout.

Every character and every example below is typed through the layout itself
(the same state machine build_and_verify.py checks), so the references cannot
drift from the .keylayout. Run after tools/build_and_verify.py.
"""
import unicodedata
from build_and_verify import ROOT, OUTPUT, LAYOUT_NAME, parse_layout, tables, resolve

DOCS = ROOT / 'docs'

# macOS key codes, US/ABC QWERTY positions.
CODES = {'A': 0, 'S': 1, 'D': 2, 'F': 3, 'H': 4, 'G': 5, 'Z': 6, 'X': 7, 'C': 8,
         'V': 9, 'B': 11, 'Q': 12, 'W': 13, 'E': 14, 'R': 15, 'Y': 16, 'T': 17,
         '1': 18, '2': 19, '3': 20, '4': 21, '6': 22, '5': 23, '=': 24, '9': 25,
         '7': 26, '-': 27, '8': 28, '0': 29, ']': 30, 'O': 31, 'U': 32, '[': 33,
         'I': 34, 'P': 35, 'L': 37, 'J': 38, "'": 39, 'K': 40, ';': 41, '\\': 42,
         ',': 43, '/': 44, 'N': 45, 'M': 46, '.': 47, '空白鍵': 49, '`': 50}
NAMES = {'-': '減號', '=': '等號', '`': '反引號', '[': '左方括號', ']': '右方括號',
         '\\': '反斜線', ';': '分號', "'": '單引號', ',': '逗號', '.': '句號',
         '/': '斜線', '空白鍵': '空白鍵'}
PHYSICAL = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=',
            'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\',
            'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'",
            'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', '空白鍵']
STATES = {'s1': 'grave', 's2': 'caron', 's4': 'cedilla', 's10': 'acute',
          's14': 'breve', 's16': '特殊字母', 's17': '下逗號', 's18': '下點',
          's22': '上圓圈', 's23': 'circumflex'}

root = parse_layout(OUTPUT.read_text(encoding='utf-8'))
actions, terminators, modifiers, maps = tables(root)


def parse(token):
    """'⌥⇧E' -> ('shift option', 14); a bare lowercase letter is an unmodified key."""
    mods = []
    while token[0] in '⌥⇧':
        mods.append({'⌥': 'option', '⇧': 'shift'}[token[0]])
        token = token[1:]
    if len(token) == 1 and token.islower():
        token = token.upper()
    return ' '.join(sorted(mods, reverse=True)), CODES[token]


def press(mods, code, state='none'):
    index = modifiers['mods0'][frozenset(mods.split())]
    return resolve(actions, terminators, maps['maps0'][index][code], state)


def type_keys(keys):
    """Type a space-separated key sequence and return the text it produces."""
    text, state = '', 'none'
    for token in keys.split():
        out, state = press(*parse(token), state)
        text += out
    # Apple's layout enters silent post-composition states (e.g. after ⌥B a);
    # only a pending dead key, which has a terminator, means the sequence is unfinished.
    assert not terminators.get(state), keys
    return text


def label(keys):
    """'⌥Y ⌥4' -> '⌥Y → ⌥4', with punctuation keys spelled out."""
    def one(token):
        prefix = token.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-=`[]\\;\',./')
        key = token[len(prefix):]
        return prefix + NAMES.get(key, key)
    return ' → '.join(one(t) for t in keys.split())


def codepoints(text):
    return ' '.join('U+%04X' % ord(c) for c in text)


def shown(text):
    """Combining marks are shown on a dotted circle; the layout never outputs the circle."""
    if text and all(unicodedata.combining(c) for c in text):
        return '◌' + text
    return text


def cell(mods, key):
    text, state = press(mods, CODES[key])
    if state != 'none' and not text:
        return '死鍵：' + STATES.get(state, state)
    if text == ' ':
        return '空格'
    if text == ' ':
        return '不換行空格'
    if text and all(unicodedata.combining(c) for c in text):
        return '追加' + shown(text)
    return text


def table(header, rows):
    widths = [max(width(r[i]) for r in [header] + rows) for i in range(len(header))]
    def line(r):
        return '  '.join(c + ' ' * (w - width(c)) for c, w in zip(r, widths)).rstrip()
    return '\n'.join([line(header), line(['-' * w for w in widths])] + [line(r) for r in rows])


def width(s):
    """Display width: CJK and fullwidth count as 2, combining marks as 0."""
    return sum(0 if unicodedata.combining(c) else
               2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)


def check(rows):
    """rows: (expected text, key sequence, ...). Assert each sequence types its text."""
    for expected, keys, *_ in rows:
        actual = type_keys(keys)
        assert unicodedata.normalize('NFC', actual) == unicodedata.normalize('NFC', expected), (keys, expected, actual)
    return rows


# ---------------------------------------------------------------- shared data

LETTERS = [('ā', 'A'), ('ī', 'I'), ('ū', 'U'), ('ṛ', 'R'), ('r̥', 'Y'), ('ḷ', 'L'),
           ('ṃ', 'M'), ('ṁ', 'W'), ('m̐', 'F'), ('ḥ', 'H'), ('ḫ', '1'), ('ẖ', '2'),
           ('ṭ', 'T'), ('ḍ', 'D'), ('ṇ', 'N'), ('ṅ', 'G'), ('ñ', 'J'), ('ś', 'Z'), ('ṣ', 'S')]
for lower, key in LETTERS:
    assert type_keys('⌥' + key) == lower, key

LONG = check([('ā', '⌥A', '直接'), ('ī', '⌥I', '直接'), ('ū', '⌥U', '直接'),
              ('ē', 'e ⌥4', '追加'), ('ō', 'o ⌥4', '追加'), ('ṝ', '⌥R ⌥4', '追加'),
              ('ḹ', '⌥L ⌥4', '追加'), ('r̥̄', '⌥Y ⌥4', '追加'), ('Ē', '⇧E ⌥4', '追加'),
              ('ā', 'a ⌥⇧=', '舊入口')])
SHORT = check([('ă', '⌥B a', '前置'), ('ĭ', '⌥B i', '前置'), ('ŭ', '⌥B u', '前置'),
               ('ĕ', 'e ⌥⇧B', '追加'), ('ŏ', 'o ⌥⇧B', '追加')])
METRE = check([('⏑', '⌥9', 'laghu 短音節'), ('–', '⌥-', 'guru 長音節（en dash）'),
               ('⏓', '⌥0', 'anceps 可長可短')])
CRITICAL = check([('⟨', '⇧,', '單角括號（左）'), ('⟩', '⇧.', '單角括號（右）'),
                  ('⟪', '⌥⇧,', '雙角括號（左）'), ('⟫', '⌥⇧.', '雙角括號（右）'),
                  ('°', '⌥7', '省略符，如 °kṣaiḥ、sva°（亦可 ⌥⇧5）'), ('§', '⌥5', '節號'),
                  ('•', '⌥8', '圓點'), ('◊', '⌥⇧8', '菱形'), ('·', '⌥⇧9', '中點'),
                  ('…', '⌥;', '刪節號'), ('—', '⌥⇧-', 'em dash'), ('‡', '⌥⇧7', '雙劍號'),
                  ('¨', '⌥⇧Q', '獨立兩點（不附著）')])
PUNCT = check([('“', '⌥[', ''), ('”', '⌥⇧[', ''), ('‘', '⌥]', ''), ('’', '⌥⇧]', ''),
               ('«', '⌥\\', ''), ('»', '⌥⇧\\', ''), ('‹', '⌥⇧3', ''), ('›', '⌥⇧4', ''),
               ('≤', '⌥,', ''), ('≥', '⌥.', ''), ('≠', '⌥=', ''), ('÷', '⌥/', '')])
# (name, prefix dead key or None, append key, examples)
MARKS = [('acute 尖音符', '⌥E', '⌥⇧E', [('á', '⌥E a'), ('ā́', '⌥A ⌥⇧E')]),
         ('grave 抑音符', '⌥`', '⌥⇧`', [('à', '⌥` a'), ('ā̀', '⌥A ⌥⇧`')]),
         ('circumflex 揚抑符', '⌥6', '⌥⇧6', [('â', '⌥6 a'), ('ā̂', '⌥A ⌥⇧6')]),
         ('macron 長音符', None, '⌥4（或 ⌥⇧=）', [('ē', 'e ⌥4'), ('ṝ', '⌥R ⌥4')]),
         ('diaeresis 兩點', None, '⌥Q', [('ä', 'a ⌥Q'), ('ü', 'u ⌥Q')]),
         ('breve 短音符', '⌥B', '⌥⇧B', [('ă', '⌥B a'), ('ŏ', 'o ⌥⇧B')]),
         ('caron 抑揚符', '⌥V', '⌥⇧V', [('č', '⌥V c'), ('ǎ', 'a ⌥⇧V')]),
         ('cedilla 下加符', '⌥C', '⌥⇧C', [('ç', '⌥C c')]),
         ('ring 上圓圈', '⌥K', '⌥⇧K', [('å', '⌥K a')]),
         ('dot below 下點', '⌥X', '⌥⇧X', [('ṇ', '⌥X n'), ('ẹ', 'e ⌥⇧X')]),
         ('comma below 下逗號', '⌥P', '⌥⇧P', [('ș', '⌥P s')])]
for _, prefix, append, examples in MARKS:
    check(examples)
    if prefix:
        assert press(*parse(prefix))[1] != 'none', prefix
    assert all(unicodedata.combining(c) for c in type_keys(append.split('（')[0]))
STACKED = check([('r̥̄́', '⌥Y ⌥4 ⌥⇧E'), ('ā́', '⌥E ⌥A'), ('Ā́', '⌥⇧A ⌥⇧E')])


def mark_rows():
    rows = []
    for name, prefix, append, examples in MARKS:
        ex = '；'.join(label(k) + ' = ' + t for t, k in examples)
        key, _, note = append.partition('（')
        rows.append([name, label(prefix) if prefix else '—', label(key) + ('（' + note if note else ''), ex])
    return rows


VERSION = LAYOUT_NAME.rsplit(' ', 1)[1]
LEGEND = '''⌥ = Option，⇧ = Shift，均同時按住；左右兩側皆可。
→ 表示放開後再按下一組。小寫字母（如 a）表示直接按該鍵。
鍵位以 ABC Extended／美式 QWERTY 為準；數字指上排數字鍵。
IAST 字母鍵請關閉 Caps Lock（數字鍵、Q 及符號鍵不受影響）。'''

# ---------------------------------------------------------------- 符號速查

quick = f'''{LAYOUT_NAME}：符號速查
本檔由 tools/generate_reference.py 從布局檔生成，所有例子都經模擬輸入驗證。

{LEGEND}


一、IAST 字母（⌥ 小寫，⌥⇧ 大寫）

{table(['字母', '按鍵', '大寫', '按鍵', 'Unicode'],
       [[l, '⌥' + k, type_keys('⌥⇧' + k), '⌥⇧' + k, codepoints(l)] for l, k in LETTERS])}


二、長短音

元音長音（直接輸入，或先打字母再追加 ⌥4）：
{table(['輸出', '按鍵', '方式'], [[t, label(k), m] for t, k, m in LONG])}

元音短音（breve）：
{table(['輸出', '按鍵', '方式'], [[t, label(k), m] for t, k, m in SHORT])}

格律符號：
{table(['符號', '按鍵', '說明'], [[t, label(k), m] for t, k, m in METRE])}


三、校勘符號

{table(['符號', '按鍵', '說明'], [[t, label(k), m] for t, k, m in CRITICAL])}

其他標點：
{table(['符號', '按鍵'], [[t, label(k)] for t, k, _ in PUNCT])}


四、組合鍵輸入

前置（死鍵）：先按組合鍵，再打字母。
追加（後置）：先打字母，再按組合鍵，中間不按空格。

{table(['附加符號', '前置', '追加', '例子'], mark_rows())}

可疊加：{'；'.join(label(k) + ' = ' + t for t, k in STACKED)}。
已帶長音的 ā 不要再按 ⌥4，否則會疊上第二個長音符。
'''

# ---------------------------------------------------------------- 輸出對照

nonascii = []
for key in PHYSICAL:
    for mods, prefix in [('option', '⌥'), ('shift option', '⌥⇧'), ('shift', '⇧')]:
        text, state = press(mods, CODES[key])
        if state == 'none' and text and not text.isascii() and text != ' ':
            name = ' + '.join(unicodedata.name(c, '?') for c in text)
            nonascii.append([shown(text), prefix + NAMES.get(key, key), codepoints(text), name])

CAPS_CHANGED = [NAMES.get(k, k) for k in PHYSICAL
                if any(press(m, CODES[k]) != press('caps ' + m, CODES[k]) for m in ['option', 'shift option'])]

full = f'''{LAYOUT_NAME}：輸出對照
本檔由 tools/generate_reference.py 從布局檔生成。

{LEGEND}
「死鍵」：按下後等待下一個字母，例如 ⌥E → a = á。
「追加」：輸出一個組合附加符號，附著在前一個字母上，例如 a → ⌥4 = ā。
◌ 只是示意位置，布局不會輸出這個圓圈。


一、全部實體鍵的四層輸出

{table(['實體鍵', '直接', '⇧', '⌥', '⌥⇧'],
       [[NAMES.get(k, k)] + [cell(m, k) for m in ['', 'shift', 'option', 'shift option']] for k in PHYSICAL])}


二、非 ASCII 輸出的精確碼位

{table(['輸出', '按鍵', 'Unicode', '名稱'], nonascii)}

H̱、m̐、M̐、r̥、R̥ 由「字母＋組合符號」兩個碼位組成，其餘多為單一預組字元。
⌥A 輸出預組 ā（U+0101），a → ⌥4 輸出 a + U+0304；兩者在 Unicode 中等價，
但布局不會替整份文件做正規化。


三、Caps Lock 與其他修飾鍵

• Caps Lock 開啟時，下列鍵的 ⌥／⌥⇧ 層回到系統 ABC Extended 的原有輸出
  （例如 ⌥A 變回長音死鍵、⌥R 變成 ®）：
  {'、'.join(CAPS_CHANGED)}
• 其餘鍵（包括 1、2、4、Q、所有格律與校勘符號）Caps Lock 開或關都一樣。
• 含 Command 或 Control 的組合保持 ABC Extended 原樣，不影響系統快捷鍵。
• ⇧逗號、⇧句號 已改為 ⟨ ⟩，本布局中無法輸入 < 和 >；需要時請切回 ABC 或 ABC Extended。


四、{VERSION} 相對 2.0 的變更

⌥1／⌥⇧1：¡／⁄ → ḫ／Ḫ（ḫ 由 Q 移來）
⌥2／⌥⇧2：™／€ → ẖ／H̱
⌥4：¢ → 追加長音符 U+0304（⌥⇧4 的 › 保留）
⌥Q：ḫ → 追加兩點 U+0308
⌥⇧Q：Ḫ → 獨立兩點 ¨ U+00A8
其餘 IAST、重音、格律與校勘符號全部沿用 2.0。
'''

DOCS.mkdir(exist_ok=True)
(DOCS / '符號速查.txt').write_text(quick, encoding='utf-8')
(DOCS / '輸出對照.txt').write_text(full, encoding='utf-8')
print('Generated docs/符號速查.txt and docs/輸出對照.txt from', OUTPUT.name)
