# lexTerm.py jcj 2019-07-08, 2020-02-11, 2020-02-18, 2020-05-12, 2020-05-25,
#            2020-06-02

'''A VT-100-style smart-terminal interface for lexitron'''

## Support for gettext
# This file assumes that _ and pgettext have been injected
# into the builtins namespace by the '__main__' file.
# Python doesn't support pgettext until version 3.8. So...
try:
    pgettext
except NameError:
    from my.pgettext import pgettext
__ = pgettext

# standard-library imports
import os
import sys
from collections import namedtuple

# private imports
from my.error import *       # PROGNAME, STATUS, error 
from my.xyterm import *      # termwrap, display, gotoxy, etc
from my.textutils import *   # fmt and prefixOf

# project imports
import lexicon
from lexOut import *
from lexStrings import ID, CMD, COMMANDS

def interact(lex):

    def resize():
        # curses (on which terminal is based) does not report changes in
        # screen dimensions, so this only works at the start of the session
        nonlocal nrows, xmax, ymax, maxWidth
        xmax, ymax = scrsize()
        if ymax < MIN_YMAX or xmax < MIN_XMAX:
            message(fmt(_('Sorry, terminal must be at least '
                      '{MIN_XMAX} x {MIN_YMAX} characters. ')))
            getkey()
            return False
        nrows = ymax - 4
        maxWidth = ((xmax - XOFFSET * 2) //
                    languageWidth(languageName(lex.getLanguage())))
        return True

    def status(line, s):
        gotoxy(0, ymax + line)
        clreol()
        display(s[:xmax], BOLD | color(MAGENTA))

    def message(s):
        gotoxy(0, ymax - 1)
        clreol()
        display(s[:xmax - 1], BOLD | color(RED))

    def languages():
        '''Return a list of languages available'''
        nonlocal LANGUAGES
        if LANGUAGES is None:
            LANGUAGES = [ languageName(code) for code in lex.languages() ]
        return LANGUAGES

    def setLanguage(string):
        '''Try to set the language to string and return a report'''
        nonlocal maxWidth
        string = string.replace('_', ' ') # because the available list shows _
        candidates = prefixOf(languages(), string)
        if not candidates:
            return [fmt(_(('[Language "{string}" is not supported]')))]
        elif len(candidates) > 1:
            return [fmt(_('[Language "{string}" is ambiguous]'))]
        else:
            candidate = candidates[0]
            lex.setLanguage(languageCode(candidate))
            maxWidth = ((xmax - XOFFSET * 2) //
                         languageWidth(languageName(lex.getLanguage())))
            return [fmt(_('[Language "{candidate}" set]'))]

    def showAnswer(lines):
        assert isinstance(lines, list), 'Unexpected non-list lines'
        if not lines:
            lines = [__('No matching entries', '[None]')]
        # need to show a screenful at a time
        pageFull = ymax - 5 - YOFFSET
        length = len(lines)
        start = 0
        while True:
            for i in range(pageFull):
                gotoxy(XOFFSET, YOFFSET + i)
                clreol()
                if start + i < length:
                    display(lines[start+i])
            if start + i >= length:
                return
            gotoxy(XOFFSET, YOFFSET+pageFull)
            display(__('Key menu 2 (all items): keypresses available '
                       'to the user to see More matching entries. <whitespace> '
                       'includes the spacebar, the tab key, and Enter/Return.',
                       '[More] ←↑→↓ <whitespace> eX)it '), BOLD | color(GREEN))
            while True:
                key = getkey()
                if key in finished:
                    gotoxy(XOFFSET, YOFFSET + pageFull)
                    clreol()
                    message('')
                    return
                if key in backwards:
                    start = max(0, start - pageFull)
                    break
                elif key in forwards:
                    start = min(length - pageFull, start + pageFull)
                    break


    # Initialize key bindings
    forwards = {KEY_RIGHT, KEY_DOWN, KEY_PGDN, KEY_END,
                ord(' '), ord('\t'), ord('\n'), ord('\r')}
    backwards = {127, KEY_LEFT, KEY_UP, KEY_PGUP, KEY_HOME, KEY_BS, KEY_DEL}
    finished = { ord(__('Keypress: eX)it', 'X')),
                 ord(__('Keypress: eX)it', 'x')) }

    # Initialize window dimensions
    MIN_YMAX = 24
    MIN_XMAX = 70
    NCOLS = 16
    XOFFSET = 8
    YOFFSET = 2
    xmax = ymax = nrows = maxWidth = 0
    if not resize(): return

    # Initialize commands and prompts
    LANGUAGES = None   # will be set the first time it's asked for
    FUNCTIONS = {
        CMD.WORD: lambda s: defsDisplay(lex, s, maxWidth) if lex.hasWordNet
                               else headsDisplay(lex, s, maxWidth),
        CMD.RELS: lambda s: nymsDisplay(lex, s, maxWidth),
        CMD.HOMS: lambda s: wordsDisplay(lex.homophones(s), maxWidth),
        CMD.ANAG: lambda s: wordsDisplay(lex.anagrams(s), maxWidth),
        CMD.REGX: lambda s: wordsDisplay(lex.regex(s), maxWidth),
        CMD.LANG: lambda s: wordsDisplay(setLanguage(s), maxWidth),
        CMD.QUIT: None
    }
    # Remove unavailable commands
    del COMMANDS[CMD.HELP]
    del COMMANDS[CMD.STAT]
    del COMMANDS[CMD.AVBL]
    if not(lex.fileName or lex.hasWordNet):
        del COMMANDS[CMD.WORD]
    if not lex.hasWordNet:
        del COMMANDS[CMD.RELS]
        del COMMANDS[CMD.LANG]
    if not lex.fileName:
        del COMMANDS[CMD.HOMS]
        del COMMANDS[CMD.ANAG]
        del COMMANDS[CMD.REGX]
    # Make remaining commands visible and effective
    KS = namedtuple('KEY_SET',      # particular values of CS.KEY
                    'PS2,'   # = CS.NAME
                    'FUN')   # = FUNCTIONS[key]
    KEYS = { val.KEY: KS(val.NAME, FUNCTIONS[key])
             for key, val in COMMANDS.items() }

    # Interactive loop
    programName = ID.NAME.upper()
    banner = fmt('— {programName} —')
    gotoxy(xmax // 2 - len(banner) // 2 - 1, 0)
    display(banner, BOLD | color(CYAN))
    while True:
        if lex.fileName:
            nHeads, nProns, nVars = lex.stats()
            fileName = os.path.basename(lex.fileName)
            status(-3, fmt(_('File: {fileName} '
                         '[{nHeads:,d} /{nProns:,d} ({nVars:,d})/]')))
        else:
            status(-3, _('File: [None]'))
        if lex.hasWordNet:
            language = languageName(lex.getLanguage())
            status(-2, fmt(_('Language: {language} '
                         '(Type = for list of available languages)')))
        else:
            status(-2, _('Language: [None]'))
        message(' '.join(val.PROMPT for key, val in COMMANDS.items()) + ': ')
        try:
            ch = chr(getkey()).upper()
        except ValueError:   # can happen if function key pressed
            continue
        if ch == '=' and lex.hasWordNet:
            showAnswer(wordsDisplay(languages(), maxWidth))
            continue
        elif ch not in KEYS:
            continue
        if KEYS[ch].FUN is None:  # Quit command
            return
        # prompt for the argument
        message(KEYS[ch].PS2 + ': ')
        string = getstr().strip()
        if not string:
            continue
        answer = KEYS[ch].FUN(string)
        showAnswer(answer)

def termMain(options):
    try:
        lex = lexicon.Lexicon(options, busyWait=busyWait)
    except lexicon.LexiconError as err:
        error(STATUS.FAIL, str(err))
    termwrap(interact, lex)
    sys.exit(STATUS.OK)

if __name__ == '__main__':
    print(_('This module is part of the Lexitron package'))

