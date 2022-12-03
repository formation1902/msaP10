#
# 1. Creation de l'adaptateur 
#    1.1 adaptateur settings
#       1.1.1 Lecture de la configuration
#    1.2 creation des espaces memoires
#    1.3 Integration des telemetry
# 2. 
#
from http import HTTPStatus
from aiohttp        import web as aiohttp_web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import     BotFrameworkAdapterSettings,    ConversationState,    MemoryStorage,    UserState,    TelemetryLoggerMiddleware
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity
from botbuilder.applicationinsights import ApplicationInsightsTelemetryClient
from botbuilder.integration.applicationinsights.aiohttp import     AiohttpTelemetryProcessor,    bot_telemetry_middleware


from dialogs import MainDialog, BookingDialog
from bots import DialogAndWelcomeBot

from adapter_with_error_handler import AdapterWithErrorHandler

from Reserver_un_billet_d_avion_Recognizer import Reserver_un_billet_d_avion_Recognizer

#######################################################
#
# Creation de l'adaptateur
#    1.1 adaptateur settings
#       1.1.1 Lecture de la configuration
#    1.2 creation des espaces memoires
#    1.3 Integration des telemetry
#######################################################
#
# Chargement de la configuration +  Creation de l'adapateur
#
from config import Bot_luis_app_and_nsights_configuration
CONFIG = Bot_luis_app_and_nsights_configuration()
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)

# Create MemoryStorage, UserState and ConversationState
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
#
ADAPTER = AdapterWithErrorHandler(SETTINGS, CONVERSATION_STATE)

# Create telemetry client.
# Note the small 'client_queue_size'.  This is for demonstration purposes.  Larger queue sizes
# result in fewer calls to ApplicationInsights, improving bot performance at the expense of
# less frequent updates.
INSTRUMENTATION_KEY = CONFIG.APPINSIGHTS_INSTRUMENTATION_KEY
TELEMETRY_CLIENT = ApplicationInsightsTelemetryClient(
    INSTRUMENTATION_KEY, 
    telemetry_processor=AiohttpTelemetryProcessor(), 
    client_queue_size=10
)

# Code for enabling activity and personal information logging.
# TELEMETRY_LOGGER_MIDDLEWARE = TelemetryLoggerMiddleware(telemetry_client=TELEMETRY_CLIENT, log_personal_information=True)
# ADAPTER.use(TELEMETRY_LOGGER_MIDDLEWARE)

#######################################################
#
# Creation des dialogs et du bot
#    1.1 adaptateur settings
#       1.1.1 Lecture de la configuration
#    1.2 creation des espaces memoires
#    1.3 Integration des telemetry
#######################################################

# Create dialogs and Bot
RECOGNIZER      = Reserver_un_billet_d_avion_Recognizer(CONFIG)
BOOKING_DIALOG  = BookingDialog()
DIALOG          = MainDialog(RECOGNIZER, BOOKING_DIALOG, telemetry_client=TELEMETRY_CLIENT)
BOT             = DialogAndWelcomeBot(CONVERSATION_STATE, USER_STATE, DIALOG, TELEMETRY_CLIENT)


# Listen for incoming requests on /api/messages.
async def messages(req: Request) -> Response:
    # 
    # On n accepte que de JSON
    #
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    #
    # On creer l'object Activity avec ce qui est recu
    #
    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    #
    # On envoie l'objet Activity a l'adaptateur et on attend
    #
    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)

#
# Declaration de l'application 
#
APP = aiohttp_web.Application(
    middlewares = [
        bot_telemetry_middleware, 
        aiohttp_error_middleware
    ]
)

#
# Definition des EndPoints
#
APP.router.add_post("/api/messages", messages)

#
# Finally : 
#
if __name__ == "__main__":
    try:
        aiohttp_web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
