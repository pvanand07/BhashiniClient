import requests
import json
import base64

class BhashiniClient:
    """
    A client for interacting with Bhashini's ASR, NMT, and TTS services.

    Methods:
        list_available_languages(task_type): Lists available languages for a given task.
        get_supported_voices(source_language): Gets supported genders for TTS in a language.
        asr(audio_content, source_language, audio_format='wav', sampling_rate=16000): Performs ASR.
        translate(text, source_language, target_language): Translates text from source to target language.
        tts(text, source_language, gender='female', sampling_rate=8000): Performs TTS.
    """

    PIPELINE_CONFIG_ENDPOINT = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
    INFERENCE_ENDPOINT = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
    PIPELINE_ID = "64392f96daac500b55c543cd"

    def __init__(self, user_id, api_key, pipeline_id = PIPELINE_ID):
        """
        Initializes the BhashiniClient with user credentials and pipeline ID.

        Args:
            user_id (str): Your user ID.
            api_key (str): Your ULCA API key.
            pipeline_id (str): The pipeline ID.

        Raises:
            Exception: If the pipeline configuration retrieval fails.
        """
        self.user_id = user_id
        self.api_key = api_key
        self.pipeline_id = pipeline_id
        self.headers = {
            "Content-Type": "application/json",
            "userID": self.user_id,
            "ulcaApiKey": self.api_key
        }
        self.config = self._get_pipeline_config()
        self.pipeline_data = self._parse_pipeline_config(self.config)
        self.inference_api_key = self.pipeline_data['inferenceApiKey']

    def _get_pipeline_config(self):
        """
        Retrieves the pipeline configuration.

        Returns:
            dict: The pipeline configuration.

        Raises:
            Exception: If the request fails.
        """
        payload = {
            "pipelineTasks": [
                {"taskType": "asr"},
                {"taskType": "translation"},
                {"taskType": "tts"}
            ],
            "pipelineRequestConfig": {
                "pipelineId": self.pipeline_id
            }
        }
        response = requests.post(
            self.PIPELINE_CONFIG_ENDPOINT,
            headers=self.headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()

    def _parse_pipeline_config(self, config):
        """
        Parses the pipeline configuration and extracts necessary information.

        Args:
            config (dict): The pipeline configuration.

        Returns:
            dict: Parsed pipeline data.
        """
        inference_api_key = config['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value']
        callback_url = config['pipelineInferenceAPIEndPoint']['callbackUrl']
        pipeline_data = {
            'asr': {},
            'tts': {},
            'translation': {},
            'inferenceApiKey': inference_api_key,
            'callbackUrl': callback_url
        }

        for pipeline in config['pipelineResponseConfig']:
            task_type = pipeline['taskType']
            if task_type in ['asr', 'translation', 'tts']:
                for language_config in pipeline['config']:
                    source_language = language_config['language']['sourceLanguage']

                    if task_type != 'translation':
                        if source_language not in pipeline_data[task_type]:
                            pipeline_data[task_type][source_language] = []

                        language_info = {
                            'serviceId': language_config['serviceId'],
                            'sourceScriptCode': language_config['language'].get('sourceScriptCode')
                        }

                        if task_type == 'tts':
                            language_info['supportedVoices'] = language_config.get('supportedVoices', [])

                        pipeline_data[task_type][source_language].append(language_info)
                    else:
                        target_language = language_config['language']['targetLanguage']
                        if source_language not in pipeline_data[task_type]:
                            pipeline_data[task_type][source_language] = {}

                        if target_language not in pipeline_data[task_type][source_language]:
                            pipeline_data[task_type][source_language][target_language] = []

                        language_info = {
                            'serviceId': language_config['serviceId'],
                            'sourceScriptCode': language_config['language'].get('sourceScriptCode'),
                            'targetScriptCode': language_config['language'].get('targetScriptCode')
                        }

                        pipeline_data[task_type][source_language][target_language].append(language_info)

        return pipeline_data

    def list_available_languages(self, task_type):
        """
        Lists the available languages for the specified task.

        Args:
            task_type (str): The task type ('asr', 'translation', or 'tts').

        Returns:
            list or dict: A list of available languages, or a dictionary for translation.

        Raises:
            ValueError: If an invalid task type is provided.

        Usage Example:
            client = BhashiniClient(user_id, api_key, pipeline_id)
            asr_languages = client.list_available_languages('asr')
            print("Available ASR Languages:", asr_languages)

            translation_languages = client.list_available_languages('translation')
            print("Available Translation Languages:", translation_languages)
        """
        if task_type not in ['asr', 'translation', 'tts']:
            raise ValueError("Invalid task type. Choose from 'asr', 'translation', or 'tts'.")

        if task_type == 'translation':
            languages = {}
            for src_lang in self.pipeline_data['translation']:
                languages[src_lang] = list(self.pipeline_data['translation'][src_lang].keys())
            return languages
        else:
            return list(self.pipeline_data[task_type].keys())

    def get_supported_voices(self, source_language):
        """
        Returns the supported genders for TTS in the specified language.

        Args:
            source_language (str): The language code (e.g., 'hi' for Hindi).

        Returns:
            list: A list of supported genders (e.g., ['male', 'female']).

        Raises:
            ValueError: If TTS is not supported for the language.

        Usage Example:
            client = BhashiniClient(user_id, api_key, pipeline_id)
            voices = client.get_supported_voices('hi')
            print("Supported voices for Hindi TTS:", voices)
        """
        if source_language not in self.pipeline_data['tts']:
            available_languages = ', '.join(self.list_available_languages('tts'))
            raise ValueError(
                f"TTS not supported for language '{source_language}'. "
                f"Available languages: {available_languages}"
            )

        service_info = self.pipeline_data['tts'][source_language][0]
        supported_voices = service_info.get('supportedVoices', [])
        return supported_voices


    def asr(self, audio_content, source_language, audio_format='wav', sampling_rate=16000):
        """
        Performs Automatic Speech Recognition on the provided audio content.

        Args:
            audio_content (bytes): The audio content in bytes.
            source_language (str): The language code of the audio (e.g., 'hi' for Hindi).
            audio_format (str): supported formats of audio content: ('wav', 'mp3', 'flac', 'ogg'.)
            sampling_rate (int): The sampling rate of the audio in Hz.

        Returns:
            dict: The ASR response from the API.

        Raises:
            ValueError: If the language is not supported.
            Exception: If the API request fails.

        Usage Example:
            client = BhashiniClient(user_id, api_key, pipeline_id)
            with open('audio.wav', 'rb') as f:
                audio_content = f.read()
            asr_result = client.asr(audio_content, source_language='hi', audio_format='wav')
            print("ASR Result:", asr_result)
        """
        if source_language not in self.pipeline_data['asr']:
            available_languages = ', '.join(self.list_available_languages('asr'))
            raise ValueError(
                f"ASR not supported for language '{source_language}'. "
                f"Available languages: {available_languages}"
            )

        service_info = self.pipeline_data['asr'][source_language][0]
        service_id = service_info['serviceId']

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {
                            "sourceLanguage": source_language
                        },
                        "serviceId": service_id,
                        "audioFormat": audio_format,
                        "samplingRate": sampling_rate
                    }
                }
            ],
            "inputData": {
                "audio": [
                    {
                        "audioContent": base64.b64encode(audio_content).decode('utf-8')
                    }
                ]
            }
        }

        headers = {
            'Accept': '*/*',
            'Authorization': self.inference_api_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(
            self.INFERENCE_ENDPOINT,
            headers=headers,
            data=json.dumps(payload)
        )

        self._handle_response_errors(response)
        return response.json()

    def translate(self, text, source_language, target_language):
        """
        Translates the provided text from the source language to the target language.

        Args:
            text (str): The text to translate.
            source_language (str): The source language code.
            target_language (str): The target language code.

        Returns:
            dict: The translation response from the API.

        Raises:
            ValueError: If the language pair is not supported.
            Exception: If the API request fails.

        Usage Example:
            client = BhashiniClient(user_id, api_key, pipeline_id)
            translation_result = client.translate(
                'मेरा नाम विहिर है।',
                source_language='hi',
                target_language='gu'
            )
            print("Translation Result:", translation_result)
        """
        if source_language not in self.pipeline_data['translation']:
            available_languages = ', '.join(self.list_available_languages('translation').keys())
            raise ValueError(
                f"Translation not supported from language '{source_language}'. "
                f"Available source languages: {available_languages}"
            )

        if target_language not in self.pipeline_data['translation'][source_language]:
            available_targets = ', '.join(self.pipeline_data['translation'][source_language].keys())
            raise ValueError(
                f"Translation from '{source_language}' to '{target_language}' not supported. "
                f"Available target languages for '{source_language}': {available_targets}"
            )

        service_info = self.pipeline_data['translation'][source_language][target_language][0]
        service_id = service_info['serviceId']

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_language,
                            "targetLanguage": target_language
                        },
                        "serviceId": service_id
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": text
                    }
                ]
            }
        }

        headers = {
            'Accept': '*/*',
            'Authorization': self.inference_api_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(
            self.INFERENCE_ENDPOINT,
            headers=headers,
            data=json.dumps(payload)
        )

        self._handle_response_errors(response)
        return response.json()

    def tts(self, text, source_language, gender='female', sampling_rate=8000):
        """
        Converts the provided text to speech in the specified language.

        Args:
            text (str): The text to convert to speech.
            source_language (str): The language code of the text.
            gender (str): The desired voice gender ('male' or 'female').
            sampling_rate (int): The sampling rate in Hz.

        Returns:
            dict: The TTS response from the API.

        Raises:
            ValueError: If the language or gender is not supported.
            Exception: If the API request fails.

        Usage Example:
            client = BhashiniClient(user_id, api_key, pipeline_id)
            tts_result = client.tts(
                'હેલો વર્લ્ડ',
                source_language='gu',
                gender='female'
            )
            # Save the audio output
            audio_base64 = tts_result['pipelineResponse'][0]['audio'][0]['audioContent']
            audio_data = base64.b64decode(audio_base64)
            with open('output_audio.wav', 'wb') as f:
                f.write(audio_data)
        """
        if source_language not in self.pipeline_data['tts']:
            available_languages = ', '.join(self.list_available_languages('tts'))
            raise ValueError(
                f"TTS not supported for language '{source_language}'. "
                f"Available languages: {available_languages}"
            )

        service_info = self.pipeline_data['tts'][source_language][0]
        service_id = service_info['serviceId']
        supported_voices = service_info.get('supportedVoices', [])

        if gender not in ['male', 'female']:
            raise ValueError("Voice must be 'male' or 'female'.")

        if supported_voices and gender not in supported_voices:
            available_voices = ', '.join(supported_voices)
            raise ValueError(
                f"Gender '{gender}' not supported for language '{source_language}'. "
                f"Available voices: {available_voices}"
            )

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {
                        "language": {
                            "sourceLanguage": source_language
                        },
                        "serviceId": service_id,
                        "gender": gender,
                        "samplingRate": sampling_rate
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": text
                    }
                ]
            }
        }

        headers = {
            'Accept': '*/*',
            'Authorization': self.inference_api_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(
            self.INFERENCE_ENDPOINT,
            headers=headers,
            data=json.dumps(payload)
        )

        self._handle_response_errors(response)
        return response.json()

    def _handle_response_errors(self, response):
        """
        Handles errors in the response.

        Args:
            response (requests.Response): The response object.

        Raises:
            Exception: If an HTTP error occurs.
        """
        try:
            response.raise_for_status()
        except requests.HTTPError as http_err:
            try:
                error_info = response.json()
                error_message = error_info.get('message', 'An error occurred.')
            except json.JSONDecodeError:
                error_message = response.text
            raise Exception(f"HTTP error occurred: {error_message}") from http_err
