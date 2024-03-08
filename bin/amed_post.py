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

class AmedRecord:
    def __init__(self, record):
        self.record = record.split('\t')
        logging.info(self.record)
        self.values = OrderedDict([
            ('AN', 0),  # Accession number
            ('AU', 5),  # Authors
            ('TI', 3),  # Title
            ('SO', 4),  # Source
            ('ET', 9),  # Entry terms
            ('KW', 10),  # Keywords
            ('MT', 11),  # Minor terms
            ('TY', 8),  # Publication type
            ('LA', 12),  # Language
            ('ES', 13),  # English summary indicator
            ('IS', 1),  # ISSN
            ('MD', 7),  # Abstract indicator
            ('AB', 6),  # Abstract
        ])
        for v in self.values:
            try:
                self.values[v] = clean(self.record[self.values[v]])
            except:
                self.values[v] = None
            if self.values[v] == '"':
                self.values[v] = None
            if self.values[v] and self.values[v].startswith('"') and self.values[v].endswith('"'):
                self.values[v] = self.values[v].strip('"')
            if v in ['ET', 'KW', 'MT', 'TY']:
                self.values[v] = ', '.join(val for val in sorted(self.values[v].split(',')) if val)
        self.id = self.values['AN']
        if self.values['AB'] and not self.values['MD']:
            self.values['MD'] = 'AB'

    def __str__(self):
        s = '\n     [REC]'
        for v in self.values:
            if self.values[v]:
                s += '\n     ' + text_wrap(f'{str(v)}: {str(self.values[v])}]')
            else:
                s += ']'
        if not self.values['AB']:
            s += ']'
        return s

    def no_wrap(self):
        s = '\n     [REC]'
        for v in self.values:
            if self.values[v]:
                s += f'\n     {v}: {self.values[v]}]'
            else:
                s += ']'
        if not self.values['AB']:
            s += ']'
        return s


# ====================
#      Main code
# ====================


NAME = 'amed_post'
SUMMARY = 'Process AMED files exported from Excel'


def main(args=None):
    if args is None:
        name = str(argv[1])

    amed = AMED(NAME, SUMMARY, ['i', 'c'])
    args = amed.parse_args(args)

    check_file_location(args.c[0], 'config file')
    date_time_message(f'Reading config file from {str(args.c[0])}')

    today = datetime.date.today()
    month = today.month

    cfile = open(args.c[0], mode='r', encoding='utf-8', errors='replace')
    for line in cfile:
        if line.startswith('MONTH'):
            month = line.strip().split('=', 1)[1].strip()
            try:
                month = int(month)
            except:
                date_time_exit('Error: The value of the parameter MONTH must be an integer')
            if month == 0:
                today = datetime.date.today()
                month = today.month
            if not 1 <= month <= 12:
                date_time_exit('Error: The value of the parameter MONTH must be between 1 and 12')
            if month == 12 and today.month <= 5:
                today = datetime.date(today.year - 1, month, today.day)
            else:
                today = datetime.date(today.year, month, today.day)
    cfile.close()

    logging.info(f'MONTH: {str(month)}')
    logging.info(f'Processing date: {str(today)}')

    output_files = OrderedDict([
        ('hosts', 'AMED{:%m%y} for hosts.txt'.format(today).lower()),
        ('spl', 'AMED' + '{:%b}.spl'.format(today).lower()),
        ('dat', 'F164{:%m%d}.dat'.format(today)),
        ('txt', 'amd{:%b%y}.txt'.format(today).lower()),
        ('stats', 'AMED stats {:%Y-%m-%d}.txt'.format(today)),
        ('end', 'F164.end'),
    ])

    file = args.i[0]
    if not os.path.isfile(file):
        raise AMEDError(f'Error: Could not locate {str(file)}')

    # --------------------
    # Process input file
    # --------------------

    log_print(f'Input file: {str(file)}')

    # Open input and output files
    ifile = open(file, mode='r', encoding='utf-8', errors='replace')

    first, last, count = None, '', 0
    for f in output_files:
        output_files[f] = open(output_files[f], mode='w', encoding='utf-8', errors='replace', newline='\r\n')

    for f in ['hosts', 'spl', 'dat', 'txt']:
        output_files[f].write('[STA]')

    count = 0
    for filelineno, line in enumerate(ifile):
        if filelineno == 0:
            continue
        count += 1
        print(f'{str(filelineno)} records processed', end='\r')
        rec = AmedRecord(line.strip('\n'))
        for f in ['hosts', 'dat']:
            output_files[f].write(str(rec))
        output_files['spl'].write(rec.no_wrap())
        output_files['txt'].write(str(rec).replace('     AU:', '     UD: {:%Y%m}]\n     AU:'.format(today)))
        for f in output_files:
            output_files[f].flush()
        if not first:
            first = rec.id
        last = rec.id
    for f in ['hosts', 'spl', 'dat', 'txt']:
        output_files[f].write('\n[END]\n')
    ifile.close()

    output_files['end'].write('FILE f164{:%m%d}.dat'.format(today))

    # Write statistics
    output_files['stats'].write(f'Number of records processed: {str(count)}\n')
    output_files['stats'].write(f'First record: {first}\n')
    output_files['stats'].write(f'Last record: {last}\n')
    output_files['stats'].write(f'Start next processing with accession number: {str(int(last) + 1)}\n')
    output_files['stats'].write('\n\nText for email:\n\n' +
                                'The {:%m/%Y} update for AMED is now on the FTP server. '.format(today) +
                                f'There are {str(count)} records ({first} to {last})')

    # Close files
    for f in output_files:
        output_files[f].close()

    date_time_exit()


if __name__ == '__main__':
    main(argv[1:])
