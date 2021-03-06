__author__ = 'zhanelya'

from localsys.environment import context
from models.score import score_model
import json
import web
from models.simulation import simulation


class score_rest:
    def GET(self):
        web.header('Content-Type', 'application/json')
        return json.dumps(score_model.get_scores(context.user_id()))


# This seems to make simulation calls that are long outdated
# However, it is not obsolete, because the multiple scores functionality is needed
class multiple_score:
    def POST(self):
        web.header('Content-Type', 'application/json')
        sim = simulation()
        post_data = json.loads(web.data())
        policy_costs_risks = []

        # last_policy = policies_model().get_policy_history(context.user_id())
        policy_context = post_data['context']
        for policy_entry in post_data['data']:
            result_entry = {}
            for key, value in policy_entry.iteritems():
                if key == "data":
                    next_policy = json.loads(value)
                else:
                    result_entry[key] = value
            result_entry["risk"] = sim.calc_risk_prob(next_policy, policy_context)
            result_entry["cost"] = sim.calc_prod_cost(next_policy, policy_context)
            policy_costs_risks.append(result_entry)

        # print('return cost '+ policy_costs_risks)

        return json.dumps(policy_costs_risks)
