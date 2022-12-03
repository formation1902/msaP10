# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from botbuilder.core    import Recognizer
from botbuilder.core    import RecognizerResult
from botbuilder.core    import TurnContext
from botbuilder.core    import BotTelemetryClient
from botbuilder.core    import NullTelemetryClient


from config import Bot_luis_app_and_nsights_configuration


class Reserver_un_billet_d_avion_Recognizer(Recognizer):
    def __init__(self, configuration: Bot_luis_app_and_nsights_configuration, telemetry_client: BotTelemetryClient = None):
        self._recognizer = None
        #
        # Presence des elements de la configuration LUIS
        #
        luis_is_configured = (configuration.LUIS_APP_ID  and configuration.LUIS_API_KEY and configuration.LUIS_API_HOST_NAME )

        if luis_is_configured:
            # Set the recognizer options depending on which endpoint version you want to use e.g v2 or v3.
            # More details can be found in https://docs.microsoft.com/azure/cognitive-services/luis/luis-migration-api-v3
            #
            # Instantiation de l'application LUIS
            #
            luis_application = LuisApplication( configuration.LUIS_APP_ID, configuration.LUIS_API_KEY, "https://" + configuration.LUIS_API_HOST_NAME )
            

            options = LuisPredictionOptions()
            options.telemetry_client = telemetry_client or NullTelemetryClient()

            self._recognizer = LuisRecognizer(  luis_application, prediction_options=options)

    @property
    def is_configured(self) -> bool:
        # Returns true if luis is configured in the config.py and initialized.
        return self._recognizer is not None

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        return await self._recognizer.recognize(turn_context)
