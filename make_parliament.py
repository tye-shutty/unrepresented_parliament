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
'Independent', 'National Citizens Alliance', 'Communist', 'Animal Protection Party', 'Libertarian']
parties = {}
total_rep_votes = 0
total_unrep_votes = 0

for candidate in candidates:
  (prov, district_name, district_num, name_and_party, residence, occupation, votes, vote_per, maj, maj_per) = candidate
  votes = int(votes)

  if district_num not in districts:
    districts[district_num]['district_name'] = district_name
    districts[district_num] = {'candidate_votes': {name_and_party: votes}}
    districts[district_num]['total_votes'] = votes
    districts[district_num]['winner'] = name_and_party
  else:
    districts[district_num]['candidate_votes'][name_and_party] = votes
    districts[district_num]['total_votes'] += votes
    if votes > districts[district_num]['candidate_votes'][districts[district_num]['winner']]:
      districts[district_num]['runner_up'] = districts[district_num]['winner']
      districts[district_num]['winner'] = name_and_party
    elif votes > districts[district_num]['candidate_votes'][districts[district_num]['runner_up']]:
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
      if party not in parties:
        parties[party] = {name: {'rep_votes': rep_votes, 'unrep_votes': unrep_votes}}
      else:
        parties[party][name] = votes

      break
  if not found:
    raise Exception('no party for',name_and_party)





# print(doc.prettify())
