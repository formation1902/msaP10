#
#
#
from datatypes_date_time.timex import Timex

from botbuilder.dialogs         import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core            import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog    import CancelAndHelpDialog
from .date_resolver_dialog      import DateResolverDialog,DateResolverDialogRetour
from .budget_resolver_dialog    import BudgetResolverDialog


class ReservationDialog(CancelAndHelpDialog):
    #
    #
    #
    nb = 0
    def __init__( self, dialog_id: str = None, telemetry_client: BotTelemetryClient = NullTelemetryClient()):
        ReservationDialog.nb+=1
        print("INFO :[ ReservationDialog : Instantiated ] nb = ",ReservationDialog.nb)
        #        
        super(ReservationDialog, self).__init__( dialog_id or ReservationDialog.__name__, telemetry_client )
        self.telemetry_client        = telemetry_client
        text_prompt                  = TextPrompt(TextPrompt.__name__)
        confirm_prompt                  = ConfirmPrompt(ConfirmPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client
        confirm_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.fx_ville_depart_step,
                self.fx_ville_destination_step,
                self.fx_date_depart_step,
                self.fx_date_retour_step,
                self.fx_budget_step,
                self.fx_confirm_step,
                self.fx_final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        
        print("##############\n\n toto = ",DateResolverDialogRetour.__name__,"\n\n")
        self.add_dialog(
            DateResolverDialog(DateResolverDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(
            DateResolverDialogRetour(DateResolverDialogRetour.__name__, self.telemetry_client)
        )
        self.add_dialog(waterfall_dialog)
        self.add_dialog(confirm_prompt)
        
        
        self.initial_dialog_id = WaterfallDialog.__name__

    async def fx_ville_depart_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # - prompt pour ville_depart si absente
        #
        if x.ville_depart is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please, enter your ville depart : ?")
                ),
            )

        return await step_context.next(x.ville_depart)
    
    async def fx_ville_destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel modif ou l'information d'origine (next<->result)
        #
        x.ville_depart = step_context.result
        
        #
        # - prompt pour ville_destination si absente
        #
        # x.ville_destination = step_context.ville_destination

        if x.ville_destination is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please, enter your ville destination : ?")
                ),
            )

        return await step_context.next(x.ville_destination)
    
    async def fx_date_depart_step( self, step_context: WaterfallStepContext ) -> DialogTurnResult:
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel la derniere modif ou son information d'origine (next<->result)
        #
        x.ville_destination = step_context.result

        #
        # - prompt pour la date depart si absente
        #
        if not x.date_depart or self.is_ambiguous( x.date_depart):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, 
                x.date_depart
            )

        return await step_context.next(x.date_depart)
    
    async def fx_date_retour_step( self, step_context: WaterfallStepContext ) -> DialogTurnResult:
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel la derniere modif ou son information d'origine (next<->result)
        #
        x.date_depart = step_context.result

        #
        # - prompt pour  la date retour si absente
        #
        if not x.date_retour or self.is_ambiguous( x.date_retour):
            return await step_context.begin_dialog(
                DateResolverDialogRetour.__name__, 
                x.date_retour
            )

        return await step_context.next(x.date_retour)
    
    async def fx_budget_step( self, step_context: WaterfallStepContext ) -> DialogTurnResult:
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel la derniere modif ou son information d'origine (next<->result)
        #
        x.date_retour = step_context.result

        #
        # - prompt  le budget si absent
        #
        if not x.budget or self.is_ambiguous( x.date_retour):
            # return await step_context.begin_dialog(
            #     BudgetResolverDialog.__name__, 
            #     x.budget
            # )
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please, enter your budget : ?")
                ),
            )
        return await step_context.next(x.date_retour)

    async def fx_confirm_step( self, step_context: WaterfallStepContext ) -> DialogTurnResult:
        # ---> On finalise la collecte des donées utilisateurs : 
        #
        # on recupere le context  :  
        # 
        x = step_context.options
        
        #
        # On flash l'eventuel la derniere modif ou son information d'origine (next<->result)
        #
        x.budget = step_context.result
        
        # ---> On demande confirmation de l'ensemble des données par l'utilisateurs:
        #
        #
        #
        user_gathered_resevation_details = x
        
        msg = (
            f"Please confirm, I have you traveling"
            f"\n\t    from: { user_gathered_resevation_details.ville_depart }"
            f"\n\t      to: { user_gathered_resevation_details.ville_destination }"
            f"\n\t      on: { user_gathered_resevation_details.date_depart}"
            f"\n\t     oFF: { user_gathered_resevation_details.date_retour}"
            f"\n\t  budget: { user_gathered_resevation_details.budget}"
        )

        #
        # Permettre à l'utilisateur de confimer ou non les informations collectées
        #
        return await step_context.prompt(
            ConfirmPrompt.__name__, 
            PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def fx_final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        #
        # Finaliser le turn : 
        #
        x = step_context.options
        confirmation = step_context.result

        if confirmation:
            return await step_context.end_dialog(x)
        else:
            #
            # Ici, il faut tous recommencer
            #
            return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
