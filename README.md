# Django Speech To Text Api Wrapper

## About the project

Project provides a real-time streaming speech recognition API 
wrapped around the most popular speech-to-text API providers.
It provides an ability to transcribe input audio stream to the 
plain text using different API providers via single interface.


## Available transcription providers

Currently, there are 4 speech-to-text API providers implemented in project.

| Provider  | Sample rate  | Format |
|:---------:|:------------:|:------:|
|  Amazon   |   16000 hz   |  Mono  |
|  Google   |   16000 hz   |  Mono  |
| Microsoft |   16000 hz   |  Mono  |
| Deepgram  |   16000 hz   |  Mono  |

A list of API providers can be easily extend with own or existing implementation.

## Running the project on the local machine

First of all, copy the `dev.env` file to the `.env` file in the same directory.

```shell
$ cp dev.env .env
```

Open the `.env` file in your editor and specify the settings:

```shell
PYTHONENCODING=utf8
COMPOSE_IMAGES_PREFIX=speachanalysis
DEBUG=1
CONFIGURATION=dev
DJANGO_LOG_LEVEL=INFO
SECRET_KEY="<secret_key>"
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=db
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=dbpassword
REDIS_URL=redis://redis:6379/0
SITE_URL=http://speachanalysis.local:8000
EMAIL_HOST=mailhog
EMAIL_PORT=1025
AWS_ACCESS_KEY_ID="<aws_access_key_id>"
AWS_SECRET_ACCESS_KEY="<aws_secret_access_key>"
AZURE_SPEECH_KEY="<azure_speech_key>"
AZURE_SERVICE_REGION="<azure_service_region>"
DEEPGRAM_API_KEY="<deepgram_api_key>"
GOOGLE_APPLICATION_CREDENTIALS="<path_to_json_with_keys>"
```

To work with given API providers corresponding secrets should be set.

Note, google API is authenticated using `.json` file with relevant keys (check documentation). 
Instead of providing this keys, you should provide the path to `.json` file. 
Example of path for file located in `src` folder (./src/google-stt-keys.json):

```
GOOGLE_APPLICATION_CREDENTIALS=.\google-stt-keys.json
```

Due to Azure python SDK incompatibilities with ARM platform, you should build Django container in x86 emulation mode before the actual start. For this purpose uncomment next string in `docker-compose.dev.yml` file:

```yaml
services:
  django:
    <<: *django
    ports:
      - "8000:8000"
    command: dev
    platform: x86_64 # <- uncomment
```

Use the following command to build the containers:

```shell
$ docker-compose -f docker-compose.dev.yml build
```

Use the next command to run the project in detached mode:

```shell
$ docker-compose -f docker-compose.dev.yml up -d
```

Use next command to run `bash` inside the container to create Django superuser:

```shell
$ docker-compose -f docker-compose.dev.yml exec django bash
```

## Example of usage

To try a web client JS implementation visit http://localhost:8080/.
Due to the use of token based authentication you need to obtain the token.
Using already created superuser account you can create token manually from 
admin panel which is available on http://localhost:8000/ or retrieve it directly 
using api-auth-token endpoint (more info here http://localhost:8000/api/v1/doc/).

To transcribe audio stream using javascript follow next steps.

- Step 1. Open websocket connection use the following block of code:

```javascript
const token = '...';
const language = '...';
const provider = '...';
const ws = new WebSocket(`ws://localhost:8000/ws/transcription/?token=${token}&stt_provider=${provider}&language=${language}`);
```

- Step 2. Send an audio stream to the API, use `send` method on websocket instance, note input audio stream should be encoded in base64 format:

```javascript
ws.send(JSON.stringify({
    action: "transcribe",
    request_id: new Date().getTime(),
    voice_stream: base64string
}));
```

- Step 3. Retrieve transcription by implementing `onmessage` handler:

```javascript
ws.onmessage = (message) => {
    let response = JSON.parse(message.data);
    let data = response.data;
    let errors = response.errors;
    
    if (data) {
        // do something with response data.transcript;
    } else if (errors) {
        // do something with errors errors[0];
    }
}
```

- Step 4. Stop the transcription by closing the websocket using close method:

```javascript
ws.close();
```

Example of request:
```json
{
  "action": "transcribe",
  "request_id": 1665149563770,
  "voice_stream": "UklGRiQgAABXQVZFZm1...EzAg=="
}
```
Example of response (not authenticated):
```json
{
    "errors": ["You do not have permission to perform this action."], 
    "data": null, 
    "action": "transcribe", 
    "response_status": 403, 
    "request_id": 1665150123279
}

```
Example of response (transcribed):
```json
{
  "errors": [], 
  "data": {
    "language": "en-US", 
    "stt_provider": "amazon", 
    "transcript": "hello world"
  }, 
  "action": "transcribe", 
  "response_status": 200, 
  "request_id": 1665149764866
}
```