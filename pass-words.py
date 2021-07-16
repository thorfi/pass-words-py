#!/usr/bin/env python
#
# The MIT License (MIT)
#
# Copyright (c) 2014-2021 David Goh <david@goh.id.au>
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
#
# Python script to generate correct horse battery staple passwords on Unix
# http://xkcd.com/936/

from random import SystemRandom
import getopt
import itertools
import math
import os
import os.path
import string
import sys

COPYRIGHT = "Copyright (c) 2014 David Goh <david@goh.id.au>"
AUTHOR = "David Goh <david@goh.id.au> - https://goh.id.au/~david/"
SOURCE = "GIT: https://github.com/thorfi/pass-words-py"
LICENSE = "MIT License - https://github.com/thorfi/pass-words-py/blob/master/LICENSE"

DEFAULT_MAX_WORD_LEN = 8
DEFAULT_MIN_WORD_LEN = 4
DEFAULT_WORD_COUNT = 5
DEFAULT_WORD_SEPARATOR = " "

WORDS_SUB_PATHS = (
    "share/dict/words",
    "dict/words",
    "share/words",
    "words",
)
DEFAULT_WORDS_PATHS = set()
for p in os.environ["PATH"].split(":"):
    p = os.path.dirname(p.rstrip(os.path.sep))
    for w in WORDS_SUB_PATHS:
        w_path = os.path.join(p, w)
        if os.path.isfile(w_path):
            DEFAULT_WORDS_PATHS.add(w_path)


def usage_exit(msg=None):
    """Exit with a potential error message."""
    exitcode = 0
    f = sys.stderr if msg else sys.stdout
    if msg is not None:
        print("Error:", msg, file=f)
        exitcode = 1
    print("Usage:", sys.argv[0], "[...]", file=f)
    print(
        """
Python script that generates correct horse battery staple passwords from Unix dictionaries
See https://xkcd.com/936/
 -c n: count n words in password (Default: {})
 -m N: max length of words to use (Default: {})
 -n n: min length of words to use (Default: {})
 -s s: word separator to use (Default: {!r})
 -p /path/to/words: Add this file to look for words in.
    If none specified, file(s) used: {}
 -v: verbose print of more common password entropies for comparison
 -h: print this help
 """.format(
            DEFAULT_WORD_COUNT,
            DEFAULT_MAX_WORD_LEN,
            DEFAULT_MIN_WORD_LEN,
            DEFAULT_WORD_SEPARATOR,
            ":".join(DEFAULT_WORDS_PATHS),
        ),
        file=f,
    )
    sys.exit(exitcode)


def main():
    words_paths = []
    word_count = DEFAULT_WORD_COUNT
    max_word_len = DEFAULT_MAX_WORD_LEN
    min_word_len = DEFAULT_MIN_WORD_LEN
    word_separator = DEFAULT_WORD_SEPARATOR
    verbose = False

    try:
        opts, remainder_args = getopt.getopt(
            sys.argv[1:],
            "p:c:m:n:s:vh",
            [
                "path=",
                "count=",
                "max=",
                "min=",
                "sep=",
                "verbose",
                "help",
            ],
        )
    except getopt.GetoptError as exc:
        usage_exit(str(exc))
        assert False

    for o, a in opts:
        if o in ("-c", "--count"):
            try:
                word_count = int(a)
            except ValueError as exc:
                usage_exit(f"--count={a!r} {str(exc)}")
        elif o in ("-m", "--max"):
            try:
                max_word_len = int(a)
            except ValueError as exc:
                usage_exit(f"--max={a!r} {str(exc)}")
        elif o in ("-n", "--min"):
            try:
                min_word_len = int(a)
            except ValueError as exc:
                usage_exit(f"--min={a!r} {str(exc)}")
        elif o in ("-p", "--path"):
            if not os.path.isfile(a):
                usage_exit(f"--path={a!r} is not a file")
            words_paths.append(a)
        elif o in ("-s", "--sep"):
            word_separator = a
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage_exit()
        else:
            usage_exit(f"unknown option {o} {a!r}")
    if max_word_len < min_word_len:
        usage_exit(f"--max={max_word_len} < --min={min_word_len}")
    min_word_len = DEFAULT_MIN_WORD_LEN

    entropies = []
    if verbose:
        desc_texts = (
            ("ASCII lowercase letters", string.ascii_lowercase),
            ("ASCII letters", string.ascii_letters),
            ("ASCII letters or digits", string.ascii_letters + string.digits),
            ("ASCII printable non whitespace", "".join(string.printable.split())),
        )
        counts = (8, 10, 16, 20)
        for (desc, text), n in itertools.product(desc_texts, counts):
            len_text = len(text)
            choices = len_text ** n
            choices_desc = f"{n:2d}*[{len_text:d} {desc}]"
            entropies.append((choices, choices_desc))

    if not words_paths:
        words_paths = list(DEFAULT_WORDS_PATHS)

    words = set()
    for wp in words_paths:
        with open(wp) as wf:
            for line in (line.strip().lower() for line in wf):
                if min_word_len <= len(line) <= max_word_len:
                    words.add(line)

    def count_choices(len_w, w_count):
        if w_count == 1:
            return len_w
        assert w_count > 1
        return len_w * count_choices(len_w - 1, w_count - 1)

    len_words = len(words)
    choices = count_choices(len_words, word_count)
    choices_desc = (
        f"{word_count:2d}*[{len_words:d} words ({min_word_len:d}-{max_word_len:d} letters) from {':'.join(words_paths)}]"
    )
    entropies.append((choices, choices_desc))
    if len(entropies) > 1:
        print("Bit Entropy comparisons")
    entropies.sort()
    for n, d in entropies:
        log2 = math.log(n, 2) if n else 0
        print(f"{log2:5.1f} bits - {d}")

    random = SystemRandom()
    words = random.sample(list(words), word_count)
    for word in words:
        print(word)

    print(word_separator.join(words))


if __name__ == "__main__":
    main()
