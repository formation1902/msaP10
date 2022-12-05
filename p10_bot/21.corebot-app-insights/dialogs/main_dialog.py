#
#
#
from botbuilder.dialogs         import ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core            import MessageFactory, TurnContext, BotTelemetryClient, NullTelemetryClient
from botbuilder.schema          import InputHints

from ReservationDetails                     import ReservationDetails
from Reserver_un_billet_d_avion_Recognizer  import  Reserver_un_billet_d_avion_Recognizer
from p10bot_utils.luis_helper               import LuisHelper, Intent
from .reservation_dialog                    import ReservationDialog


class MainDialog(ComponentDialog):
    #
    #
    #
    nb = 0       
    def __init__( self, luis_recognizer: Reserver_un_billet_d_avion_Recognizer, reservation_dialog: ReservationDialog, telemetry_client: BotTelemetryClient = None):
        MainDialog.nb+=1
        print("INFO :[ MainDialog : Instantiated ] nb = ",MainDialog.nb)
        #
        super(MainDialog, self).__init__(MainDialog.__name__)
        self.telemetry_client = telemetry_client or NullTelemetryClient()

        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = self.telemetry_client

        reservation_dialog.telemetry_client = self.telemetry_client

        wf_dialog = WaterfallDialog(
            "WFDialog", 
            [
                self.fx_welcoming_step, 
                self.fx_activation_step, 
                self.fx_terminate_step
            ]
        )
        wf_dialog.telemetry_client = self.telemetry_client

        self._luis_recognizer = luis_recognizer
        self._reservation_dialog_id = reservation_dialog.id

        self.add_dialog(text_prompt)
        self.add_dialog(reservation_dialog)
        self.add_dialog(wf_dialog)

        self.initial_dialog_id = "WFDialog"

    async def fx_welcoming_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        print("----> main-dialog fx_welcoming_step")
        #
        # Les coordonnées de l'application LUIS doivent etre renseignées
        #
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
                
            )

            return await step_context.next(None)
        
        #
        #
        #
        message_text = str(step_context.options) if step_context.options else "Hello! I can assist you to make a reservation."
        
        prompt_message = MessageFactory.text(
            message_text, 
            message_text, 
            InputHints.expecting_input
        )

        return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))

    async def fx_activation_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        print("----> main-dialog : act_step")
        #
        #
        #
        if not self._luis_recognizer.is_configured:
            # LUIS is not configured, we just run the BookingDialog path with an empty BookingDetailsInstance.
            #
            #
            #
            empty_brand_new_reservation_details_object = ReservationDetails()
            
            return await step_context.begin_dialog(self._reservation_dialog_id, empty_brand_new_reservation_details_object)

        intent, luis_result = await LuisHelper.execute_luis_query(self._luis_recognizer, step_context.context)

        if intent == Intent.BOOK_FLIGHT.value and luis_result:
            return await step_context.begin_dialog(self._reservation_dialog_id, luis_result)
        else:
            didnt_understand_text =  "I can assist you to book a flight"
            didnt_understand_message = MessageFactory.text(
                didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(didnt_understand_message)

        return await step_context.next(None)

    async def fx_terminate_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        print("----> main-dialog : final_step")
        # If the child dialog ("BookingDialog") was cancelled or the user failed to confirm,
        # the Result here will be null.
        if step_context.result is not None:
            user_gathered_resevation_details = step_context.result

            # Now we have all the booking details call the booking service.

            # If the call to the booking service was successful tell the user.
            # time_property = Timex(result.travel_date)
            # travel_date_msg = time_property.to_natural_language(datetime.now())
            msg_txt = (
                f"I have you traveling for less than the given budget : "
                f"    from: { user_gathered_resevation_details.ville_depart }"
                f"      to: { user_gathered_resevation_details.ville_destination }"
                f"      on: { user_gathered_resevation_details.date_depart}"
                f"     oFF: { user_gathered_resevation_details.date_retour}"
                f"  budget: { user_gathered_resevation_details.budget}"
            )
            message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
            await step_context.context.send_activity(message)

        prompt_message = "Goodbye."
        return await step_context.replace_dialog(self.id, prompt_message)

