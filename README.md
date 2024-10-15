# BhashiniClient

A Python client library for interacting with [Bhashini services](https://bhashini.gov.in/services), including Automatic Speech Recognition (ASR), Neural Machine Translation (NMT), and Text-to-Speech (TTS) for 13 indian languages.

- Test the API [online here](https://bhashini.gov.in/ulca/model/explore-models) and create a free API key and USER ID from profile.
- For Detailed API DOCS click [here](https://bhashini.gitbook.io/bhashini-apis/pre-requisites-and-onboarding)

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Initialization](#initialization)
  - [Examples](#examples)
    - [ASR Example](#asr-example)
    - [Translation Example](#translation-example)
    - [TTS Example](#tts-example)
  - [Methods](#methods)
    - [`list_available_languages(task_type)`](#list_available_languagestask_type)
    - [`get_supported_voices(source_language)`](#get_supported_voicessource_language)
    - [`asr(audio_content, source_language, audio_format='wav', sampling_rate=16000)`](#asraudio_content-source_language-audio_formatwav-sampling_rate16000)
    - [`translate(text, source_language, target_language)`](#translatetext-source_language-target_language)
    - [`tts(text, source_language, gender='female', sampling_rate=8000)`](#ttstext-source_language-genderfemale-sampling_rate8000)
- [License](#license)

## Features

- **ASR (Automatic Speech Recognition)**: Convert speech audio to text.
  - **Supported Formats**: `.wav`, `.mp3`, `.flac`, `.ogg`
  - **Sampling Rates**: `8000 Hz`, `16000 Hz`, `48000 Hz`
- **Translation**: Translate text between supported language pairs.
- **TTS (Text-to-Speech)**: Convert text to speech audio with gender options.

## Requirements

- Python 3.x
- `requests` library

Install the required Python package:

```bash
pip install requests
```

## Installation

Copy the `BhashiniClient` class into your project or save it as a module (e.g., `bhashini_client.py`).

## Usage

### Initialization

Initialize the `BhashiniClient` with your user credentials and pipeline ID.

```python
from bhashini_client import BhashiniClient

USER_ID = 'your_user_id'
API_KEY = 'your_ulca_api_key'
PIPELINE_ID = 'your_pipeline_id'  # Optional, defaults to predefined PIPELINE_ID

client = BhashiniClient(USER_ID, API_KEY, PIPELINE_ID)
```

### Examples

#### ASR Example

```python
# Initialize the client
client = BhashiniClient(USER_ID, API_KEY)

# Perform ASR
with open('speech.wav', 'rb') as f:
    audio_content = f.read()

asr_result = client.asr(
    audio_content,
    source_language='hi',
    audio_format='wav',       # Supported formats: 'wav', 'mp3', 'flac', 'ogg'
    sampling_rate=16000       # Supported rates: 8000, 16000, 48000
)
print("Transcribed Text:", asr_result['pipelineResponse'][0]['output'][0]['source'])
```

#### Translation Example

```python
# Initialize the client
client = BhashiniClient(USER_ID, API_KEY)

# Translate text
text = 'मेरा नाम विहिर है।'
translation_result = client.translate(text, source_language='hi', target_language='en')
print("Translated Text:", translation_result['pipelineResponse'][0]['output'][0]['target'])
```

#### TTS Example

```python
# Initialize the client
client = BhashiniClient(USER_ID, API_KEY)

# Convert text to speech
text = 'नमस्ते दुनिया'
tts_result = client.tts(
    text,
    source_language='hi',
    gender='female',
    sampling_rate=8000       # Supported rates: 8000, 16000, 48000
)

# Save the audio file
audio_base64 = tts_result['pipelineResponse'][0]['audio'][0]['audioContent']
audio_data = base64.b64decode(audio_base64)
with open('output.wav', 'wb') as f:
    f.write(audio_data)
```

### Methods

#### `list_available_languages(task_type)`

Lists the available languages for a specified task.

- **Parameters**:
  - `task_type` (str): The task type (`'asr'`, `'translation'`, or `'tts'`).

- **Returns**:
  - `list` or `dict`: A list of languages or a dictionary of language pairs for translation.

**Usage Example**:

```python
# For ASR
asr_languages = client.list_available_languages('asr')
print("ASR Languages:", asr_languages)

# For Translation
translation_languages = client.list_available_languages('translation')
print("Translation Languages:", translation_languages)
```

#### `get_supported_voices(source_language)`

Retrieves supported voices for TTS in the specified language.

- **Parameters**:
  - `source_language` (str): Language code (e.g., `'hi'` for Hindi).

- **Returns**:
  - `list`: Supported voices (`['male', 'female']`).

**Usage Example**:

```python
voices = client.get_supported_voices('hi')
print("Supported Voices for Hindi TTS:", voices)
```

#### `asr(audio_content, source_language, audio_format='wav', sampling_rate=16000)`

Performs ASR on the provided audio content.

- **Parameters**:
  - `audio_content` (bytes): Audio content in bytes.
  - `source_language` (str): Language code of the audio.
  - `audio_format` (str): Audio format (`'wav'`, `'mp3'`, `'flac'`, `'ogg'`).
  - `sampling_rate` (int): Sampling rate in Hz (`8000`, `16000`, `48000`).

- **Returns**:
  - `dict`: ASR response from the API.

**Usage Example**:

```python
with open('audio.wav', 'rb') as f:
    audio_content = f.read()

asr_result = client.asr(
    audio_content,
    source_language='hi',
    audio_format='wav',       # Supported formats: 'wav', 'mp3', 'flac', 'ogg'
    sampling_rate=16000       # Supported rates: 8000, 16000, 48000
)
print("ASR Result:", asr_result)
```

#### `translate(text, source_language, target_language)`

Translates text from the source language to the target language.

- **Parameters**:
  - `text` (str): Text to translate.
  - `source_language` (str): Source language code.
  - `target_language` (str): Target language code.

- **Returns**:
  - `dict`: Translation response from the API.

**Usage Example**:

```python
translation_result = client.translate(
    'मेरा नाम विहिर है।',
    source_language='hi',
    target_language='en'
)
print("Translation Result:", translation_result)
```

#### `tts(text, source_language, gender='female', sampling_rate=8000)`

Converts text to speech in the specified language and gender.

- **Parameters**:
  - `text` (str): Text to convert.
  - `source_language` (str): Language code.
  - `gender` (str): `'male'` or `'female'`.
  - `sampling_rate` (int): Sampling rate in Hz (`8000`, `16000`, `48000`).

- **Returns**:
  - `dict`: TTS response from the API.

**Usage Example**:

```python
tts_result = client.tts(
    'હેલો વર્લ્ડ',
    source_language='gu',
    gender='female',
    sampling_rate=16000       # Supported rates: 8000, 16000, 48000
)

# Save the audio output
audio_base64 = tts_result['pipelineResponse'][0]['audio'][0]['audioContent']
audio_data = base64.b64decode(audio_base64)
with open('output_audio.wav', 'wb') as f:
    f.write(audio_data)
```

## License

This project is licensed under the MIT License.

---

Feel free to contribute to this project by submitting issues or pull requests.
