"""Cross-script helpers for Hinglish search (§6.12).

* romanize(): Devanagari -> loose Latin (ITRANS-like, inherent 'a' kept, anusvara -> '~').
  Used when the optional `indic_transliteration` package is absent.
* phonkey(): the phonetic key stored in chunks_fts.text_rom and applied to queries.
  Rules (§6.12): lowercase; aa->a, ee/ii->i, oo/uu->u; drop word-final schwa; w->v, z->j,
  sh->s, ph->f; collapse doubled letters; remove nasal marks / n before a consonant.
  [impl] plus Hindi medial schwa syncope (VC a CV -> VCCV) so 'milate' (from मिलते) == 'milte'.
* LatinToDeva: Devanagari shadow for Latin-script Hindi tokens (chunks_fts.text_deva). The real
  engine is pm-xlit (IndicXlit, §6.11); the built-in fallback is a small lexicon (stub).
"""
from __future__ import annotations

import re
import unicodedata

_CONS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n", "च": "ch", "छ": "chh", "ज": "j", "झ": "jh",
    "ञ": "n", "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n", "त": "t", "थ": "th", "द": "d",
    "ध": "dh", "न": "n", "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m", "य": "y", "र": "r",
    "ल": "l", "व": "v", "श": "sh", "ष": "sh", "स": "s", "ह": "h", "ळ": "l",
    "क़": "q", "ख़": "kh", "ग़": "g", "ज़": "z", "ड़": "r", "ढ़": "rh", "फ़": "f",
}
_VOW = {"अ": "a", "आ": "aa", "इ": "i", "ई": "ii", "उ": "u", "ऊ": "uu", "ऋ": "ri", "ए": "e", "ऐ": "ai",
        "ओ": "o", "औ": "au", "ऑ": "o"}
_MATRA = {"ा": "aa", "ि": "i", "ी": "ii", "ु": "u", "ू": "uu", "ृ": "ri", "े": "e", "ै": "ai", "ो": "o",
          "ौ": "au", "ॉ": "o"}
_VIRAMA = "्"
_NASAL = {"ं": "n", "ँ": "n"}  # anusvara/chandrabindu
_NUKTA = "़"
_DIGITS = {chr(0x0966 + i): str(i) for i in range(10)}

_DEVA_RE = re.compile(r"[\u0900-\u097F]")


def has_devanagari(s: str) -> bool:
    return bool(_DEVA_RE.search(s))


def romanize(text: str) -> str:
    try:  # optional, better quality
        from indic_transliteration import sanscript  # type: ignore[import-not-found]
        from indic_transliteration.sanscript import transliterate  # type: ignore[import-not-found]
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS).lower()
    except ImportError:
        pass
    text = unicodedata.normalize("NFC", text)
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if ch in _CONS or (ch + nxt) in _CONS:
            if (ch + nxt) in _CONS and nxt == _NUKTA:
                base = _CONS[ch + nxt]
                i += 1
                nxt = text[i + 1] if i + 1 < n else ""
            else:
                base = _CONS[ch]
            out.append(base)
            if nxt == _VIRAMA:
                i += 2
                continue
            if nxt in _MATRA:
                out.append(_MATRA[nxt])
                i += 2
                continue
            out.append("a")
            i += 1
            continue
        if ch in _VOW:
            out.append(_VOW[ch])
        elif ch in _MATRA:
            out.append(_MATRA[ch])
        elif ch in _NASAL:
            out.append(_NASAL[ch])
        elif ch in _DIGITS:
            out.append(_DIGITS[ch])
        elif ch in (_NUKTA, _VIRAMA):
            pass
        elif ch in "।॥":
            out.append(".")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


_VOWELS = set("aeiou")


def _key_word(w: str) -> str:
    w = w.lower()
    w = (w.replace("aa", "a").replace("ee", "i").replace("ii", "i").replace("oo", "u").replace("uu", "u"))
    w = w.replace("sh", "s").replace("ph", "f").replace("w", "v").replace("z", "j")
    # nasal marks and n/m before a consonant
    w = w.replace("~", "n")   # anusvara/chandrabindu ~ n (हैं -> hain)
    w = re.sub(r"n(?=[bcdfghjklmpqrstvxy])", "", w)
    # word-final schwa after a consonant (kala -> kal); keep 1-2 letter words ('na', 'ka')
    if len(w) > 2 and w.endswith("a") and w[-2] not in _VOWELS:
        w = w[:-1]
    # medial schwa syncope: V C a C V -> V C C V
    w = re.sub(r"(?<=[aeiou][^aeiou\W\d])a(?=[^aeiou\W\d][aeiou])", "", w)
    # collapse doubled letters
    w = re.sub(r"(.)\1+", r"\1", w)
    return w


WORD_RE = re.compile(r"(?:[^\W_]|[\u0900-\u0963\u0966-\u097F])+")  # words incl. Devanagari vowel signs
_WORD = WORD_RE


def phonkey(text: str) -> str:
    """Phonetic key of `text` (any script). Returns space-separated keys."""
    if has_devanagari(text):
        text = romanize(text)
    return " ".join(k for k in (_key_word(w) for w in _WORD.findall(text)) if k)


# --- Latin Hindi -> Devanagari shadow -------------------------------------------------
_LEXICON = {
    "kal": "कल", "aaj": "आज", "aj": "आज", "parso": "परसों", "subah": "सुबह", "subha": "सुबह",
    "shaam": "शाम", "sham": "शाम", "raat": "रात", "baje": "बजे", "milte": "मिलते", "milenge": "मिलेंगे",
    "hai": "है", "hain": "हैं", "dawai": "दवाई", "dawa": "दवा", "doctor": "डॉक्टर", "ghar": "घर",
    "paise": "पैसे", "kitab": "किताब", "yaad": "याद", "mummy": "मम्मी", "papa": "पापा", "kaam": "काम",
}


class LatinToDeva:
    """Fallback xlit: lexicon lookup for Latin tokens. Replace with pm-xlit (IndicXlit) on device."""

    def __init__(self, lexicon: dict[str, str] | None = None) -> None:
        self.lexicon = dict(_LEXICON if lexicon is None else lexicon)

    def __call__(self, text: str) -> str:
        out = []
        for w in _WORD.findall(text.lower()):
            if has_devanagari(w):
                continue
            d = self.lexicon.get(w)
            if d:
                out.append(d)
        return " ".join(out)
