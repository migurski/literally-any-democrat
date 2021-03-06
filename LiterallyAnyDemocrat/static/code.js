function load_candidates(url)
{
    var request = new XMLHttpRequest();
    request.open('GET', url, true);

    request.onload = function()
    {
        if(request.status >= 200 && request.status < 400)
        {
            // Returns a dict with head and rows lists
            var data = JSON.parse(request.responseText);
            pick_random_candidate(make_candidate_dicts(data['head'], data['rows']));
            return;
        }
    };

    request.onerror = function() { /* There was a connection error of some sort */ };
    request.send();
}

function make_candidate_dicts(head, rows)
{
    var dicts = [], cumulative_weight = 0;
    
    for(var i = 0; i < rows.length; i++)
    {
        dicts.push({});

        for(var j = 0; j < head.length; j++)
        {
            dicts[i][head[j]] = rows[i][j];
        }
        
        // scale logarithmically so big state Senate races don't dominate
        dicts[i].weight = Math.log(dicts[i].weight);
        
        if(dicts[i].incumbent)
        {
            // return incumbents half as frequently
            dicts[i].weight /= 2;
        }
        
        dicts[i].filing_deadline = new Date(dicts[i].filing_deadline);
        dicts[i].primary_election = new Date(dicts[i].primary_election);
        dicts[i].cumulative_weight = cumulative_weight + dicts[i].weight;
        cumulative_weight = dicts[i].cumulative_weight;
    }
    
    console.log('Cumulative weight:', cumulative_weight);
    return dicts;
}

function pick_random_candidate(candidates)
{
    console.log('Loaded candidates:', candidates.length);
    
    var total_weight = candidates[candidates.length - 1].cumulative_weight,
        random_cutoff = Math.random() * total_weight;
    
    for(var i = 0; i < candidates.length; i++)
    {
        if(candidates[i].cumulative_weight > random_cutoff)
        {
            return show_candidate(candidates[i]);
        }
    }
}

function show_candidate(candidate)
{
    console.log('Random candidate:', candidate.name, candidate);
    document.getElementById('name1').innerHTML = candidate.name;
    document.getElementById('name2').innerHTML = candidate.name;
    
    if(candidate.incumbent) {
        document.getElementById('verb').innerHTML = 'running as an incumbent';

    } else if(candidate.pronouns) {
        var possessive = candidate.pronouns.split('/')[1];
        document.getElementById('verb').innerHTML = 'seeking '+possessive+' first term';

    } else {
        document.getElementById('verb').innerHTML = 'seeking their first term';
    }
    
    if((new Date()) < candidate.primary_election)
    {
        document.getElementById('election').innerHTML = [
            candidate.state, 'primary election is coming up',
            candidate.primary_election.toLocaleDateString()].join(' ');
    }
    
    if(candidate.reason == 'Redistricting') {
        document.getElementById('reason').innerHTML = ['The',
            candidate.chamber, 'will determine', candidate.state,
            'district boundaries for 2021-2030, including U.S. Congressional',
            'districts. A win by', candidate.name, 'helps a once-in-a-decade',
            'chance to control redistricting.'].join(' ');
    
    } else if(candidate.reason == 'Senate Control') {
        document.getElementById('reason').innerHTML = ['The U.S. Senate approves',
        'judicial nominees and determines the makeup of the Supreme Court.',
        'A win by', candidate.name, 'helps Democrats win the Senate.'].join(' ');
    
    } else {
        document.getElementById('reason').style.display = 'none';
    }
    
    var phrase = ['the', candidate.state, candidate.chamber, 'in District', candidate.district].join(' '),
        search = [candidate.name, candidate.state, candidate.chamber, 'District', candidate.district].join(' ');
    
    if(candidate.chamber == 'U.S. Senate')
    {
        phrase = ['the', candidate.chamber, 'in', candidate.state].join(' ');
        search = [candidate.name, candidate.chamber, candidate.state].join(' ');
    }
    
    if(candidate.donation_url) {
        document.getElementById('link').href = candidate.donation_url;

    } else {
        document.getElementById('link').href = 'https://www.google.com/search?q=support+campaign+' + escape(search);
    }

    document.getElementById('race').innerHTML = phrase;
    document.getElementById('candidate').style.display = 'block';
}

function load_states(url)
{
    var request = new XMLHttpRequest();
    request.open('GET', url, true);

    request.onload = function()
    {
        if(request.status >= 200 && request.status < 400)
        {
            // Returns a dict with head and rows lists
            var data = JSON.parse(request.responseText);
            show_states(make_state_dicts(data['head'], data['rows']));
            return;
        }
    };

    request.onerror = function() { /* There was a connection error of some sort */ };
    request.send();
}

function make_state_dicts(head, rows)
{
    var dicts = [];
    
    for(var i = 0; i < rows.length; i++)
    {
        dicts.push({});

        for(var j = 0; j < head.length; j++)
        {
            dicts[i][head[j]] = rows[i][j];
        }

        dicts[i].filing_deadline = new Date(dicts[i].filing_deadline);
        dicts[i].primary_election = new Date(dicts[i].primary_election);
    }
    
    return dicts;
}

function show_states(states)
{
    var first_row = document.getElementById('first-state'),
        table_body = first_row.parentNode,
        template_row = table_body.removeChild(first_row);
    
    for(var i = 0; i < states.length; i++)
    {
        var new_row = template_row.cloneNode(true),
            row_cells = new_row.getElementsByTagName('TD');
        
        row_cells[0].innerHTML = states[i].state;
        row_cells[1].innerHTML = states[i].chamber;
        row_cells[2].innerHTML = states[i].reason;
        
        if(states[i].filing_deadline < (new Date())) {
            row_cells[3].innerHTML = ('<strike>' 
                + states[i].filing_deadline.toLocaleDateString() + '</strike>');
        
        } else {
            row_cells[3].innerHTML = states[i].filing_deadline.toLocaleDateString();
        }
        
        if(states[i].primary_election < (new Date())) {
            row_cells[4].innerHTML = ('<strike>' 
                + states[i].primary_election.toLocaleDateString() + '</strike>');
        
        } else {
            row_cells[4].innerHTML = states[i].primary_election.toLocaleDateString();
        }

        if(states[i].detail_url)
        {
            row_cells[5].innerHTML = ('<a href="' + states[i].detail_url + '">' 
                + 'Ballotpedia</a>');
        }

        table_body.appendChild(new_row);
    }
}
