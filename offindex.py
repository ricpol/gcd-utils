#! python
# -*- coding: utf-8 -*-

# (c) 2017 - Riccardo Polignieri
# license: FreeBSD
# https://github.com/ricpol/gcd-utils

"""
This is a little toolkit to help you with your offline GCD indexing.
If you don't know how offline indexing works, start by reading this:
http://docs.comics.org/wiki/Indexing_Offline
This script allows you 
- to convert a TSV (tab-separated) index file donwnloaded from GCD 
  into a human-readable TXT file;
- to make a new, empty TXT human-readable file ready to use as a grid 
  for your own offline indexes;
- to convert your TXT file(s) back into TSV files ready to be uploaded 
  on GCD web interface.
The intended usage is quite simple: just drop this script in a directory 
with all your TSV and/or TXT files. You may specify alternative in/out 
directories if you prefer. You may also toy a little with the global 
variables of the script. 
Then, just double click and follow the interactive interface. 
For more help, see https://github.com/ricpol/gcd-utils
"""

from __future__ import print_function, unicode_literals

ISSUE_FIELDS = (
 #               name             display?  order    default
 #         (do NOT change this!)
                ('number',          True,     1,     ''), 
                ('volume',          False,    2,     ''), 
                ('ind-publisher',   True,     4,     ''),
                ('brand',           True,     5,     ''),
                ('pub-date',        True,     6,     ''), 
                ('key-date',        True,     7,     ''),
                ('ind-frequency',   True,     9,     ''),
                ('price',           True,    10,     ''),
                ('page-count',      True,    11,     '1'),
                ('editing',         True,    12,     ''), 
                ('isbn',            False,   13,     'None'),
                ('notes',           False,   16,     ''),
                ('barcode',         False,   14,     'None'),
                ('on-sale-date',    False,    8,     ''),
                ('issue-title',     False,    3,     ''), 
                ('keywords',        False,   15,     ''), 
               )

SEQUENCE_FIELDS = (
 #               name             display?  order    default
 #         (do NOT change this!)
                ('title',           True,      1,    ''),
                ('type',            True,      2,    ''),
                ('feature',         True,      3,    ''),
                ('pages',           True,      5,    '1.000'),
                ('script',          True,      6,    'None'), 
                ('pencils',         True,      7,    'None'),
                ('inks',            True,      8,    'None'),
                ('colors',          True,      9,    'None'),
                ('letters',         True,     10,    'None'),
                ('editing',         False,    11,    'None'), 
                ('genre',           True,      4,    ''),
                ('characters',      False,    13,    ''),
                ('job-number',      False,    12,    ''),
                ('reprint-notes',   False,    17,    ''),
                ('synopsis',        False,    14,    ''), 
                ('notes',           False,    16,    ''),
                ('keywords',        False,    15,    ''), 
                   )

ALLOWED_TYPES = (
 #  real name (do NOT change)                       short form
    ('activity',                                    ''),
    ('advertisement',                               ''),
    ('blank page(s)',                               'blank'),
    ('cartoon',                                     ''),
    ('character profile',                           ''),
    ('comic story',                                 ''),
    ('cover',                                       ''),
    ('cover reprint (on interior page)',            'cover reprint'),
    ('credits, title page',                         'credits'),
    ('foreword, introduction, preface, afterword',  'foreword'),
    ('illustration',                                ''),
    ('insert or dust jacket',                       ''),
    ('letters page',                                'letters'),
    ('photo story',                                 ''),
    ('promo (ad from the publisher)',               'promo'),
    ('public service announcement',                 ''),
    ('recap',                                       ''),
    ('statement of ownership',                      ''),
    ('table of contents',                           'contents'),
    ('text article',                                'article'),
    ('text story',                                  ''),
        )

ALLOWED_GENRES = (
 #  real name (do NOT change)                       short form
    ('adventure',                                   ''),
    ('drama',                                       ''),
    ('humor',                                       ''),
    ('non-fiction',                                 ''),
    ('advocacy',                                    ''),
    ('animal',                                      ''),
    ('anthropomorphic-funny animals',               ''),
    ('aviation',                                    ''),
    ('biography',                                   ''),
    ('car',                                         ''),
    ('children',                                    ''),
    ('crime',                                       ''),
    ('detective-mystery',                           ''),
    ('domestic',                                    ''),
    ('erotica',                                     ''),
    ('fantasy-supernatural',                        'fantasy'),
    ('fashion',                                     ''),
    ('historical',                                  ''),
    ('history',                                     ''),
    ('horror-suspense',                             'horror'),
    ('jungle',                                      ''),
    ('martial arts',                                ''),
    ('math & science',                              ''),
    ('medical',                                     ''),
    ('military',                                    ''),
    ('nature',                                      ''),
    ('religious',                                   ''),
    ('romance',                                     ''),
    ('satire-parody',                               ''),
    ('science fiction',                             'sf'),
    ('sports',                                      ''),
    ('spy',                                         ''),
    ('superhero',                                   ''),
    ('sword and sorcery',                           ''),
    ('teen',                                        ''),
    ('war',                                         ''),
    ('western-frontier',                            'western'),
        )


# path to default output directory (relative to this script file)
OUTPUT_DIR = '.'

# path to default input directory (relative to this script file)
INPUT_DIR = '.'

# put this in blank line inside a sequence 
# to skip that sequence when generating output
SKIP_WORD = '--SKIP'

# everything after this mark will be ignored
COMMENT_MARK = '//'

# default name for new (empty) indexes
EMPTY_DEFAULT_NAME = 'empty.txt'

MIN_VALID_YEAR = 1930 
MAX_VALID_YEAR = 2018 # allow some margin...

# your editor's encoding of choice - utf-8 *recommended*
ENCODING = 'utf-8'

# ======================================================================
# you should not edit below this point!
# ======================================================================
import os, os.path
import sys
if sys.version_info.major == 2:
    from io import open
    input = raw_input
    #FIXME can't remember a better way to do this in py2
    import codecs
    writer = codecs.getwriter('utf8') # at least we won't crash 
    sys.stdout = writer(sys.stdout)   # on non-ascii paths in py2

PADDING = 15
SEQ_DELIMITER = '='*30
ERROR_FILENAME = 'ERRORS.txt'
HERE = os.path.abspath(os.path.dirname(__file__))

def validate_keydate(data):
    err = 'invalid date: ' + data
    if data == '': 
        return '', data
    if len(data) != 10:
        return err, data
    try: 
        y, m, d = data.split('-')
    except ValueError: 
        return err, data
    try: 
        if not (MIN_VALID_YEAR <= int(y) <= MAX_VALID_YEAR):
            return err, data
    except ValueError: 
        return err, data
    try:
        if not (0 <= int(m) <= 12):
            return err, data
    except ValueError:
        return err, data
    try:
        if not (0 <= int(d) <= 31):
            return err, data
    except ValueError:
        return err, data
    if m == '00' and d != '00':
        return err, data
    return '', data

def validate_pagecount(data):
    err = 'invalid page count: ' + data
    data = data.replace('?', '')
    try:
        float(data)
    except ValueError:
        return err, data
    return '', data

def validate_type(data):
    err = 'invalid type: ' + data
    if data == '':
        return err + '<none>', data
    data = data.lower()
    for name, short in ALLOWED_TYPES:
        name = name.lower()
        short = short.lower()
        if data == name:
            return '', data
        elif data == short:
            return '', name
    return err, data

def validate_genres(data):
    err = 'invalid genre(s): ' + data
    if data == '':
        return '', data
    raw_genres = data.split(';')
    genres = []
    for g in raw_genres:
        found = False
        g = g.strip().lower()
        for name, short in ALLOWED_GENRES:
            name = name.lower()
            short = short.lower()
            if g == short or g == name:
                genres.append(name)
                found = True
                break
        if not found:
            return err, data
    return '', '; '.join(genres)

VALIDATORS = {'key-date'   : validate_keydate,
              'page-count' : validate_pagecount,
              'pages'      : validate_pagecount,
              'type'       : validate_type,
              'genre'      : validate_genres,   
            }


class OfflineIndexer:
    def __init__(self):
        self.in_dir = os.path.join(HERE, INPUT_DIR)
        self.out_dir = os.path.join(HERE, OUTPUT_DIR)
        self.srt_issue_fields = sorted(ISSUE_FIELDS, key=lambda i:i[2])
        self.srt_seqs_fields = sorted(SEQUENCE_FIELDS, key=lambda i:i[2])

    def set_in_dir(self, d):
        d = os.path.join(HERE, d)
        if os.path.exists(d):
            self.in_dir = d
            return True
        return False

    def set_out_dir(self, d):
        d = os.path.join(HERE, d)
        if os.path.exists(d):
            self.out_dir = d
            return True
        return False

    def _parse_tsv_line(self, line, is_issue=True):
        fields = ISSUE_FIELDS if is_issue else SEQUENCE_FIELDS
        data = dict(zip([i[0] for i in fields], line[:-1].split('\t')))
        fields = self.srt_issue_fields if is_issue else self.srt_seqs_fields
        data_fields = []     # fields with some data to show
        no_data_fields = []  # fields with no data
        for name, _disp, _order, _def in fields:
            if data[name]:
                data_fields.append(name.ljust(PADDING) + data[name])
            else:
                no_data_fields.append(name)
        return data_fields, no_data_fields

    def tsv2txt(self):
        """Converts all .tsv index files found in the input directory 
           into human-readable .txt files.
        """
        in_files = [i for i in os.listdir(self.in_dir) if i.endswith('.tsv')]
        if not in_files:
            print('No ".tsv" files found in', self.in_dir)
        for f in in_files:
            print('working on', f)
            with open(os.path.join(self.in_dir, f), 
                      'r', encoding='utf-8') as in_file:
                out_path = os.path.join(self.out_dir, f[:-3]+'txt')
                with open(out_path, 'a', encoding='utf-8') as out_file:
                    # issue fields parsing
                    print(COMMENT_MARK, 'issue data:', file=out_file)
                    first = in_file.readline()
                    data, no_data = self._parse_tsv_line(first, True)
                    print('\n'.join(data), file=out_file)
                    print(COMMENT_MARK, 'other fields:', 
                          ' '.join(no_data), file=out_file)
                    print(SEQ_DELIMITER, file=out_file)
                    # sequences data output
                    print(COMMENT_MARK, 'sequences data:', file=out_file)
                    for line in in_file:
                        data, no_data = self._parse_tsv_line(line, False)
                        print('\n'.join(data), file=out_file)
                        print(COMMENT_MARK, 'other fields:', 
                              ' '.join(no_data), file=out_file)
                        print(SEQ_DELIMITER, file=out_file)

    def _sequence2tsvline(self, seq_lines, is_issue=True):
        "Converts a single sequence to a single tsv line."
        fields = ISSUE_FIELDS if is_issue else SEQUENCE_FIELDS
        field_names = [i[0] for i in fields]
        data = {}
        errors = []
        tsvline = []
        for raw_line in seq_lines:
            if raw_line.startswith(SKIP_WORD):
                return '', ''
            line = raw_line.split(COMMENT_MARK)[0]
            line = line.strip()
            if line:
                k = line[:PADDING].strip()
                if k in field_names:
                    v = line[PADDING:].strip()
                    try:
                        data[k] += v
                    except KeyError:
                        data[k] = v
                else:
                    err = 'invalid line: ' + line
                    errors.append(err)
        for name, disp, ord_, default in fields:
            try:
                data[name]
            except KeyError:
                tsvline.append(default)
                continue
            try:
                err, valid = VALIDATORS[name](data[name])
                tsvline.append(valid)
                if err:
                    errors.append(err)
            except KeyError:
                tsvline.append(data[name])
        return '\t'.join(tsvline), '\n'.join(errors)

    def _file2tsvfiles(self, f):
        "Converts a single txt file in 2 separate (issue/seqs) tsv files."
        errors = ''
        with open(os.path.join(self.in_dir, f), 
                      'r', encoding=ENCODING) as in_file:
            seq_lines = []
            # generating separate issue file output
            out_path = os.path.join(self.out_dir, f[:-4]+'_issue.tsv')
            with open(out_path, 'a', encoding='utf-8') as out_file:
                for line in in_file:
                    if line.startswith(SEQ_DELIMITER):
                        tsvline, err = self._sequence2tsvline(seq_lines, True)
                        if tsvline:
                            print(tsvline, file=out_file)
                        if err:
                            errors += '-- file %s, issue data:\n%s\n' % (f, err)
                        seq_lines = []
                        break
                    else:
                        seq_lines.append(line)
            # generating sequences file output
            out_path = os.path.join(self.out_dir, f[:-4]+'_seqs.tsv')
            seq_no = 0
            with open(out_path, 'a', encoding='utf-8') as out_file:
                for line in in_file:
                    if line.startswith(SEQ_DELIMITER):
                        tsvline, err = self._sequence2tsvline(seq_lines, False)
                        if tsvline:
                            print(tsvline, file=out_file)
                        if err:
                            errors += \
                                '-- file %s, seq. %i:\n%s\n' % (f, seq_no, err)
                        seq_lines = []
                        seq_no += 1
                    else:
                        seq_lines.append(line)
        return errors

    def txt2tsv(self):
        """Converts all .txt index files found in the input directory 
           into .tsv files ready for uploading on GCD. 
           Outputs an error log file if errors were found.
        """
        in_files = [i for i in os.listdir(self.in_dir) if i.endswith('.txt')]
        try:
            in_files.remove(ERROR_FILENAME)
        except ValueError:
            pass
        if not in_files:
            print('No ".txt" files found in', self.in_dir)
        errors = ''
        for f in in_files:
            print('working on', f)
            errors += self._file2tsvfiles(f)
        if errors:
            with open(os.path.join(self.out_dir, ERROR_FILENAME), 
                      'a', encoding='utf-8') as out_file:
                print(errors, file=out_file)
            print('\nErrors were found.',
                  'See %s before importing outputs in gcd!' % ERROR_FILENAME)

    def make_empty(self, empty_seqs=10):
        """Generates a new empty index file. 
           empty_seqs: how many empty sequences (defaults to 10).
        """ 
        with open(os.path.join(self.out_dir, EMPTY_DEFAULT_NAME), 
                  'a', encoding='utf-8') as out_file:
            # issue data output
            print(COMMENT_MARK, 'issue data:', file=out_file)
            fields = sorted(ISSUE_FIELDS, key=lambda i:i[2])
            others = []
            for name, display, order, default in fields:
                if not default:
                    default = '<replace this>'
                if display:
                    print(name.ljust(PADDING), default, file=out_file, sep='')
                else:
                    others.append(name)
            print(COMMENT_MARK, 'other allowed fields:', file=out_file)
            print(COMMENT_MARK, ' '.join(others), file=out_file)
            print(SEQ_DELIMITER, file=out_file)
            # sequences data output
            print(COMMENT_MARK, 'sequences data:', file=out_file)
            fields = sorted(SEQUENCE_FIELDS, key=lambda i:i[2])
            for _ in range(empty_seqs): 
                others = []
                for name, display, order, default in fields:
                    if not default:
                        default = '<replace this>'
                    if display:
                        print(name.ljust(PADDING), default, file=out_file, sep='')
                    else:
                        others.append(name)
                print(COMMENT_MARK, 'other fields:', file=out_file)
                print(COMMENT_MARK, ' '.join(others), file=out_file)
                print(SEQ_DELIMITER, file=out_file)


def main():
    o = OfflineIndexer()
    print('GCD offline index toolkit.')
    while True:
        print('--------------------------------------------------')
        print('[1] make empty index file')
        print('[2] convert TSV > TXT        [3] convert TXT > TSV')
        print('[4] change input dir         [5] change output dir')
        print('[h] display help             [q] exit program')
        choice = input('select: (default [3])').strip()
        if choice == '1':
            o.make_empty()
        elif choice == '2':
            o.tsv2txt()
        elif choice == '4':
            print('Current input dir:', o.in_dir)
            print('Insert new input dir (relative to %s)' % HERE)
            new_dir = input('> ').strip()
            if new_dir and not o.set_in_dir(new_dir):
                print("Can't set new directory (maybe it does not exist?)")
            else:
                print('Current input dir:', o.in_dir)
        elif choice == '5':
            print('Current output dir:', o.out_dir)
            print('Insert new output dir (relative to %s)' % HERE)
            new_dir = input('> ').strip()
            if new_dir and not o.set_out_dir(new_dir):
                print("Can't set new directory (maybe it does not exist?)")
            else:
                print('Current output dir:', o.out_dir)
        elif choice == 'h':
            print(__doc__)
        elif choice == 'q':
            sys.exit(0)
        else:               # default
            o.txt2tsv()


if __name__ == '__main__':
    main()
