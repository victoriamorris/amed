#  -*- coding: utf8 -*-

"""Functions used within amed_tools."""

# Import required modules
import sqlite3
from amed_tools.functions import *

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


# ====================
#       Classes
# ====================

class CitationDatabase:

    def __init__(self, database_path):
        """Open a new database connection, and ensure that the correct tables are present"""
        date_time_message('Connecting to local database')
        self.path = database_path
        self.conn = sqlite3.connect(database_path)
        self.cursor = self.conn.cursor()

        # Set up database
        self.cursor.execute('PRAGMA synchronous = OFF')
        self.cursor.execute('PRAGMA journal_mode = OFF')
        self.cursor.execute('PRAGMA locking_mode = EXCLUSIVE')
        self.cursor.execute('PRAGMA count_changes = FALSE')

        self.cursor.execute('CREATE TABLE IF NOT EXISTS citations (id INTEGER PRIMARY KEY, citation TEXT UNIQUE);')

    def close(self):
        """Close the database connection"""
        self.conn.close()
        collect()

    def clean(self, quick_clean=False):
        """Clean the database to remove unnecessary values"""
        date_time_message('Cleaning')
        self.cursor.execute('DELETE FROM citations WHERE citation IS NULL OR citation = "" ;')
        self.conn.execute("VACUUM")
        self.conn.commit()
        collect()

    def build_index(self):
        """Function to build indexes in a table"""
        date_time_message('Building indexes in citations table')
        self.cursor.execute('DROP INDEX IF EXISTS IDX_citations ;')
        self.cursor.execute('CREATE INDEX IDX_citations ON citations (citation);')
        self.conn.commit()
        collect()

    def execute_all(self, query, values):
        if values:
            self.cursor.executemany(query, values)
            self.conn.commit()
            collect()
        return []

    def get_citations(self):
        date_time_message('Reading list of citations from database')
        self.cursor.execute('SELECT citation FROM citations WHERE citation IS NOT NULL ORDER BY citation ASC ;')
        try: results = list(s[0] for s in self.cursor.fetchall())
        except:
            print('none')
            return None
        return results

    def add_citations(self, citations):
        if citations is None or len(citations) == 0: return None
        sql_query = 'INSERT OR IGNORE INTO citations (id, citation) VALUES (NULL, ?) ;'
        self.execute_all(sql_query, citations)
        date_time_message('{} citations added'.format(str(len(citations))))
        self.build_index()
        self.export()
        return len(citations)

    def export(self):
        date_time_message('Exporting citations from database')
        citations = self.get_citations()
        if not citations or len(citations) == 0: return
        file = open(self.path.replace('.db','_list.txt'), mode='w', encoding='utf-8', errors='replace')
        for c in sorted(citations):
            file.write('{}\n'.format(str(c)))
        file.close()
        collect()
