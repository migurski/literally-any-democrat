import collections, datetime, requests, io, csv
import unittest, httmock

# Ballotpedia conventionally uses an '(i)' next to candidate names
IMARK = ' (i)'

Candidate = collections.namedtuple('Candidate', ('name', 'incumbent'))

State = collections.namedtuple('State', ('state', 'chamber', 'reason',
    'filing_deadline', 'primary_election', 'weight', 'detail_url'))

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
    
    def test_parse_number(self):
        self.assertEqual(parse_number('14,350,000'), 14350000)
        self.assertEqual(parse_number(''), 0)
    
    def test_load_states(self):
        def mock_requests(url, request):
            return b'State,Chamber,Reason,Filing Deadline,Primary Candidates,Primary Election,General Candidates,Weight,Race Detail\nTexas,House of Representatives,Redistricting,"December 9, 2019",Yes,"March 3, 2020",,"191,333","https://ballotpedia.org/Texas_House_of_Representatives_elections,_2020"\n'
    
        with httmock.HTTMock(mock_requests):
            states = load_states('http://example.com/states')
        
        self.assertEqual(len(states), 1)
        self.assertIn(('Texas', 'House of Representatives'), states)
        
        state = states[('Texas', 'House of Representatives')]
        self.assertEqual(state.state, 'Texas')
        self.assertEqual(state.chamber, 'House of Representatives')
        self.assertEqual(state.reason, 'Redistricting')
        self.assertEqual(state.filing_deadline, datetime.date(2019, 12, 9))
        self.assertEqual(state.primary_election, datetime.date(2020, 3, 3))
        self.assertEqual(state.weight, 191333)
        self.assertEqual(state.detail_url, 'https://ballotpedia.org/Texas_House_of_Representatives_elections,_2020')

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

def parse_number(cell):
    '''
    '''
    return int(cell.replace(',', '') or '0')

def load_states(url):
    '''
    '''
    got = requests.get(url)
    text = io.StringIO(got.text)
    rows = csv.DictReader(text, dialect='excel')

    return {
        (row['State'], row['Chamber']): State(
            row['State'], row['Chamber'], row['Reason'],
            parse_date(row['Filing Deadline']), parse_date(row['Primary Election']),
            parse_number(row['Weight']), row['Race Detail']
            )
        for row in rows
        }