#!/usr/bin/env python
#
# The MIT License (MIT)
# 
# Copyright (c) 2014 David Goh <david@goh.id.au>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 

COPYRIGHT = 'Copyright (c) 2014 David Goh <david@goh.id.au>'
AUTHOR = 'David Goh <david@goh.id.au> - http://goh.id.au/~david/'
SOURCE = 'GIT: http://github.com/thorfi/pass-words-py'
LICENSE = 'MIT License - https://github.com/thorfi/pass-words-py/blob/master/LICENSE'

from random import SystemRandom
import getopt
import math
import os
import os.path
import string
import sys

DEFAULT_MAX_WORD_LEN = 8
DEFAULT_MIN_WORD_LEN = 4
DEFAULT_WORD_COUNT = 5
DEFAULT_WORD_SEPARATOR = '-'

WORDS_SUBPATHS = ['share/dict/words', 'dict/words', 'share/words', 'words', ]
DEFAULT_WORDS_PATHS = []
for p in os.environ['PATH'].split(':'):
    p = p.rstrip(os.path.sep)
    p = os.path.dirname(p)
    for w in WORDS_SUBPATHS:
        wp = os.path.join(p, w)
        if not os.path.isfile(wp): continue
        if wp in DEFAULT_WORDS_PATHS: continue
        DEFAULT_WORDS_PATHS.append(wp)

def main():

    words_paths = DEFAULT_WORDS_PATHS
    word_count = DEFAULT_WORD_COUNT
    max_word_len = DEFAULT_MAX_WORD_LEN
    min_word_len = DEFAULT_MIN_WORD_LEN

    random = SystemRandom()
    #random.seed(int(time.time() * 1000) ^ os.getpid())
    words = set()
    for wp in words_paths:
        wf = open(wp)
        for line in wf.xreadlines():
            l = line.strip().lower()
            len_l = len(l)
            if len_l > max_word_len: continue
            if len_l < min_word_len: continue
            words.add(l)
        wf.close()

    len_words = len(words)
    def count_choices(len_words, word_count):
        if word_count == 1: return len_words
        assert word_count > 1
        return len_words * count_choices(len_words - 1, word_count - 1)

    choices = count_choices(len_words, word_count)
    choices_desc = '%2d/%d words (%d-%d letters) from %s' % (
        word_count, len_words, min_word_len, max_word_len,
        ':'.join(words_paths), )

    entropies = []
    ascii_printable_non_whitespace = ''.join(string.printable.split())
    for (desc, text, ) in (
        ('ASCII lowercase letters', string.ascii_lowercase, ),
        ('ASCII letters', string.ascii_letters, ),
        ('ASCII letters or digits', string.letters + string.digits, ),
        ('ASCII printable non whitespace', ascii_printable_non_whitespace, ),
        ):
        for n in (8, 10, 16, 20, ):
            len_text = len(text)
            entropies.append(('%2d/%d %s' % (
                n, len_text, desc, ), len_text ** n, ))

    entropies.append((choices_desc, choices))
    for (d, n, ) in entropies:
        print '%5.1f bits - %s' % (math.log(n, 2), d, )

    words = random.sample(words, word_count)
    for word in words:
        print word

    print '-'.join(words)


if __name__ == '__main__':
    main()
