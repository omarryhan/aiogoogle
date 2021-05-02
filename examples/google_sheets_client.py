from googleapiclient.discovery import build
from google.oauth2 import service_account
import google_auth_httplib2
import httplib2

import json
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
import urllib

"""
This client includes both Google synchronous and AIOGoogle asyncronous methods.
loadasyncsheetservice and GetValuesAsync provide the basics for getting AIOGoogle working to read Google sheets.
To use this client add the following lines to your main python script:

import api_client

api_client.InitializeClient(os.path.join('..', 'resources', 'credentials_service.json'))
await api_client.InitializeClientAsync(os.path.join('..', 'resources', 'credentials_service.json'))

Add the following lines to your other python files:

import api_client


values = await api_client.GetClientAsync().GetValuesAsync(MASTER_SPREADSHEET_ID, ADMINS_RANGE_NAME)

or

req = api_client.GetClientAsync()._spreadsheetAsync.values.batchUpdate(spreadsheetId=spreadsheetid, json=body)
await api_client.GetClientAsync()._aiogoogle.as_service_account(req)

"""


class Sheet:
    def __init__(self, sheet):
        properties = sheet.get('properties')
        self.id = properties.get('sheetId')
        self.title = properties.get('title')
        self.index = properties.get('index')
        gridProperties = properties.get('gridProperties')
        self.rows = gridProperties.get('rowCount')
        self.cols = gridProperties.get('columnCount')


class Spreadsheet:
    def __init__(self, spreadsheet):
        self.id = spreadsheet.get('spreadsheetId')
        self.url = spreadsheet.get('spreadsheetUrl')
        self.sheets = list(map(Sheet, spreadsheet.get('sheets')))

    def GetSheetByTitle(self, title):
        for sheet in self.sheets:
            if sheet.title == title:
                return sheet
        raise Exception('no sheet found for title {}'.format(title))


def ToCellData(cell):
    return {'userEnteredValue': {'stringValue': str(cell)}}


def ToRowData(row):
    return {'values': list(map(ToCellData, row))}


class SheetApiClient:
    def __init__(self, serviceAccountFile):
        creds = None
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = service_account.Credentials.from_service_account_file(
            serviceAccountFile, scopes=SCOPES)
        http = httplib2.Http(timeout=200)
        authed_http = google_auth_httplib2.AuthorizedHttp(creds, http=http)
        
        self._sheetService = build('sheets', 'v4', http=authed_http)
        self._spreadsheet = self._sheetService.spreadsheets()

    async def loadasyncsheetservice(self, serviceAccountFile):
        with open(serviceAccountFile, "r") as read_file:
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            credfile = json.load(read_file)
            asynccreds = None
            asynccreds = ServiceAccountCreds(scopes=SCOPES, **credfile)
            async with Aiogoogle(service_account_creds=asynccreds) as aiogoogle:
                self._sheetServiceAsync = await aiogoogle.discover("sheets", "v4")
            self._spreadsheetAsync = self._sheetServiceAsync.spreadsheets
            self.aiogoogle = aiogoogle

    def Create(self, title, sheets=['Sheet1']):
        print('creating sheet, title={}, sheets={}'.format(title, sheets))
        sheetBody = [{'properties': {'title': title}} for title in sheets]
        resp = self._spreadsheet.create(
            body={
                'properties': {
                    'title': title,
                },
                'sheets': sheetBody
            }).execute()
        print(json.dumps(resp))
        return Spreadsheet(resp)

    def Get(self, id):
        resp = self._spreadsheet.get(spreadsheetId=id, includeGridData=False).execute()
        return Spreadsheet(resp)
        
    async def GetAsync(self, id):

        resp = await self.aiogoogle.as_service_account(self._spreadsheetAsync.get(spreadsheetId=id, includeGridData=False))
        return Spreadsheet(resp)

    def GetValues(self, id, range):
        resp = self._spreadsheet.values().get(spreadsheetId=id, range=range).execute()
        return resp.get('values', [])
        
    async def GetValuesAsync(self, id, range):
        resp = await self.aiogoogle.as_service_account(self._spreadsheetAsync.values.get(spreadsheetId=id, range=range))
        return resp.get('values', [])
    
    def BatchGetValues(self, id, ranges):
        resp = self._spreadsheet.values().batchGet(spreadsheetId=id, ranges=ranges).execute()
        return [r.get('values', []) for r in resp.get('valueRanges')]
    
    async def BatchGetValuesAsync(self, id, ranges):
        rangestring = ''
        req = self._spreadsheetAsync.values.batchGet(spreadsheetId=id, ranges=ranges[0])

#        following is a temporary fix for passing multiple ranges in request
        if len(ranges) > 1:
            remainingranges = ranges.copy()
            del remainingranges[0]
            for batchrange in remainingranges:
                rangestring += f'&ranges={urllib.parse.quote_plus(batchrange)}' 
            req.url = req.url + rangestring
        
        resp = await self.aiogoogle.as_service_account(req)
        return [r.get('values', []) for r in resp.get('valueRanges')]

    def AppendValues(self, id, range, values):
        valueRange = {
            'range': range,
            'values': values
        }
        self._spreadsheet.values().append(spreadsheetId=id, range=range, valueInputOption='USER_ENTERED', body=valueRange).execute()

    async def AppendValuesAsync(self, id, range, values):
        valueRange = {
            'range': range,
            'values': values
        }
        await self.aiogoogle.as_service_account(self._spreadsheetAsync.values.append(spreadsheetId=id, range=range, valueInputOption='USER_ENTERED', json=valueRange))

    def BatchUpdateValues(self, id, ranges, values):
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': [{'range': r, 'values': v} for r, v in zip(ranges, values)]
        }
        self._spreadsheet.values().batchUpdate(spreadsheetId=id, body=body).execute()

    async def BatchUpdateValuesAsync(self, id, ranges, values):
        body = {
            "valueInputOption": "USER_ENTERED",
            "data": [{"range": r, "values": v} for r, v in zip(ranges, values)]
        }
        req = self._spreadsheetAsync.values.batchUpdate(spreadsheetId=id, json=body)
        await self.aiogoogle.as_service_account(req)
    
    def UpdateValues(self, id, Range, InsertValues):
        body = {'values': InsertValues}
        self._spreadsheet.values().update(spreadsheetId=id, range=Range, valueInputOption='USER_ENTERED', body=body).execute()

    async def UpdateValuesAsync(self, id, Range, InsertValues):
        body = {'values': InsertValues}
        await self.aiogoogle.as_service_account(self._spreadsheetAsync.values.update(spreadsheetId=id, range=Range, valueInputOption='USER_ENTERED', json=body))

       
defaultClient = None


defaultClientAsync = None


def InitializeClient(serviceAccountFile):
    global defaultClient
    if defaultClient is None:
        defaultClient = SheetApiClient(serviceAccountFile)

    
async def InitializeClientAsync(serviceAccountFile):
    global defaultClient
    global defaultClientAsync
    if defaultClient is None:
        defaultClient = SheetApiClient(serviceAccountFile)
    
    if defaultClientAsync is None:
        defaultClientAsync = await defaultClient.loadasyncsheetservice(serviceAccountFile)
        
    return defaultClientAsync


def GetClient():
    return defaultClient


def GetClientAsync():
    return defaultClientAsync
