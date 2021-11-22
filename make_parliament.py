from os import name
from bs4 import BeautifulSoup, NavigableString
import csv
import re
from math import ceil
from pprint import pprint
import json

template = ''
with open('template.html', 'r') as t_file:
  for line in t_file:
    template += line

YEAR_SEATS = {2019: 338, 2021: 338}
PARTY_NAMES = ['Liberal', 'Conservative', 'NDP-New Democratic Party', 'Green Party', 'VCP', "People's Party", 'Christian Heritage Party',
'Independent', 'National Citizens Alliance', 'Communist', 'Animal Protection Party', 'Libertarian', 'Parti Rhinocéros Party', 'Bloc Québécois',
'Radical Marijuana', "l'Indépendance du Québec", 'ML', 'PC Party', 'Nationalist', "CFF - Canada's Fourth Front", 'UPC',
'Stop Climate Change', 'Free Party Canada', 'Parti Patriote', 'Maverick Party', 'Centrist']
TRANSLATE_NAMES = {"People's Party - PPC": "People's Party", 'Marxist-Leninist': 'ML', 'Marijuana Party': 'Radical Marijuana',
"Pour l'Indépendance du Québec": "l'Indépendance du Québec", 'No Affiliation': 'Independent'}

def make_year_html(year):
  return f"""
  <div id="_{year}" class="year">
    <h2>{year}</h2>
    <div class="vertical">
      <div class="unrepresented">
        <h3>Parliament of the Unrepresented</h3>
        <table class="house">
        </table>
      </div>
      <div class="represented">
        <h3>House of Commons</h3>
        <table class="house">
        </table>
      </div>
    </div>
  </div>"""

def assign_seats(doc,num_seats,SEATS_PER_AISLE,year,curr_parties,party_winners,rep_status):
  row_count = ceil(num_seats/(SEATS_PER_AISLE*2))

  for row_i in range(row_count):
    row = doc.new_tag('tr', id=f'row_{year}_{rep_status}_{row_i}')
    doc.find(id=f'_{year}').find(class_=rep_status).find('table').append(row)

  gov_seat_count = 0
  opp_seat_count = 0
  last_row_seat_count = num_seats - (row_count-1)*(SEATS_PER_AISLE*2)
  
  for party in curr_parties:
    for winner in party_winners[party]:
      offset = 0
      threshold = ((row_count-1)*SEATS_PER_AISLE)+last_row_seat_count/2
      if gov_seat_count > threshold or opp_seat_count > threshold:
        offset = (SEATS_PER_AISLE*2)-last_row_seat_count
      if party == curr_parties[0]:
        group = ((gov_seat_count+offset)//SEATS_PER_AISLE)
        gov_seat_count += 1
      else:
        group = ((opp_seat_count+offset)//SEATS_PER_AISLE)
        opp_seat_count += 1
      row = group if group < row_count else row_count-(1 + group - row_count)
      row_id = f'row_{year}_{rep_status}_{row}'
      if party != curr_parties[0] and len(doc.find(id=row_id).find_all(recursive=False)) == 0:
        blank = doc.new_tag('td')
        doc.find(id=row_id).append(blank)
        blank['class'] = 'aisle'

      cell = doc.new_tag('td')
      if opp_seat_count <= num_seats/2:
        doc.find(id=row_id).append(cell)
      else:
        doc.find(id=row_id).insert(0,cell)
      cell['class'] = 'seat '+'_'.join(party.replace('\'','').split(' '))
      if winner[2]:
        dot = doc.new_tag('div')
        cell.append(dot)
        dot['class'] = 'in_parliament'
      cell['title'] = f'{winner[0]}: {winner[1]} {rep_status} votes'
      #UNCOMMENT if bug appears:
      # doc = BeautifulSoup(str(doc), 'html.parser') #find requires
      if (
        doc.find(id=row_id).select_one(".aisle") is None and 
        (len(doc.find(id=row_id).find_all(recursive=False)) == SEATS_PER_AISLE
        or winner[0] == party_winners[curr_parties[0]][-1][0])
      ):
        blank = doc.new_tag('td')
        doc.find(id=row_id).append(blank)
        blank['class'] = 'aisle'
  return doc

def make_parliament(doc, candidates, year):
  districts = {}
  party_candidate_vote = {}
  party_total_vote = {}
  total_rep_votes = 0
  total_unrep_votes = 0
  party_unrep_winners = {}
  party_rep_winners = {}
  SEATS_PER_AISLE = 10
  curr_parties = []
  for candidate in candidates:
    (district_name, district_num, name, party, votes, name_and_party) = (candidate['district_name'],candidate['district_num'],candidate['name'],candidate['party'],candidate['votes'],candidate['name_and_party'])
    votes = int(votes)
    if district_num not in districts:
      districts[district_num] = {}
      districts[district_num]['district_name'] = district_name
      districts[district_num] = {'candidate_votes': {name_and_party: votes}}
      districts[district_num]['total_votes'] = votes
      districts[district_num]['winner'] = name_and_party
      districts[district_num]['runner_up'] = 'none'
    else:
      districts[district_num]['candidate_votes'][name_and_party] = votes
      districts[district_num]['total_votes'] += votes
      if votes > districts[district_num]['candidate_votes'][districts[district_num]['winner']]:
        districts[district_num]['runner_up'] = districts[district_num]['winner']
        districts[district_num]['winner'] = name_and_party
      elif districts[district_num]['runner_up'] == 'none' or votes > districts[district_num]['candidate_votes'][districts[district_num]['runner_up']]:
        districts[district_num]['runner_up'] = name_and_party

    if party not in curr_parties:
      curr_parties += [party]

  for candidate in candidates:
    (district_name, district_num, name, party, votes, name_and_party) = (candidate['district_name'],candidate['district_num'],candidate['name'],candidate['party'],candidate['votes'],candidate['name_and_party'])
    votes = int(votes)

    rep_votes = 0
    unrep_votes = votes
    if name_and_party == districts[district_num]['winner']:
      rep_votes = districts[district_num]['candidate_votes'][districts[district_num]['runner_up']]+1
      unrep_votes = votes - rep_votes

    total_rep_votes += rep_votes
    total_unrep_votes += unrep_votes
    
    if party not in party_candidate_vote:
      party_candidate_vote[party] = {name: {'rep_votes': rep_votes, 'unrep_votes': unrep_votes}}
      party_total_vote[party] = {'rep_votes': rep_votes, 'unrep_votes': unrep_votes}
    else:
      party_candidate_vote[party][name] = {'rep_votes': rep_votes, 'unrep_votes': unrep_votes}
      party_total_vote[party]['rep_votes'] += rep_votes
      party_total_vote[party]['unrep_votes'] += unrep_votes

  seats_in_unrep_parliament = round(YEAR_SEATS[year]*total_unrep_votes/total_rep_votes)
  print(year,total_rep_votes/YEAR_SEATS[year], 'votes/elected member')
  new_seat_count = 0

  for party in curr_parties:
    party_total_vote[party]['seats'] = round(seats_in_unrep_parliament*party_total_vote[party]['unrep_votes']/total_unrep_votes)
    new_seat_count += party_total_vote[party]['seats']
    # print(party,'rep votes=',party_total_vote[party]['rep_votes'], 
    # 'unrep votes=',party_total_vote[party]['unrep_votes'],
    # 'unrep seats=',round(seats_in_unrep_parliament*party_total_vote[party]['unrep_votes']/total_unrep_votes))

    # print(party_candidate_vote[party])
    party_unrep_winners[party] = []
    party_rep_winners[party] = {}
    for candidate in list(party_candidate_vote[party]):
      x=(candidate, 
        party_candidate_vote[party][candidate]['unrep_votes'], 
        party_candidate_vote[party][candidate]['rep_votes'] > 0) 
      party_unrep_winners[party] += [x]
      if x[2]:
        party_rep_winners[party][candidate] = [candidate, party_candidate_vote[party][candidate]['rep_votes'], False]
    party_unrep_winners[party] = sorted(party_unrep_winners[party], key=lambda candidate: candidate[1]*-1)[:party_total_vote[party]['seats']]
    for candidate_tuple in party_unrep_winners[party]:
      if candidate_tuple[2]:
        party_rep_winners[party][candidate_tuple[0]][2] = True
    party_rep_winners[party] = list(party_rep_winners[party].values())
    party_rep_winners[party] = sorted(party_rep_winners[party], key=lambda candidate: candidate[1]*-1)
    

    # print(party,'winners:')
    # print(json.dumps(party_unrep_winners[party], indent=2))

  # print('unrep seats', seats_in_unrep_parliament, new_seat_count)
  seats_in_unrep_parliament = new_seat_count
  curr_unrep_parties = sorted(curr_parties, key=lambda party: -len(party_unrep_winners[party]))
  curr_rep_parties = sorted(curr_parties, key=lambda party: -len(party_rep_winners[party]))
  # print(curr_parties)
  year_div = BeautifulSoup(make_year_html(year),'html.parser')
  doc.find(class_='vertical').append(year_div)
  doc = assign_seats(doc,seats_in_unrep_parliament,SEATS_PER_AISLE,year,curr_unrep_parties,party_unrep_winners,'unrepresented')
  doc = assign_seats(doc,YEAR_SEATS[year],SEATS_PER_AISLE//2,year,curr_rep_parties,party_rep_winners,'represented')
  return doc


doc = BeautifulSoup(template, 'html.parser')

with open('2019 results by candidate.csv', "r", newline='') as csvfile:
  candidates = csv.reader(csvfile, delimiter=',', quotechar='"')
  candidates = list(candidates)[1:]
candidates_2019 = []
# district_name, district_num, name_and_party, votes
for candidate in candidates:
  (prov, district_name, district_num, name_and_party, residence, occupation, votes, vote_per, maj, maj_per) = candidate
  c = {}
  found = False
  for party in PARTY_NAMES:
    if party in name_and_party:
      found = True
      m = re.finditer(r'(^[^\*]*) [\* ]*'+party, name_and_party)
      name = ''
      for v in m:
        name = v.group(1)
      if name == '':
        raise Exception('no name in', name_and_party)
      else:
        name += f' ({district_name})'
      break
  if not found:
    for party in TRANSLATE_NAMES:
      if party in name_and_party:
        found = True
        m = re.finditer(r'(^[^\*]*) [\* ]*'+party, name_and_party)
        name = ''
        for v in m:
          name = v.group(1)
        if name == '':
          raise Exception('no name in', name_and_party)
        else:
          name += f' ({district_name})'
          party = TRANSLATE_NAMES[party]
        break
  if not found:
    raise Exception('no party for',name_and_party)
  c['district_name'] = district_name
  c['district_num'] = district_num
  c['name'] = name
  c['party'] = party
  c['votes'] = votes
  c['name_and_party'] = f'{name}@{party}'
  candidates_2019 += [c]

with open('2021results_nov14.csv', "r", newline='') as csvfile:
  candidates = csv.reader(csvfile, delimiter='\t')
  candidates = list(candidates)[2:-3]
candidates_2021 = []
# district_name, district_num, name_and_party, votes
for candidate in candidates:
  (district_num, district_name, _, result_type, _, surname, middle_name, given_name, party, _, votes, vote_per, votes_rejected, 
  total_ballots) = candidate
  if result_type == 'validated':
    name = f'{given_name} {surname}'
    c = {}
    found = False
    for party_name in PARTY_NAMES:
      if party_name in party:
        party = party_name
        found = True
        break
    if not found:
      for party_name in TRANSLATE_NAMES:
        if party_name in party:
          party = TRANSLATE_NAMES[party_name]
          found = True
          break
    if not found:
      raise Exception('no party for',name, party)

    c['district_name'] = district_name
    c['district_num'] = district_num
    c['name'] = f'{name} ({district_name})'
    c['party'] = party
    c['votes'] = votes
    c['name_and_party'] = f'{name}@{party}'
    candidates_2021 += [c]

doc = make_parliament(doc, candidates_2019, 2019)
doc = make_parliament(doc, candidates_2021, 2021)

with open("parliament.html", "w") as file:
  file.write(doc.prettify())

# for row in range(row_count):
#   print(f'row {row} count = {len(doc.find(id=f"row_{row}").find_all(recursive=False))}')
