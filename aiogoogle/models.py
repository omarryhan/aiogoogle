from urllib.parse import urlparse, parse_qsl, urlunparse
from urllib.parse import urlencode
from dataclasses import dataclass


class ResumableUpload:
    ''' Works in conjustion with media upload '''
    def __init__(self, file_path, multipart=None, upload_path=None):
        '''
        file_path: Full path of the file to be uploaded
        upload_path: The URI path to be used for upload. Should be used in conjunction with the rootURL property at the API-level.
        multipart: True if this endpoint supports upload multipart media.
        '''
        self.file_path = file_path
        self.upload_path = upload_path
        self.multipart = multipart

class MediaUpload:
    def __init__(self, file_path, upload_path=None, mime_range=None, max_size=None, multipart=False, resumable=None):
        '''
        file_path: Full path of the file to be uploaded
        upload_path: The URI path to be used for upload. Should be used in conjunction with the rootURL property at the API-level.
        mime_range: list of MIME Media Ranges for acceptable media uploads to this method.
        max_size: Maximum size of a media upload, such as "1MB", "2GB" or "3TB".
        multipart: True if this endpoint supports upload multipart media.
        resumable: A ResumableUpload object
        '''
        self.file_path = file_path
        self.upload_path = upload_path
        self.mime_range = mime_range
        self.max_size = max_size
        self.multipart = multipart
        self.resumable = resumable

class MediaDownload:
    def __init__(self, file_path):
        '''
        file_path: Full path of the file to be downloaded
        '''
        self.file_path = file_path

class Request:
    '''
    Request class for the whole library. Auth Managers, GoogleAPI and Sessions should all use this
    '''

    def __init__(
        self, method=None, url=None, headers=None, json=None, data=None,
        media_upload=None, media_download=None, timeout=None):
        '''
        Parameters:

            method: HTTP method as a string (upper case) e.g. 'GET'
            url: full url as a string. e.g. 'https://example.com/api/v1/resource?filter=filter#something
            headers: headers as a dict
            
            HTTP BODY (Only pass one of the following):
              
              - json: json as a dict
              - data: www-url-form-encoded form as a dict/ bytes/ text/ 

            media_download: MediaDownload object
            media_upload: MediaUpload object
            timeout: total request timeout in seconds

        '''
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data
        self.json = json
        self.media_upload = media_upload
        self.media_download = media_download
        self.timeout = timeout

    def _add_query_param(self, query: dict):
        if not self.url:
            raise TypeError('no url to query to')

        url = list(urlparse(self.url))
        url_query = dict(parse_qsl(url[4]))
        url_query.update(query)
        url[4] = url_query
        self.url = urlunparse(url)

    @classmethod
    def batch_requests(cls, *requests):
        # https://developers.google.com/discovery/v1/batch
        raise NotImplementedError

    @classmethod
    def from_response(cls, response):
        return Request(
            url = response.url,
            headers = response.headers,
            json = response.json,
            data = response.data
        )

@dataclass
class Response:
    status_code: int
    headers: dict
    url: str
    json: dict = None
    data: any = None
    content: any = None
    download_file: str = None
    upload_file: str = None
