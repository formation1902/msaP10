# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class ReservationDetails:
    
    def __init__(self,ville_depart: str = None,ville_destination: str = None,date_depart: str = None,date_retour=None,budget=None):
        #
        #
        #
        self.ville_depart = ville_depart
        self.ville_destination = ville_destination
        self.date_depart = date_depart
        self.date_retour = date_retour
        self.budget = budget
