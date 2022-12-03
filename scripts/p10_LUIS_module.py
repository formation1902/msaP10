from azure.cognitiveservices.language.luis.authoring        import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from msrest.authentication                                  import CognitiveServicesCredentials
from azure.cognitiveservices.language.luis.runtime          import LUISRuntimeClient
import sys,os
from prepare_data import get_utterances

from functools import reduce
import json, time,datetime, uuid,pickle
import pandas as pd

def entete(*msgz):
    print("#"*len(' '.join(msgz))+"#"*10,"\n###")
    for msg in msgz:
        print("### --> ",msg)
    print("###")
    print("#"*len(' '.join(msgz))+"#"*10) 
    
def fp(obj_as_json):
    print(json.dumps(obj_as_json,indent=3))    

    

#
# La classe principale
#
class Project10():
    CONFIG_FILE = os.path.join(os.getcwd(),"application.conf")
    APPS_N = 0
    APP_NAME_SUFFIX = "000"
    INITIAL_VERSION_ID = "0.1"
    
    def __init__(self,config_file=None,initial_version_id=None):
        if initial_version_id:
            self.INITIAL_VERSION_ID = Project10.INITIAL_VERSION_ID
        else:
            self.INITIAL_VERSION_ID = initial_version_id
        if config_file==None:
            config_file = Project10.CONFIG_FILE
        self.parameters = {}
        with open(config_file,'r') as f:
                try:
                    for pline in f.readlines():
                        param,value = pline.split('=')
                        self.parameters[param.strip()]=eval(value.strip())
                except:
                    print("Error : fichier de configuration inaccessible")
                    sys.exit(-1)
            
        
        self.active_luis_app_id = None
        self.active_luis_app_version_id = None
        self.authoring_endpoint = self.parameters['authoring_endpoint']
        self.authoring_key = self.parameters['authoring_key']
        try:
            self.luis_authoring_client = LUISAuthoringClient(
                self.authoring_endpoint,
                CognitiveServicesCredentials(self.authoring_key)
            )
            Project10.APPS_N = len(self.luis_authoring_client.apps.list())
            print("3. The luis_authoring_client object successfully created : ",Project10.APPS_N,"found luis applications")
        except Exception as err:
            print("Pb lors de la creation du zgreat luis :", err)
            
    
    def project_set_active_luis_app(self,app_id,version_id):
        entete("Configuration de la z luis application active","app_id == "+str(app_id),"version_id == "+str(version_id))
        self.active_luis_app_id = app_id
        self.active_luis_app_version_id=version_id
        
    def _all_delete(self):
        entete('Suppression de tout ce qui bouge !')
        all_luis_apps  = self.list_apps()
        print("Nombre d'applications louis configurées :",len(all_luis_apps))
        for e in self.list_apps(quiete=True):
            self.delete_app(e.id)  
        all_luis_apps  = self.list_apps(quiete=True)
        print("Nouveau nombre d'applications louis configurées :",len(all_luis_apps))
        self.active_luis_app_id=None
        self.active_luis_app_version_id=None
    ####################################################################################################
    #
    # Management d'une application LUIS et de ses versions
    #
    ####################################################################################################
    def list_apps(self,quiete=False):
        try:
            if not quiete:
                entete("List des applications définies")
                for luisApp in self.luis_authoring_client.apps.list():
                    print("\t --->  app:",luisApp.name," id==",luisApp.id," versions_n==",luisApp.versions_count," active_version==",luisApp.active_version)
            return self.luis_authoring_client.apps.list()
        except Exception as err:
            print("Pb rencontrée lors de la recuperation de la liste des luisApp :",err)
                
    def create_application(self,application_name='p10_luisApp',initial_version_id=None,description="Nouvelle application LUIS cree pour le projet p10",culture="en-us"):
        """_summary_

        Args:
            application_name (str, optional): _description_. Defaults to 'p10_luisApp'.
            initial_version_id (str, optional): _description_. Defaults to "0.1".
            description (str, optional): _description_. Defaults to "Nouvelle application LUIS cree pour le projet p10".
            culture (str, optional): _description_. Defaults to "en-us".

        Returns:
            _type_: app_id de l'application luis cree
        """
        if initial_version_id==None:
            initial_version_id=Project10.INITIAL_VERSION_ID
        apps_nc=str(Project10.APPS_N+1)
        msaAppName = application_name+'_'+Project10.APP_NAME_SUFFIX[:len(apps_nc)+1]+apps_nc
        Project10.APPS_N+=1
        msaAppConf = ApplicationCreateObject(
            name=msaAppName, 
            initial_version_id=initial_version_id, 
            culture=culture,
            description=description
        )
        try:
            app_id =  self.luis_authoring_client.apps.add(msaAppConf)
            return app_id
        except Exception as err:
            print("Pb lors de la creation de l'application ",msaAppName,":", err)
        
        
    def app_show_details(self,app_id,quiete=True):
        try:
            details = self.luis_authoring_client.apps.get(app_id).as_dict()
            if not quiete:
                entete("Détails de l'application luis : ","app_id==" + app_id)
                print(json.dumps(details,indent=3))
                print("###\n")
            return details
        except Exception as err:
            print("Probleme rencontree lors de la collecte d'info sur l'applications :\n\t - app_id == ",app_id,"\n\t - Error == ",err)
    
    def app_make_clone(self,app_id,preexisting_version="0.1",to_version="0.2"):
        """
        Creation d'une nouvelle version de l'application luis passe en argumlent

        Args:
            app_id (_type_): _description_
            preexisting_version (str, optional): _description_. Defaults to "0.1".
            to_version (str, optional): _description_. Defaults to "0.2".
        """
        try:
            self.luis_authoring_client.versions.clone(
                app_id,
                preexisting_version,
                to_version
            )
        except Exception as err:
            print("Pb rencontrée lors de clonage de l'application :",app_id," - from_version==",preexisting_version," to_version==",to_version)
            print("--> Error :",err)
    
    def app_list_all_versions(self,app_id):
        try:
            entete("List de toutes les versions dispoibles de l'application luis :","\t - " + app_id)
            for version in self.luis_authoring_client.versions.list(app_id):
                print("\t->Version: '{}', training status: {}".format(version.version,version.training_status))
        except Exception as err:
            print("Probleme rencontrées lors de la collecte des informations sur les versions de l'application luis:\n\t - app_id ==",app_id,"\n\t - Error ==",err)
    
    def app_version_show_details(self,app_id,version_id,quiete=True):
        try:
            details = self.luis_authoring_client.versions.get(app_id, version_id).as_dict()
            if not quiete:
                entete("Détails de la version : "+version_id,"Luis application : app_id==" + app_id)
                print(json.dumps(details,indent=3))
            return details
        except Exception as err:
            print("Encountered exception. {}".format(err))
            
    def app_export_version_as_json(self,app_id,version_id,quiete=True):
        try:
            entete("LuisApp: " + app_id,"Exporting version :" + version_id)
            # print("\nLuisApp:",app_id,"\nExporting version ",version_id," as JSON")
            res =  json.dumps(
                self.luis_authoring_client.versions.export(
                    app_id,
                    version_id
                ).serialize()
            )
            if not quiete:
                print(json.dumps(eval(res),indent=3))
            return res
        except Exception as err:
            print("Pb rencontrée lors de l'export de la luisApp ",app_id," version==",version_id,"\n\tError==",err)
        
    def app_import_version_from_json_export(self,app_id,preexisting_app_export_as_json,version_id):
        try:
            return self.luis_authoring_client.versions.import_method(
                app_id,
                json.loads(preexisting_app_export_as_json),
                version_id
            )
        except Exception as err:
            print("Pb rencontrée lors de l'import de la luisApp :\n\t - ",app_id,"\n\t - version==",version_id,"\n\t - export_json==",preexisting_app_export_as_json,"\n\t - Error==",err)
    
    def delete_app(self,app_id):
        try:
            self.luis_authoring_client.apps.delete(app_id)
        except Exception as err:
            print("Problem lors de la suppression de l'application luis:\n\t - app_id ==",app_id,"\n\t - Error == ",err)
            
    
            
    ####################################################################################################
    #
    # Management du modele d'une application LUIS (Specifique au context du projet 9)
    # 1. Creation de 5 entitées : 
    ####################################################################################################
    def set_model(self):
        """
            1. Definition des entites
            2. Definitions des intents
        """
        #
        #
        #
        assert self.active_luis_app_id != None and self.active_luis_app_version_id != None
        app_id = self.active_luis_app_id
        version_id = self.active_luis_app_version_id
        #
        # 
        #
        # 1. Definition des entitées
        #
        print("\nNous allons creer les 5 entites suivantes : ")
        print("\t - budget")
        print("\t - ville_depart")
        print("\t - ville_destination")
        print("\t - date_aller")
        print("\t - date_retour")
        
        budget = "budget"
        budget_id = self.luis_authoring_client.model.add_entity(
            app_id,
            version_id,
            budget
        )
        
        ville_depart = "ville_depart"
        ville_depart_id = self.luis_authoring_client.model.add_entity(
            app_id,
            version_id,
            ville_depart
        )
        
        ville_destination = "ville_destination"
        ville_destination_id = self.luis_authoring_client.model.add_entity(
            app_id,
            version_id,
            ville_destination
        )
        
        date_depart = "date_depart"
        date_depart_id = self.luis_authoring_client.model.add_entity(
            app_id,
            version_id,
            date_depart
        )
        
        date_retour = "date_retour"
        date_retour_id = self.luis_authoring_client.model.add_entity(
            app_id,
            version_id,
            date_retour
        )
        
        # userEntity = "DescriptionDeVoyageSouhaite"
        # userEntity_id = self.luis_authoring_client.model.add_composite_entity(
        #     app_id,
        #     version_id,
        #     name=userEntity,
        #     children=[budget, ville_depart,ville_destination,date_depart,date_retour]
        # )
        
        intent_DecrireLeVoyageSouhaitee = self.luis_authoring_client.model.add_intent(
            app_id,
            version_id,
            "intention_reserver_un_billet_d_avion"
        )
        
        # intent_salutationBonjour = self.luis_authoring_client.model.add_intent(
        #     app_id,
        #     version_id,
        #     "salutationBonjour"
        # )
        # intent_salutationAurevoir = self.luis_authoring_client.model.add_intent(
        #     app_id,
        #     version_id,
        #     "salutationAurevoir"
        # )      
        
        
    
    def model_utterances_batch(self):
        assert self.active_luis_app_id != None and self.active_luis_app_version_id != None
        app_id = self.active_luis_app_id
        version_id = self.active_luis_app_version_id
        
        
        utterances = get_utterances('book',wizardSuccess=True,absent_n=0,strict=True)
        utterances = [json.dumps(utterance,indent=2) for utterance in utterances]
        
        entete("Contenu des utterances :" + str(len(utterances)))      
        
        utterances_result = self.luis_authoring_client.examples.batch(
            app_id,
            version_id,
            [eval(e) for e in utterances[:100]]
        )
        return utterances_result
        
    def model_train(self):
        #
        # Entrainer le modele en lui associant à une :
        #    - à une version specifique d'une luis_app_id specifique
        #
        assert self.active_luis_app_id != None and self.active_luis_app_version_id != None
        app_id = self.active_luis_app_id
        version_id = self.active_luis_app_version_id
        
        async_training = self.luis_authoring_client.train.train_version(app_id, version_id)

        is_trained = async_training.status == "UpToDate"

        trained_status = ["UpToDate", "Success"]
        
        i=0
        
        while not is_trained:
            time.sleep(5)
            status = self.luis_authoring_client.train.get_status(app_id, version_id)
            is_trained = all(m.details.status in trained_status for m in status)
            if i%100==0:
                entete("Iteration : " +str(i))
                for m in status:
                    print("\t - ",m," : ",m.details.status)
            i+=1
        print("L'entrainement de l'application active du projet est terminée.")
