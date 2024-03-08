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
#   Global variables
# ====================


ISSNS = {}
TITLES = {}
NEW_JOURNALS = {}


# ====================
#      Classes
# ====================

class AMEDConverter:
    """Class for converting ETOC records to tsv or csv for import to Excel or Library Master, respectively"""

    def __init__(self, record, accession_number):
        self.record = record
        self.values = OrderedDict([
            ('Running number', None),
            ('ISSN', None),
            ('Blank', ''),
            ('Title', None),
            ('Citation', None),
            ('Authors', None),
            ('Abstract', None),
            ('Abstract indicator', None),
        ])

        self.values['Running number'] = '{:07d}'.format(accession_number)
        self.values['ISSN'] = re.sub(r'^.*?<ISSN>\s*([0-9X\-]+)</ISSN>.*?$',
                                     lambda m: re.sub(r'([0-9X]{4})\-?([0-9X]{4})', r'\1-\2', m.group(1)),
                                     record.upper())
        if len(self.values['ISSN']) != 9:
            self.values['ISSN'] = None
        self.values['Title'] = clean(
            re.sub(r'^.*?<TEXT>\s*(.*?)</TEXT>.*?$', r'\1', record)) if '<TEXT>' in record else ''
        if self.values['ISSN'] in ISSNS:
            journal_title = ISSNS[self.values['ISSN']]
        else:
            journal_title = clean(
                re.sub(r'^.*?<TITLE>\s*(.*?)</TITLE>.*?$', r'\1', record)) if '<TITLE>' in record else ''
            test = re.sub(r'\s+', ' ', re.sub(r'[^0-9a-zA-Z\s]', '', re.sub(r'(:|--|=).*$', '', re.sub(
                r'^\[.*\](?!$)|(?<!^)\(.*?\)$|(?<!^)\[.*?\]$', '', journal_title)))).upper()
            if test != '' and test in TITLES:
                journal_title = TITLES[test]
            else:
                print(f'\nJournal title not recognised:\n{test}')
                while True:
                    abbreviation = input('Please enter the abbreviation for this journal: ').strip()
                    confirm = input(
                        'Type Y to confirm that\n\'{}\'\nis the correct abbreviation for journal\n{}:'.format(
                            abbreviation, test)).upper().strip()
                    if confirm == 'Y':
                        NEW_JOURNALS[test] = abbreviation
                        TITLES[test] = abbreviation
                        break
        issue = re.sub(r'\s*VOL\s*', '', re.sub(r'\s*VOL\s*([^\s]*?);\s*NUMBER\s*(.*)$', r'\1(\2)', clean(
            re.sub(r'\s*\(S/\s*([0-9]+)\)', r'(Suppl \1)', re.sub(r'\s*SUPP/([0-9]+)', r'(Suppl \1)',
                                                                  re.sub(r'^.*?<ISSUE>\s*(.*?)</ISSUE>.*?$', r'\1',
                                                                         record)))))) if '<ISSUE>' in record else ''
        pages = re.sub(r'^([^\-]+)-\1$', r'\1',
                       clean(re.sub(r'^.*?<PAGE>\s*(.*?)</PAGE>.*?$', r'\1', record))) if '<PAGE>' in record else ''
        self.values['Citation'] = journal_title + ' ' + issue + ':' + pages
        a_1 = re.sub(r'^.*?<AUTH>\s*(.*?)</AUTH>.*?$', r'\1', record) if '<AUTH>' in record else ''
        if a_1 != '':
            a_2 = []
            for a in a_1.split(';'):
                if name_format(a.strip()) not in a_2:
                    a_2.append(name_format(a.strip()))
            if len(a_2) > 10: a_2 = a_2[:9] + a_2[-1:]
            self.values['Authors'] = ', '.join(a_2)
        else:
            self.values['Authors'] = ''

        self.values['Abstract'] = clean_html(
            re.sub(r'^.*?<ABS>\s*(.*?)</ABS>.*?$', r'\1', record)) if '<ABS>' in record else ''
        self.values['Abstract indicator'] = 'AB' if self.values['Abstract'] != '' else None

    def __str__(self):
        s = ''
        for key in self.values:
            s += '{}{}'.format('' if key == 'Running number' else '\t',
                               str(self.values[key]) if self.values[key] else '', key)
        s += '\n'
        return s


# ====================
#      Main code
# ====================


NAME = 'amed_pre'
SUMMARY = 'Prepare AMED files for import to Excel'
DATABASE_PATH = '\\Lookup files\\amed_citations.db'
JOURNAL_ABBREVIATION_PATH = '\\Lookup files\\AMED journal title lookup table.txt'
ACCESSION_NUMBER = 0


def main(args=None):

    if args is None:
        name = str(argv[1])

    amed = AMED(NAME, SUMMARY, ['i+', 'c'])
    args = amed.parse_args(argv)
    dbp, jap, accession_start = DATABASE_PATH, JOURNAL_ABBREVIATION_PATH, ACCESSION_NUMBER

    check_file_location(args.c[0], 'config file')
    date_time_message(f'Reading config file from {str(args.c[0])}')
    cfile = open(args.c[0], mode='r', encoding='utf-8', errors='replace')
    for line in cfile:
        if line.startswith('DATABASE_PATH'):
            dbp = line.strip().split('=', 1)[1].strip()
            check_file_location(dbp, 'DATABASE_PATH')
        if line.startswith('JOURNAL_ABBREVIATION_PATH'):
            jap = line.strip().split('=', 1)[1].strip()
            check_file_location(jap, 'JOURNAL_ABBREVIATION_PATH')
        if line.startswith('ACCESSION_NUMBER'):
            accession_start = line.strip().split('=', 1)[1].strip()
    cfile.close()

    if not accession_start or not isinstance(accession_start, int) or accession_start == 0:
        accession_start = get_accession_number()
    accession_start = int(accession_start)

    logging.info(f'DATABASE_PATH: {str(dbp)}\n'
                 f'JOURNAL_ABBREVIATION_PATH: {str(jap)}\n'
                 f'ACCESSION_NUMBER: {str(accession_start)}\n')

    for a in args.i:
        file_list = glob.glob(a)
        for file in file_list:
            if not os.path.isfile(file):
                raise AMEDError(f'Error: Could not locate {str(file)}')

            # --------------------
            # Read journal abbreviations into memory:
            # --------------------

            jfile = open(jap, mode='r', encoding='utf-8', errors='replace')
            for filelineno, line in enumerate(jfile):
                line = line.strip('\n')
                if line != '':
                    try:
                        title, abbreviation, p_issn, o_issn = line.split('\t')
                    except:
                        title, abbreviation, p_issn, o_issn = None, None, None, None
                    if p_issn:
                        ISSNS[p_issn] = abbreviation
                    if o_issn:
                        ISSNS[o_issn] = abbreviation
                    TITLES[title] = abbreviation
            jfile.close()

            # --------------------
            # Read citations into memory:
            # --------------------

            db = CitationDatabase(dbp)
            citations_already_present = db.get_citations()
            citations_to_add = list()

            # --------------------
            # Process input file
            # --------------------

            # Open input and output files
            ifile = open(file, mode='r', encoding='utf-8', errors='replace')

            ofile = open('amed_as_tsv.tsv', mode='w', encoding='utf-8', errors='replace')
            efile = open('amed_as_tsv_duplicates.tsv', mode='w', encoding='utf-8', errors='replace')
            count = 0
            accession_start -= 1

            for filelineno, line in enumerate(ifile):
                if line.strip() != '':
                    count += 1
                    print(f'{str(count)} records processed', end='\r')
                    amed = AMEDConverter(clean(line.strip()), accession_start + count)
                    citation = amed.values['Citation']
                    # Append 20 characters from title
                    citation += re.sub(r'[^A-Z0-9]', '', amed.values['Title'].upper())[:20]
                    if citation and citation in citations_already_present:
                        print('Citation {} is a duplicate'.format(str(citation)))
                        efile.write(str(amed))
                    else:
                        citations_already_present.append(citation)
                        citations_to_add.append((citation,))
                        ofile.write(str(amed))

            db.add_citations(citations_to_add)
            db.close()

            for f in [ofile, ifile, efile]:
                f.close()

            # --------------------
            # Save new journals
            # --------------------

            jfile = open(jap, mode='a', encoding='utf-8', errors='replace')
            for title in NEW_JOURNALS:
                jfile.write('{}\t{}\t\t\n'.format(title, NEW_JOURNALS[title]))
            jfile.close()

    date_time_exit()


if __name__ == '__main__':
    main(argv[1:])