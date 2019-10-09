#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ====================
#       Set-up
# ====================

# Import required modules
from collections import OrderedDict
import gc
import getopt
import locale
import sys
from amed.amed_pre import *
from amed.amed_post import *

# Set locale to assist with sorting
locale.setlocale(locale.LC_ALL, '')

# Set threshold for garbage collection (helps prevent the program run out of memory)
gc.set_threshold(400, 5, 5)

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'

# ====================
#     Constants
# ====================


OPTIONS = OrderedDict([
    ('E1',	('Prepare AMED files for import to Excel', amed_pre_Excel)),
    ('E2',	('Process AMED files exported from Excel', amed_post_Excel)),
    ('LM1',	('Prepare AMED files for import to Library Master', amed_pre_LM)),
    ('LM2',	('Process AMED files exported from Library Master', amed_post_LM)),
    ('R', 	('Rebuild database [VM use only :-)]', rebuild_db)),
    ('E', 	('Exit program', sys.exit)),
])


# ====================
#       Classes
# ====================


class OptionHandler:

    def __init__(self, selected_option=None):
        self.selection = None
        if selected_option in OPTIONS:
            self.selection = selected_option
        else: self.get_selection()

    def get_selection(self):
        print('\n----------------------------------------')
        print('\n'.join('{}:\t{}'.format(o, OPTIONS[o][0]) for o in OPTIONS))
        self.selection = input('Choose an option:').upper()
        while self.selection not in OPTIONS:
            self.selection = input('Sorry, your choice was not recognised. '
                                   'Please enter one of {}:'.format(', '.join(opt for opt in OPTIONS))).upper()

    def set_selection(self, selected_option):
        if selected_option in OPTIONS:
            self.selection = selected_option

    def execute(self, ifile, month):

        if self.selection not in OPTIONS:
            self.get_selection()

        date_time(message(OPTIONS[self.selection][0]))

        if self.selection == 'E':
            sys.exit()

        OPTIONS[self.selection][1](ifile, month)
        self.selection = None
        return


# ====================
#      Functions
# ====================

def usage(extended=False):
    """Function to print information about the program"""
    print('Correct syntax is:')
    print('\named_tools  -i <ifile> [options]')
    print('    -i    path to Input file')
    print('\nOptions')
    print('nEXACTLY ONE of the following:')
    for o in OPTIONS:
        print('    --{}    {}'.format(o.lower(), OPTIONS[o][0]))
    print('\nANY of the following:')
    print('    --help    Display this message and exit')
    print('    --month   Month number if file is not for current month')
    print('              e.g. --month=04 for April')
    if extended:
        print('\nFor options E1 and LM1, Input file must be a .txt file with one AMED record per line')
        print('\nUse quotation marks (") around arguments which contain spaces')
        print('\n\'AMED journal title lookup table.txt\' must be present in the folder K:\AMED\Exports\Lookup')
        print('\n\'amed_citations.db\' must be present in the folder K:\AMED\Exports\Lookup')
    exit_prompt()
	
	
	
# ====================
#      Main code
# ====================


def main(argv=None):
    if argv is None:
        name = str(sys.argv[1])

    selected_option = None
    ifile = None
    month = None

    print('========================================')
    print('amed_tools')
    print('========================================')

    try: opts, args = getopt.getopt(argv, 'ei:m:r', ['help', 'ifile=', 'month=', 'lm1', 'lm2', 'e1', 'e2'] + [o for o in OPTIONS] + [o.lower() for o in OPTIONS])
    except getopt.GetoptError as err:
        exit_prompt('Error: {}'.format(str(err)))
    for opt, arg in opts:
        if opt == '--help': usage(extended=True)
        elif opt in ['-i', '--ifile']:
            ifile = FilePath('input', arg)
        elif opt in ['-m', '--month']:
            month = arg			
        elif opt.upper().strip('-') in OPTIONS:
            selected_option = opt.upper().strip('-')
        else: exit_prompt('Error: Option {} not recognised'.format(opt))

    # Check that files exist
    if selected_option not in ['E', 'R'] and not ifile:
        exit_prompt('Error: No path to input file has been specified')

    option = OptionHandler(selected_option)

    while option.selection:
        option.execute(ifile, month)
        option.get_selection()

    date_time_exit()


if __name__ == '__main__':
    main(sys.argv[1:])
