#!/usr/bin/env python
# -*- coding: utf8 -*-

# ====================
#       Set-up
# ====================

# Import required modules
from amed_tools import *

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '3.0.0'
__status__ = '4 - Beta Development'


# ====================
#       Classes
# ====================

class AmedRecord():
    def __init__(self, record, export_type='LM'):
        self.export_type = export_type
        if self.export_type == 'Excel':
            self.record = record.split('\u0009')
            self.values = OrderedDict([
                ('AN', 0),  # Accession number
                ('AU', 4),  # Authors
                ('TI', 2),  # Title
                ('SO', 3),  # Source
                ('ET', 8),  # Entry terms
                ('KW', 9),  # Keywords
                ('MT', 10),  # Minor terms
                ('TY', 7),  # Publication type
                ('LA', 11),  # Language
                ('ES', 12),  # English summary indicator
                ('IS', 1),  # ISSN
                ('MD', 6),  # Abstract indicator
                ('AB', 5),  # Abstract
            ])
        else:
            self.record = record.strip('"').split('","')
            self.values = OrderedDict([
                ('AN', 1),  # Accession number
                ('AU', 2),  # Authors
                ('TI', 3),  # Title
                ('SO', 4),  # Source
                ('ET', 5),  # Entry terms
                ('KW', 6),  # Keywords
                ('MT', 7),  # Minor terms
                ('TY', 8),  # Publication type
                ('LA', 9),  # Language
                ('ES', 10),  # English summary indicator
                ('IS', 11),  # ISSN
                ('MD', 12),  # Abstract indicator
                ('AB', 14),  # Abstract
            ])
        for v in self.values:
            try:
                self.values[v] = clean(self.record[self.values[v]])
            except:
                self.values[v] = None
            if self.values[v] == '"': self.values[v] = None
            if self.export_type == 'Excel':
                if self.values[v] and self.values[v].startswith('"') and self.values[v].endswith('"'):
                    self.values[v] = self.values[v].strip('"')
        self.id = self.values['AN']
        if self.values['AB'] and not self.values['MD']: self.values['MD'] = 'AB'

    def __str__(self):
        s = '\n     [REC]'
        for v in self.values:
            if self.values[v]:
                s += '\n     ' + text_wrap('{}: {}]'.format(v, self.values[v]))
            else:
                s += ']'
        if not self.values['AB']: s += ']'
        return s

    def no_wrap(self):
        s = '\n     [REC]'
        for v in self.values:
            if self.values[v]:
                s += '\n     {}: {}]'.format(v, self.values[v])
            else:
                s += ']'
        if not self.values['AB']: s += ']'
        return s


# ====================
#      Main code
# ====================


"""
def amed_post(export_type='LM', ifile=None, month=None):
    if not ifile:
        exit_prompt('Error: No path to input file has been specified')

    # Get date parameters for output filenames
    if month:
        try:
            month = int(month)
        except:
            exit_prompt('Error: The value of the parameter --month must be an integer')
        today = datetime.date.today()
        if month == 12 and today.month <= 5:
            today = datetime.date(today.year - 1, month, today.day)
        else:
            today = datetime.date(today.year, month, today.day)
    else:
        today = datetime.date.today()

    output_files = OrderedDict([
        ('hosts', 'AMED{:%m%y} for hosts.txt'.format(today).lower()),
        ('spl', 'AMED' + '{:%b}.spl'.format(today).lower()),
        ('dat', 'F164{:%m%d}.dat'.format(today)),
        ('txt', 'amd{:%b%y}.txt'.format(today).lower()),
        ('stats', 'AMED stats {:%Y-%m-%d}.txt'.format(today)),
        ('end', 'F164.end'),
    ])

    # --------------------
    # Parameters seem OK => start program
    # --------------------

    # Display confirmation information about the transformation

    print('Input file: {}'.format(str(ifile.path)))
    print('Processing date: {}'.format(str(today)))

    # --------------------
    # Process input file
    # --------------------

    first, last, count = None, '', 0
    for f in output_files:
        output_files[f] = open(output_files[f], mode='w', encoding='utf-8', errors='replace', newline='\r\n')

    # Open input and output files
    ifile = open(ifile.path, mode='r', encoding='utf-8', errors='replace')
    for f in ['hosts', 'spl', 'dat', 'txt']:
        output_files[f].write('[STA]')

    for filelineno, line in enumerate(ifile):
        if export_type == 'Excel' and filelineno == 0: continue
        count += 1
        print('{} records processed'.format(str(count)), end='\r')
        if export_type == 'Excel':
            amed = AmedRecord(clean(line.strip('\n')), export_type=export_type)
        else:
            # Unescape Unicode escape sequences at this point
            amed = AmedRecord(clean(html.unescape(line.strip())), export_type=export_type)
        for f in ['hosts', 'dat']:
            output_files[f].write(str(amed))
        output_files['spl'].write(amed.no_wrap())
        output_files['txt'].write(str(amed).replace('     AU:', '     UD: {:%Y%m}]\n     AU:'.format(today)))
        if not first: first = amed.id
    if not last: last = amed.id
    for f in ['hosts', 'spl', 'dat', 'txt']:
        output_files[f].write('\n[END]\n')
    ifile.close()

    output_files['end'].write('FILE f164{:%m%d}.dat'.format(today))

    # Write statistics
    output_files['stats'].write('Number of records processed: {}\n'.format(str(count)))
    output_files['stats'].write('First record: {}\n'.format(first))
    output_files['stats'].write('Last record: {}\n'.format(last))
    if export_type == 'Excel':
        output_files['stats'].write('Start next processing with accession number: {}\n'.format(str(int(last) + 1)))
    output_files['stats'].write('\n\nText for email:\n\n' +
                                'The {:%m/%Y} update for AMED is now on the FTP server. '.format(today) +
                                'There are {} records ({} to {})'.format(str(count), first, last))

    # Close files
    for f in output_files:
        output_files[f].close()

    date_time_exit()
"""

NAME = 'amed_post'
SUMMARY = 'Process AMED files exported from Excel'


def main(args=None):

    if args is None:
        name = str(argv[1])

    amed = AMED(NAME, SUMMARY, ['i+', 'c'])
    args = amed.parse_args(args)
    total = 0
    date_time_exit()


if __name__ == '__main__':
    main(argv[1:])
