#!/usr/bin/env python

import os


class Bot_luis_app_and_insights_configuration:
    """Configuration for the bot."""
    PORT = 3978
    
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    
    LUIS_APP_ID = os.environ.get("LuisAppId","9e766d76-6172-4727-91c1-b6fdb641f2bf")
    
    LUIS_API_KEY = os.environ.get("LuisAPIKey","c0ecc2043afe4ae3a2eb7a97b8e0c8e4")
    
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName","msa-luis-1902.cognitiveservices.azure.com")
    
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "c45a70f0-8468-4279-823b-3661ee26be63"
    )
