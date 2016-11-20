import requests
import json
import csv
import sys
import datetime
import time
import getopt


FPL_URL = "https://fantasy.premierleague.com/drf/"
USER_SUMMARY_SUBURL = "element-summary/"
LEAGUE_CLASSIC_STANDING_SUBURL = "leagues-classic-standings/"
LEAGUE_H2H_STANDING_SUBURL = "leagues-h2h-standings/"
TEAM_ENTRY_SUBURL = "entry/"
PLAYERS_INFO_SUBURL = "bootstrap-static"
PLAYERS_INFO_FILENAME_OLD = "allPlayersInfo.json"
PLAYERS_INFO_FILENAME_NEW = "allPlayersInfoNew.json"
TRANSFER_SUBURL = "transfers"
CURRENT_EVENT = "event/12"

USER_SUMMARY_URL = FPL_URL + USER_SUMMARY_SUBURL
PLAYERS_INFO_URL = FPL_URL + PLAYERS_INFO_SUBURL

START_PAGE = 1

def getPlayersInfo():
  r = requests.get(PLAYERS_INFO_URL)
  jsonResponse = r.json()
  jsonResponse['elements'] = insertTransferHistory(jsonResponse);
  with open(PLAYERS_INFO_FILENAME_NEW, 'w') as outfile:
    json.dump(jsonResponse, outfile)


def insertTransferHistory(newJson):

  with open(PLAYERS_INFO_FILENAME_OLD, 'r') as outfile:
    oldJson = json.load(outfile)

  oldJson = oldJson['elements']
  newJson = newJson['elements']
  todayDate = str(datetime.date.today())
  todayUnix = int(time.mktime(datetime.datetime.strptime(todayDate, "%Y-%m-%d").timetuple()))  
  todayUnixMs = str(todayUnix) + '000'
  changes = 0


  for counter in range(0,598):

    newJson[counter]['change_history'] = oldJson[counter]['change_history']
    if oldJson[counter]['now_cost'] != newJson[counter]['now_cost']:

      changes += 1

      print '\nDifference Found'       
      print str(oldJson[counter]['now_cost']) + str(newJson[counter]['now_cost'])
      print newJson[counter]['web_name']

      newJson[counter]['change_history'][todayUnixMs] = newJson[counter]['now_cost'] - oldJson[counter]['now_cost']
  if changes == 0:
    print 'No Changes'

  return newJson


def calculateTrueValue(teamId,playerInfo):
  r = requests.get(FPL_URL + TEAM_ENTRY_SUBURL + teamId + '/' + TRANSFER_SUBURL)
  debug(FPL_URL + TEAM_ENTRY_SUBURL + teamId + '/' + TRANSFER_SUBURL)
  jsonResponse = r.json()
  history = jsonResponse['history']
  transferProfit = int(jsonResponse['entry']['bank'])
  topIndex = len(history) - 1

  for i in range(0,topIndex):
    transferProfit += history[i]['element_out_cost']
    transferProfit -= history[i]['element_in_cost']

  print transferProfit

  r = requests.get(FPL_URL + TEAM_ENTRY_SUBURL + teamId + '/' + CURRENT_EVENT)
  jsonResponse = r.json()

  entryData = jsonResponse
  currentTeam = jsonResponse['picks']

  currentTeamValue = 0

  for j in range(0,15):
    boughtFor = 0

    found = 0
    playerId = currentTeam[j]['element']
    priceDifference = 0

    for k in range(topIndex, 0, -1):
      if playerId == history[k]['element_in']:
        priceDifference = int(playerInfo[playerId - 1]['now_cost']) - int(history[k]['element_in_cost']) 
        debug('Found ' + unicode(playerInfo[playerId - 1]['web_name']) + ' in transfers')
        debug('Difference ' + str(priceDifference))
        found = 1
        break

    if not(found):
      priceDifference = int(playerInfo[playerId - 1]['cost_change_start'])
      debug('Getting base value for ' + unicode(playerInfo[playerId - 1]['web_name']))
      debug('Difference ' + str(priceDifference))


    if priceDifference <= 0:
      debug('Price is negative or even. Adding player price to total')
      currentTeamValue += playerInfo[playerId - 1]['now_cost']

    else:
      debug('Price is positive. Adding ' + str(int(playerInfo[playerId - 1]['now_cost']) - (priceDifference/2)))
      currentTeamValue += int(playerInfo[playerId - 1]['now_cost']) - priceDifference + (priceDifference/2)

  print 'Value on field: ' + str(currentTeamValue)
  print 'Bank: ' + str(entryData['entry']['bank'])

def doStuff(operation,teamId):

  with open(PLAYERS_INFO_FILENAME_NEW, 'r') as outfile:
    playerInfo = json.load(outfile)
  
  playerInfo = playerInfo['elements']

  if operation == 'value':
    print 'Calculating true value'
    calculateTrueValue(teamId,playerInfo)
  
def debug(message):
  print message

def main(argv):

  players = {
    'Toby':'733529',
    'Andy':'159227',
    'Joe':'1809398'
  }
  
  team = ''

  try:
    #args = -u (update) -t [team number] -o ['value']
    opts, args = getopt.getopt(argv,"ut:o:") 
  except getopt.GetoptError:
    print 'bad args'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-u':
      print 'Updating...'
      getPlayersInfo()
    if opt == '-t':
      try:
        team = players[arg]
      except:
        team = arg
    if opt == '-o':
      debug(players['Andy'])
      doStuff(arg,team)

if __name__ == "__main__":
   main(sys.argv[1:])









    