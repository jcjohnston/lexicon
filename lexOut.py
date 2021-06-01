# lexOut.py jcj 2020-05-11, 2020-05-27, 2020-05-31

'''Format lexicon data for output'''

## Support for gettext
# This file assumes that _ and pgettext have been injected
# into the builtins namespace by the '__main__' file.
# Python doesn't support pgettext until version 3.8. Meanwhile...
try:
    pgettext
except NameError:
    from my.pgettext import pgettext
__ = pgettext

import sys
from textwrap import wrap
from my.textutils import fmt

__all__ = ['languageNames', 'languageName', 'languageCode', 'languageWidth',
           'headsDisplay', 'defsDisplay', 'nymsDisplay', 'wordsDisplay',
           'busyPhase', 'busyWait']

LG_CODE_TO_NAME = {
    # See https://en.wikipedia.org/wiki/ISO_639-3
    # See http://compling.hss.ntu.edu.sg/omw/ for qcn
    'als':  __('Name of language', 'Tosk Albanian'),
    'arb':  __('Name of language', 'Standard Arabic'),
    'bul':  __('Name of language', 'Bulgarian'),
    'cat':  __('Name of language', 'Catalan'),
    'cmn':  __('Name of language', 'Mandarin Chinese'),
    'dan':  __('Name of language', 'Danish'),
    'ell':  __('Name of language', 'Modern Greek'),
    'eng':  __('Name of language', 'English'),
    'eus':  __('Name of language', 'Basque'),
    'fas':  __('Name of language', 'Persian'),
    'fin':  __('Name of language', 'Finnish'),
    'fra':  __('Name of language', 'French'),
    'glg':  __('Name of language', 'Galician'),
    'heb':  __('Name of language', 'Hebrew'),
    'hrv':  __('Name of language', 'Croatian'),
    'ind':  __('Name of language', 'Indonesian'),
    'ita':  __('Name of language', 'Italian'),
    'jpn':  __('Name of language', 'Japanese'),
    'nld':  __('Name of language', 'Dutch'),
    'nno':  __('Name of language', 'Norwegian Nynorsk'),
    'nob':  __('Name of language', 'Norwegian Bokmål'),
    'pol':  __('Name of language', 'Polish'),
    'por':  __('Name of language', 'Portuguese'),
    'qcn':  __('Name of language', 'Taiwan Chinese'),    # No official name
    'slv':  __('Name of language', 'Slovenian'),
    'spa':  __('Name of language', 'Spanish'),
    'swe':  __('Name of language', 'Swedish'),
    'tha':  __('Name of language', 'Thai'),
    'zsm':  __('Name of language', 'Standard Malay')
}
LG_NAME_TO_CODE = { val: key for key, val in LG_CODE_TO_NAME.items()}

TAB = ' ' * 4     # avoid literal 4 spaces in case a tabifier alters them

HTML_ESCAPES = {
    '<': '&lt;',    '>': '&gt;',
    '&': '&amp;',   '"': '&dquot;'
    }

PHASE_STRINGS = __('Progress loading lexicon (5 phases separated by ;)', 
    'Reading...;Normalizing...;Sorting...;Hashing...;Done.').split(';')

prevPhase = None

def escaped(s):
    '''Return a version of s with HTML-meaningful characters escaped'''
    return ''.join(HTML_ESCAPES.get(c, c) for c in s)
    
def WNDisplayText(wnis, indent=0, maxWidth=70):
    '''Return a list of lines containing wrapped and formatted info in wni'''

    def wrapped(ind, s, hanging=False):
        '''Deal with the indentation and wrapping'''
        initialIndent = TAB * ind
        subsequentIndent = (initialIndent + '  ') if hanging else initialIndent
        return wrap(s,
                    initial_indent=initialIndent,
                    subsequent_indent=subsequentIndent,
                    width=maxWidth)
    lines = []
    for wni in wnis:
        lines.extend(wrapped(indent,
            fmt('|{wni.base} {wni.pos} {wni.number}|')))
        for kind in wni.info.keys():
            info = wni.info[kind]
            if info:   # skip over empty ones
                relation_title = kind.title().replace('_', ' ')
                lines.extend(wrapped(indent + 1, fmt('{relation_title}:')))
                if type(info) == str:
                    info = info.replace('_', ' ')
                    lines.extend(wrapped(indent + 2, info, hanging=False))
                elif type(info) == list:
                    for item in info:
                        item = item.replace('_', ' ')
                        lines.extend(wrapped(indent + 2,
                            item[0].upper() + item[1:], hanging=True))
    return lines

def WNDisplayHTML(wnis):
    '''Return a list of lines containing HTML-formatted info in wni'''

    lines = []
    for wni in wnis:
        lines.append(
            fmt('<h4 class="synset">|{wni.base} {wni.pos} {wni.number}|</h4>'))
        for kind in wni.info.keys():
            info = wni.info[kind]
            if info:   # skip over empty ones
                lines.append('<dl class="rellist">')
                relation_title = escaped(kind.title().replace('_', ' '))
                lines.append(fmt('<dt class="relname">'
                                 '{relation_title}:</dt>'))
                if type(info) == str:
                    info = escaped(info)
                    info = info.replace('_', ' ')
                    lines.append(fmt('<dd class= "reldata">{info}</dd>'))
                elif type(info) == list:
                    for item in info:
                        item = escaped(item[0].upper() + item[1:])
                        item = item.replace('_', ' ')
                        lines.append(fmt('<dd class="reldata">{item}</dd>'))
                lines.append('</dl>')
    return lines

def entryDisplay(lex, word, wnKind='', maxWidth=70):
    '''Return a list of lines displaying headwords, possibly with WordNet info.
    If wnKind is 'defs', the info is definitions and examples; if 'nyms',
    synonyms, antonyms, and a range of other *nyms. Text output is wrapped
    to maxWidth, unless maxWidth == 0, in which case the output is HTML.'''
    lines = []
    spacing = 4 * ('&nbsp;' if maxWidth == 0 else ' ')
    headwords = lex.contains(word) or [None]
    for headword in headwords:
        wnis = []
        # title is what is displayed at top, head is what is looked up
        head = title = word if headword is None else headword
        if wnKind == 'nyms':
            wnis = lex.related(head)
        else:
            pronunciations = lex.pronunciations(head)
            if pronunciations:
                pronunciations = ', '.join(pronunciations)
                title = fmt('{title}{spacing}/{pronunciations}/')
            if wnKind == 'defs':
                wnis = lex.definitions(head)
        if maxWidth == 0:
            lines.append(fmt('<h3 class="headword">{title}</h3>'))
            lines.extend(WNDisplayHTML(wnis))
        else:
            lines.extend(wrap(title, initial_indent='', subsequent_indent='  ',
                          width=maxWidth))
            lines.extend(WNDisplayText(wnis, 1, maxWidth))
    if not(headword or wnis):  # it was neither in the lexicon nor in WordNet
        lines = []
    return lines

# The following are imported with 'from lexFormat import *'

def languageNames():
    '''Return a list of all the supported language names'''
    return sorted(LG_NAME_TO_CODE.keys())

def languageName(code):
    '''Return the official name of a language given ISO 639-3 code'''
    return LG_CODE_TO_NAME.get(code, '')

def languageCode(name):
    '''Return the ISO 639-3 code of a language given its name'''
    return LG_NAME_TO_CODE.get(name, '')

def languageWidth(name):
    '''Return the average width of characters in this language,
    as compared to Latin characters'''
    if ('Chinese' in name) or ('Japanese' in name):
        return 1.7
    else:
        return 1

def headsDisplay(lex, word, maxWidth=70):
    '''Return a list of lines displaying normalized spellings,
    optionally with pronunciations'''
    return entryDisplay(lex, word, wnKind='', maxWidth=maxWidth)

def defsDisplay(lex, word, maxWidth=70):
    '''Return a list of lines displaying definitions and examples'''
    return entryDisplay(lex, word, wnKind='defs', maxWidth=maxWidth)

def nymsDisplay(lex, word, maxWidth=70):
    '''Return a list of lines displaying synonyms and other nyms'''
    return entryDisplay(lex, word, wnKind='nyms', maxWidth=maxWidth)

def wordsDisplay(words, maxWidth=70):
    '''Return a list of lines displaying a list of words.
    Text is wrapped to maxWidth, unless maxWidth == 0, in which case
    the output is HTML.'''
    if not words:
        return []
    words = ', '.join([word.replace('_', ' ') for word in words])
    if maxWidth == 0: 
        return [fmt('<p class="words">{words}</p>')]
    else:
        return wrap(words, width=maxWidth)

def busyPhase(index):
    '''Return the string for busy phase #index'''
    return PHASE_STRINGS[index]

def busyWait(phase, percent):
    '''A console-based callable for the lexicon module'''
    global prevPhase
    if phase != prevPhase:
        print(PHASE_STRINGS[phase], end=' ')
        sys.stdout.flush()
        prevPhase = phase
    if phase == len(PHASE_STRINGS) - 1:    # last phase
        print()
        prevPhase = None

if __name__ == '__main__':
    print(_('This module is part of the Lexitron package'))

