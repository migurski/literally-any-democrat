import unittest, collections, datetime

# Ballotpedia conventionally uses an '(i)' next to candidate names
IMARK = ' (i)'

Candidate = collections.namedtuple('Candidate', ('name', 'incumbent'))

class TestData (unittest.TestCase):
    
    def test_parse_candidates(self):
        c1 = parse_candidates('Bill Brannon')
        self.assertEqual(c1, [('Bill Brannon', None)])

        c2 = parse_candidates("Janet Dudding\nRaza Rahman")
        self.assertEqual(c2, [('Janet Dudding', None), ('Raza Rahman', None)])

        c3 = parse_candidates('Joe Deshotel (i)')
        self.assertEqual(c3, [('Joe Deshotel', True)])

        c4 = parse_candidates("Ron Reynolds (i)\nByron Ross\n")
        self.assertEqual(c4, [('Ron Reynolds', True), ('Byron Ross', None)])
    
    def test_parse_date(self):
        d1 = parse_date('December 9, 2019')
        self.assertEqual(d1, datetime.date(2019, 12, 9))

        d2 = parse_date('March 3, 2020')
        self.assertEqual(d2, datetime.date(2020, 3, 3))

        d3 = parse_date('August 18, 2020')
        self.assertEqual(d3, datetime.date(2020, 8, 18))

def parse_candidates(cell):
    ''' Return a list of Candidates for a cell value
    '''
    names = cell.split('\n')
    return [Candidate(name.replace(IMARK, ''), True if (IMARK in name) else None)
        for name in names if name.strip()]

def parse_date(cell):
    ''' Return a datetime.date object for a cell value
    '''
    return datetime.datetime.strptime(cell, '%B %d, %Y').date()