from botbuilder.core import TurnContext
from botbuilder.core import MemoryStorage, ConversationState, UserState
from botbuilder.core import Activity, ActivityTypes, Attachement
from botbuilder.dialogs import DialogSet, DialogTurnStatus

from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core            import MessageFactory

from botbuilder.core.adapters import TestAdapter
import aiounittest



class Budget_prompt_test(aiounittest.AsyncTestCase):
    def __init__(self) -> None:
        super().__init__()
        
    async def test_budget_prompt(self):    
        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property('setForBudgetPromptTest_state')
        dialogs = DialogSet(dialogs_state)
        budget_prompt  = TextPrompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please, enter your budget : ?")
            )
        )
        dialogs.add(budget_prompt)
        
        
        def execute_test(self,turn_context:TurnContext):
            global dialogs
            dialog_context =  await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()
            if ( results.status == DialogTurnStatus.Empty):
                options = PromptOptions        
    
        
# await step_context.prompt(
#     TextPrompt.__name__,
#     PromptOptions(
#         prompt=MessageFactory.text("Please, enter your budget : ?")
#     ),
# )        