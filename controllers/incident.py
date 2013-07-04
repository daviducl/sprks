__author__ = 'mruskov'

import web
import json
from localsys.environment import render
from localsys.environment import context
from models.incident import incident as model
from models.policies import policies_model
from sim.classifier_sklearn import classifier_sklearn
class incident:
    def GET(self):

        if context.user_id() > 0: #if a user is logged in
            last_policy = policies_model().get_latest_policy(context.user_id())
            name = classifier_sklearn().predict_data(last_policy)[0]
            #event = json.dumps(model.get_incident_by_name(name))

            return render.incident(context.username(),name)
        else:
            raise web.seeother('/home')

    def POST(self):
        raise web.seeother('/policy/password')

    """
    class incident:
    def GET(self, policies):
        sim = simulation()
        incident = sim.get_incident()
        #incident = 'bla'
        return render.incident(incident)

    def get_incident(self):

        name = 'easy_incident'
        return name
    """