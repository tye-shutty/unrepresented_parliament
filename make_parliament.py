from os import name
from bs4 import BeautifulSoup, NavigableString
import csv
import re
from math import ceil
from pprint import pprint
import json

template = """
<html>
  <head>
    <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
    <meta content="utf-8" http-equiv="encoding">
    <style>
    .house tr {
      display: flex;
      justify-content: center;
    }
    .seat{
      height: 16;
      width: 16;
      border: 1px;
      border-color: black;
      border-style: solid;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .aisle{
      height: 16;
      width: 16;
    }
    .in_parliament{
      height: 12;
      width: 12;
      background-color: black;
      border-radius: 50%;
    }
    .Conservative{
      background-color: blue;
    }
    .Green_Party{
      background-color: green;
    }
    .Liberal{
      background-color: red;
    }
    .NDP-New_Democratic_Party{
      background-color: orange;
    }
    .Peoples_Party{
      background-color: violet;
    }
    .Bloc_Québécois{
      background-color: lightblue;
    }
    .Parti_Rhinocéros_Party{
      background-color: brown;
    }
    .Independent{
      background-color: grey;
    }
    .Christian_Heritage_Party{
      background-color: darkmagenta;
    }
    .Libertarian{
      background-color: yellow;
    }
    .vertical {
      display: flex;
    }
    </style>
  </head>

  <body>
    <h1>Parliament of the Unrepresented</h1>
    <p>What if all the voters that didn't matter made their own parliament, with blackjack and proportional representation?</p>
    <p>Voters are unrepresented if they could've stayed home without changing the results. So the only votes that are represented
    are the votes for the winning candidate of an amount equal to the runner up candidate plus 1.</p>
    <p>How many seats should our parliament have? Well I guess it's only fair if we take the number of seats in the House of Commons (HOC)
    multiply that by the number of unrepresented votes divided by represented votes.</p>
    <p>How should we assign seats? Proportional representation, of course, is the best way to improve representation.
    Each party is given a share of seats proportional to its total vote share.</p>
    <p>Who should sit in our parliament? The people the unrepresented voters voted for. In some cases, especially for the top Conservatives,
    they will also sit in the HOC. Below you can see our members ranked (within party) in order from most unrepresented votes to least. Hover over the
    seats to see more information.</p>
    <div class="vertical">
      <div class="unrep_2019">
        <h2>2019 Unrepresented</h2>
        <table class="house unrepresented">
        </table>
      </div>
      <div class="rep_2019">
        <h2>2019 Represented (HOC)</h2>
        <table class="house represented">
        </table>
      </div>
      <div>
        <h3>Legend</h3>
        <table>
          <tr><td><div class="seat in_parliament"/></td><td>sits in both parliaments</td></tr>
          <tr><td class="seat Conservative"></td><td>Conservative</td></tr>
          <tr><td class="seat Liberal"></td><td>Liberal</td></tr>
          <tr><td class="seat NDP-New_Democratic_Party"></td><td>New Democratic</td></tr>
          <tr><td class="seat Green_Party"></td><td>Green</td></tr>
          <tr><td class="seat Bloc_Québécois"></td><td>Bloc Québécois</td></tr>
          <tr><td class="seat Peoples_Party"></td><td>People's</td></tr>
          <tr><td class="seat Independent"></td><td>Independent</td></tr>
          <tr><td class="seat Christian_Heritage_Party"></td><td>Christian Heritage</td></tr>
          <tr><td class="seat Libertarian"></td><td>Libertarian</td></tr>
          <tr><td class="seat Parti_Rhinocéros_Party"></td><td>Rhinocéros</td></tr>
        </table>
      </div>
    </div>
  </body>
</html>
"""

doc = BeautifulSoup(template, 'html.parser')

with open('2019 results by candidate.csv', "r", newline='') as csvfile:
  candidates = csv.reader(csvfile, delimiter=',', quotechar='"')
  candidates = list(candidates)[1:]

districts = {}
party_names = ['Liberal', 'Conservative', 'NDP-New Democratic Party', 'Green Party', 'VCP', "People's Party", 'Christian Heritage Party',
'Independent', 'National Citizens Alliance', 'Communist', 'Animal Protection Party', 'Libertarian', 'Parti Rhinocéros Party', 'Bloc Québécois',
'Radical Marijuana', "l'Indépendance du Québec", 'ML', 'No Affiliation', 'PC Party', 'Nationalist', "CFF - Canada's Fourth Front", 'UPC',
'Stop Climate Change']
party_candidate_vote = {}
party_total_vote = {}
total_rep_votes = 0
total_unrep_votes = 0
SEATS_IN_PARLIAMENT = 338
party_winners = {}
SEATS_PER_AISLE = 10

for candidate in candidates:
  (prov, district_name, district_num, name_and_party, residence, occupation, votes, vote_per, maj, maj_per) = candidate
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


for candidate in candidates:
  (prov, district_name, district_num, name_and_party, residence, occupation, votes, vote_per, maj, maj_per) = candidate
  votes = int(votes)

  rep_votes = 0
  unrep_votes = votes
  if name_and_party == districts[district_num]['winner']:
    rep_votes = districts[district_num]['candidate_votes'][districts[district_num]['runner_up']]+1
    unrep_votes = votes - rep_votes

  total_rep_votes += rep_votes
  total_unrep_votes += unrep_votes
  found = False
  for party in party_names:
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
      if party not in party_candidate_vote:
        party_candidate_vote[party] = {name: {'rep_votes': rep_votes, 'unrep_votes': unrep_votes}}
        party_total_vote[party] = {'rep_votes': rep_votes, 'unrep_votes': unrep_votes}
      else:
        party_candidate_vote[party][name] = {'rep_votes': rep_votes, 'unrep_votes': unrep_votes}
        party_total_vote[party]['rep_votes'] += rep_votes
        party_total_vote[party]['unrep_votes'] += unrep_votes

      break
  if not found:
    raise Exception('no party for',name_and_party)

seats_in_unrep_parliament = round(SEATS_IN_PARLIAMENT*total_unrep_votes/total_rep_votes)
new_seat_count = 0

for party in party_names:
  party_total_vote[party]['seats'] = round(seats_in_unrep_parliament*party_total_vote[party]['unrep_votes']/total_unrep_votes)
  new_seat_count += party_total_vote[party]['seats']
  # print(party,'rep votes=',party_total_vote[party]['rep_votes'], 
  # 'unrep votes=',party_total_vote[party]['unrep_votes'],
  # 'unrep seats=',round(seats_in_unrep_parliament*party_total_vote[party]['unrep_votes']/total_unrep_votes))

  # print(party_candidate_vote[party])
  party_winners[party] = []
  for candidate in list(party_candidate_vote[party]):
    x=(candidate, 
      party_candidate_vote[party][candidate]['unrep_votes'], 
      party_candidate_vote[party][candidate]['rep_votes'] > 0) 
    # print(x)
    party_winners[party] += [x]
  party_winners[party] = sorted(party_winners[party], key=lambda candidate: candidate[1]*-1)[:party_total_vote[party]['seats']]
  # print()
  # print(party,'winners:')
  # print(json.dumps(party_winners[party], indent=2))

# print('unrep seats', seats_in_unrep_parliament, new_seat_count)
seats_in_unrep_parliament = new_seat_count
party_names.sort(key=lambda party: -len(party_winners[party]))
# print(party_names)
row_count = ceil(seats_in_unrep_parliament/(SEATS_PER_AISLE*2))
# print(row_count)

for row_i in range(row_count):
  row = doc.new_tag('tr', id=f'row_2019_{row_i}')
  doc.find(class_='unrep_2019').find('table', class_='unrepresented').append(row)

gov_seat_count = 0
opp_seat_count = 0
last_row_seat_count = seats_in_unrep_parliament - (row_count-1)*(SEATS_PER_AISLE*2)
# print('lrc',last_row_seat_count)
for party in party_names:
  for winner in party_winners[party]:
    # if party == 'Independent':
    #   print(seat_count, row_count, (seat_count//5) % row_count)
    offset = 0
    threshold = ((row_count-1)*SEATS_PER_AISLE)+last_row_seat_count/2
    if gov_seat_count > threshold or opp_seat_count > threshold:
      offset = (SEATS_PER_AISLE*2)-last_row_seat_count
    if party == party_names[0]:
      group = ((gov_seat_count+offset)//SEATS_PER_AISLE)
      gov_seat_count += 1
    else:
      group = ((opp_seat_count+offset)//SEATS_PER_AISLE)
      opp_seat_count += 1
    row = group if group < row_count else row_count-(1 + group - row_count)
    row_id = f'row_2019_{row}'
    # print(row_id)
    if party != party_names[0] and len(doc.find(id=row_id).find_all(recursive=False)) == 0:
      blank = doc.new_tag('td')
      doc.find(id=row_id).append(blank)
      blank['class'] = 'aisle'

    cell = doc.new_tag('td')
    if opp_seat_count <= seats_in_unrep_parliament/2:
      doc.find(id=row_id).append(cell)
    else:
      doc.find(id=row_id).insert(0,cell)
    cell['class'] = 'seat '+'_'.join(party.replace('\'','').split(' '))
    # cell['winner'] = winner[0]
    if winner[2]:
      dot = doc.new_tag('div')
      cell.append(dot)
      dot['class'] = 'in_parliament'
    # name = doc.new_tag('div')
    # cell.append(name)
    cell['title'] = f'{winner[0]}: {winner[1]} unrepresented votes'
    # name.contents.append(NavigableString(winner[0]))
    # name.contents.append(NavigableString(f'{winner[1]} unrepresented votes'))
    #UNCOMMENT (slow but needed):
    # doc = BeautifulSoup(str(doc), 'html.parser') #find requires
    if (
      doc.find(id=row_id).select_one(".aisle") is None and 
      (len(doc.find(id=row_id).find_all(recursive=False)) == SEATS_PER_AISLE
      or winner[0] == party_winners[party_names[0]][-1][0])
    ):
      # if row == 64:
      #   print(doc.find(id=row_id).prettify())
      blank = doc.new_tag('td')
      doc.find(id=row_id).append(blank)
      blank['class'] = 'aisle'

with open("parliament2019.html", "w") as file:
  file.write(doc.prettify())

# for row in range(row_count):
#   print(f'row {row} count = {len(doc.find(id=f"row_{row}").find_all(recursive=False))}')
