import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from .exceptions import *

class GoogleManager(object):

    def __init__(self, authtype="service", folderId=None, secretsFile=None, scopes=None, resource="drive", api_version="v3"):
        self.allowed_authtypes = ["service"]
        self.folderid = folderId
        self.service = None
        try:
            if authtype not in self.allowed_authtypes:
                raise BadAuthtypeException("Authtype % is not allowed." % authtype)
            elif authtype == "service":
                credentials = service_account.Credentials.from_service_account_file(secretsFile, scopes=scopes)
            self.service = build(resource, api_version, credentials=credentials)
        except Exception as err:
            raise GoogleAuthException(err)


    def list_files(self):
        if self.service:
            kwargs = {"supportsAllDrives": True,
                      "includeItemsFromAllDrives": True,
                      "fields": "files(id,parents,name)"}
            if self.folderid:
                kwargs["q"] = "'%s' in parents" % self.folderid
            request = self.service.files().list(**kwargs).execute()
            return request["files"]

    def upload_file(self, infile=None, upload_name=None, folderId=None, mtype="text/plain", meta_mtype="text/plain"):

        if os.path.exists(infile):
            if not upload_name:
                upload_name = infile.split("/")[-1]
            if folderId:
                self.folderid = folderId
            filemeta = {"name": upload_name,
                        "mimeType": meta_mtype,
                        "parents": [self.folderid]}
            data = MediaFileUpload(infile,
                                   mimetype=mtype,
                                   resumable=False)
            try:
                upfile = self.service.files().create(body=filemeta,
                                                     media_body=data,
                                                     supportsAllDrives=True,
                                                     fields="id").execute()
                return upfile.get("id")
            except Exception as err:
                raise GoogleUploadException(err)
        else:
            raise MissingFileException("The file '%s' cannot be found." % infile)

    def download_file_contents(self, fileId=None, convert=True):
        # Note: this doesn't work on Workspace Doctypes (e.g. Sheets)!
        # Use self.export_sheet_contents() for those
        try:
            request = self.service.files().get_media(fileId=fileId)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        except Exception as err:
            raise GoogleDownloadException(err)
        else:
            return file.getbuffer()

    def export_sheet_contents(self, fileId=None, export_type="text/tab-separated-values"):
        try:
            request = self.service.files().export(fileId=fileId, mimeType=export_type).execute()
        except Exception as err:
            raise GoogleSheetExportException(err)
        else:
            return request
    
    def get_tab_contents(self, fileId=None, tab_range=None):
        sheet = self.service.spreadsheets()
        result = sheet.values().get(
                spreadsheetId=fileId,
                range=tab_range).execute()
        try:
            data = result.get('values',[])
        except Exception as err:
            raise GoogleSheetExportException(err)
        else:
            return data
        
    def get_tab_names(self, fileId=None):
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=fileId).execute()
        try:
            tab_names = [sheet['properties']['title'] for sheet in sheet_metadata.get('sheets', [])]
        except Exception as err:
            raise GoogleSheetExportException(err)
        else:
            return tab_names

    def reparent_file(self, fileId=None, removeParents=None, addParents=None):
        try:
            kwargs = {"supportsAllDrives": True}
            request = self.service.files().update(fileId=fileId, removeParents=removeParents, addParents=addParents, **kwargs).execute()
        except Exception as err:
            raise GoogleReparentException(err)
        else:
            return request

