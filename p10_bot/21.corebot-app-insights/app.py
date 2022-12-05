from botbuilder.core    import BotFrameworkAdapterSettings
from botbuilder.core    import ConversationState,    MemoryStorage,    UserState
from botbuilder.core    import TelemetryLoggerMiddleware
#
from botbuilder.schema  import Activity
#
from botbuilder.core.integration                        import aiohttp_error_middleware
from botbuilder.applicationinsights                     import ApplicationInsightsTelemetryClient
from botbuilder.integration.applicationinsights.aiohttp import AiohttpTelemetryProcessor, bot_telemetry_middleware
#
from dialogs  import MainDialog, ReservationDialog
from bots     import DialogAndWelcomeBot
from adapter_with_error_handler            import AdapterWithErrorHandler
from Reserver_un_billet_d_avion_Recognizer import Reserver_un_billet_d_avion_Recognizer
from config import Bot_luis_app_and_insights_configuration
#
from http import HTTPStatus
from aiohttp        import web as aiohttp_web
from aiohttp.web    import Request, Response, json_response
#

#######################################################
# Creation de l'adaptateur :
#   - lecture de la configuration
#   - creation des espaces memoires
#   - configuration et activation de la telemetrie
#######################################################
CONFIG      = Bot_luis_app_and_insights_configuration()
SETTINGS    = BotFrameworkAdapterSettings(CONFIG.APP_ID)#, CONFIG.APP_PASSWORD)
MEMORY              = MemoryStorage()
USER_STATE          = UserState(MEMORY)
CONVERSATION_STATE  = ConversationState(MEMORY)
ADAPTER = AdapterWithErrorHandler(SETTINGS, CONVERSATION_STATE)


# Create telemetry client. Note the small 'client_queue_size'.  This is for demonstration purposes.  
# Larger queue sizes result in fewer calls to ApplicationInsights, improving bot performance at the expense of less frequent updates.
INSTRUMENTATION_KEY = CONFIG.APPINSIGHTS_INSTRUMENTATION_KEY
TELEMETRY_CLIENT = ApplicationInsightsTelemetryClient(
    INSTRUMENTATION_KEY, 
    telemetry_processor=AiohttpTelemetryProcessor(), 
    client_queue_size=10
)

# Code for enabling activity and personal information logging.
#
#
#
TELEMETRY_LOGGER_MIDDLEWARE = TelemetryLoggerMiddleware(telemetry_client=TELEMETRY_CLIENT, log_personal_information=True)
ADAPTER.use(TELEMETRY_LOGGER_MIDDLEWARE)

#######################################################
#
# Creation des dialogs et du bot
# 
#######################################################

# Create dialogs and Bot

RECOGNIZER          = Reserver_un_billet_d_avion_Recognizer(CONFIG)
print(("ZZZZZZZZZZ temoin"))
Reservation_DIALOG  = ReservationDialog()
DIALOG          = MainDialog(RECOGNIZER, Reservation_DIALOG, telemetry_client=TELEMETRY_CLIENT)
BOT             = DialogAndWelcomeBot(CONVERSATION_STATE, USER_STATE, DIALOG, TELEMETRY_CLIENT)


#
async def fx_handle_new_connexion_tobot_api(req: Request) -> Response:
    # 
    # On n accepte que de JSON
    #
    print("----> [App : Handling new connexion ]")
    print("\t ----> [App : 1. receiving user text ]")
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    #
    # On creer l'object Activity avec ce qui est recu
    #
    print("\t ----> [App : 2. creating the Activity object ]")
    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    #
    # On envoie l'objet Activity a l'adaptateur et on attend
    #
    print("\t ----> [App : 3. Calling the adapter with the activtity object ]")
    print("App 3 --- START")
    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        print("\t ----> [App : received response from the adapter ]")
        print("\t\t - responde.body : ",response.body)
        print("\t\t - responde.status : ",response.status)
        return json_response(data=response.body, status=response.status)
    else:
        print("\t ----> [App : OK with no received response from the adapter]")
    print("App 3 --- END")
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
APP.router.add_post("/p10/api/messages", fx_handle_new_connexion_tobot_api)

#
# Finally : 
#
if __name__ == "__main__":
    print("INFO: [App - start running the bot APP]")
    try:
        aiohttp_web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
