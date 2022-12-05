#
#
#
from botbuilder.core import ActivityHandler
from botbuilder.core import ConversationState,    UserState
from botbuilder.core import TurnContext
from botbuilder.core import BotTelemetryClient,    NullTelemetryClient
from botbuilder.dialogs import Dialog, DialogExtensions
from p10bot_utils.dialog_helper import DialogHelper


class DialogBot(ActivityHandler):
    nb=0
    def __init__(self,conversation_state: ConversationState,  user_state: UserState, dialog: Dialog,telemetry_client: BotTelemetryClient):
        DialogBot.nb+=1
        print("INFO: [DialogBot : instatiated] nb = ",DialogBot.nb)
        #
        #   conversation_state : 
        #   user_state         :
        #   dialog             :
        #   telemetry_client   :
        #
        if conversation_state is None:
            raise Exception("[DialogBot]: Missing parameter. conversation_state is required")
        
        if user_state is None:
            raise Exception("[DialogBot]: Missing parameter. user_state is required")
        
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state         = user_state
        self.dialog             = dialog
        self.telemetry_client   = telemetry_client

    async def on_message_activity(self, turn_context: TurnContext):
        print('[DialogBot : on_message_activity ] turn_context : ',turn_context)
        #
        #
        #
        print("\nINFO: [DialogBot - on_message_activity ] 1............... turn_context : ",turn_context)
        
        await DialogExtensions.run_dialog(self.dialog,turn_context,self.conversation_state.create_property("DialogState") )
        
        
        print("\nINFO: [DialogBot - on_message_activity ] 2............... turn_context : ",turn_context)

        # Save any state changes that might have occured during the turn.
        #
        #
        #
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)
        print("\nINFO: [DialogBot - on_message_activity ] 3............... turn_context : ",turn_context)

    @property
    def telemetry_client(self) -> BotTelemetryClient:
        """
        Gets the telemetry client for logging events.
        """
        return self._telemetry_client

    
    @telemetry_client.setter
    def telemetry_client(self, value: BotTelemetryClient) -> None:
        """
        Sets the telemetry client for logging events.
        """
        if value is None:
            self._telemetry_client = NullTelemetryClient()
        else:
            self._telemetry_client = value
