# Examples

Copy `_keys.yaml` and make a new file and name it `keys.yaml` that way its gitignored and readable by the examples below.

All examples listed in this directory should use the file `keys.yaml` for storing user & client credentials.

## Perform OAuth2 for personal use

* For just an access token: run `auth\(production_unsafe\)/oauth2.py` or `auth\(production_unsafe\)/oauth2.py`

* for an access token + openid connect tokens: run `auth\(production_unsafe\)/openid_connect.py` or `auth\(production_unsafe\)/openid_connect_cli.py`

## GoogleAPI Examples

### 0.{cookiecutter}.py

What it does:

* A cookiecutter

API name and API version required:

* cookiecutter-v1

Scopes Required:

* "https://www.googleapis.com/auth/cookiecutter"

User Credentials Required:

* no

API Key Required:

* no

API explorer link:

* https://developers.google.com/apis-explorer/#p/cookiecutter/cookiecutter_version/cookiecutter.resource.method

Extra Dependencies (Other than aiogoogle's)):

* a_pip_package

Extra Steps (Other than running the file):

* do this
* then do that

Notes:

* keep in mind that this is a note
* this is only a note. One can run this example without reading this note

Warning:

* this is a warning
* It is highly recommended that whoever runs this examples, reads this warning msg first.

### 1.list_contacts.py

What it does:

* Lists user's contacts

API name and API version required:

* people-v1

Scopes Required:

* "https://www.googleapis.com/auth/contacts",
* "https://www.googleapis.com/auth/contacts.readonly",
* "https://www.googleapis.com/auth/plus.login",
* "https://www.googleapis.com/auth/user.addresses.read",
* "https://www.googleapis.com/auth/user.birthday.read",
* "https://www.googleapis.com/auth/user.emails.read",
* "https://www.googleapis.com/auth/user.phonenumbers.read",
* "https://www.googleapis.com/auth/userinfo.email",
* "https://www.googleapis.com/auth/userinfo.profile"

User Credentials Required:

* Yes

API Key Required:

* No

API explorer link:

* https://developers.google.com/apis-explorer/#p/people/v1/people.people.getBatchGet

### 2.list_youtube_playlists.py

What it does:

* lists playlists of a user's channel

API name and API version required:

* youtube-v3

Scopes Required:

* https://www.googleapis.com/auth/youtubepartner
* https://www.googleapis.com/auth/youtube.force-ssl
* https://www.googleapis.com/auth/youtube

User Credentials Required:

* yes

API explorer link:

* https://developers.google.com/apis-explorer/#p/youtube/v3/youtube.playlists.list?part=snippet&mine=true&_h=1&

Notes:

* You must have a channel on Youtube, not just a normal Google account.

### 3.list_calendar_events.py

What it does:

* List events in your primary calendar

API name and API version required:

* calendar-v3

Scopes Required:

* "https://www.googleapis.com/auth/calendar",
* "https://www.googleapis.com/auth/calendar.events",
* "https://www.googleapis.com/auth/calendar.events.readonly",
* "https://www.googleapis.com/auth/calendar.readonly"

User Credentials Required:

* yes

API explorer link:

* https://developers.google.com/apis-explorer/#p/calendar/v3/calendar.events.list?calendarId=primary&_h=2&

### 4. list_drive_files.py

What it does:

* Lists "id: names" of your google drive files

API name and API version required:

* drive-v3

Scopes Required:

* https://www.googleapis.com/auth/drive
* https://www.googleapis.com/auth/drive.file

User Credentials Required:

* yes

API explorer link:

* https://developers.google.com/apis-explorer/#p/drive/v3/drive.files.list

### 5. download_drive_file.py

What it does:

* Downloads a file from your google drive given a file ID

API name and API version required:

* drive-v3

Scopes Required:

* https://www.googleapis.com/auth/drive
* https://www.googleapis.com/auth/drive.file

User Credentials Required:

* yes

API explorer link:

* https://developers.google.com/apis-explorer/#p/drive/v3/drive.files.get

### 6. upload_drive_file.py

What it does:

* Upload a file to your Google Drive given it's full path and name

API name and API version required:

* drive-v3

Scopes Required:

* https://www.googleapis.com/auth/drive
* https://www.googleapis.com/auth/drive.file

User Credentials Required:

* yes

API explorer link:

* https://developers.google.com/apis-explorer/#p/drive/v3/drive.files.create
* https://developers.google.com/apis-explorer/#p/drive/v3/drive.files.update

## OAuth2


## OpenID Connect