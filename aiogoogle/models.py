from urllib.parse import urlparse, parse_qsl, urlunparse
from urllib.parse import urlencode
from dataclasses import dataclass


class ResumableUpload:
    '''
    Resumable Upload Object. Works in conjuction with media upload 
    
    Arguments:

        
        file_path (str): Full path of the file to be uploaded
        
        upload_path (str): The URI path to be used for upload. Should be used in conjunction with the rootURL property at the API-level.
        
        multipart (bool): True if this endpoint supports upload multipart media.

    '''
    def __init__(self, file_path, multipart=None, upload_path=None):
        self.file_path = file_path
        self.upload_path = upload_path
        self.multipart = multipart

class MediaUpload:
    '''

    Media Upload

    Arguments:

        file_path (str): Full path of the file to be uploaded
        
        upload_path (str): The URI path to be used for upload. Should be used in conjunction with the rootURL property at the API-level.
        
        mime_range (list): list of MIME Media Ranges for acceptable media uploads to this method.
        
        max_size (str): Maximum size of a media upload, such as "1MB", "2GB" or "3TB".
        
        multipart (bool): True if this endpoint supports upload multipart media.
        
        resumable (aiogoogle.models.ResumableUplaod): A ResumableUpload object

    '''
    def __init__(self, file_path, upload_path=None, mime_range=None, max_size=None, multipart=False, resumable=None):
        self.file_path = file_path
        self.upload_path = upload_path
        self.mime_range = mime_range
        self.max_size = max_size
        self.multipart = multipart
        self.resumable = resumable

class MediaDownload:
    '''
    Media Download

    Arguments:

        file_path (str): Full path of the file to be downloaded
    '''
    def __init__(self, file_path):
        self.file_path = file_path

class Request:
    '''
    Request class for the whole library. Auth Managers, GoogleAPI and Sessions should all use this.

    .. note::
        
        For HTTP body, only pass one of the following params:
            
            - json: json as a dict
            - data: www-url-form-encoded form as a dict/ bytes/ text/ 


    Parameters:

        method (str): HTTP method as a string (upper case) e.g. 'GET'
        
        url (str): full url as a string. e.g. 'https://example.com/api/v1/resource?filter=filter#something
        
        json (dict): json as a dict
        
        data (any): www-url-form-encoded form as a dict/ bytes/ text/ 
        
        headers (dict): headers as a dict
        
        media_download (aiogoogle.models.MediaDownload): MediaDownload object
        
        media_upload (aiogoogle.models.MediaUpload): MediaUpload object
        
        timeout (int): Individual timeout for this request

    '''
    def __init__(
        self, method=None, url=None, headers=None, json=None, data=None,
        media_upload=None, media_download=None, timeout=None):
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
        '''
        Given many requests, will create a batch request per https://developers.google.com/discovery/v1/batch

        Arguments:

            *requests (aiogoogle.models.Request): Request objects

        Returns:

            aiogoogle.models.Request:
        '''
        raise NotImplementedError

    @classmethod
    def from_response(cls, response):
        return Request(
            url = response.url,
            headers = response.headers,
            json = response.json,
            data = response.data
        )


class Response:
    '''
    Respnse Object

    Arguments:

        status_code (int): HTTP Status code

        headers (dict): HTTP response headers

        url (str): Request URL

        json (dict): Json Response if any

        data (any): data

        download_file (str): path of the download file specified in the request

        upload_file (str): path of the upload file specified in the request

    Attributes:

        content (any): equals either ``self.json`` or ``self.data``
    '''
    
    def __init__(self, status_code=None, headers=None, url=None, json=None, data=None, download_file=None, upload_file=None):
        if json and data:
            raise TypeError('Pass either json or data, not both.')
        
        self.status_code = status_code
        self.headers = headers
        self.url = url
        self.json = json
        self.data = data
        self.content = self.json or self.data
        self.download_file = download_file
        self.upload_file = upload_file

    def next_page(self, req_token_name='pageToken', res_token_name='nextPageToken', json_req=False) -> Request:
        '''
        Method that returns a request object that requests the next page of a resource

        Arguments:

            req_token_name (str): name of the next_page token in the request
            
            res_token_name (str): name of the next_page token in json response

            json_req (dict): Normally, nextPageTokens should be sent in URL query params. If you want it in A json body, set this to True

        Returns:

            A request object (aiogoogle.models.Request):
        '''
        res_token = self.json.get(res_token_name, None)
        if not res_token:
            return None
        request = Request.from_response(self)
        if json_req:
            request.json[req_token_name] = res_token
        else:
            request._add_query_param({req_token_name : res_token})
        return request
