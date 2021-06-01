# lexStrings.py jcj 2020-02-06, 2020-02-11, 2020-05-27, 2020-06-02, 2021-03-27

'''
Constant strings used in multiple modules of lexitron
'''

## Support for gettext
# This file assumes that _ and pgettext have been injected
# into the builtins namespace by the '__main__' file.
# Python doesn't support pgettext until version 3.8. Meanwhile...
try:
    pgettext
except NameError:
    from my.pgettext import pgettext
__ = pgettext

# standard-library imports
import os
from collections import namedtuple, OrderedDict

# private imports
from my.constants import StrConsts
from my.textutils import fmt

__all__ = ['ENV', 'ID', 'OPT', 'INTER', 'CMD', 'COMMANDS']

class ENV:
    '''Directory and file-name information'''
    APP_DIR = os.path.dirname(__file__)
    LANGUAGE = os.environ.get('LANGUAGE',
	           os.environ.get('LANG',
			   'en'))[:2]
    HELP_DIR = os.path.join(APP_DIR, 'help', LANGUAGE) 
    if not os.path.exists(HELP_DIR):
        HELP_DIR = os.path.join(APP_DIR, 'help', 'en')
    HELP_FILE = os.path.join(HELP_DIR, 'lexitron.html')
    DISPLAY_NAME = 'Lexitron'
    PATH_NAME = 'lexitron'
    ICON_FILE = 'lexitron.png'
    CONFIG_FILE = '.lexitronrc'

class URLS:
    CMU = 'http://www.speech.cs.cmu.edu/cgi-bin/cmudict'
    WN  = 'https://wordnet.princeton.edu'
    OMW = 'http://compling.hss.ntu.edu.sg/omw'
    HELP = fmt('file://{ENV.HELP_FILE}')

class HTML:
    _PREFIX = '<a href="'
    _SUFFIX = '">'
    CMU_LINK = fmt('{_PREFIX}{URLS.CMU}{_SUFFIX}')
    WN_LINK = fmt('{_PREFIX}{URLS.WN}{_SUFFIX}')
    OMW_LINK = fmt('{_PREFIX}{URLS.OMW}{_SUFFIX}')
    HELP_LINK = fmt('{_PREFIX}{URLS.HELP}{_SUFFIX}')
    END_LINK = '</a>'

class TERM:
    _PREFIX = '\x1B]8;;'
    _SUFFIX = '\x1B\\'
    CMU_LINK = fmt('{_PREFIX}{URLS.CMU}{_SUFFIX}')
    WN_LINK = fmt('{_PREFIX}{URLS.WN}{_SUFFIX}')
    OMW_LINK = fmt('{_PREFIX}{URLS.OMW}{_SUFFIX}')
    HELP_LINK = fmt('{_PREFIX}{URLS.HELP}{_SUFFIX}')
    END_LINK = '\x1B]8;;\x1B\\'

class ID:
    '''Program identification and acknowledgements'''
    NAME = 'Lexitron'
    VERSION = 'v1.0'
    COPYRIGHT = '(c) 2020 Jason C Johnston'
    THANKS_PLAIN = fmt(_(
        'With thanks to:\n'
        '  * {TERM.CMU_LINK}the CMU Pronouncing Dictionary{TERM.END_LINK}\n'
        '  * {TERM.WN_LINK}WordNet{TERM.END_LINK}\n'
        '  * {TERM.OMW_LINK}the Open Multilingual WordNet{TERM.END_LINK}'))
    THANKS_RICH = fmt(_(
        'With thanks to '
        '{HTML.CMU_LINK}the CMU Pronouncing Dictionary{HTML.END_LINK}, '
        '{HTML.WN_LINK}WordNet{HTML.END_LINK}, '
        'and {HTML.OMW_LINK}the Open Multilingual WordNet{HTML.END_LINK}'))
    HELP_PLAIN = fmt(_('See {TERM.HELP_LINK}the help file{TERM.END_LINK} '
                  'for complete documentation.')) 
    HELP_RICH = fmt(_('See {HTML.HELP_LINK}the help file{HTML.END_LINK} '
                 'for complete documentation.'))
 
# Keys in options dictionary 
OPT = StrConsts('icase, idiac, interface, language, lexicon, style, exec')

# Types of user interface
INTER = StrConsts('console, terminal, graphic')

# Command strings
CMD = StrConsts('help, stat, word, rels, anag, homs, regx, avbl, lang, quit')

CS = namedtuple('COMMAND_SET',  # info keyed to arbitrary 4-char ID
                'NAME,'   # string representing the command
                'LABEL,'  # label of radio button in graphic interface
                'PROMPT,' # prompt appearing in terminal interface
                'KEY,'    # single keystroke used in terminal interface
                'NARGS')  # number of arguments required

COMMANDS = OrderedDict([
    (CMD.HELP, CS('?', '', '', '', 0)),
    (CMD.STAT, CS('=', '', '', '', 0)),
    (CMD.WORD, CS(__('Menu C1, no spaces', 'Word'),
                  __('Button G1', '&Word'),
                  __('Menu T1, no spaces', 'W)ord'),
                  __('Keypress: W)ord', 'W'), 1)),
    (CMD.RELS, CS(__('Menu C1, refers to words, no spaces', 'Related'),
                  __('Button G1, refers to words', '&Related'),
                  __('Menu T1, refers to words, no spaces', 'R)elated'),
                  __('Keypress: R)elated', 'R'), 1)),
    (CMD.HOMS, CS(__('Menu C1, no spaces', 'Homophones'),
                  __('Button G1', 'Ho&mophones'),
                  __('Menu T1, no spaces', 'H)omophones'),
                  __('Keypress: H)omophones', 'H'), 1)),
    (CMD.ANAG, CS(__('Menu C1, no spaces', 'Anagrams'),
                  __('Button G1', '&Anagrams'),
                  __('Menu T1, no spaces', 'A)nagrams'),
                  __('Keypress: A)nagrams', 'A'), 1)),
    (CMD.REGX, CS(__('Menu C1, no spaces', 'Regex'),
                  __('Button G1', 'Re&gex'),
                  __('Menu T1, no spaces', 'ReG)ex'),
                  __('Keypress: ReG)ex', 'G'), 1)),
    (CMD.AVBL, CS(__('Menu C1, refers to languages, no spaces', 'Available'),
                  '', '', '', 0,)),
    (CMD.LANG, CS(__('Menu C1, no spaces', 'Language'),
                  '',
                  __('Menu T1, no spaces', 'L)anguage'),
                  __('Keypress: L)anguage', 'L'), 1)),
    (CMD.QUIT, CS(__('Menu C1, no spaces', 'Quit'),
                  '',
                  __('Menu T1, no spaces', 'Q)uit'),
                  __('Keypress: Q)uit', 'Q'), 0))
    ])

if __name__ == '__main__':
    print(_('This module is part of the Lexitron package'))

