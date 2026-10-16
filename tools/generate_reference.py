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

# Rows: (output, keys, 中文說明, English note). check() types every row through the layout.
LONG = check([('ā', '⌥A', '直接', 'direct'), ('ī', '⌥I', '直接', 'direct'), ('ū', '⌥U', '直接', 'direct'),
              ('ē', 'e ⌥4', '追加', 'append'), ('ō', 'o ⌥4', '追加', 'append'),
              ('ṝ', '⌥R ⌥4', '追加', 'append'), ('ḹ', '⌥L ⌥4', '追加', 'append'),
              ('r̥̄', '⌥Y ⌥4', '追加', 'append'), ('Ē', '⇧E ⌥4', '追加', 'append'),
              ('ā', 'a ⌥⇧=', '舊入口', 'legacy key')])
SHORT = check([('ă', '⌥B a', '前置', 'dead key'), ('ĭ', '⌥B i', '前置', 'dead key'),
               ('ŭ', '⌥B u', '前置', 'dead key'), ('ĕ', 'e ⌥⇧B', '追加', 'append'),
               ('ŏ', 'o ⌥⇧B', '追加', 'append')])
METRE = check([('⏑', '⌥9', 'laghu 短音節', 'laghu, light syllable'),
               ('–', '⌥-', 'guru 長音節（en dash）', 'guru, heavy syllable (en dash)'),
               ('⏓', '⌥0', 'anceps 可長可短', 'anceps')])
CRITICAL = check([('⟨', '⇧,', '單角括號（左）', 'angle bracket, left'),
                  ('⟩', '⇧.', '單角括號（右）', 'angle bracket, right'),
                  ('⟪', '⌥⇧,', '雙角括號（左）', 'double angle bracket, left'),
                  ('⟫', '⌥⇧.', '雙角括號（右）', 'double angle bracket, right'),
                  ('{', '⇧[', '花括號（左）', 'curly bracket, left'),
                  ('}', '⇧]', '花括號（右）', 'curly bracket, right'),
                  ('°', '⌥7', '省略符，如 °rakṣita、sva°（亦可 ⌥⇧5）', 'abbreviation sign, e.g. °rakṣita, sva° (also ⌥⇧5)'),
                  ('§', '⌥5', '節號', 'section sign'), ('•', '⌥8', '圓點', 'bullet'),
                  ('◊', '⌥⇧8', '菱形', 'lozenge'), ('·', '⌥⇧9', '中點', 'middle dot'),
                  ('…', '⌥;', '刪節號', 'ellipsis'), ('—', '⌥⇧-', 'em dash', 'em dash'),
                  ('‡', '⌥⇧7', '雙劍號', 'double dagger'),
                  ('¨', '⌥⇧Q', '獨立兩點（不附著）', 'spacing diaeresis (does not attach)')])
PUNCT = check([('<', '⌥,', '', ''), ('>', '⌥.', '', ''),
               ('“', '⌥[', '', ''), ('”', '⌥⇧[', '', ''), ('‘', '⌥]', '', ''), ('’', '⌥⇧]', '', ''),
               ('«', '⌥\\', '', ''), ('»', '⌥⇧\\', '', ''), ('‹', '⌥⇧3', '', ''), ('›', '⌥⇧4', '', ''),
               ('≠', '⌥=', '', ''), ('÷', '⌥/', '', '')])
# (中文名, English name, prefix dead key or None, append key, note, examples)
MARKS = [('尖音符', 'acute', '⌥E', '⌥⇧E', '', [('á', '⌥E a'), ('ā́', '⌥A ⌥⇧E')]),
         ('抑音符', 'grave', '⌥`', '⌥⇧`', '', [('à', '⌥` a'), ('ā̀', '⌥A ⌥⇧`')]),
         ('揚抑符', 'circumflex', '⌥6', '⌥⇧6', '', [('â', '⌥6 a'), ('ā̂', '⌥A ⌥⇧6')]),
         ('長音符', 'macron', None, '⌥4', '⌥⇧=', [('ē', 'e ⌥4'), ('ṝ', '⌥R ⌥4')]),
         ('兩點', 'diaeresis', None, '⌥Q', '', [('ä', 'a ⌥Q'), ('ü', 'u ⌥Q')]),
         ('短音符', 'breve', '⌥B', '⌥⇧B', '', [('ă', '⌥B a'), ('ŏ', 'o ⌥⇧B')]),
         ('抑揚符', 'caron', '⌥V', '⌥⇧V', '', [('č', '⌥V c'), ('ǎ', 'a ⌥⇧V')]),
         ('下加符', 'cedilla', '⌥C', '⌥⇧C', '', [('ç', '⌥C c')]),
         ('上圓圈', 'ring above', '⌥K', '⌥⇧K', '', [('å', '⌥K a')]),
         ('下點', 'dot below', '⌥X', '⌥⇧X', '', [('ṇ', '⌥X n'), ('ẹ', 'e ⌥⇧X')]),
         ('下逗號', 'comma below', '⌥P', '⌥⇧P', '', [('ș', '⌥P s')])]
for _, _, prefix, append, alt, examples in MARKS:
    check(examples)
    if prefix:
        assert press(*parse(prefix))[1] != 'none', prefix
    for key in filter(None, [append, alt]):
        assert all(unicodedata.combining(c) for c in type_keys(key)), key
# ⌥E then ⌥A: Option can stay held down through both keys.
ACUTE_LONG = check([('ā́', '⌥E ⌥A')])
STACKED = check([('r̥̄́', '⌥Y ⌥4 ⌥⇧E'), ('ā́', '⌥E ⌥A'), ('Ā́', '⌥⇧A ⌥⇧E')])


def mark_rows():
    rows = []
    for zh, en, prefix, append, alt, examples in MARKS:
        ex = '；'.join(label(k) + ' = ' + t for t, k in examples)
        key = label(append) + ('（或 ' + label(alt) + '）' if alt else '')
        rows.append([en + ' ' + zh, label(prefix) if prefix else '—', key, ex])
    return rows


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
{table(['輸出', '按鍵', '方式'], [[t, label(k), m] for t, k, m, _ in LONG])}

元音短音（breve）：
{table(['輸出', '按鍵', '方式'], [[t, label(k), m] for t, k, m, _ in SHORT])}

格律符號：
{table(['符號', '按鍵', '說明'], [[t, label(k), m] for t, k, m, _ in METRE])}


三、校勘符號

{table(['符號', '按鍵', '說明'], [[t, label(k), m] for t, k, m, _ in CRITICAL])}

其他標點：
{table(['符號', '按鍵'], [[t, label(k)] for t, k, _, _ in PUNCT])}


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
• ⇧逗號／⇧句號 輸出 ⟨ ⟩；需要 < > 時按 ⌥逗號／⌥句號（2.3 起，原來的 ≤ ≥ 已移除）。


四、版本變更

2.3 相對 2.1：
⌥逗號／⌥句號：≤／≥ → < ／ >（Caps Lock 開啟時相同）
（2.2 原本要做同一改動，但 < > 的寫法 macOS 不接受，打不出來；請改用 2.3。）

2.1 相對 2.0：
⌥1／⌥⇧1：¡／⁄ → ḫ／Ḫ（ḫ 由 Q 移來）
⌥2／⌥⇧2：™／€ → ẖ／H̱
⌥4：¢ → 追加長音符 U+0304（⌥⇧4 的 › 保留）
⌥Q：ḫ → 追加兩點 U+0308
⌥⇧Q：Ḫ → 獨立兩點 ¨ U+00A8
'''

# ---------------------------------------------------------------- README tables


def md_key(token):
    return '`` ' + token + ' ``' if '`' in token else '`' + token + '`'


def md_keys(keys):
    return ' → '.join(md_key(t) for t in keys.split())


def md_table(header, rows):
    return '\n'.join(['| ' + ' | '.join(header) + ' |', '|' + '---|' * len(header)] +
                     ['| ' + ' | '.join(r) + ' |' for r in rows])


def readme_block(zh):
    T = (lambda z, e: z) if zh else (lambda z, e: e)
    def notes(rows, with_code=False):
        return [[t, md_keys(k), (z if zh else e)] + ([codepoints(t)] if with_code else []) for t, k, z, e in rows]
    marks = []
    for z, e, prefix, append, alt, examples in MARKS:
        name = (z + '（' + e + '）') if zh else e
        key = md_keys(append) + ((' 或 ' if zh else ' or ') + md_keys(alt) if alt else '')
        marks.append([name, md_keys(prefix) if prefix else '—', key,
                      '<br>'.join(md_keys(k) + ' = ' + t for t, k in examples)])
    return '\n'.join([
        T('### IAST 符號', '### IAST letters'), '',
        T('按住 `⌥` 輸入小寫，`⌥ ⇧` 輸入大寫。', 'Hold `⌥` for lowercase, `⌥ ⇧` for uppercase.'), '',
        md_table(T(['小寫', '按鍵', '大寫', '按鍵', 'Unicode'], ['Lower', 'Keys', 'Upper', 'Keys', 'Unicode']),
                 [[l, md_key('⌥' + k), type_keys('⌥⇧' + k), md_key('⌥⇧' + k),
                   codepoints(l) + ' / ' + codepoints(type_keys('⌥⇧' + k))] for l, k in LETTERS]), '',
        T('### 長短音', '### Vowel length and metre'), '',
        T('**長音**：ā ī ū 可直接輸入；其他字母先打字母，再按 `⌥4` 追加長音符。',
          '**Long vowels**: ā ī ū have their own keys; for any other letter, type it first, then `⌥4` to add a macron.'), '',
        md_table(T(['輸出', '按鍵', '方式'], ['Output', 'Keys', 'Method']), notes(LONG)), '',
        T('**短音**（breve）：', '**Short vowels** (breve):'), '',
        md_table(T(['輸出', '按鍵', '方式'], ['Output', 'Keys', 'Method']), notes(SHORT)), '',
        T('**格律符號**：', '**Metrical signs**:'), '',
        md_table(T(['符號', '按鍵', '說明', 'Unicode'], ['Sign', 'Keys', 'Meaning', 'Unicode']), notes(METRE, True)), '',
        T('### 校勘符號', '### Text-critical signs'), '',
        md_table(T(['符號', '按鍵', '說明', 'Unicode'], ['Sign', 'Keys', 'Use', 'Unicode']), notes(CRITICAL, True)), '',
        T('<details>\n<summary>其他標點</summary>\n', '<details>\n<summary>Other punctuation</summary>\n'),
        md_table(T(['符號', '按鍵', 'Unicode'], ['Sign', 'Keys', 'Unicode']),
                 [[t.replace('<', '&lt;').replace('>', '&gt;'), md_keys(k), codepoints(t)] for t, k, _, _ in PUNCT]),
        '\n</details>', '',
        T('### 組合鍵輸入', '### Combining input'), '',
        T('**前置**（死鍵）：先按組合鍵，再打字母。**追加**：先打字母，再按組合鍵，中間不按空格。',
          '**Dead key**: press it first, then the letter. **Append**: type the letter first, then the key, with no space in between.'), '',
        md_table(T(['附加符號', '前置', '追加', '例子'], ['Mark', 'Dead key', 'Append', 'Examples']), marks), '',
        T('可以疊加：', 'Marks stack:') + ' ' + ('；' if zh else '; ').join(md_keys(k) + ' = ' + t for t, k in STACKED), '',
        T('**快速打出 ā́**：' + md_keys(ACUTE_LONG[0][1]) + '。可以一直按住 Option，依次按 E、A，不必中途放開。',
          '**Typing ā́ quickly**: ' + md_keys(ACUTE_LONG[0][1]) + '. You can keep holding Option and press E, then A.'),
    ])


def fill(path, block):
    text = path.read_text(encoding='utf-8')
    begin, end = '<!-- BEGIN GENERATED KEYMAP -->', '<!-- END GENERATED KEYMAP -->'
    head, rest = text.split(begin)
    _, tail = rest.split(end)
    path.write_text(head + begin + '\n' + block + '\n' + end + tail, encoding='utf-8')


# ---------------------------------------------------------------- keyboard SVGs

SVG_ROWS = [[('`', 1)] + [(k, 1) for k in '1234567890-='] + [('⌫', 1.5)],
            [('⇥', 1.5)] + [(k, 1) for k in 'QWERTYUIOP[]'] + [('\\', 1)],
            [('⇪', 1.75)] + [(k, 1) for k in "ASDFGHJKL;'"] + [('↩', 1.75)],
            [('⇧', 2.25)] + [(k, 1) for k in 'ZXCVBNM,./'] + [('⇧', 2.25)]]
SVG_COLORS = {'letter': '#f3dcb0', 'mark': '#cfe0f5', 'sign': '#e3e9d8', 'plain': '#f7f7f5'}


def svg_key(mods, key):
    text, state = press(mods, CODES[key])
    if state != 'none' and not text:
        return terminators[state], 'mark', True
    if text and all(unicodedata.combining(c) for c in text):
        return '◌' + text, 'mark', False
    if any(unicodedata.category(c).startswith('L') for c in text):
        return text, 'letter', False
    return text, 'sign', False


def keyboard_svg(mods, title):
    unit, gap, pad = 54, 4, 12
    width = int(15 * unit + 2 * pad)
    height = int(4 * unit + 2 * pad + 58)
    esc = lambda t: t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
           'font-family="-apple-system, Helvetica Neue, Arial, sans-serif">',
           f'<rect width="{width}" height="{height}" rx="14" fill="#ffffff"/>',
           f'<text x="{pad + 4}" y="{pad + 18}" font-size="17" font-weight="600" fill="#222">{esc(title)}</text>']
    y = pad + 30
    for row in SVG_ROWS:
        x = pad
        for key, size in row:
            w, h = size * unit - gap, unit - gap
            if key in CODES:
                text, kind, dead = svg_key(mods, key)
                dash = ' stroke-dasharray="4 3"' if dead else ''
                out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{SVG_COLORS[kind]}" stroke="#9a9a96"{dash}/>')
                out.append(f'<text x="{x + 6}" y="{y + 14}" font-size="11" fill="#777">{esc(key)}</text>')
                out.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 12}" font-size="22" text-anchor="middle" fill="#111">{esc(text)}</text>')
            else:
                out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#e6e6e3" stroke="#b5b5b0"/>')
                out.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 6}" font-size="15" text-anchor="middle" fill="#999">{esc(key)}</text>')
            x += size * unit
        y += unit
    legend = [('letter', 'IAST / letters'), ('mark', 'combining (dashed = dead key)'), ('sign', 'symbols')]
    x = pad + 4
    for kind, name in legend:
        out.append(f'<rect x="{x}" y="{y + 10}" width="16" height="16" rx="3" fill="{SVG_COLORS[kind]}" stroke="#9a9a96"/>')
        out.append(f'<text x="{x + 22}" y="{y + 23}" font-size="13" fill="#444">{esc(name)}</text>')
        x += 26 + 8 * len(name) + 24
    out.append('</svg>')
    return '\n'.join(out) + '\n'


ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
(ASSETS / 'keyboard-option.svg').write_text(keyboard_svg('option', '⌥ Option'), encoding='utf-8')
(ASSETS / 'keyboard-option-shift.svg').write_text(keyboard_svg('shift option', '⌥ Option + ⇧ Shift'), encoding='utf-8')

DOCS.mkdir(exist_ok=True)
(DOCS / '符號速查.txt').write_text(quick, encoding='utf-8')
(DOCS / '輸出對照.txt').write_text(full, encoding='utf-8')
fill(ROOT / 'README.md', readme_block(zh=False))
fill(ROOT / 'README.zh-Hant.md', readme_block(zh=True))
print('Generated docs/符號速查.txt, docs/輸出對照.txt and README keymaps from', OUTPUT.name)
