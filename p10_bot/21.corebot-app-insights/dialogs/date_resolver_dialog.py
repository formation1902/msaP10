#
# resolution des dates et des budgets
#
from datatypes_date_time.timex import Timex

from botbuilder.core            import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.dialogs         import WaterfallDialog, DialogTurnResult, WaterfallStepContext
from botbuilder.dialogs.prompts import DateTimePrompt, PromptValidatorContext, PromptOptions, DateTimeResolution
from .cancel_and_help_dialog import CancelAndHelpDialog

class DateResolverDialog(CancelAndHelpDialog):
    #
    #
    #
    def __init__( self, dialog_id: str = None, telemetry_client: BotTelemetryClient = NullTelemetryClient(),msaType="depart"):
        #
        #
        #
        super(DateResolverDialog, self).__init__( dialog_id or DateResolverDialog.__name__, telemetry_client )
        self.telemetry_client = telemetry_client

        date_time_prompt = DateTimePrompt( DateTimePrompt.__name__, DateResolverDialog.datetime_prompt_validator )
        date_time_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog( WaterfallDialog.__name__ + "2", [self.initial_step, self.final_step] )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(date_time_prompt)
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__ + "2"
        self.msaType = msaType

    async def initial_step(self, step_context: WaterfallStepContext    ) -> DialogTurnResult:
        #
        # 
        #
        timex = step_context.options
        prompt_msg   = "Please, can you specify the " + self.msaType + " date?"
        reprompt_msg = "Pour une meilleur lisibilité : dd/mm/yyy"

        if timex is None:
            #
            # Absence de l'information date 
            #
            return await step_context.prompt(
                DateTimePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(prompt_msg),
                    retry_prompt=MessageFactory.text(reprompt_msg),
                ),
            )

        # We have a Date we just need to check it is unambiguous.
        #
        # check for validation
        #
        if "definite" in Timex(timex).types:
            # This is essentially a "reprompt" of the data we were given up front.
            #
            # 
            #
            return await step_context.prompt(
                DateTimePrompt.__name__, PromptOptions(prompt=reprompt_msg)
            )

        return await step_context.next(DateTimeResolution(timex=timex))

    async def final_step(self, step_context: WaterfallStepContext):
        """Cleanup - set final return value and end dialog."""
        #
        # commit de la valeur et terminaison du dialog
        #
        timex = step_context.result[0].timex
        return await step_context.end_dialog(timex)

    @staticmethod
    async def datetime_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        #
        # Validation de la date communiqué par l'utilisateur est 
        #
        """ Validate the date provided is in proper form. """
        if prompt_context.recognized.succeeded:
            timex = prompt_context.recognized.value[0].timex.split("T")[0]

            # TODO: Needs TimexProperty
            return "definite" in Timex(timex).types

        return False


class DateResolverDialogRetour(DateResolverDialog):
    #
    #
    #
    def __init__( self, dialog_id: str = None, telemetry_client: BotTelemetryClient = NullTelemetryClient()):
        super(DateResolverDialogRetour, self).__init__( dialog_id or DateResolverDialogRetour.__name__, telemetry_client,msaType="retour" )
        print("---------> ",DateResolverDialogRetour.__name__)
        print("---------> ",dialog_id)
        self.msaType = "retour"