# lexCon.py jcj 2019-07-04, 2020-02-11, 2020-05-11, 2020-05-25, 2020-06-02

'''
Pure command-line and dumb-console interfaces for lexitron
'''

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
import sys
import os.path
import shutil
import textwrap
import readline   # the mere import itself gives readline functionality
from collections import deque, namedtuple, OrderedDict

# private imports
from my.error import *
from my.textutils import *

# project imports
import lexicon
from lexOut import *
from lexStrings import ID, OPT, CMD, COMMANDS

FN = namedtuple('FUNCTION_INFO',   # info keyed to CS.NAME
                'NARGS,'    # = CS.NARGS
                'FUNCT')    # = FUCTIONS[key]

def doCommands(lex, queue):
    '''Repeatedly fetch a command from the queue and execute it,
    until the command is Quit. Prompt for fresh commands as necessary.'''

    def getWidth():
        '''Set a variable to the current terminal width adjusted for
        the average width of characters in the current language'''
        nonlocal maxWidth
        cols, rows = shutil.get_terminal_size()
        maxWidth = cols // languageWidth(languageName(lex.getLanguage()))
    
    def languages():
        '''Return the list of languages available, having consulted WordNet
        only on the first occasion'''
        nonlocal LANGUAGES
        if LANGUAGES is None:
            LANGUAGES = [ languageName(code) for code in lex.languages() ]
        return LANGUAGES
    
    def currentLanguage():
        '''Return the current language'''
        if lex.hasWordNet:
            currentLanguage = languageName(lex.getLanguage())
            return fmt(_('LANGUAGE: {currentLanguage}'))
        else:
            return _('LANGUAGE: [None]')
    
    def setLanguage(s):
        '''Set the language to that specified by full name s if valid'''
        s = s.replace('_', ' ')   # because the available list shows _
        names = prefixOf(languages(), s)
        if not names:
            return [_('! Unrecognised language name')]
        elif len(names) > 1:
            return [_('! Ambiguous language name')]
        name = names[0]
        lex.setLanguage(languageCode(name))
        # readjust maxWidth for characters in current language
        getWidth()
        
    def stats():
        '''Return information about the available resources'''
        if lex.fileName:
            nHeads, nProns, nVars = lex.stats()
            fileName = os.path.basename(lex.fileName)
            fileInfo = fmt(_('FILE: {fileName} '
                '[{nHeads:,d} /{nProns:,d} ({nVars:,d})/]'))
        else:
            fileInfo = _('FILE: [None]')
        return [fileInfo, currentLanguage()]
    
    def help():
        '''Summarize the available commands'''
        return [' '.join(CMDS.keys())]
    
    def show(answer):
        '''Display answer, assumed to be a list of lines'''
        assert isinstance(answer, list), 'Unexpected non-list answer'
        if not answer:
            print(__('No matching entries', '[None]'))
        else:
            for line in answer:
                print(line)

    LANGUAGES = None  # set when first needed
    maxWidth = None   # set once or periodically by getWidth()
    PROMPT = '» ' 
    FUNCTIONS = {
        CMD.HELP: lambda s: help(),
        CMD.STAT: lambda s: stats(),
        CMD.WORD: lambda s: defsDisplay(lex, s, maxWidth) if lex.hasWordNet
                               else headsDisplay(lex, s, maxWidth),
        CMD.RELS: lambda s: nymsDisplay(lex, s, maxWidth),
        CMD.HOMS: lambda s: wordsDisplay(lex.homophones(s), maxWidth),
        CMD.ANAG: lambda s: wordsDisplay(lex.anagrams(s), maxWidth),
        CMD.REGX: lambda s: wordsDisplay(lex.regex(s), maxWidth),
        CMD.AVBL: lambda s: wordsDisplay(languages(), maxWidth),
        CMD.LANG: lambda s: setLanguage(s),
        CMD.QUIT: lambda s: sys.exit(STATUS.OK),
    }
    # Remove unavailable commands
    if not(lex.fileName or lex.hasWordNet):
        del COMMANDS[CMD.WORD]
    if not lex.hasWordNet:
        del COMMANDS[CMD.RELS]
        del COMMANDS[CMD.LANG]
    if not lex.fileName:
        del COMMANDS[CMD.HOMS]
        del COMMANDS[CMD.ANAG]
        del COMMANDS[CMD.REGX]
    # Reorganize remaining commands for name-based lookup
    CMDS = OrderedDict([
        (val.NAME, FN(val.NARGS, FUNCTIONS[key]))
            for key, val in COMMANDS.items()
        ])

    getWidth()
    # get a command from the queue and execute it until the command is Quit
    while True:
        while not queue:
            try:
                line = input(PROMPT).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                line = COMMANDS[CMD.QUIT].NAME
            if line:
                queue.append(line)
        prefix, *args = queue.popleft().split() # removes spaces at ends
        candidates = prefixOf(CMDS.keys(), prefix)
        if not candidates:
            print(fmt(_('! Unrecognized command "{prefix}"')))
            continue
        elif len(candidates) > 1:
            print(fmt(_('! Ambiguous command "{prefix}"')))
            continue
        # there is only 1 candidate, and it's valid
        command = candidates[0]
        nargs = CMDS[command].NARGS
        if (nargs == 0 and len(args) > 0) or (nargs != 0 and len(args) == 0):
            print(_('! Wrong number of arguments to command'))
            continue
        result = CMDS[command].FUNCT(' '.join(args)) # CMD.QUIT will exit here
        if result is not None:
            show(result)

def conMain(options):
    queue = deque()
    commands = options[OPT.EXEC]
    try:
        lex = lexicon.Lexicon(options, busyWait=None if commands else busyWait)
    except lexicon.LexiconError as err:
        error(STATUS.FAIL, str(err))       
    # non-interactive use
    if commands:
        for command in commands:
            for cmd in command.split(';'):
                queue.append(cmd)
        queue.append(COMMANDS[CMD.QUIT].NAME)
    # interactive use
    else:
        queue.append(COMMANDS[CMD.STAT].NAME)
        queue.append(COMMANDS[CMD.HELP].NAME)
    doCommands(lex, queue)
    sys.exit(STATUS.OK)

if __name__ == '__main__':
    print(_('This module is part of the Lexitron package'))

