import urllib.parse
import urllib.request
import bs4
from dateutil import parser

gotSoccerScheduleURL = "https://system.gotsport.com/org_event/events/13587/schedules?team=575437"
gotSoccerRootUrlParts = urllib.parse.urlparse(gotSoccerScheduleURL)
gotSoccerRootUrl = gotSoccerRootUrlParts[0] + "://" + gotSoccerRootUrlParts[1]

gotSoccerUrlRequest = urllib.request.urlopen(gotSoccerScheduleURL)
gotSoccerParsed = bs4.BeautifulSoup(gotSoccerUrlRequest, features="html.parser")
schedule_items = gotSoccerParsed.find_all("div", {"class": "hidden-xs"})
teamSchedule = []
addressCache = {}

for items in schedule_items:
    possibleDateHeader = items.findChildren("h4")
    possibleGameDataRow = items.findChildren("tbody")
    if len(possibleDateHeader) > 0:
        gameATags = possibleGameDataRow[0].findChildren("a")
        gameDateStr = possibleDateHeader[0].text
        gameInfo = possibleGameDataRow[0].text.split("\n\n\n")
        gameTimeStr = gameInfo[2].strip()

        locationATag = gameATags[3]
        locationUrl = gotSoccerRootUrl + locationATag.get('href')
        locationAddress = addressCache.get(locationUrl);
        if locationAddress is None:
            locationUrlRequest = urllib.request.urlopen(locationUrl)
            locationUrlParsed = bs4.BeautifulSoup(locationUrlRequest, features="html.parser")
            locationAddressDivs = locationUrlParsed.find_all("div", {"class": "widget-body"})
            locationAddressDiv = locationAddressDivs[1]
            locationAddress = locationAddressDiv.text.strip().replace("Export Pitch Schedule", "")
            while '\n\n' in locationAddress:
                locationAddress = locationAddress.replace("\n\n", "\n")
            addressCache.update({locationUrl: locationAddress})

        eventRow = {}
        eventRow.update({'matchId': gameInfo[1].strip()})
        eventRow.update({'gameDateTime': parser.parse(gameDateStr + " " + gameTimeStr)})
        eventRow.update({'homeTeam': gameInfo[4].strip()})
        eventRow.update({'results': gameInfo[5].strip()})
        eventRow.update({'awayTeam': gameInfo[6].strip()})
        eventRow.update({'locationName': gameInfo[7].strip()})
        eventRow.update({'locationUrl': locationUrl})
        eventRow.update({'locationAddress': locationAddress})
        teamSchedule.append(eventRow)

print(teamSchedule)
