import collections, datetime, requests, io, csv
import unittest, httmock

# Ballotpedia conventionally uses an '(i)' next to candidate names
IMARK = ' (i)'

# Westernmost timezone
TZ = datetime.timezone(datetime.timedelta(hours=-12))

Person = collections.namedtuple('Person', ('name', 'incumbent'))

Candidate = collections.namedtuple('Candidate',
    ('state', 'chamber', 'district', 'name', 'incumbent'))

State = collections.namedtuple('State', ('state', 'chamber', 'reason',
    'filing_deadline', 'primary_election', 'weight', 'detail_url'))

class TestData (unittest.TestCase):
    
    def test_parse_persons(self):
        p1 = parse_persons('Bill Brannon')
        self.assertEqual(p1, [('Bill Brannon', None)])

        p2 = parse_persons("Janet Dudding\nRaza Rahman")
        self.assertEqual(p2, [('Janet Dudding', None), ('Raza Rahman', None)])

        p3 = parse_persons('Joe Deshotel (i)')
        self.assertEqual(p3, [('Joe Deshotel', True)])

        p4 = parse_persons("Ron Reynolds (i)\nByron Ross\n")
        self.assertEqual(p4, [('Ron Reynolds', True), ('Byron Ross', None)])
    
    def test_parse_date(self):
        d1 = parse_date('December 9, 2019')
        self.assertEqual(d1.date(), datetime.date(2019, 12, 9))

        d2 = parse_date('March 3, 2020')
        self.assertEqual(d2.date(), datetime.date(2020, 3, 3))

        d3 = parse_date('August 18, 2020')
        self.assertEqual(d3.date(), datetime.date(2020, 8, 18))
    
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
        self.assertEqual(state.filing_deadline.date(), datetime.date(2019, 12, 9))
        self.assertEqual(state.primary_election.date(), datetime.date(2020, 3, 3))
        self.assertEqual(state.weight, 191333)
        self.assertEqual(state.detail_url, 'https://ballotpedia.org/Texas_House_of_Representatives_elections,_2020')
    
    def test_load_candidates_basic(self):
        def mock_requests(url, request):
            return b'State,Chamber,Reason,Primary Election,District,Democratic Candidate(s),Incumbent\nTexas,House of Representatives,Redistricting,"March 3, 2020",27,"Ron Reynolds (i)\nByron Ross",Yes\nTexas,House of Representatives,Redistricting,"March 3, 2020",28,Elizabeth Markowitz,No\nTexas,House of Representatives,Redistricting,"March 3, 2020",29,Travis Boldt,No\nTexas,House of Representatives,Redistricting,"March 3, 2020",31,Ryan Guillen (i),Yes\n'
    
        with httmock.HTTMock(mock_requests):
            candidates = load_candidates('http://example.com/candidates')
        
        self.assertEqual(len(candidates), 5)
        
        c1 = candidates[0]
        self.assertEqual(c1.state, 'Texas')
        self.assertEqual(c1.chamber, 'House of Representatives')
        self.assertEqual(c1.district, 27)
        self.assertEqual(c1.name, 'Ron Reynolds')
        self.assertTrue(c1.incumbent)
        
        c2 = candidates[1]
        self.assertEqual(c2.district, 27)
        self.assertEqual(c2.name, 'Byron Ross')
        self.assertIsNone(c2.incumbent)
        
        c3 = candidates[2]
        self.assertEqual(c3.district, 28)
        self.assertEqual(c3.name, 'Elizabeth Markowitz')
        self.assertIsNone(c3.incumbent)
        
        c4 = candidates[3]
        self.assertEqual(c4.district, 29)
        self.assertEqual(c4.name, 'Travis Boldt')
        self.assertIsNone(c4.incumbent)
        
        c5 = candidates[4]
        self.assertEqual(c5.district, 31)
        self.assertEqual(c5.name, 'Ryan Guillen')
        self.assertTrue(c5.incumbent)

    def test_load_candidates_senate(self):
        def mock_requests(url, request):
            return b'State,Chamber,Reason,Primary Election,District,Democratic Candidate(s),Incumbent\nNorth Carolina,U.S. Senate,Senate Control,"March 3, 2020",,Cal Cunningham,No\n\n'
    
        with httmock.HTTMock(mock_requests):
            candidates = load_candidates('http://example.com/candidates')
        
        self.assertEqual(len(candidates), 1)
        
        c1 = candidates[0]
        self.assertEqual(c1.state, 'North Carolina')
        self.assertEqual(c1.chamber, 'U.S. Senate')
        self.assertIsNone(c1.district)
        self.assertEqual(c1.name, 'Cal Cunningham')
        self.assertIsNone(c1.incumbent)

    def test_load_candidates_unicode(self):
        def mock_requests(url, request):
            return 'State,Chamber,Reason,Primary Election,District,Democratic Candidate(s),Incumbent\nTexas,U.S. Senate,Senate Control,"March 3, 2020",,"Cristina Tzintzún Ramirez"\n'.encode('utf8')
    
        with httmock.HTTMock(mock_requests):
            candidates = load_candidates('http://example.com/candidates')
        
        self.assertEqual(len(candidates), 1)
        
        c1 = candidates[0]
        self.assertEqual(c1.state, 'Texas')
        self.assertEqual(c1.chamber, 'U.S. Senate')
        self.assertIsNone(c1.district)
        self.assertEqual(c1.name, 'Cristina Tzintzún Ramirez')
        self.assertIsNone(c1.incumbent)

def parse_persons(cell):
    ''' Return a list of Persons for a cell value
    '''
    names = cell.split('\n')
    return [Person(name.replace(IMARK, ''), True if (IMARK in name) else None)
        for name in names if name.strip()]

def parse_date(cell):
    ''' Return a datetime.date object for a cell value
    '''
    return datetime.datetime.strptime(cell, '%B %d, %Y').replace(tzinfo=TZ)

def parse_number(cell):
    '''
    '''
    return int(cell.replace(',', '') or '0')

def load_states(url):
    '''
    '''
    got = requests.get(url)
    text = io.StringIO(got.content.decode('utf8'))
    rows = csv.DictReader(text, dialect='excel')

    return {
        (row['State'], row['Chamber']): State(
            row['State'], row['Chamber'], row['Reason'],
            parse_date(row['Filing Deadline']), parse_date(row['Primary Election']),
            parse_number(row['Weight']), row['Race Detail']
            )
        for row in rows
        }

def load_candidates(url):
    '''
    '''
    got = requests.get(url)
    text = io.StringIO(got.content.decode('utf8'))
    rows = csv.DictReader(text, dialect='excel')
    
    candidates = []
    
    for row in rows:
        for person in parse_persons(row['Democratic Candidate(s)']):
            candidates.append(Candidate(
                row['State'], row['Chamber'],
                parse_number(row['District']) if row['District'] else None,
                person.name, person.incumbent
                ))
    
    return candidates
