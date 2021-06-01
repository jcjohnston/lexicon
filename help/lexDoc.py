#!/usr/bin/env python3
# lexDoc.py jcj 2020-06-15

'''Generate localized HTML documentation for Lexitron'''

# gettext must be installed before importing modules that use it
import os
import gettext
from my.system import SYSTEM
LOCALE_DOMAIN = 'lexitron-documentation'
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

from my.textutils import fmt

def out(s):
    # Do not use for HEAD because of all the braces in it
    print(fmt(s))

### HTML Definitions

HEAD = '''\
<!DOCTYPE HTML>
<html>
<head>
<title>Lexitron</title>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
  body {
    font-family: 'Open Sans', arial, sans-serif;
    color: #494d55;
    font-size: 14px;
  }
  html, body {
    height: 100%;
  }
  .sidenav {
    height: 100%;
    width: 160px;
    position: fixed;
    z-index: 1;
    top: 0;
    left: 0;
    background-color: #222222;
    overflow-x: hidden;
    padding-top: 20px
  }
  .sidenav a {
    padding: 6px 8px 6px 16px;
    text-decoration: none;
    font-size: 12px;
    color: #cfcfcf;
    display: block;
  }
  .sidenav a hover {
    color: #f1f1f1;
  }
  .main {
    margin-left: 160px;
    padding: 0px 10px;
  }
  .main-icon {
    height: 70px;
    padding-right: 15px;
    vertical-align: middle;
  }
  .main-title {
    font-size: 24pt
  }
  .section-title {
    color: #0000f8;
    padding-top: 10px;
  }
  .subsection-title {
    color: #008f00;
    font-style: italic;
  }
  .multi-column-list {
    list-style-type: none;
    column-width: 12em;
    column-gap: 3em;
    column-rule-style: solid;
    column-rule-width: 1px
  }  
  p {
    line-height: 1.25;
  }
  p.note
  {
    background-color: #f0f7fb;
    background-image: url("../images/pencil.png");
    background-position: 9px 0px;
    background-repeat: no-repeat;
    border-left: solid 1px #3498db;
    line-height: 18px;
    overflow: hidden;
    padding: 15px 60px;
  }
  a {
    color: #3aa7aa;
  }
  a:hover {
    text-decoration: underline;
    color: #339597;
  }
  a:focus {
    text-decoration: none;
  }
  pre {
    color: #ff0f00;
    font-family: monospace;
  }
  code {
    color: #ff0f00;
    font-size: 14px;
    font-wdith: bold;
    font-family: Consolas, Monacor, 'Andale Mono', 'Ubuntu Mono', monospace;
    line-height: 1.25;
    display: inline-block;
  }
  dt {
    font-style: italic;
    padding-top: 4px;
  }
  td {
    padding-right: 6px;
  }
  @media screen and (max-height: 450px) {
    .sidenav {padding-top: 10px;}
    .sidenav a {font-size: 10px;}
  }
</style>
</head>
'''
BODY = '<body>'
TAIL = '</body></hmtl>'

PRE_IMPORT = '''
<pre>
    from nltk.corpus import wordnet
    from nltk.stem import WordNetLemmatizer
</pre>
'''
PRE_CONFIG = '''
<pre>
    [DEFAULT]
    Lexicon = /path/to/LexiconFile
    iDiac = True
    Interface = terminal
    Language = Catalan
</pre>
'''
PRE_SYNSETS = '''
<pre>
    perro
        |dog N 01|
            Synonyms:
                can perro
            Hypernyms:
                cánido
            Hyponyms:
                basenji chucho gozque mestizo grifón pug spitz
        |rotter N 01|
            Synonyms:
                perro
            Hypernyms:
                antipático desagradable
</pre>
'''
PRE_STYLES = '''
<pre>
    body {}
    .headword  { color: red; }
    .synset { color: blue; }
    .rellist {}
    .relname { font-style: italic; }
    .reldata {}
    .words {}
</pre>
'''
PRE_SETLANGUAGE = '''
<pre>
    $ LANGUAGE=fr lexitron --interface graphic
</pre>
'''
DIV_MAIN = '<div class="main">'
DIV_SIDENAV = '<div class="sidenav">'
DIV_END = '</div>'

H1_MAIN = '<h1 class="main-title"><img src="../../lexitron.png" class="main-icon">'
H1_END = '</h1>'
H3_SYNOPSIS = '<h3 id="Synopsis" class="section-title">'
H3_PREREQUISITES = '<h3 id="Prerequisites" class="section-title">'
H3_CONFIGFILE = '<h3 id="ConfigFile" class="section-title">'
H3_LEXICONFILE = '<h3 id="LexiconFile" class="section-title">'
H3_CSSFILE = '<h3 id="CSSFile" class="section-title">'
H3_LANGUAGES = '<h3 id="Languages" class="section-title">'
H3_CONSOLEINTER = '<h3 id="ConsoleInter" class="section-title">'
H3_TERMINALINTER = '<h3 id="TerminalInter" class="section-title">'
H3_GRAPHICINTER = '<h3 id="GraphicInter" class="section-title">'
H3_ACKNOWLEDGEMENTS = '<h3 id="Acknowledgements" class="section-title">'
H3_CONTACT = '<h3 id="Contact" class="section-title">'
H3_INTRODUCTION = '<h3 id="Introduction" class="section-title">'
H3_END = '</h3>'
H4_CONSOLELAUNCH = '<h4 id="ConsoleLaunch" class="subsection-title">'
H4_GUILAUNCH = '<h4 id="GUILaunch" class="subsection-title">'
H4_APPLICATIONLANGUAGES = '<h4 id="Application-Languages" class="subsection-title">'
H4_WORDNETLANGUAGES = '<h4 id="WordNetLanguages" class="subsection-title">'
H4_END = '</h4>'

LINK_INTRODUCTION = '<a href="#Introduction">'
LINK_SYNOPSIS = '<a href="#Synopsis">'
LINK_PREREQUISITES = '<a href="#Prerequisites">'
LINK_CONFIGFILE = '<a href="#ConfigFile">'
LINK_LEXICONFILE = '<a href="#LexiconFile">'
LINK_CSSFILE = '<a href="#CSSFile">'
LINK_LANGUAGES = '<a href="#Languages">'
LINK_WORDNETLANGUAGES = '<a href="#WordNetLanguages">'
LINK_CONSOLEINTER = '<a href="#ConsoleInter">'
LINK_TERMINALINTER = '<a href="#TerminalInter">'
LINK_GRAPHICINTER = '<a href="#GraphicInter">'
LINK_ACKNOWLEDGEMENTS = '<a href="#Acknowledgements">'
LINK_CONTACT = '<a href="#Contact">'
LINK_NLTK = '<a href="https://www.nltk.org/index.html">'
LINK_CONFIGLIB = '<a href="https://docs.python.org/3/library/configparser.html">'
LINK_CMU = '<a href="http://www.speech.cs.cmu.edu/cgi-bin/cmudict">'
LINK_QT5STYLES = '<a href="https://doc.qt.io/qt-5/stylesheet-reference.html">'
LINK_WORDNET = '<a href="https://wordnet.princeton.edu">'
LINK_OMW = '<a href="http://compling.hss.ntu.edu.sg/omw">'
LINK_END = '</a>'

P = '<p>'
P_BOLD = '<p style="font-weight: bold">'
P_NOTE = '<p class="note">'
P_END = '</p>'

CODE = '<code>'
CODE_END = '</code>'
CITE = '<i>'
CITE_END = '</i>'

LIST_MULTICOL = '<ul class="multi-column-list">'
LIST_SQUAREBULLETS = '<ul style="list-style-type: square">'
LIST_END = '</ul>'
ITEM = '<li>'
ITEM_END = '</li>'

DEFINITIONS = '<dl>'
DEFINED = '<dt>'
DEFINED_END = '</dt>'
DEFINITION = '<dd>'
DEFINITION_END = '</dd>'
DEFINITIONS_END = '</dl>'

TABLE = '<table id="OPTIONSLIST">'
ROW = '<tr><td>'
ROW_SEP = '</td><td>'
ROW_END = '</td></tr>'
TABLE_END = '</table>'

IMG_CONSOLE = '<img style="padding-left: 20px" src="../images/lexitron-console.png"/>'
IMG_TERMINAL = '<img style="padding-left: 20px" src="../images/lexitron-terminal.png"/>'
IMG_GUI = '<img style="padding-left: 20px" src="../images/lexitron-gui.png"/>'

OPEN_ANGLE = '&lt;'
CLOSE_ANGLE = '&gt;'
EM_DASH = '&mdash;'

### Generate output

print(HEAD)   # not out(HEAD) because of the embedded stylesheet
out(BODY)
out(DIV_SIDENAV)
out(__('Hyperlinked section headings forming a navigation menu. '
       'These names should match the section titles.', '''
{LINK_INTRODUCTION}Introduction{LINK_END}
{LINK_SYNOPSIS}Synopsis{LINK_END}
{LINK_PREREQUISITES}Prerequisites{LINK_END}
{LINK_CONFIGFILE}Configuration File{LINK_END}
{LINK_LEXICONFILE}Lexicon File{LINK_END}
{LINK_CSSFILE}CSS File{LINK_END}
{LINK_LANGUAGES}Language Support{LINK_END}
{LINK_CONSOLEINTER}Console Interface{LINK_END}
{LINK_TERMINALINTER}Terminal Interface{LINK_END}
{LINK_GRAPHICINTER}Graphic Interface{LINK_END}
{LINK_ACKNOWLEDGEMENTS}Acknowledgements{LINK_END}
{LINK_CONTACT}Contact{LINK_END}'''))
out(DIV_END)

out(DIV_MAIN)
out(__('Main heading, with icon', '{H1_MAIN}Lexitron{H1_END}'))

out(__('Section heading', '{H3_INTRODUCTION}Introduction{H3_END}'))
out(_('''
{P}Lexitron uses an external lexicon file and/or the resources of WordNet to
check for definitions, related words, pronunciations, homophones, anagrams, and
regular expressions. Matches may ignore case and/or diacritics. Queries can be
submitted on the command line or interactively via a dumb console, smart
terminal, or fully graphical interface.{P_END}'''))

out(__('Section heading', '{H3_SYNOPSIS}Synopsis{H3_END}'))
out(_('''
{P}Lexitron can be launched from the command line, or via an icon in a
graphical user interface.{P_END}'''))

out(__('Subsection heading', '{H4_CONSOLELAUNCH}By command{H4_END}'))
out(_('''
{P_BOLD}Usage: {CODE}lexitron OPTIONS{CODE_END}{P_END}
{P}OPTIONS:{P_END}
{TABLE}

{ROW}{CODE}-h{CODE_END}{ROW_SEP}{CODE}--help{CODE_END}{ROW_SEP}print this
message and exit{ROW_END}

{ROW}{CODE}-V{CODE_END}{ROW_SEP}{CODE}--version{CODE_END}{ROW_SEP}print version
information and exit{ROW_END}

{ROW}{CODE}-c{CODE_END}{ROW_SEP}{CODE}--icase
{CITE}BOOLEAN{CITE_END}{CODE_END}{ROW_SEP}ignore letter-case in matching,
default: {CODE}no{CODE_END}{ROW_END}

{ROW}{CODE}-d{CODE_END}{ROW_SEP}{CODE}--idiac {CITE}BOOLEAN{CITE_END}{CODE_END}{ROW_SEP}ignore diacritics in matching, default: {CODE}no{CODE_END}{ROW_END}

{ROW}{CODE}-l{CODE_END}{ROW_SEP}{CODE}--language
{CITE}LANGUAGE{CITE_END}{CODE_END}{ROW_SEP}use language
{CITE}LANGUAGE{CITE_END} for WordNet lookups, default:
{CODE}English{CODE_END}{ROW_END}

{ROW}{CODE}-f{CODE_END}{ROW_SEP}{CODE}--lexicon
{CITE}LEXICON-FILE{CITE_END}{CODE_END}{ROW_SEP}use lexicon file
{CITE}LEXICON-FILE{CITE_END} for spelling and pronunciation lookups{ROW_END}

{ROW}{CODE}-i{CODE_END}{ROW_SEP}{CODE}--interface
{CITE}INTERFACE{CITE_END}{CODE_END}{ROW_SEP}use the specified kind of user
interface, default: {CODE}console{CODE_END}{ROW_END}

{ROW}{CODE}-s{CODE_END}{ROW_SEP}{CODE}--style
{CITE}CSS-FILE{CITE_END}{CODE_END}{ROW_SEP}use CSS file
{CITE}CSS-FILE{CITE_END} to control appearance of GUI output{ROW_END}

{ROW}{CODE}-x{CODE_END}{ROW_SEP}{CODE}--exec
{CITE}COMMAND{CITE_END}{CODE_END}{ROW_SEP}execute console-style command
{CITE}COMMAND{CITE_END} and exit{ROW_END}

{TABLE_END}

{P}In these options, the terms in italics have the following meanings:{P_END}

{DEFINITIONS}

{DEFINED}{CODE}BOOLEAN{CODE_END}{DEFINED_END}

{DEFINITION}{CODE}1|0{CODE_END}, {CODE}true|false{CODE_END},
{CODE}yes|no{CODE_END}, {CODE}on|off{CODE_END} without regard to
case{DEFINITION_END}

{DEFINED}{CODE}COMMAND{CODE_END}{DEFINED_END}

{DEFINITION}Any command accepted by the {LINK_CONSOLEINTER}console user
interface{LINK_END} (which use of the {CODE}-x/--exec{CODE_END} option
implies){DEFINITION_END}

{DEFINED}{CODE}CSS-FILE{CODE_END}{DEFINED_END}

{DEFINITION}The path to a {LINK_CSSFILE}CSS file{LINK_END} conforming to CSS
2.1 or later{DEFINITION_END}

{DEFINED}{CODE}INTERFACE{CODE_END}{DEFINED_END}

{DEFINITION}{CODE}console|terminal|graphic{CODE_END} (or any unique prefix of
one of these) without regard to case, representing respectively a
{LINK_CONSOLEINTER}dumb-console{LINK_END},
{LINK_TERMINALINTER}smart-terminal{LINK_END} or {LINK_GRAPHICINTER}fully
graphical{LINK_END} user interface{DEFINITION_END}

{DEFINED}{CODE}LANGUAGE{CODE_END}{DEFINED_END}

{DEFINITION}The name of any of the {LINK_WORDNETLANGUAGES}supported
languages{LINK_END} (or any unique prefix of one of these) without regard to
case{DEFINITION_END}

{DEFINED}{CODE}LEXICON-FILE{CODE_END}{DEFINED_END}

{DEFINITION}The path to a user-supplied {LINK_LEXICONFILE}lexicon
file{LINK_END} containing spellings and, optionally,
pronunciations{DEFINITION_END}

{DEFINITIONS_END}

{P}Option names are case-sensitive. Long-form option names can be abbreviated
to any unique prefix. For instance, {CODE}--icase{CODE_END} can be given as
{CODE}--ic{CODE_END} but not as {CODE}--i{CODE_END} (ambiguous with
{CODE}--idiac{CODE_END} and {CODE}--interface{CODE_END}) or as
{CODE}--iCase{CODE_END} (wrong case).{P_END}

{P}Options may be specified in a {LINK_CONFIGFILE}configuration file{LINK_END}.
Command-line options have precedence over configuration-file options, which in
turn have precedence over built-in options.{P_END}'''))

out(__('Subsection heading', '{H4_GUILAUNCH}By icon{H4_END}'))
out(_('''
{P}Lexitron can be launched by activating its icon. The details {EM_DASH} where
the icon is located, whether it requires a single click or a double click, and
so on {EM_DASH} will vary from system to system. It may be that when Lexitron
is launched in this way, options can only be set in the
{LINK_CONFIGFILE}configuration file{LINK_END}.{P_END}'''))

out(__('Section heading', '{H3_PREREQUISITES}Prerequisites{H3_END}'))
out(_('''
{P}Lexitron requires Python 3 and its standard library to run.{P_END}

{P}The {LINK_GRAPHICINTER}graphical user interface{LINK_END} requires PyQt5 to
run.{P_END}

{P}The WordNet features {EM_DASH} definitions, examples, and related words
{EM_DASH} require the {LINK_NLTK}Natural Language Toolkit{LINK_END} (NLTK, which
in turn requires at least Python 3.5), and also the WordNet corpus and
lemmatizer, which can be downloaded as part of the NLTK data.{P_END}

{P}The Python import commands executed to supply these facilities are
equivalent to:{P_END}

{PRE_IMPORT}

{P}WordNet contains only lexical words (nouns, adjectives, verbs and some
adverbs), and not function words. A user-supplied lexicon is required for
Lexitron to recognize function words.{P_END}

{P}Pronunciations can only come from a user-supplied lexicon file. See
{LINK_LEXICONFILE}below{LINK_END} for further details.{P_END}

{P_NOTE}It is possible to run Lexitron with neither a user-supplied lexicon nor
WordNet, but in that case the only action available in either of the text-only
user interfaces will be to quit. (In the {LINK_GRAPHICINTER}graphical user
interface{LINK_END} you will also be able to load a lexicon file.){P_END}'''))

out(__('Section heading', '{H3_CONFIGFILE}The Configuration File{H3_END}'))
out(_('''
{P}Default options can be set in a per-user configuration file, called
{CODE}.lexitronrc{CODE_END} and located in the user’s home directory.{P_END}

{P}All command-line options can be set, using their long-form option name
without the leading ‘{CODE}--{CODE_END}’ and without regard to case. The same
abbreviations that are recognized on the command line can also be used in the
configuration file.{P_END}

{P}An example configuration (but without the indentation) would be:{P_END}

{PRE_CONFIG}

{P}The {CODE}[DEFAULT]{CODE_END} heading is obligatory. All other lines are for
exemplification only. (Too much information on the format of the configuration
file can be had from the {LINK_CONFIGLIB}Python
documentation{LINK_END}.){P_END}'''))

out(__('Section heading', '{H3_LEXICONFILE}The Lexicon File{H3_END}'))
out(_('''
{P}The lexicon file is a plain-text list of entries encoded in UTF-8. There
must be one word or phrasal entry per line. The entries must be unique but need
not be sorted.{P_END}

{P}Comment lines are allowed and ignored. They begin with
{CODE}#{CODE_END}.{P_END}

{P}Unix-like systems including Linux and Mac OSX have a suitable lexicon file
located at {CODE}/usr/share/dict/words{CODE_END}, and this is the built-in
default. On Windows systems, you will need to build or access a lexicon file
externally, and there is no built-in default.{P_END}

{P}Any spelling may be followed, after a
{CODE}{OPEN_ANGLE}TAB{CLOSE_ANGLE}{CODE_END} character, by a list of possible
pronunciations, each separated by a comma followed by a space.{P_END}

{P}Substantial open-source files of pronunciations are not common. However, the
{LINK_CMU}CMU Pronouncing Dictionary{LINK_END} can be freely downloaded and
gives General American pronunciations for more than 134,000 words in ARPAbet
transcription.{P_END}

{P_NOTE}You will need to undertake a certain amount of processing to be able to
use the CMU file with Lexitron: the file is encoded in ISO 8859, entries are
entirely in upper case, and variants are given in separate entries.  You may
also prefer to use some phonetic transcription other than ARPAbet. You will
need to address these issues, possibly combining with a separate wordlist that
uses mixed case.{P_END}'''))

out(__('Section heading', '{H3_CSSFILE}The CSS File{H3_END}'))
out(_('''
{P}The CSS file is interpreted by PyQt5 rather than a browser and therefore
needs to conform to the subset of CSS that PyQt5 recognizes. See
{LINK_QT5STYLES}the PyQt5 documentation{LINK_END} for complete details.{P_END}

{P}The following example of a CSS file illustrates both the default style
settings and all the CSS selectors that can usefully be accessed:{P_END}

{PRE_STYLES}'''))

out(__('Section heading', '{H3_LANGUAGES}Language Support{H3_END}'))
out(_('''
{P}Lexitron provides two kinds of support for non-English languages: in the
application’s interface, and in the languages for which WordNet data is
available.{P_END}'''))

out(__('Subsection heading', '{H4_APPLICATIONLANGUAGES}Internationalization of the application interface{H4_END}'))
out(_('''
{P}Lexitron has support for internationalization (I18N) and localization (L10N)
via the {CODE}gettext{CODE_END} system. This means that, if an appropriate L10N
file is available, all prompts, menus, widget labels, messages and so on will
appear in the language of the current locale.{P_END}

{P}Depending on the operating environment, the locale language can be set by
the user globally, and may be able to be set on a per-instance basis. For
example, on a Unix-like system, the following command may launch Lexitron with
a graphical user interface in the French-language locale:{P_END}

{PRE_SETLANGUAGE}

{P_NOTE}Please {LINK_CONTACT}contact the author{LINK_END} if you are
interested in creating a localization of Lexitron.{P_END}'''))

out(__('Subsection heading', '{H4_WORDNETLANGUAGES}WordNet languages{H4_END}'))
out(_('''
{P}WordNet information can be retrieved in a number of languages as well as
English.{P_END}

{P}WordNet internally uses ISO 639-3 three-letter codes to identify languages,
but Lexitron options and interfaces display and accept natural-language names
(or unique abbreviations of them). These are the languages currently
available:{P_END}

{LIST_MULTICOL}
    {ITEM}Basque{ITEM_END}
    {ITEM}Bulgarian{ITEM_END}
    {ITEM}Catalan{ITEM_END}
    {ITEM}Croatian{ITEM_END}
    {ITEM}Danish{ITEM_END}
    {ITEM}Dutch{ITEM_END}
    {ITEM}English{ITEM_END}
    {ITEM}Finnish{ITEM_END}
    {ITEM}French{ITEM_END}
    {ITEM}Galician{ITEM_END}
    {ITEM}Hebrew{ITEM_END}
    {ITEM}Indonesian{ITEM_END}
    {ITEM}Italian{ITEM_END}
    {ITEM}Japanese{ITEM_END}
    {ITEM}Mandarin Chinese{ITEM_END}
    {ITEM}Modern Greek{ITEM_END}
    {ITEM}Norwegian Bokmål{ITEM_END}
    {ITEM}Norwegian Nynorsk{ITEM_END}
    {ITEM}Persian{ITEM_END}
    {ITEM}Polish{ITEM_END}
    {ITEM}Portuguese{ITEM_END}
    {ITEM}Slovenian{ITEM_END}
    {ITEM}Spanish{ITEM_END}
    {ITEM}Standard Arabic{ITEM_END}
    {ITEM}Standard Malay{ITEM_END}
    {ITEM}Swedish{ITEM_END}
    {ITEM}Taiwan Chinese{ITEM_END}
    {ITEM}Thai{ITEM_END}
    {ITEM}Tosk Albanian{ITEM_END}
{LIST_END}

{P}WordNet-derived information is displayed under WordNet “synonym-sets” or
“synsets”, which are used by WordNet internally as labels in a
language-agnostic way. To emphasize their status as WordNet-internal labels,
Lexitron displays synset designators within vertical bars. Thus the following
entry for related words to {CITE}perro{CITE_END} (‘dog’) is displayed in one of
Lexitron’s text-only user interfaces when the language is set to
Spanish:{P_END}

{PRE_SYNSETS}

{P_NOTE}WordNet has a built-in lemmatizer for English only. This means that,
when the language is set to English, you can enter an inflected form such as
{CITE}houses{CITE_END} or {CITE}housed{CITE_END} and see information about
{CITE}house{CITE_END} as a noun and/or a verb as appropriate. The WordNet
interface used by Lexitron does not perform lemmatization in any other
language, so non-English words must be entered in their base or dictionary form
in order to retrieve WordNet-derived information.{P_END}'''))

out(__('Section heading', '{H3_CONSOLEINTER}The Console Interface{H3_END}'))
out(_('''

{P}The console interface can be used interactively (for example, over a network
connection) and is also the basis for non-interactive (possibly scripted) use
of Lexitron. All output goes to the standard output file and can therefore be
redirected in non-interactive use. Commands entered interactively must be
followed by the {CODE}{OPEN_ANGLE}Enter{CLOSE_ANGLE}{CODE_END} or
{CODE}{OPEN_ANGLE}Return{CLOSE_ANGLE}{CODE_END} key.{P_END}

{P}Commands are whole words which may be abbreviated to any unique prefix,
disregarding case. The command <code>?</code> displays the list of available
commands, while <code>=</code> displays information about the current lexicon
file (number of entries, and number of pronunciations excluding and including
variants), as well as the current language for WordNet lookups. All the
remaining commands other than <code>Available</code> and <code>Quit</code>
require an argument.{P_END}

{P}The following screenshot shows the console interface during a session where
the application interface language is English and the WordNet lookup language
is Polish.{P_END}

{IMG_CONSOLE}

{P_NOTE}The argument to the {CODE}-x/--exec{CODE_END} command-line option may
contain multiple commands separated by a semicolon ({CODE};{CODE_END}). Also,
{CODE}-x/--exec{CODE_END} may be given multiple times. However given, Lexitron
will execute all the commands in sequence and then exit.{P_END}'''))

out(__('Section heading', '{H3_TERMINALINTER}The Terminal Interface{H3_END}'))
out(_('''
{P}The terminal interface emulates a 1980s-style “smart” terminal such as the
DEC VT100, with single-keystroke input and cursor-addressed output. Unlike the
{LINK_GRAPHICINTER}graphical user interface{LINK_END}, it does not require the
installation of any modules beyond those in the Python standard library.{P_END}

{P}All commands are invoked by pressing a single key. Commands other than Quit
will then prompt for an argument, which will need to be terminated by pressing
the {CODE}{OPEN_ANGLE}Enter{CLOSE_ANGLE}{CODE_END} or
{CODE}&lt;Return&gt;{CODE_END} key. Where the output exceeds the available
screen space, it is “paged” into smaller chunks, each followed by a prompt
which offers options to scroll up and down or exit.{P_END}

{P}The following screenshot shows the terminal interface during a session where
the application interface language is English and the WordNet lookup language
is Japanese.{P_END}

{IMG_TERMINAL}
'''))

out(__('Section heading', '{H3_GRAPHICINTER}The Graphical Interface{H3_END}'))
out(_('''
{P}The graphical user interface is intended to be self-explanatory. Its exact
appearance will depend on the environment in use, as well as any
{LINK_CSSFILE}CSS file{LINK_END} supplied by the user. The following is a
screenshot of a typical session in the Gnome environment of a Linux-based
operating system, with the French-language version of Lexitron using Spanish
for WordNet lookups, and no user-specified CSS file:{P_END}

{IMG_GUI}
'''))

out(__('Section heading', '{H3_ACKNOWLEDGEMENTS}Acknowledgements{H3_END}'))
out(_('''
{P}With thanks to:{P_END}
{LIST_SQUAREBULLETS}
{ITEM}{LINK_CMU}the CMU Pronouncing Dictionary{LINK_END}{ITEM_END}
{ITEM}{LINK_WORDNET}WordNet{LINK_END}{ITEM_END}
{ITEM}{LINK_OMW}the Open Multilingual WordNet{LINK_END}{ITEM_END}
{LIST_END}
'''))

out(__('Section heading', '{H3_CONTACT}Contact{H3_END}'))
out(_('''
{P}Please contact the author at {CODE}{OPEN_ANGLE}jasoncjohnston at gmail dot
com{CLOSE_ANGLE}{CODE_END}.{P_END}'''))

out(DIV_END)
out(TAIL)

