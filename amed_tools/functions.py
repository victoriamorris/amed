#  -*- coding: utf8 -*-

import argparse
from collections import OrderedDict
import datetime
from gc import set_threshold, collect
import glob
from locale import setlocale, LC_ALL
import os
import  re
from sys import exit, argv
import unicodedata
from amed_tools.logs import *

# Set locale to assist with sorting
setlocale(LC_ALL, '')

# Set threshold for garbage collection (helps prevent the program run out of memory)
set_threshold(400, 5, 5)

# ====================
#      Constants
# ====================

ACCESSION_NUMBER = 0

ARGS = {
    'i': lambda parser: parser.add_argument('-i', metavar='<input_file>', required=True, action='store', type=str,
                                            nargs=1, help='path to input file'),
    'i+': lambda parser: parser.add_argument('-i', metavar='<input_file>', required=True, action='store', type=str,
                                             nargs='+', help='path to input file(s)'),
    'o': lambda parser: parser.add_argument('-o', metavar='<output_file>', required=True, action='store', type=str,
                                            nargs=1, help='path to output file'),
    'c': lambda parser: parser.add_argument('-c', metavar='<config_file>', required=True, action='store', type=str,
                                            nargs=1, help='path to config file'),
}

OPTS = OrderedDict([
    ('debug', ['Debug mode', False]),
    ('help', ['Show help message and exit', False]),
])


class AMEDError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, value):
        logging.error(str(value))
        self.value = value

    def __str__(self):
        return repr(self.value)


class AMED:

    def __init__(self, name: str, summary: str, args: list) -> None:
        self.name = name
        self.summary = summary
        self.info()
        self.parser = argparse.ArgumentParser(prog=name)
        for a in args:
            ARGS[a](self.parser)
        self.parser.add_argument('--debug', required=False, action='store_true', help='debug mode'),

    def __repr__(self) -> str:
        return (f'========================================\n{self.name}\n'
                f'========================================\n{self.summary}\n')

    def info(self) -> None:
        logging.info(self.name)
        print(repr(self))

    def parse_args(self, args_to_parse) -> argparse.Namespace:
        if len(args_to_parse) == 0:
            self.parser.print_help()
            logging.info('No options set')
            date_time_exit(message='Exiting')
        args = self.parser.parse_args()
        logging.debug(f'Command-line arguments: {repr(args)}')
        if args.debug:
            logger.setLevel(logging.DEBUG)
            logging.info('Logging level set to DEBUG')
        return args


def check_file_location(to_check, role):
    for file in glob.glob(to_check):
        file = re.sub(r'[\\]+', '\\\\', file)
        if not os.path.isfile(file):
            raise AMEDError(f'Error: Could not locate {role} at {str(file)}')


def log_print(message: str = '', level=logging.INFO, end='\n') -> None:
    logging.log(level, message)
    print(message, end=end)


def date_time_message(message: str = '') -> None:
    """Function to print a message, followed by the current date and time"""
    if message != '':
        logging.info(message)
        print('\n\n{} ...\n----------------------------------------'.format(message))
    print(str(datetime.datetime.now()))


def date_time_exit(message: str = 'All processing complete', prompt: bool = False) -> None:
    """Function to exit the program after displaying the current date and time"""
    date_time_message(message)
    if prompt:
        input('\nPress [Enter] to exit ...')
    exit()


# ====================
#      Constants
# ====================


BRACKETS = [('[', ']'), ('(', ')'), ('{', '}')]

RE_HTML_REMOVE = re.compile(
    r'</?(ce:)?(alt|alt-text|attrib|bold|cross-ref|cross-out|disp-quote|display|ext-link|figure|glyph|'
    r'inf|inter|inter-ref|italic|link|ref|sc|small-caps|sub|sup|ul|underline|x|xlink)>')
RE_HTML_SPACE = re.compile(r'</?(ce:)?(abstract-sec|div|hsp|inline-formula|inline-graphic|item|label|li|list|list-item|'
                           r'monospace|para|ol|sec|section|section-title|simple-para|space|title)>')

RE_SMART_DOUBLE_QUOTES_UNICODE = re.compile(r'[\u201C\u201D\u201E\u201F\u275D\u275E\u301D\u301E\u301F\uFF02]')
RE_SMART_SINGLE_QUOTES_UNICODE = re.compile(r'[\u2018\u2019\u201A\u201B\u275B\u275C\u275F]')

SUPERSCRIPTS = {
    '^+': '\u207A',
    '^-': '\u207B',
    '^=': '\u207C',
    '^(': '\u207D',
    '^)': '\u207E',
    '^n': '\u207F',
    '^o': '\u00B0',
    '^0': '\u2070',
    '^i': '\u2071',
    '^1': '\u00B9',
    '^2': '\u00B2',
    '^3': '\u00B3',
    '^4': '\u2074',
    '^5': '\u2075',
    '^6': '\u2076',
    '^7': '\u2077',
    '^8': '\u2078',
    '^9': '\u2079',
}

SUBSCRIPTS = {
    '~.': '.',
    '~+': '\u208A',
    '~-': '\u208B',
    # '~0': '\u2080',
    # '~1': '\u2081',
    # '~2': '\u2082',
    # '~3': '\u2083',
    # '~4': '\u2084',
    # '~5': '\u2085',
    # '~6': '\u2086',
    # '~7': '\u2087',
    # '~8': '\u2088',
    # '~9': '\u2089',
    '~=': '\u208C',
    '~(': '\u208D',
    '~)': '\u208E',
    '~a': '\u2090',
    '~e': '\u2091',
    '~o': '\u2092',
    '~x': '\u2093',
}


# ====================
#    Functions for
#   cleaning strings
# ====================


def normalize_space(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip()


def clean(s: str) -> str:
    s = re.sub(r'^[\uFEFF]+', '', s)
    s = re.sub(r'[\u0020\u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFEFF]+', ' ', s)

    s = re.sub(r'[\u002D\u2010-\u2015]', '-', s)
    s = s.replace('@@@', ', ').replace('//', ', ')
    s = re.sub(r'([\.:;,]),+', r'\1', s)
    s = re.sub(r'\.{3,}', '\u2026', s)
    s = re.sub(r'\.\.+,', '.', s)
    s = normalize_space(s)
    # Convert superscript and subscript shorthands to Unicode equivalents
    for super in SUPERSCRIPTS:
        s = s.replace(super, SUPERSCRIPTS[super])
    for sub in SUBSCRIPTS:
        s = s.replace(sub, SUBSCRIPTS[sub])
    # Replace quotation marks
    s = RE_SMART_DOUBLE_QUOTES_UNICODE.sub('"', s)
    s = RE_SMART_SINGLE_QUOTES_UNICODE.sub('\'', s)
    # Remove space around brackets
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\s+\)', ')', s)
    s = normalize_space(s)
    return unicodedata.normalize('NFC', s)


def text_wrap(s: str) -> str:
    if len(s) < 70:
        return s
    while re.search(r'[^ ](?=.{,65}><)[^ ]{64,}', s) and '><' in s:
        s = re.sub(r'[^ ](?=.{,65}><)[^ ]{64,}', lambda m: m.group().replace('><', '> <', 1), s)
    while re.search(r'[^ ]{65,}', s):
        s = re.sub(r'([^ ]{65})([^ ])', r'\1 \2', s)
    words = s.split(' ')
    i, j = 0, 0
    s = ''
    while j < len(words):
        while len(' '.join(words[i:j])) < 70:
            j += 1
            if j - 1 == len(words):
                break
        j -= 1
        s += '     ' + ' '.join(words[i:j]) + ' \n'
        i = j
    return s.strip()


def clean_html(s: str) -> str:
    if s is None or not s: return ''
    s = clean(s)
    s = re.sub(
        r'<ce:display>\s*(<ce:figure>\s*(<ce:link>\s*</ce:link>)?\s*</ce:figure>)?\s*</ce:display>'
        r'|<inline-graphic>\s*<inline-graphic>',
        ' [Image not shown] ', s)
    s = re.sub(r'<(ce:)?sup>', '^', s)
    s = re.sub(r'<(ce:)?(sub|inf)>', '~', s)
    s = RE_HTML_SPACE.sub(' ', s)
    s = RE_HTML_REMOVE.sub('', s)
    if '<p>' in s and '</p>' in s:
        s = s.replace('<p>', '').replace('</p>', '')
    s = re.sub(r'<inter-ref locator="([^"]+)" locator-type="urn">', r'\1', s)
    # Add colons and space after subheadings
    s = re.sub(
        r'[\.:]?\s*(Abstract|Analysis|Background|Conclusion\(?s?\)?|Design'
        r'|Highlights|Intervention\(?s?\)?|Introduction|'
        r'M[e\u00E9]thode?\(?s?\)?|Objectives?|Patient\(?s?\)?|Patient\(?s?\)? and method\(?s?\)?|'
        r'Purpose|R[e\u00E9]sult(?:at)?\(?s?\)?|Resumen|Setting|Summary):?\s*(?=[A-Z]|\u2022)',
        r'. \1: ', s).replace(': .', ':').lstrip('.').strip()
    # Add square brackets around Formula Not Shown
    s = s.replace(' Formula Not Shown ', ' [Formula Not Shown] ')
    return clean(s)


def name_format(name):
    if ',' not in name:
        return name
    surname, forename = name.rsplit(',',1)
    forename = re.sub(r'(\p{Upper})\s+(?=\p{Upper})', r'\1',
                      re.sub(r'(\p{Upper})(\p{Lower}+|[\.\-])', r'\1', forename))
    return surname + forename


def get_accession_number() -> int:
    accession_start = input('Please enter the starting accession number: ')
    try:
        accession_start = int(accession_start)
    except:
        accession_start = ''
    while not isinstance(accession_start, int):
        accession_start = input('Sorry, your input was not a valid integer.\n'
                                'Please enter the starting accession number: ').strip()
        try:
            accession_start = int(accession_start)
        except:
            accession_start = ''
    return accession_start
