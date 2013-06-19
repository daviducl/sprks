import web
import json
import session
from sim.simulation import simulation
from datetime import time, timedelta, datetime, date
from environment import render_private as render
from environment import db
from models.pw_policy import pw_policy_model

class pwpolicy_form:
    def GET(self):
        if session.mysession.session.loggedin:
            #use this variable to request any ID number
            id_user = session.mysession.session.id
            check = db.select('pw_policy', where="userid=$id_user", order="date DESC", vars=locals())
            if len(check) > 0:
                notfound=0
              #  result_get = db.select('pw_policy', where="idpolicy=$id_tmp", vars=locals())[0]
                result_get = check[0]
                session.mysession.session.date = result_get.date
                return render.pwpolicy_form(session.mysession.session.user,result_get.userid, result_get.plen, result_get.psets,
                                result_get.pdict, result_get.phist, result_get.prenew,
                                result_get.pattempts, result_get.pautorecover, notfound, str(result_get.date))
            else:
                notfound=1
                dt = datetime.now()
                dtt = dt - timedelta(days=dt.weekday())
                db.insert('pw_policy', plen=8, psets=2, pdict=0,
                          phist=1, prenew=1, pattempts=0,
                          pautorecover=1, userid=id_user, date=dtt.strftime("%Y/%m/%d %H:%M:%S"))
                result_get = db.select('pw_policy', where="userid=$id_user", vars=locals())[0]
                session.mysession.session.date = result_get.date
                return render.pwpolicy_form(session.mysession.session.user, result_get.userid, result_get.plen, result_get.psets,
                                result_get.pdict, result_get.phist, result_get.prenew,
                                result_get.pattempts, result_get.pautorecover, notfound, result_get.date)
        else:
            raise web.seeother('/login')

    def POST(self):
        web.header('Content-Type', 'application/json')
        usrid = session.mysession.session.id
        sim = simulation()
        data = json.loads(web.data())
        dat = eval(data["data"])
        if "pdict" in dat:
            dict1=1
        else:
            dat["pdict"]=0
        if "pautorecover" in dat:
            pautorecover1=1
        else:
            dat["pautorecover"]=0
        if "pattempts" in dat:
            pattempts1=1
        else:
            dat["pattempts"]=0
        pw_policy_model().update({'userid':str(usrid), 'date':data["date"]}, dat)
        for k, value in dat.iteritems():
            sim.set_policy(k, value)
#        return json.dumps(data)
        return json.dumps([{"name": "prob", "value": sim.calc_risk_prob()},
                           {"name": "impact", "value": sim.calc_risk_impact()},
                           {"name": "cost", "value": sim.calc_prod_cost()}])


class add:
    def POST(self):
        # make sure that the following line stays as per your local installation
        web.header('Content-Type', 'application/json')
        usrid = session.mysession.session.id
        sim = simulation()
        data = json.loads(web.data())
        dat = eval(data["data"])
        date = data["date"]
        dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        dtt = dt + timedelta(days=7)
        if "pdict" in dat:
            dict1=1
        else:
            dat["pdict"]=0
        if "pautorecover" in dat:
            dat["pautorecover"]=1
        else:
            dat["pautorecover"]=0
        if "pattempts" in dat:
            pattempts1=1
        else:
            dat["pattempts"]=0
        for k, value in dat.iteritems():
            sim.set_policy(k, value)
        db.insert('scores', userid=usrid, score_type=1, score_value = sim.calc_risk_prob(), date=dtt.strftime("%Y/%m/%d %H:%M:%S"), rank=0)
        db.insert('scores', userid=usrid, score_type=2, score_value = sim.calc_prod_cost(), date=dtt.strftime("%Y/%m/%d %H:%M:%S"), rank=0)
        db.insert('pw_policy', plen=dat["plen"], psets=dat["psets"], pdict=dat["pdict"],
                          phist=dat["phist"], prenew=dat["prenew"], pattempts=dat["pattempts"],
                          pautorecover=dat["pautorecover"], userid=usrid, date=dtt.strftime("%Y/%m/%d %H:%M:%S"))
        return json.dumps([{"value":dtt.strftime("%Y/%m/%d %H:%M:%S")}])