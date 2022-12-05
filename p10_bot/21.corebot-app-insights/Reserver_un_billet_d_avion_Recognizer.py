# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from botbuilder.core    import Recognizer
from botbuilder.core    import RecognizerResult
from botbuilder.core    import TurnContext
from botbuilder.core    import BotTelemetryClient
from botbuilder.core    import NullTelemetryClient


from config import Bot_luis_app_and_insights_configuration


class Reserver_un_billet_d_avion_Recognizer(Recognizer):
    nb = 0
    def __init__(self, configuration: Bot_luis_app_and_insights_configuration, telemetry_client: BotTelemetryClient = None):
        Reserver_un_billet_d_avion_Recognizer.nb+=1
        print("INFO :[ Reserver_un_billet_d_avion_Recognizer : Instantiation ] nb = ",Reserver_un_billet_d_avion_Recognizer.nb)
        
        print("\n############# [Reserver_un_billet_d_avion_Recognizer] instatiation start")
        self._recognizer = None
        #
        # Presence des elements de la configuration LUIS
        #
        print("\t ### --->  [Reserver_un_billet_d_avion_Recognizer ]\n\t - 1. Lecture des elements de configuration : luis is configured = ",end ='')
        luis_is_configured = (configuration.LUIS_APP_ID  and configuration.LUIS_API_KEY and configuration.LUIS_API_HOST_NAME )
        print(luis_is_configured)
        
        print("\t Manual check :")
        print("\t\t  configuration.LUIS_APP_ID        : ",configuration.LUIS_APP_ID)
        print("\t\t  configuration.LUIS_API_KEY       : ",configuration.LUIS_API_KEY)
        print("\t\t  configuration.LUIS_API_HOST_NAME : ",configuration.LUIS_API_HOST_NAME)
        print("\t------> Done 1.")
        
        if luis_is_configured:
            # Set the recognizer options depending on which endpoint version you want to use e.g v2 or v3.
            # More details can be found in https://docs.microsoft.com/azure/cognitive-services/luis/luis-migration-api-v3
            #
            # Instantiation de l'application LUIS
            #
            print("\t ### ---> luis_is_configured == True  [Reserver_un_billet_d_avion_Recognizer ]\n\t - 2. creation de l'application luis = ",end ='')
            luis_application = LuisApplication( configuration.LUIS_APP_ID, configuration.LUIS_API_KEY, "https://" + configuration.LUIS_API_HOST_NAME )
            print(luis_application)

            options = LuisPredictionOptions()
            
            options.telemetry_client = telemetry_client or NullTelemetryClient()

            self._recognizer = LuisRecognizer( luis_application, prediction_options=options)
            
            print("\t Manual check : ---> self.recognizer : ",self._recognizer is not None)
        else:
            print("\t ### ---> luis_is_configured == False  [Reserver_un_billet_d_avion_Recognizer ]\n\t - 2. luis is not configured\n")
        #
        print("############# [Reserver_un_billet_d_avion_Recognizer] instatiation end\n")

    @property
    def is_configured(self) -> bool:
        # Returns true if luis is configured in the config.py and initialized.
        #
        # Le recognizer est initalisée (not Not) apres lecture de la configuration et initialisation de l'application LUIS
        #
        return self._recognizer is not None

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        print("\n############# ------------> [Reserver_un_billet_d_avion_Recognizer : call to recognize() ]")
        return await self._recognizer.recognize(turn_context)
