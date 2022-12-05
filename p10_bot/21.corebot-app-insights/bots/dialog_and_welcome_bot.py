#
# Le bot principal : acceuil utilisateur
#
import json
import os.path
from typing import List

from botbuilder.dialogs import Dialog
from botbuilder.core    import TurnContext    
from botbuilder.core    import ConversationState, UserState
from botbuilder.core    import BotTelemetryClient

from botbuilder.schema import Activity 
from botbuilder.schema import Attachment
from botbuilder.schema import ChannelAccount


from p10bot_utils.activity_helper import create_activity_reply
from .dialog_bot import DialogBot


class DialogAndWelcomeBot(DialogBot):
    #
    # Bot acceuil des utilisateurs 
    #
    nb=0
    def __init__(self,conversation_state: ConversationState,user_state: UserState,dialog: Dialog,telemetry_client: BotTelemetryClient):
        DialogAndWelcomeBot.nb+=1
        print("INFO: [DialogAndWelcomeBot : instatiated] nb = ",DialogAndWelcomeBot.nb)
        super(DialogAndWelcomeBot, self).__init__(conversation_state, user_state, dialog, telemetry_client)
        self.telemetry_client = telemetry_client
        self.already_sent = False
    
    async def on_members_added_activity(self, members_added: List[ChannelAccount], turn_context: TurnContext):
        print(" --> [ DialogAndWelcomeBot: call to  on_members_added_activity ]")
        for member in members_added:
            # Greet anyone that was not the target (recipient) of this message.
            # To learn more about Adaptive Cards, see https://aka.ms/msbot-adaptivecards
            #
            # C'est la qu'il faut greeter any new connected user
            #
            if member.id != turn_context.activity.recipient.id and not self.already_sent:
                welcome_card = self.create_adaptive_card_attachment()
                response = self.create_response(turn_context.activity, welcome_card)
                print("\nINFO: [on_members_added_activity - on_members_added_activity ] 2_1............... new member.id : ",member.id)
                await turn_context.send_activity(response)
                print("\nINFO: [on_members_added_activity - on_members_added_activity ] 2_2............... new member.id : ",member.id)
                self.already_sent = True
                
    def create_response(self, activity: Activity, attachment: Attachment):
        print(" --> [ DialogAndWelcomeBot: call to  create_response ]")
        """Create an attachment message response."""
        response = create_activity_reply(activity)
        response.attachments = [attachment]
        return response

    # Load attachment from file.
    def create_adaptive_card_attachment(self):
        print(" --> [ DialogAndWelcomeBot: call to  create_adaptive_card_attachment ]")
        """Create an adaptive card."""
        relative_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(relative_path, "resources/p10Bot_greetingCard.json")
        with open(path) as card_file:
            card = json.load(card_file)

        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive", content=card
        )
