# ABC Extended – IAST

**English** · [中文](README.zh-Hant.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
![Version 2.3](https://img.shields.io/badge/version-2.3-cf9a4c)
![macOS](https://img.shields.io/badge/platform-macOS-lightgrey)

A macOS keyboard layout for typing **IAST** ([International Alphabet of Sanskrit
Transliteration](https://en.wikipedia.org/wiki/International_Alphabet_of_Sanskrit_Transliteration)),
vowel length, metrical signs and text-critical signs with `⌥ Option`. It is built on Apple's
**ABC Extended**: everything you don't hold `⌥` for types exactly as before.

## Features

- Every IAST letter with one chord: `⌥` for lowercase, `⌥ ⇧` for uppercase,
  including ṛ, r̥, ḷ, ṃ, ṁ, m̐, ḥ, ḫ and ẖ
- Add a macron or diaeresis **after** any letter (`e` → `⌥4` = ē, `⌥R` → `⌥4` = ṝ, `a` → `⌥Q` = ä),
  and stack accents (`⌥Y` → `⌥4` → `⌥⇧E` = r̥̄́)
- Metrical signs ⏑ – ⏓ and text-critical signs ⟨ ⟩ ⟪ ⟫ ° § ◊ on their own keys
- Packaged as a bundle tagged **English**, so Word treats what you type as English text
  (see [Microsoft Word](#microsoft-word))
- macOS **press and hold** still works: hold a letter such as `a` or `e` and pick an accented form
  from the popup, alongside the `⌥` chords. The popup's choices come from macOS's English set
- Nothing runs in the background: no app, no input method, no admin rights

## Quick examples

Accents combine with letters in one or two strokes:

<!-- BEGIN GENERATED EXAMPLES -->
- Type ā́: `⌥E` → `⌥A`. You can keep holding Option and press E, then A.
- Type ŕ̥: `⌥E` → `⌥Y`. You can keep holding Option and press E, then Y.
- Type ó: `⌥E` → `o`. Press `⌥E`, release, then press `o`.
- Type ô: `⌥6` → `o`. Press `⌥6`, release, then press `o`.
<!-- END GENERATED EXAMPLES -->

## Preview

| ⌥ Option | ⌥ Option + ⇧ Shift |
|---|---|
| <img src="assets/keyboard-option.svg" alt="Keyboard map of the Option layer"> | <img src="assets/keyboard-option-shift.svg" alt="Keyboard map of the Option+Shift layer"> |

Gold keys type letters, blue keys add combining marks (dashed: a dead key, press it before the letter),
green keys type symbols. The two images are drawn from the layout file itself.

## Installation

### 1. Download

Click **Code → Download ZIP** on this page and unzip it, or use git:

```sh
git clone https://github.com/zyr-97/MacOS-ABC-Extended-IAST.git
```

### 2. Install

Copy the whole **`ABC-Extended-IAST-2.3.bundle`** folder into `~/Library/Keyboard Layouts/`.
In Finder press `⇧⌘G` and paste that path; create the `Keyboard Layouts` folder if it doesn't exist.
From the terminal:

```sh
mkdir -p ~/Library/Keyboard\ Layouts
cp -R ./MacOS-ABC-Extended-IAST/ABC-Extended-IAST-2.3.bundle ~/Library/Keyboard\ Layouts/
```

Copy the bundle, not just the `.keylayout` inside it: the bundle carries the English
language tag. Then **log out and back in** (or restart).

### 3. Enable it

- **macOS 13 and later:** System Settings → Keyboard → Text Input → Input Sources **Edit…** → **+**
- **macOS 12 and earlier:** System Preferences → Keyboard → Input Sources → **+**

Choose **ABC Extended - IAST 2.3** under *English* or *Others*, or type **IAST** in the search field
to find it, then switch to it from the input menu in the menu bar.

> [!IMPORTANT]
> **Log out and log back in after installing.** macOS only loads new keyboard layouts when you sign in.
> Until you do, the layout may be missing from the list, or an older copy may keep running and keys
> such as `⌥,` won't type what this guide says. Do the same after every update or removal.
> If it still doesn't appear, restart your Mac.

**Upgrading from an older version:** each version is a separate input source, so 2.3 can sit next to 2.1.
Add 2.3, check that it works, then remove the old one. If you installed 2.2, remove it:
its `⌥,` / `⌥.` don't type `<` / `>`.

## Key reference

`⌥` = Option, `⇧` = Shift, held together. `→` means release, then press the next chord.
A lowercase letter such as `e` means that key alone. Positions follow US QWERTY.
Turn **Caps Lock off** for the IAST letter keys.

<!-- BEGIN GENERATED KEYMAP -->
### IAST letters

Hold `⌥` for lowercase, `⌥ ⇧` for uppercase.

| Lower | Keys | Upper | Keys | Unicode |
|---|---|---|---|---|
| ā | `⌥A` | Ā | `⌥⇧A` | U+0101 / U+0100 |
| ī | `⌥I` | Ī | `⌥⇧I` | U+012B / U+012A |
| ū | `⌥U` | Ū | `⌥⇧U` | U+016B / U+016A |
| ṛ | `⌥R` | Ṛ | `⌥⇧R` | U+1E5B / U+1E5A |
| r̥ | `⌥Y` | R̥ | `⌥⇧Y` | U+0072 U+0325 / U+0052 U+0325 |
| ḷ | `⌥L` | Ḷ | `⌥⇧L` | U+1E37 / U+1E36 |
| ṃ | `⌥M` | Ṃ | `⌥⇧M` | U+1E43 / U+1E42 |
| ṁ | `⌥W` | Ṁ | `⌥⇧W` | U+1E41 / U+1E40 |
| m̐ | `⌥F` | M̐ | `⌥⇧F` | U+006D U+0310 / U+004D U+0310 |
| ḥ | `⌥H` | Ḥ | `⌥⇧H` | U+1E25 / U+1E24 |
| ḫ | `⌥1` | Ḫ | `⌥⇧1` | U+1E2B / U+1E2A |
| ẖ | `⌥2` | H̱ | `⌥⇧2` | U+1E96 / U+0048 U+0331 |
| ṭ | `⌥T` | Ṭ | `⌥⇧T` | U+1E6D / U+1E6C |
| ḍ | `⌥D` | Ḍ | `⌥⇧D` | U+1E0D / U+1E0C |
| ṇ | `⌥N` | Ṇ | `⌥⇧N` | U+1E47 / U+1E46 |
| ṅ | `⌥G` | Ṅ | `⌥⇧G` | U+1E45 / U+1E44 |
| ñ | `⌥J` | Ñ | `⌥⇧J` | U+00F1 / U+00D1 |
| ś | `⌥Z` | Ś | `⌥⇧Z` | U+015B / U+015A |
| ṣ | `⌥S` | Ṣ | `⌥⇧S` | U+1E63 / U+1E62 |

### Vowel length and metre

**Long vowels**: ā ī ū have their own keys; for any other letter, type it first, then `⌥4` to add a macron.

| Output | Keys | Method |
|---|---|---|
| ā | `⌥A` | direct |
| ī | `⌥I` | direct |
| ū | `⌥U` | direct |
| ē | `e` → `⌥4` | append |
| ō | `o` → `⌥4` | append |
| ṝ | `⌥R` → `⌥4` | append |
| ḹ | `⌥L` → `⌥4` | append |
| r̥̄ | `⌥Y` → `⌥4` | append |
| Ē | `⇧E` → `⌥4` | append |
| ā | `a` → `⌥⇧=` | legacy key |

**Short vowels** (breve):

| Output | Keys | Method |
|---|---|---|
| ă | `⌥B` → `a` | dead key |
| ĭ | `⌥B` → `i` | dead key |
| ŭ | `⌥B` → `u` | dead key |
| ĕ | `e` → `⌥⇧B` | append |
| ŏ | `o` → `⌥⇧B` | append |

**Metrical signs**:

| Sign | Keys | Meaning | Unicode |
|---|---|---|---|
| ⏑ | `⌥9` | laghu, light syllable | U+23D1 |
| – | `⌥-` | guru, heavy syllable (en dash) | U+2013 |
| ⏓ | `⌥0` | anceps | U+23D3 |

### Text-critical signs

| Sign | Keys | Use | Unicode |
|---|---|---|---|
| ⟨ | `⇧,` | angle bracket, left | U+27E8 |
| ⟩ | `⇧.` | angle bracket, right | U+27E9 |
| ⟪ | `⌥⇧,` | double angle bracket, left | U+27EA |
| ⟫ | `⌥⇧.` | double angle bracket, right | U+27EB |
| { | `⇧[` | curly bracket, left | U+007B |
| } | `⇧]` | curly bracket, right | U+007D |
| ° | `⌥7` | abbreviation sign, e.g. °rakṣita, sva° (also ⌥⇧5) | U+00B0 |
| § | `⌥5` | section sign | U+00A7 |
| • | `⌥8` | bullet | U+2022 |
| ◊ | `⌥⇧8` | lozenge | U+25CA |
| · | `⌥⇧9` | middle dot | U+00B7 |
| … | `⌥;` | ellipsis | U+2026 |
| — | `⌥⇧-` | em dash | U+2014 |
| ‡ | `⌥⇧7` | double dagger | U+2021 |
| ¨ | `⌥⇧Q` | spacing diaeresis (does not attach) | U+00A8 |

<details>
<summary>Other punctuation</summary>

| Sign | Keys | Unicode |
|---|---|---|
| &lt; | `⌥,` | U+003C |
| &gt; | `⌥.` | U+003E |
| “ | `⌥[` | U+201C |
| ” | `⌥⇧[` | U+201D |
| ‘ | `⌥]` | U+2018 |
| ’ | `⌥⇧]` | U+2019 |
| « | `⌥\` | U+00AB |
| » | `⌥⇧\` | U+00BB |
| ‹ | `⌥⇧3` | U+2039 |
| › | `⌥⇧4` | U+203A |
| ≠ | `⌥=` | U+2260 |
| ÷ | `⌥/` | U+00F7 |

</details>

### Combining input

**Dead key**: press it first, then the letter. **Append**: type the letter first, then the key, with no space in between.

| Mark | Dead key | Append | Examples |
|---|---|---|---|
| acute | `⌥E` | `⌥⇧E` | `⌥E` → `a` = á<br>`⌥A` → `⌥⇧E` = ā́ |
| grave | `` ⌥` `` | `` ⌥⇧` `` | `` ⌥` `` → `a` = à<br>`⌥A` → `` ⌥⇧` `` = ā̀ |
| circumflex | `⌥6` | `⌥⇧6` | `⌥6` → `a` = â<br>`⌥A` → `⌥⇧6` = ā̂ |
| macron | — | `⌥4` or `⌥⇧=` | `e` → `⌥4` = ē<br>`⌥R` → `⌥4` = ṝ |
| diaeresis | — | `⌥Q` | `a` → `⌥Q` = ä<br>`u` → `⌥Q` = ü |
| breve | `⌥B` | `⌥⇧B` | `⌥B` → `a` = ă<br>`o` → `⌥⇧B` = ŏ |
| caron | `⌥V` | `⌥⇧V` | `⌥V` → `c` = č<br>`a` → `⌥⇧V` = ǎ |
| cedilla | `⌥C` | `⌥⇧C` | `⌥C` → `c` = ç |
| ring above | `⌥K` | `⌥⇧K` | `⌥K` → `a` = å |
| dot below | `⌥X` | `⌥⇧X` | `⌥X` → `n` = ṇ<br>`e` → `⌥⇧X` = ẹ |
| comma below | `⌥P` | `⌥⇧P` | `⌥P` → `s` = ș |

Marks stack: `⌥Y` → `⌥4` → `⌥⇧E` = r̥̄́; `⌥E` → `⌥A` = ā́; `⌥⇧A` → `⌥⇧E` = Ā́

**Typing ā́ quickly**: `⌥E` → `⌥A`. You can keep holding Option and press E, then A.
<!-- END GENERATED KEYMAP -->

Every key on the keyboard, in all four layers and with exact code points:
[`docs/輸出對照.txt`](docs/輸出對照.txt). A one-page cheat sheet: [`docs/符號速查.txt`](docs/符號速查.txt).

## Microsoft Word

The layout ships as a `.bundle` rather than a bare `.keylayout` because the bundle's
`Info.plist` declares the input source's language as English (`TISIntendedLanguage = en`).
macOS then reports the input source as English, and Word can use that when it tags new text,
so IAST typed with this layout stays English instead of switching proofing language and font
when you change input source.

The tag is a hint, not a lock. It does not choose a font or change text you already have:

- **Proofing language:** select the text → Tools → Language → English → OK.
  Click **Default…** in the same dialog to use it for new documents.
- **Font:** Format → Font (`⌘D`). If the dialog shows separate Latin and Asian fonts, set the Latin one.
- **Boxes or misplaced accents** on m̐, r̥̄́, ⏑, ⏓ or ⟨ ⟩ come from the font: switch to a font that
  covers these characters. The language setting can't fix missing glyphs.

## Good to know

> [!IMPORTANT]
> **Shortcut conflicts:** if pressing `⌥S` starts a screenshot, search or translation tool instead of
> typing ṣ, another app (a dictionary, for example) has taken that global shortcut. Open that app's
> settings, turn the shortcut off or assign it to different keys, then go back to Word or wherever you
> were typing. Do the same for any other `⌥` chord that behaves this way.

- With **Caps Lock on**, `⌥` + an IAST letter key falls back to ABC Extended (for example `⌥R` gives ®).
  Number keys, `Q` and all signs work either way.
- `⇧,` `⇧.` type ⟨ ⟩; `⌥,` `⌥.` type `<` `>` (since 2.3).
- `Command` and `Control` shortcuts are untouched.
- `⌥A` types a precomposed ā (U+0101), while `a` → `⌥4` types a + U+0304. Unicode treats them as
  equivalent, but some search tools don't. The layout doesn't normalize your document.
- Don't press `⌥4` after ā: you would get a second macron.

## Uninstall

Switch to another input source, remove *ABC Extended - IAST 2.3* in keyboard settings, delete
`~/Library/Keyboard Layouts/ABC-Extended-IAST-2.3.bundle`, then log out and back in.

## Building from source

You don't need this to install. With Python 3.8+ (standard library only, no network access):

```sh
python3 tools/build_and_verify.py     # rebuild the bundle from source/, write verification.json
python3 tools/generate_reference.py   # regenerate docs/, assets/ and the README key tables
```

The build changes the base layout only on the intended keys. It then checks every key, modifier
combination and dead-key state against the original and against the previous release (2.1), and types
about 400 test sequences. Every example in the docs and the tables above is typed through the layout
before it is written. These checks run on the layout file; they don't replace testing on a Mac.

| Path | Contents |
|---|---|
| `ABC-Extended-IAST-2.3.bundle/` | the layout to install |
| `docs/` | Chinese guides: installation (`安裝說明`), full output table (`輸出對照`), cheat sheet (`符號速查`) |
| `source/` | the base layout and the 2.1 release, used for the build and the delta check |
| `tools/` | build, verification and documentation scripts |
| `verification.json` | the last build's check results |

## Changelog

- **2.3** — `⌥,` / `⌥.` type `<` / `>` (previously ≤ / ≥).
- **2.2** — first attempt at `<` / `>`; they were written in a form macOS doesn't accept and didn't type. Use 2.3.
- **2.1** — `⌥1` / `⌥2` give ḫ / ẖ; `⌥4` appends a macron, `⌥Q` a diaeresis; `⌥⇧Q` is a spacing ¨.
- **2.0** — m̐, ḫ, metrical signs ⏑ ⏓, abbreviation sign °.
- **1.4** — single and double angle brackets, lozenge, accented long vowels.

## License

[MIT](LICENSE). The layout is derived from Apple's ABC Extended layout. This project isn't affiliated with
Apple, and the license covers only this project's changes, documentation and tools; see [LICENSE](LICENSE).
