from aiogoogle.models import ResumableUpload, MediaDownload, MediaUpload, Request

### Nothing special here

def test_media_upload():
    resumable_upload = ResumableUpload('path', multipart=True, upload_path='https://example.com/resumable_upload')
    media_upload = MediaUpload(
        'path',
        upload_path='https://example.com/upload',
        mime_range=['application/json'],
        max_size='3tb',
        multipart=True,
        resumable=resumable_upload
    )
    assert media_upload.file_path == 'path'
    assert media_upload.mime_range == ['application/json']
    assert media_upload.max_size == '3tb'
    assert media_upload.multipart is True
    assert media_upload.resumable is resumable_upload

def test_media_download():
    media_download = MediaUpload('path')
    assert media_download.file_path == 'path'

def test_resumable_upload():
    resumable_upload = ResumableUpload('path', multipart=True, upload_path='https://example.com/resumable_upload')
    assert resumable_upload.file_path == 'path'
    assert resumable_upload.multipart is True
    assert resumable_upload.upload_path == 'https://example.com/resumable_upload'

def test_request_constructor():
    # Silly test, look the other way
    method = 'GET'
    url = 'https://example.com/api/v1/example_resource?example_query=example_arg'
    headers = {'Authorization': 'Bearer asdasdasd'}
    json = {'data': 'asasdasd'}
    media_upload = MediaUpload('asdasd')
    media_download = MediaDownload('assda')

    req = Request(
        method=method,
        url=url,
        headers=headers,
        json=json,
        media_upload=media_upload,
        media_download=media_download
    )

    assert req.method == method
    assert req.url == url
    assert req.headers == headers
    assert req.json == json
    assert req.media_download == media_download
    assert req.media_upload == media_upload


# TODO
# def test_batch_request():
#     pass

# TODO:
# Test add query param

