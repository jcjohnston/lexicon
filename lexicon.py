# lexicon.py jcj 2019-02-20, 2020-01-23, 2020-02-07, 2020-05-10

'''A class to implement a lexicon with methods for lookup of
definitions with examples, synonyms and other related words,
pronunciations, homophones, anagrams, and regular expressions,
using a user-supplied lexicon and/or the facilities of WordNet'''

# Standard-library imports
import sys
import re
import bisect
import unicodedata as ud
from collections import namedtuple, defaultdict, OrderedDict

from my.constants import StrConsts

# WordNet-related stuff (may be unavailable)
WORDNET = False
try:
    from nltk.corpus import wordnet as wn
    from nltk.stem import WordNetLemmatizer
    WORDNET = True
except ImportError:
    pass

if WORDNET:
    wnl = WordNetLemmatizer()
    WordNetInfo = namedtuple('WordNetInfo', 'base, pos, number, info')
    WNPARAMS = namedtuple('WNPARAMS', 'GROUP, EXTENT, LEVEL, OUTTYPE')
    WNG = StrConsts('defs, rels')         # group to which relation belongs
    WNE = StrConsts('head, syns')         # extent of lemmas returned
    WNL = StrConsts('syn, lem, sub, oth') # level from which relation is drawn
    WNKINDS = OrderedDict([
        ('definition',          WNPARAMS(WNG.DEFS, WNE.HEAD, WNL.SYN, list)),
        ('examples',            WNPARAMS(WNG.DEFS, WNE.HEAD, WNL.SYN, list)),
        ('frame_strings',       WNPARAMS(WNG.DEFS, WNE.HEAD, WNL.LEM, list)),
        ('synonyms',            WNPARAMS(WNG.RELS, WNE.SYNS, WNL.OTH, str)),
        ('antonyms',            WNPARAMS(WNG.RELS, WNE.SYNS, WNL.LEM, str)),
        ('pertainyms',          WNPARAMS(WNG.RELS, WNE.SYNS, WNL.LEM, str)),
        ('hypernyms',           WNPARAMS(WNG.RELS, WNE.SYNS, WNL.SUB, str)),
        ('hyponyms',            WNPARAMS(WNG.RELS, WNE.SYNS, WNL.SUB, str)),
        ('part_meronyms',       WNPARAMS(WNG.RELS, WNE.SYNS, WNL.SUB, str)),
        ('part_holonyms',       WNPARAMS(WNG.RELS, WNE.SYNS, WNL.SUB, str)),
        ('substance_meronyms',  WNPARAMS(WNG.RELS, WNE.SYNS, WNL.SUB, str)),
        ('substance_holonyms',  WNPARAMS(WNG.RELS, WNE.SYNS, WNL.SUB, str)),
        ('entailments',         WNPARAMS(WNG.RELS, WNE.SYNS, WNL.SUB, str)),
        ('derivationally_related_forms',
                                WNPARAMS(WNG.DEFS, WNE.HEAD, WNL.LEM, str)),
        ])
    WNCATS = { 'n': 'N', 'v': 'V', 'a': 'Adj', 's': 'Sat', 'r': 'Adv' }

# Constants for busyWait callable
PHASES = 5     # How many times is each entry processed?
INTERVAL = 5   # How often in % is progress notified?
READING, NORMALIZING, SORTING, HASHING, DONE = 0, 1, 2, 3, 4   # The phases

__all__ = ['Lexicon', 'LexiconError']

class LexiconError(Exception):
    pass

class Lexicon:

    def __init__(self, options=None, busyWait=None):
        '''Initialize an object representing a lexicon from a disk file'''
        if not options: options = {}
        self.fileName = options.get('lexicon', '')
        self.caseBlind = options.get('icase')
        self.diacFilter = {}
        if options.get('idiac'):
            self.diacFilter = dict.fromkeys(c for c in range(sys.maxunicode)
                                            if ud.combining(chr(c)))
        self.language = options.get('language', 'eng') if WORDNET else ''
        self.words = []                  # list of sorted, normalized words
        self.refs = defaultdict(list)    # dict from normalized words
                                         # to lists of reference forms
                                         # eg POLISH -> [Polish, polish]
        self.anags = defaultdict(list)   # dict from normalized anagrams
                                         # to lists of anagrammatic forms
                                         # eg abeert -> [beater, berate, rebate]
        self.prons = defaultdict(list)   # spelling -> pronunciations
        self.spells = defaultdict(list)  # pronunciation -> spellings
        self.numLines = self.numProns = self.numVars = 0
        if self.fileName:
            self.readLexicon(self.fileName, busyWait)

    def readLexicon(self, fileName, busyWait):
        '''Read in a lexicon file and initialize various structures'''
        if not busyWait:
            busyWait = lambda phase, percent: None
        try:
            f = open(self.fileName)
        except Exception as err:
            raise LexiconError(err)
        busyWait(READING, 0)
        # Read in a list of lines, without showing any progress.
        # But then use the number of words read in to time progress updates
        lines = [ line.rstrip('\n') for line in f.readlines()
                                    if not line.startswith('#') ]
        self.numLines = len(lines)
        pcPerLine = 100 / (self.numLines * PHASES)   # NB result is a real
        pcDone = pcPerLine * self.numLines   # for the read itself
        # build dict of normalized forms in self.refs
        # and pronunciation-related dictionaries in self.prons and self.spells
        busyWait(NORMALIZING, int(pcDone))
        # we need the unPythonic indexed loop because we change line
        for i in range(len(lines)):
            line = lines[i]
            pcDone += pcPerLine
            if pcDone % INTERVAL < pcPerLine:
                busyWait(NORMALIZING, int(pcDone))
            tabpos = line.find('\t')
            if tabpos < 0:
                tabpos = len(line)
            normal = self.normalized(line[:tabpos], self.caseBlind,
                                     self.diacFilter)
            variants = line[tabpos+1:]
            line = line[:tabpos]
            # store pronunciations
            if variants:
                self.numProns += 1
                variants = variants.split(', ')
                self.numVars += len(variants)
                for variant in variants:
                    if variant not in self.prons[normal]:
                        self.prons[normal].append(variant)
                    self.spells[variant].append(line)
            lines[i] = line
            self.refs[normal].append(line)
        # build sorted list of normalized word forms for lookup
        busyWait(SORTING, int(pcDone))
        self.words = sorted(self.refs)   # includes only the keys
        pcDone += pcPerLine * self.numLines
        # build a separate dictionary of normalized anagram forms
        busyWait(HASHING, int(pcDone))
        for line in lines: 
            pcDone += pcPerLine
            if pcDone % INTERVAL < pcPerLine:
                busyWait(HASHING, int(pcDone))
            hash = self.anagramHash(line)
            self.anags[hash].append(line)
        busyWait(DONE, 100)
        if f:
            f.close()

    def normalized(self, s, caseBlind, diacFilter):
        '''Apply needed transformations to ignore case and/or accents'''
        if caseBlind:
            s = s.casefold()
        if diacFilter:
            s = ud.normalize('NFKD', s)
            s = s.translate(self.diacFilter)
        return s
        
    def anagramHash(self, s):
        '''Create a unique hash for anagram purposes, ignoring
        order, letter-case, and all punctuation. Diacritics
        are ignored only if self.diacFilter is set'''
        # Unfortunately the \w class (Unicode 'word' characters)
        # includes the underscore, so _ must be special-cased
        s = s.replace('_', '')
        # Upper-case the string, remove all characters which are not \w,
        # and sort the result: thus all anagrammatic strings get the same hash
        return ''.join(sorted(re.sub(r'\W', '',
                        self.normalized(s, True, self.diacFilter))))

    def WNInfo(self, word, kinds):
        '''Return a list of WordNetInfo tuples of information about word'''

        def WNNormalized(word):
            '''Return a WordNet-normalized version of word: all lower-case and
            no apostrophes'''
            return word.lower().replace("'", '')

        def addName(dic, key, name):
            '''Create dic[key] as an empty list if necessary and append name
            to it if not already present'''
            if key not in dic:
                dic[key] = []
            lst = dic[key]
            if name not in lst:
                lst.append(name)

        def excludeName(kind, lemma):
            '''Return whether this lemma should be excluded because the kind
            is restricted to strict lemmas of the headword'''
            return ((WNKINDS[kind].EXTENT == WNE.HEAD) and 
                    (lemma.name() not in heads))

        results = []
        heads = set()
        for cat in WNCATS.keys():
            heads.add(wnl.lemmatize(word, cat))
        levelKinds = {}
        for level in (WNL.SYN, WNL.LEM, WNL.SUB):
            levelKinds[level] = [kind for kind in kinds
                                 if WNKINDS[kind].LEVEL == level]
        for synset in wn.synsets(WNNormalized(word), lang=self.language):
            synset_base, synset_pos, synset_number = synset.name().split('.')
            info = OrderedDict()
            # relations defined as synset.RELATION  
            for kind in levelKinds[WNL.SYN]:
                info[kind] = getattr(synset, kind)()
            for lemma in synset.lemmas(lang=self.language):
                # synonyms are a special case: they are simply synset.lemma
                if 'synonyms' in kinds:
                    addName(info, 'synonyms', lemma.name())
                # relations defined as synset.lemma.RELATION
                for kind in levelKinds[WNL.LEM]:
                    if excludeName(kind, lemma):
                        continue
                    for nym in getattr(lemma, kind)():
                        try:
                            name = nym.name()
                        except AttributeError:
                            name = nym
                        addName(info, kind, name)
            # relations defined as synset.RELATION.lemma
            for kind in levelKinds[WNL.SUB]:
                for item in getattr(synset, kind)():
                    for lemma in item.lemmas(lang=self.language):
                        if excludeName(kind, lemma):
                            continue
                        name = lemma.name()
                        addName(info, kind, name)
            # make the output be of the required type
            for key in info.keys():
                if ((WNKINDS[key].OUTTYPE == str) and
                    (type(info[key]) != str)):
                    info[key] = ', '.join(info[key])
                elif ((WNKINDS[key].OUTTYPE == list) and
                    (type(info[key]) != list)):
                    info[key] = [ info[key] ]
            results.append(WordNetInfo(synset_base, WNCATS[synset_pos],
                            synset_number, info))
        return results

### Client-facing definitions follow ###

    @property
    def hasWordNet(self):
        return WORDNET

    @staticmethod
    def languages():
        '''Return a list of the ISO 639-3 codes for the WordNet-supported
        languages.'''
        return wn.langs() if WORDNET else []

    def getLanguage(self):
        '''Return the language for WordNet lookups'''
        return self.language

    def setLanguage(self, language):
        '''Set the language for WordNet lookups if it is supported'''
        if language in self.languages():
            self.language = language

    def stats(self):
        '''Return the number of various things as a tuple'''
        return self.numLines, self.numProns, self.numVars

    def contains(self, word):
        '''Return a list of matching spellings: its main purpose
        is to return a list of different headwords after normalization'''
        word = self.normalized(word, self.caseBlind, self.diacFilter)
        i = bisect.bisect_left(self.words, word)
        if i != len(self.words) and self.words[i] == word:
            return self.refs[word]
        else:
            return []

    def prefixed(self, prefix):
        '''Return a list of words with prefix'''
        prefix = self.normalized(prefix, self.caseBlind, self.diacFilter)
        return [ ' '.join(self.refs[w]) for w in self.words
                    if w.startswith(prefix) ]

    def suffixed(self, suffix):
        '''Return a list of words with suffix'''
        suffix = self.normalized(suffix, self.caseBlind, self.diacFilter)
        return [ ' '.join(self.refs[w]) for w in self.words
                    if w.endswith(suffix) ]

    def definitions(self, word):
        '''Return a list of WordNetInfo tuples for each sense of word.
        Each tuple will contain the definition and list, possibly empty,
        of examples.'''
        if WORDNET:
            word = self.normalized(word, False, self.diacFilter)
            return self.WNInfo(word, [key for key, val in WNKINDS.items()
                                     if val.GROUP == WNG.DEFS])
        else:
            return self.contains(word)

    def related(self, word):
        '''Return a list of WordNetInfo tuples for each sense of word.
        Each tuple will contain possibly empty lists of synonyms etc.'''
        if WORDNET:
            word = self.normalized(word, False, self.diacFilter)
            return self.WNInfo(word, [key for key, val in WNKINDS.items()
                                      if val.GROUP == WNG.RELS])
        else:
            return []

    def pronunciations(self, word):
        '''Return a list of pronunciations of word'''
        return self.prons.get(self.normalized(word, self.caseBlind,
                              self.diacFilter))

    def homophones(self, word):
        '''Return a list of homophones of the word'''
        results = []
        prons = self.prons.get(self.normalized(word, self.caseBlind,
                                               self.diacFilter))
        if prons:
            for pron in prons:
                for variant in self.spells[pron]:
                    if variant not in results:
                        results.append(variant)
        return results

    def anagrams(self, word):
        '''Return a list of anagrams of word, ignoring case and punctuation''' 
        return self.anags.get(self.anagramHash(word), [])

    def regex(self, pattern):
        '''Return list of matching words'''
        # we can normalize case but we can't do anything about diacritics
        flags = re.IGNORECASE if self.caseBlind else 0
        try:
            pattern = re.compile(pattern, flags)
        except Exception as err:   # probably an invalid regex
            raise LexiconError(str(err))
        matches = []
        for word in self.words:
            m = pattern.search(word)
            if m:
                matches.extend(self.refs[word])
        return matches

if __name__ == '__main__':
    print('This module is intended to be imported rather than run standalone')

