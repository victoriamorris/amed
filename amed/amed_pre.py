#!/usr/bin/env python
# -*- coding: utf8 -*-

# ====================
#       Set-up
# ====================

# Import required modules
from amed.functions import *
from amed.db_tools import *

# Set locale to assist with sorting
locale.setlocale(locale.LC_ALL, '')

# Set threshold for garbage collection (helps prevent the program run out of memory)
gc.set_threshold(400, 5, 5)

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
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


class AMED:
    """Class for converting ETOC records to tsv or csv for import to Excel or Library Master, respectively"""

    def __init__(self, record, accession_number, export_type='LM'):
        self.record = record
        self.export_type = export_type
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
        if len(self.values['ISSN']) != 9: self.values['ISSN'] = None
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
                print('\nJournal title not recognised:\n{}'.format(test))
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
        if self.export_type == 'Excel':
            # Format as TSV for Excel
            for key in self.values:
                s += '{}{}'.format('' if key == 'Running number' else '\t',
                                   str(self.values[key]) if self.values[key] else '', key)
        else:
            # Format as CSV and escape HTML characters for Library Master
            for key in self.values:
                s += '{}"{}"'.format('' if key == 'Running number' else ',',
                                     str(self.values[key]).replace('"', '""') if self.values[key] else '')
            s = s.encode('ascii', 'xmlcharrefreplace')
            s = s.decode('ascii')
            s = s.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        s += '\n'
        return s


# ====================
#      Functions
# ====================


def rebuild_db(ifile=None, month=None):
    db = CitationDatabase()
    db.add_citations_from_file()
    db.close()


# ====================
#      Main code
# ====================

def amed_pre_Excel(ifile=None, month=None):
    amed_pre(export_type='Excel', ifile=ifile)


def amed_pre_LM(ifile=None, month=None):
    amed_pre(export_type='LM', ifile=ifile)


def amed_pre(export_type='LM', ifile=None):
    if not ifile:
        exit_prompt('Error: No path to input file has been specified')

    # --------------------
    # Parameters seem OK => start program
    # --------------------

    # Display confirmation information about the transformation

    print('Input file: {}'.format(str(ifile.path)))

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

    # --------------------
    # Read journal abbreviations into memory:
    # --------------------

    jfile = FilePath('lookup', JOURNAL_ABBREVIATION_PATH)
    jfile = open(jfile.path, mode='r', encoding='utf-8', errors='replace')
    for filelineno, line in enumerate(jfile):
        line = line.strip('\n')
        if line != '':
            try:
                title, abbreviation, p_issn, o_issn = line.split('\t')
            except:
                title, abbreviation, p_issn, o_issn = None, None, None, None
            if p_issn: ISSNS[p_issn] = abbreviation
            if o_issn: ISSNS[o_issn] = abbreviation
            TITLES[title] = abbreviation
    jfile.close()

    # --------------------
    # Read citations into memory:
    # --------------------

    db = CitationDatabase()
    # db.add_citations_from_file()
    citations_already_present = db.get_citations()
    citations_to_add = list()

    # --------------------
    # Process input file
    # --------------------
    today = datetime.date.today()
    file_count = 1
    # File count ensures that no more than 200 records are written to each output file	

    # Open input and output files
    ifile = open(ifile.path, mode='r', encoding='utf-8', errors='replace')
    if export_type == 'LM':
        ofile = open('{:%Y%m%d}AMED{}.csv'.format(today, str(file_count)), mode='w', encoding='utf-8', errors='replace')
        efile = open('{:%Y%m%d}AMED_duplicates{}.csv'.format(today, str(file_count)), mode='w', encoding='utf-8',
                     errors='replace')
    else:
        ofile = open('amed_as_tsv.tsv', mode='w', encoding='utf-8', errors='replace')
        efile = open('amed_as_tsv_duplicates.tsv', mode='w', encoding='utf-8', errors='replace')
    count = 0
    accession_start -= 1

    for filelineno, line in enumerate(ifile):
        if line.strip() != '':
            count += 1
            print('{} records processed'.format(str(count)), end='\r')
            if export_type == 'LM':
                if count % 50 == 0:
                    ofile.close()
                    file_count += 1
                    ofile = open('{:%Y%m%d}AMED{}.csv'.format(today, str(file_count)), mode='w', encoding='utf-8',
                                 errors='replace')
            amed = AMED(clean(line.strip()), accession_start + count, export_type=export_type)
            citation = amed.values['Citation']
            # For citations without page numbers, append 20 characters from title
            if citation.endswith(':'):
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

    jfile = FilePath('lookup', JOURNAL_ABBREVIATION_PATH)
    jfile = open(jfile.path, mode='a', encoding='utf-8', errors='replace')
    for title in NEW_JOURNALS:
        jfile.write('{}\t{}\t\t\n'.format(title, NEW_JOURNALS[title]))
    jfile.close()

    date_time_exit()
