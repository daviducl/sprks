from localsys import environment
from datetime import date
from localsys.storage import db
from localsys.environment import context
from libraries.utils import date_utils


class records:

    def commit_history(self, date):
        user_id = context.user_id()
        result = db.update('journal', commited=1, where="date<$date&&user_id=$user_id", vars=locals())
        return result


    @classmethod
    def clear_history(cls, user_id, date):
        """
        Clears uncommitted entries in the journal for specified user_id on or after the specified date.
        """
        db.query('DELETE FROM journal WHERE user_id=$user_id AND committed=false AND date>=$date', vars(locals()))

    @classmethod
    def last_sync(cls, user_id):
        """
        Given user_id, returns the date of the most recent sync.
        """

        last_policy_sync = db.query('SELECT date FROM policies WHERE user_id=$user_id '
                                    'ORDER BY date DESC LIMIT 1', vars=locals())

        last_event_sync = db.query('SELECT date FROM journal WHERE user_id=$user_id AND committed=true '
                                   'ORDER BY date DESC LIMIT 1', vars=locals())

        if len(last_event_sync) > 0 and last_event_sync[0].date > last_policy_sync[0].date:
            return last_event_sync[0].date

        return last_policy_sync[0].date

    @classmethod
    def next_sync(cls, user_id, last_sync_date):
        """
        For the given user and a last sync date, returns the next sync due (whether it be policy sync or event sync).
        """

        next_due_policy_date = records.next_due_policy_date(last_sync_date)

        next_due_event_date = records.next_due_event_date(user_id)

        if next_due_event_date is not None and next_due_event_date<next_due_policy_date:
            return next_due_event_date

        return next_due_policy_date

    @classmethod
    def next_due_event_date(cls, user_id):
        """
        Given user_id, returns the date for the first event due after previous sync. If no event found, returns none.
        """

        result = db.query('SELECT date FROM journal WHERE user_id=$user_id AND committed=false '
                          'GROUP BY date ORDER BY date ASC LIMIT 1', vars=locals())
        if len(result) > 0:
            return date_utils.iso8601_to_date(result[0].date)
        return None

    @classmethod
    def next_due_policy_date(cls, last_sync_date):
        """
        Returns next day that policy review is due since the last sync.
        """

        month = last_sync_date.month + 1

        if month > 12:
            return date(last_sync_date.year+1, month-12, 1)

        return date(last_sync_date.year, month, 1)


    @classmethod
    def update_journal(self, userid, risk):
        #calendar = chronos.prophesize(risk)["prophecy"]
        calendar = self.default_calendar["calendar"]
        whole_calendar = self.default_calendar
        for dates in calendar:
            for key in dates:
                date = ""
                cost = ""
                inc_id = ""
                if key == 'date':
                    date = dates[key]
                    dtt = date
                else:
                    for event in dates[key]:
                        inc_id = event['incdt_id']
                        cost = event['cost']
                        db.insert('journal', user_id=userid, date=date, cost=cost, incident_id=inc_id, commited=0)
        return whole_calendar

    @classmethod
    def sync_history(cls, user_id, client_date):
        """
        Synchronizes history where possible, and returns the date that the client should resume at.
        The date returned should also be corrected so it can be checked whether a policy or event-triggered
        recalculation should be performed.
        """
        last_sync_date = records.last_sync(user_id)
        if client_date <= last_sync_date:
            # Client behind the last sync date.
            return last_sync_date

        next_sync_date = records.next_sync(user_id, last_sync_date)
        if client_date >= next_sync_date:
            # Client is ahead of the next predicted sync date.
            return next_sync_date

        # Client is at an arbitrary date for no apparent reason. Do nothing.
        return client_date
