#!/usr/bin/env python3
# lexitron.py jcj 2019-02-20, 2019-05-29, 2019-07-06, 2020-02-11, 2020-05-25,
# 2021-03-26

'''
Exercise the functionality of the Lexicon class implemented in lexicon.py
through a variety of different interfaces and in various languages.
'''

# gettext must be installed before importing modules that use it
import os
import gettext
from my.system import SYSTEM
LOCALE_DOMAIN = 'lexitron'
LOCALE_DIR = os.path.join(SYSTEM.HOME, 'locales')
language = gettext.translation(LOCALE_DOMAIN,
                               localedir=LOCALE_DIR, fallback=True)
language.install(['gettext', 'pgettext']) # as well as the default _
# _ as alias for gettext.gettext has been installed in the builtins namespace,
# gettext has been installed as well so we can easily test for its presence,
# and pgettext will also have been installed if supported by the Python version
# Versions prior to Python 3.8 do not support pgettext. So...
try:
    pgettext
except NameError:
    from my.pgettext import pgettext
__ = pgettext

# Remaining standard-library imports
import sys
import getopt
import configparser

# Private imports
from my.error import *          # PROGNAME, STATUS and error
from my.textutils import *      # fmt, prefixOf and getBoolean

# Project imports
from lexCon import conMain      # dumb-console user interface
from lexTerm import termMain    # smart-terminal user interface
from lexGui import guiMain      # graphical user interface
from lexStrings import *        # constant strings ID, OPT, INTER
from lexOut import *            # full language names

# Unixy OSes have a standard wordlist available, but not Windows
if SYSTEM.OS == 'Windows':
    LEXICON_FILENAME = ''
else:
    LEXICON_FILENAME = '/usr/share/dict/words'

SUMMARY = _('''\
Use an external lexicon file and/or the resources of WordNet to check for
definitions, related words, pronunciations, homophones, anagrams, and regular
expressions. Matches may ignore case and/or diacritics. Queries can be
submitted on the command line or interactively via a dumb console, smart
terminal, or fully graphical interface.
''')

USAGE = fmt(__('Do not translate the options beginning with - or -- ',
'''
USAGE: {PROGNAME} OPTIONS

OPTIONS:
    -h, --help            print this message and exit
    -V, --version         print version information and exit
    -c, --{OPT.ICASE} BOOLEAN   ignore letter-case in matching, default: no
    -d, --{OPT.IDIAC} BOOLEAN   ignore diacritics in matching, default: no
    -l, --{OPT.LANGUAGE} LANG   use language LANG for WordNet lookups,
                          default: English
    -f, --{OPT.LEXICON} LEX     use lexicon file LEX
    -i, --{OPT.INTERFACE} {INTER.CONSOLE}|{INTER.TERMINAL}|{INTER.GRAPHIC} 
                          use the specified kind of user interface,
                          default: {INTER.CONSOLE}
    -s, --{OPT.STYLE} STYLE     use CSS file STYLE to control appearance
                          of GUI output
    -x, --{OPT.EXEC} COMMAND    execute console-style command COMMAND
                          (may be used multiple times), then exit

{ID.HELP_PLAIN}'''))

LANGUAGES = languageNames()
INTERFACES = [INTER.CONSOLE, INTER.TERMINAL, INTER.GRAPHIC]

def getConfigOptions(options):
    '''Try to get default values from an INI-style  configuration file.
    Failure to read an existing configuration file raises an error,
    but other problems (eg non-existent options) are ignored.'''
    configFileName = os.path.join(SYSTEM.HOME, ENV.CONFIG_FILE)
    if os.path.exists(configFileName):
        config = configparser.ConfigParser()
        try:
            config.read(configFileName)
        except Exception as err:
            error(STATUS.FAIL, str(err))
        for key, val in config.items('DEFAULT'):
            # booleans
            if key in (OPT.ICASE, OPT.IDIAC):
                boolean = getBoolean(val)
                if boolean is not None:
                    options[key] = boolean
            # files
            elif key in (OPT.LEXICON, OPT.STYLE):
                if os.path.exists(val):
                    options[key] = val
            # enumerated values
            elif key == OPT.LANGUAGE:
                candidates = prefixOf(LANGUAGES, val)
                if len(candidates) == 1:
                    options[key] = languageCode(candidates[0])
            elif key == OPT.INTERFACE:
                candidates = prefixOf(INTERFACES, val)
                if len(candidates) == 1:
                    options[key] = candidates[0]
            # ignore other values
            else:
                pass

def main():
    '''Perform option and argument processing'''
    # Interface option value -> handler
    interfaces = { INTER.CONSOLE: conMain,
                   INTER.TERMINAL: termMain,
                   INTER.GRAPHIC: guiMain }
    # Options: ultimate defaults
    options = { OPT.ICASE: False, OPT.IDIAC: False,
                OPT.INTERFACE: INTER.CONSOLE,
                OPT.LANGUAGE: languageCode(__('Name of language', 'English')),
                OPT.LEXICON: LEXICON_FILENAME,
                OPT.STYLE: '',
                OPT.EXEC: [] }
    # Options: defaults in a configuration file
    getConfigOptions(options)
    # Options: values on command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:d:i:l:hf:s:Vx:',
            (OPT.ICASE + '=', OPT.IDIAC + '=', OPT.INTERFACE + '=',
             OPT.LANGUAGE + '=', 'help', OPT.LEXICON + '=', OPT.STYLE + '=',
             'version', OPT.EXEC + '='))
    except getopt.GetoptError:
        error(STATUS.BADUSE, USAGE)
    if args:
        error(STATUS.BADUSE, USAGE)
    for o, a in opts:
        if o in ('-h', '--help'):
            print(SUMMARY + USAGE)
            sys.exit(STATUS.OK)
        elif o in ('-V', '--version'):
            print(fmt('{ID.NAME} {ID.VERSION} {ID.COPYRIGHT}'))
            print(ID.THANKS_PLAIN)
            sys.exit(STATUS.OK)
        elif o in ('-c', '--' + OPT.ICASE):
            boolean = getBoolean(a)
            if boolean is not None:
                options[OPT.ICASE] = boolean
            else:
                error(STATUS.BADUSE, USAGE)
        elif o in ('-d', '--' + OPT.IDIAC):
            boolean = getBoolean(a)
            if boolean is not None:
                options[OPT.IDIAC] = boolean
            else:
                error(STATUS.BADUSE, USAGE)
        elif o in ('-i', '--' + OPT.INTERFACE):
            # expand possible interface abbreviation
            candidates = prefixOf(INTERFACES, a)
            if not candidates:
                error(STATUS.BADUSE, fmt(_('Unsupported interface "{a}"')))
            elif len(candidates) > 1:
                error(STATUS.BADUSE, fmt(_('Ambiguous interface "{a}"')))
            options[OPT.INTERFACE] = candidates[0]
        elif o in ('-l', '--' + OPT.LANGUAGE):
            if a == '?':
                for line in wordsDisplay(LANGUAGES):
                    print(line)
                sys.exit(STATUS.OK)
            # expand possible language abbreviation
            candidates = prefixOf(LANGUAGES, a)
            if not candidates:
                error(STATUS.BADUSE, fmt(_('Unsupported language "{a}"')))
            elif len(candidates) > 1:
                error(STATUS.BADUSE, fmt(_('Ambiguous language "{a}"')))
            # and use corresponding three-letter code
            options[OPT.LANGUAGE] = languageCode(candidates[0])
        elif o in ('-f', '--' + OPT.LEXICON):
            options[OPT.LEXICON] = a
        elif o in ('-s', '--' + OPT.STYLE):
            if a:
                if os.path.exists(a):
                    options[OPT.STYLE] = a
                else:
                    error(STATUS.FAIL, fmt(_('Cannot find file {a}')))
            options[OPT.STYLE] = a
        elif o in ('-x', '--' + OPT.EXEC):
            options[OPT.EXEC].append(a)
            options[OPT.INTERFACE] = INTER.CONSOLE
        else:
            assert False, 'Internal error: Unhandled option'
    interfaces[options[OPT.INTERFACE]](options)
    sys.exit(STATUS.OK)

if __name__ == '__main__':
    main()

