# Examples

## Instructions

0. Generate a client ID and a client secret from Google Cloud Console. Use http://localhost:5000/callback/aiogoogle as the valid redirect URL

1. Copy `_keys.yaml` and make a new file and name it `keys.yaml` that way its gitignored and readable by the examples here.

```sh
cd examples && cp _keys.yaml keys.yaml
```

2. Paste your `client_id`, `client_secret` and `scopes` in the keys.yaml file you just created. Don't worry about the user_creds now.

3. Perform OAuth2 for personal use

Run:

```sh
python auth/oauth2.py
```

To get OpenID Connect tokens as well, run this intead:

```sh
python auth/openid_connect.py
```

If you'll only be using the examples here on your desktop, you can use the CLI authentication script. With this script you won't have to specify a redirect URL nor a value javascript origin, but you have to choose "Desktop Application" when creating your credentials:

```sh
python auth/openid_connect_cli.py
```

4. Copy and paste the access token and refresh token you just generated and paste them in your keys.yaml file. You're now ready to run the examples in this folder.

## GoogleAPI Examples

### 0.boilerplate.py

What it does:

* A boilerplate

API name and API version required:

* boilerplate-v1

Scopes Required:

* "https://www.googleapis.com/auth/boilerplate"

User Credentials Required:

* no

API Key Required:

* no

API explorer link:

* https://developers.google.com/apis-explorer/#p/boilerplate/boilerplate_version/boilerplate.resource.method

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

### 7. get_email_header.py

What it does:

* Prints the headers for an email returned by the gmail list API

API name and API version required:

* gmail-v1

Scopes Required:

* "https://www.googleapis.com/auth/gmail.readonly"

User Credentials Required:

* yes

### 8. create_document_firestore.py

What it does:

* Creates a generic document on Firestore

API name and API version required:

* firestore-v1

Scopes Required:

* "https://www.googleapis.com/auth/cloud-platform"

User Credentials Required:

* yes

API explorer link:

* https://developers.google.com/apis-explorer/#search/firestore/firestore/v1/firestore.projects.databases.documents.createDocument

### 8. create_document_firestore.py

What it does:

* Lists Google Cloud Storage buckets for a project

API name and API version required:

* storage-v1

Scopes Required:

* https://www.googleapis.com/auth/devstorage.read_only
* https://www.googleapis.com/auth/devstorage.read_write
* https://www.googleapis.com/auth/devstorage.full_control
* https://www.googleapis.com/auth/cloud-platform.read-only
* https://www.googleapis.com/auth/cloud-platform

Service account required:

* yes

User credentials required:

* no

Note:

When creating the service account. Don't forget to add an owner role in step 2 (after giving the service account a name).

API explorer link:

* https://developers.google.com/apis-explorer/#search/storage/storage/v1/storage.buckets.list

## OAuth2

## OpenID Connect
