from aiogoogle.models import ResumableUpload, MediaDownload, MediaUpload


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

