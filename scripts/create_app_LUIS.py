from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient

from functools import reduce
import json, time,datetime, uuid,pickle
import pandas as pd

from p10_LUIS_module import *

####################################################################################################
####################################################################################################
####################################################################################################
INITIAL_VERSION_ID ="0.1"

if __name__=='__main__':
    my_project = Project10()
    
    all_luis_apps  = my_project.list_apps(quiete=True)
    print("Nombre d'applications louis configurées :",len(all_luis_apps))
    assert len(all_luis_apps)==1;"C'est koi ce bordel"
        
    #### app_id = my_project.create_application()
    app_id = all_luis_apps[0].id
    # my_project.project_set_active_luis_app(app_id,INITIAL_VERSION_ID)
    
    
    predictionKey = 'c0ecc2043afe4ae3a2eb7a97b8e0c8e4'
    predictionEndpoint = 'https://msa-luis-1902.cognitiveservices.azure.com/'
    runtimeCredentials = CognitiveServicesCredentials(predictionKey)
    clientRuntime = LUISRuntimeClient(endpoint=predictionEndpoint, credentials=runtimeCredentials)
    
    # Production == slot name
    predictionRequest = { "query" : "I want to travel from paris to tokyo" }

    predictionResponse = clientRuntime.prediction.get_slot_prediction(app_id, "Production", predictionRequest)
    print("Top intent: {}".format(predictionResponse.prediction.top_intent))
    print("Sentiment: {}".format (predictionResponse.prediction.sentiment))
    print("Intents: ")

    for intent in predictionResponse.prediction.intents:
        print("\t{}".format (json.dumps (intent)))
    print("Entities: {}".format (predictionResponse.prediction.entities))

    sys.exit(-1)
    
    my_project._all_delete()
    my_project.create_application()
    
    # # # #
    # # # # On garde une seule appli
    # # # #
    all_luis_apps  = my_project.list_apps(quiete=True)
    print("Nombre d'applications louis configurées :",len(all_luis_apps))
    assert len(all_luis_apps)==1;"C'est koi ce bordel"
        
    #### app_id = my_project.create_application()
    app_id = all_luis_apps[0].id
    my_project.project_set_active_luis_app(app_id,INITIAL_VERSION_ID)
    entete("L'application luis active : ")
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    
    # # #
    # # # Il faut trouver la condition adequate
    # # #
    # entete("Setteing the model on the active luis app")
    my_project.set_model()
    entete("Recheck z L'application luis active : ")
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    print("\n\n")
    entete("Ajout des utterances")
    my_project.model_utterances_batch()
    
    
    print("\n\n")
    entete("Entrainement du modele")
    # my_project.model_train()
    
    app_id = my_project.active_luis_app_id
    version_id = my_project.active_luis_app_version_id
    async_training = my_project.luis_authoring_client.train.train_version(app_id, version_id)

    is_trained = async_training.status == "UpToDate"

    trained_status = ["UpToDate", "Success"]
    
    i=0
    
    while not is_trained:
        time.sleep(1)
        status = my_project.luis_authoring_client.train.get_status(app_id, version_id)
        is_trained = all(m.details.status in trained_status for m in status)
        if i%10==0:
            entete(' status')
            print(status)
            entete("Iteration : " +str(i))
            for m in status:
                print("\t - ",m.details.status)
                print(m.details)
        i+=1

    
    
    
    
    
    entete("L'application luis active : ")
    my_project.app_show_details(my_project.active_luis_app_id,quiete=False)
    my_project.app_version_show_details(my_project.active_luis_app_id,my_project.active_luis_app_version_id,quiete=False)
    
    # Publish the app
    publish_result = my_project.luis_authoring_client.apps.publish(
        app_id,
        {
            'version_id': version_id,
            'is_staging': False,
            'region' : 'westeurope'
        }
    )
    print("\nPublication de l'application")

    publish_result = my_project.luis_authoring_client.apps.publish(
        my_project.active_luis_app_id,
        {
            'version_id': my_project.active_luis_app_version_id,
            'is_staging': False
        }
    )
    print("\n\n - publish result : \n",publish_result)
    endpoint = publish_result.endpoint_url + "?subscription-key=" + my_project.authoring_key + "&q="
    print("\n\nYour app is published. You can now go to test it on\n{}".format(endpoint))