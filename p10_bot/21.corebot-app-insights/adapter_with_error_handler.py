#
#
#
import sys
import traceback
from datetime import datetime

from botbuilder.core    import BotFrameworkAdapter,BotFrameworkAdapterSettings
from botbuilder.core    import ConversationState
from botbuilder.core    import TurnContext
from botbuilder.schema  import ActivityTypes, Activity


class AdapterWithErrorHandler(BotFrameworkAdapter):
    nb=0
    def __init__(self,settings: BotFrameworkAdapterSettings,conversation_state: ConversationState):
        AdapterWithErrorHandler.nb+=1
        print("INFO: [AdapterWithErrorHandler : instatiated] nb = ",AdapterWithErrorHandler.nb)
        super().__init__(settings)
        self._conversation_state = conversation_state

        # Catch-all for errors.
        async def on_error(context: TurnContext, error: Exception):
            # This check writes out errors to console log
            # NOTE: In production environment, you should consider logging this to Azure
            #       application insights.
            
            #
            # Integrer ces erreurs dans l'application insights
            #
            print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
            traceback.print_exc()

            #
            # Send a message to the user
            #
            await context.send_activity("Aie, un bug  a ete rencontree!")
            await context.send_activity(
                "message suplementaire 1"
            )
            await context.send_activity(
                "message suplementaire 2"
            )
            # Send a trace activity if we're talking to the Bot Framework Emulator
            #
            #
            #
            if context.activity.channel_id == "emulator":
                # Create a trace activity that contains the error object
                #
                # On peux envoyer l'objet erreur
                #
                trace_activity = Activity(
                    label="TurnError",
                    name="on_turn_error Trace",
                    timestamp=datetime.utcnow(),
                    type=ActivityTypes.trace,
                    value=f"{error}",
                    value_type="https://www.botframework.com/schemas/error",
                )
                # Send a trace activity, which will be displayed in Bot Framework Emulator
                await context.send_activity(trace_activity)

            # 
            # Liberation du context
            #
            nonlocal self
            await self._conversation_state.delete(context)

        self.on_turn_error = on_error
