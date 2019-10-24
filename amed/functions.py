#  -*- coding: utf8 -*-

"""Functions used within amed_tools."""

# Import required modules
import csv
import datetime
import fileinput
import gc
import getopt
import html
import locale
import os
import regex as re
import string
import sys
import unicodedata
from collections import OrderedDict

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'

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
#       Classes
# ====================


class FilePath:
    def __init__(self, function='input', path=None):
        self.function = function
        self.path = path
        if path:
            self.set_path(path)
        else:
            self.folder, self.filename, self.ext = '', '', ''

    def set_path(self, path):
        self.path = path
        self.folder, self.filename, self.ext = check_file_location(self.path, self.function, '.txt',
                                                                   'output' not in self.function)


# ====================
#  General Functions
# ====================


def date_time(message=None):
    if message:
        print('\n\n{} ...'.format(message))
    print('----------------------------------------')
    print(str(datetime.datetime.now()))


def message(s) -> str:
    """Function to convert OPTIONS description to present tense"""
    if s == 'Exit program': return 'Shutting down'
    return s.replace('Prepare', 'Preparing').replace('Process', 'Processing')


def date_time_exit(message='All processing complete'):
    date_time(message=message)
    sys.exit()


def exit_prompt(message=None):
    """Function to exit the program after prompting the use to press Enter"""
    if message: print(str(message))
    input('\nPress [Enter] to exit...')
    sys.exit()


def check_file_location(file_path, function, file_ext='', exists=False):
    """Function to check whether a file exists and has the correct file extension"""
    folder, file, ext = '', '', ''
    if file_path == '':
        exit_prompt('Error: Could not parse path to {} file'.format(function))
    try:
        file, ext = os.path.splitext(os.path.basename(file_path))
        folder = os.path.dirname(file_path)
    except:
        exit_prompt('Error: Could not parse path to {} file'.format(function))
    if file_ext != '' and ext != file_ext:
        exit_prompt('Error: The {} file should have the extension {}'.format(function, file_ext))
    if exists and not os.path.isfile(os.path.join(folder, file + ext)):
        exit_prompt('Error: The specified {} file cannot be found'.format(function))
    return folder, file, ext


# ====================
#    Functions for
#   cleaning strings
# ====================


def clean(string):
    string = re.sub(r'[\u0020\u00A0\u1680\u2000-\u200A\u202F\u205F\u3000]+', ' ', string)
    string = re.sub(r'[\u002D\u2010-\u2015]', '-', string)
    string = string.replace('@@@', ', ').replace('//', ', ')
    string = re.sub(r'([\.:;,]),+', r'\1', string)
    string = re.sub(r'\.{3,}', '\u2026', string)
    string = re.sub(r'\.\.+,', '.', string)
    string = re.sub(r' +', ' ', string).strip()
    # Convert superscript and subscript shorthands to Unicode equivalents
    for s in SUPERSCRIPTS:
        string = string.replace(s, SUPERSCRIPTS[s])
    for s in SUBSCRIPTS:
        string = string.replace(s, SUBSCRIPTS[s])
    # Replace quotation marks
    string = RE_SMART_DOUBLE_QUOTES_UNICODE.sub('"', string)
    string = RE_SMART_SINGLE_QUOTES_UNICODE.sub('\'', string)
    # Remove space around brackets
    string = re.sub(r'\(\s+', '(', string)
    string = re.sub(r'\s+\)', ')', string)
    string = re.sub(r' +', ' ', string).strip()
    return unicodedata.normalize('NFC', string)


def text_wrap(string):
    if len(string) < 70: return string
    while re.search(r'[^ ](?=.{,65}><)[^ ]{64,}', string) and '><' in string:
        string = re.sub(r'[^ ](?=.{,65}><)[^ ]{64,}', lambda m: m.group().replace('><', '> <', 1), string)
    while re.search(r'[^ ]{65,}', string):
        string = re.sub(r'([^ ]{65})([^ ])', r'\1 \2', string)
    words = string.split(' ')
    i, j = 0, 0
    string = ''
    while j < len(words):
        while len(' '.join(words[i:j])) < 70:
            j += 1
            if j - 1 == len(words):
                break
        j -= 1
        string += '     ' + ' '.join(words[i:j]) + ' \n'
        i = j
    return string.strip()


def clean_html(string):
    if string is None or not string: return ''
    string = clean(string)
    string = re.sub(
        r'<ce:display>\s*(<ce:figure>\s*(<ce:link>\s*</ce:link>)?\s*</ce:figure>)?\s*</ce:display>|<inline-graphic>\s*<inline-graphic>',
        ' [Image not shown] ', string)
    string = re.sub(r'<(ce:)?sup>', '^', string)
    string = re.sub(r'<(ce:)?(sub|inf)>', '~', string)
    string = RE_HTML_SPACE.sub(' ', string)
    string = RE_HTML_REMOVE.sub('', string)
    if '<p>' in string and '</p>' in string:
        string = string.replace('<p>', '').replace('</p>', '')
    string = re.sub(r'<inter-ref locator="([^"]+)" locator-type="urn">', r'\1', string)
    # Add colons and space after subheadings
    string = re.sub(
        r'[\.:]?\s*(Abstract|Analysis|Background|Conclusion\(?s?\)?|Design|Highlights|Intervention\(?s?\)?|Introduction|'
        r'M[e\u00E9]thode?\(?s?\)?|Objectives?|Patient\(?s?\)?|Patient\(?s?\)? and method\(?s?\)?|'
        r'Purpose|R[e\u00E9]sult(?:at)?\(?s?\)?|Resumen|Setting|Summary):?\s*(?=[A-Z]|\u2022)',
        r'. \1: ', string).replace(': .', ':').lstrip('.').strip()
    # string = re.sub(r'\.?\s*(Abstract|Analysis|Background|Conclusion\(?s?\)?|Design|Intervention\(?s?\)?|Introduction|'
    #                r'M[e\u00E9]thode?\(?s?\)?|Objectives?|Patient\(?s?\)?|Patient\(?s?\)? and method\(?s?\)?|'
    #                r'Purpose|R[e\u00E9]sult(?:at)?\(?s?\)?|Resumen|Setting|Summary):?\s*([A-Z])',
    #                r'. \1: \2', string).lstrip('.').strip()
    # Add square brackets around Formula Not Shown
    string = string.replace(' Formula Not Shown ', ' [Formula Not Shown] ')
    return clean(string)


def name_format(name):
    if ',' not in name: return name
    surname, forename = name.rsplit(',',1)
    forename = re.sub(r'(\p{Upper})\s+(?=\p{Upper})', r'\1', re.sub(r'(\p{Upper})(\p{Lower}+|[\.\-])', r'\1', forename))
    return surname + forename
