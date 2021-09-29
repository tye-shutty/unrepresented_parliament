from os import name
from bs4 import BeautifulSoup
import csv
import re

template = """
<html>
  <head>
    <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
    <meta content="utf-8" http-equiv="encoding">
  </head>

  <body>
    <table>
    </table>
    <p class="overview">
      Test
    </p>
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
print(seats_in_unrep_parliament, 'unrep seats')

for party in party_names:
  party_total_vote[party]['seats'] = round(seats_in_unrep_parliament*party_total_vote[party]['unrep_votes']/total_unrep_votes)
  # print(party,'rep votes=',party_total_vote[party]['rep_votes'], 
  # 'unrep votes=',party_total_vote[party]['unrep_votes'],
  # 'unrep seats=',round(seats_in_unrep_parliament*party_total_vote[party]['unrep_votes']/total_unrep_votes))

  # print(party_candidate_vote[party])
  party_winners[party] = [(candidate, party_candidate_vote[party][candidate]['unrep_votes']) for candidate in list(party_candidate_vote[party])]
  party_winners[party] = sorted(party_winners[party], key=lambda candidate: candidate[1]*-1)[:party_total_vote[party]['seats']]
  # print(party,'winners:',party_winners[party])

# new_tag = doc.new_tag('a',href='blah')
# doc.find('p').append(new_tag)
# doc.find('body').insert(0,new_tag)

party_names.sort(key=lambda party: -len(party_winners[party]))
# print(party_names)

# print(doc.prettify())
