from localsys import environment
from datetime import date
from localsys.storage import db
from localsys.environment import context
from libraries.utils import date_utils
from datetime import timedelta
import datetime


class records:

    default_calendar = {
  'date': 'YYYY-MM-DD',
  'policyAccept': True,
  'eventAccept': True,
  'calendar': [
    {
      'date': '2014-01-20',
      'events': [
        {
        'incdt_id': 5,
        'cost': 2000
        }
      ]
    },
    {
      'date': '2014-01-21',
      'events': []
    },
    {
      'date': '2014-02-05',
       'events': [
        {
          'incdt_id': 1,
          'cost': 7000000
        },
        {
          'incdt_id': 4,
          'cost': 5000
        }
      ]
    },
    {
      'date': '2014-02-07',
      'events': [
        {
          'incdt_id': 8,
          'cost': 1000
        }
      ]
    }
  ],
  'policy': [
    {
      'employee': ['executives', 'road'],
      'location': ['office', 'home'],
      'device': ['phone', 'desktop'],
      'plen': 8,
      'psets': 2,
      'pdict': 0,
      'phist': 1,
      'prenew': 1,
      'pattempts': 0,
      'precovery': 1
    },
    {
      'employee': 'executives',
      'location': 'home',
      'device': 'phone',
    }]
  }

    @classmethod
    def commit_history(cls, user_id, date):
        result = db.update('journal', committed=1, where="date<$date&&user_id=$user_id", vars=locals())
        return result

    @classmethod
    def clear_prophecy(cls, user_id, date):
        """
        Clears uncommitted entries in the journal for specified user_id on or after the specified date. Returns None.
        """
        db.query('DELETE FROM journal WHERE user_id=$user_id AND committed=false AND date>=$date', vars=locals())

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

        if next_due_event_date is not None and next_due_event_date < next_due_policy_date:
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
            return result[0].date
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
    def record_prophecy(cls, user_id, risk):
        """
        For a given risk, generates new prophecies and stores in journal for given user_id.
        """
        pass
        # TODO doesn't work!!!
        # calendar = chronos.prophesize(risk)["prophecy"]
        calendar = cls.default_calendar["calendar"]
        whole_calendar = cls.default_calendar
        # for dates in calendar:
        #     for key in dates:
        #         date = ""
        #         cost = ""
        #         inc_id = ""
        #         if key == 'date':
        #             date = dates[key]
        #             dtt = date
        #         else:
        #             for event in dates[key]:
        #                 inc_id = event['incdt_id']
        #                 cost = event['cost']
        #                 db.insert('journal', user_id=user_id, date=date, cost=cost, incident_id=inc_id, commited=0)
        # return whole_calendar

    @classmethod
    def get_calendar(cls, user_id, sync_date):
        """
        Retrieve all events (past or future) for given user_id for month that the specified date falls on.
        Returns a custom dictionary-based data structure based on the REST API JSON spec.
        :param user_id:
        :param sync_date:
        """

        start_date = datetime.date(sync_date.year, sync_date.month, 1)

        end_date = (start_date + timedelta(days=32)).replace(day=1)

        raw_calendar = db.query('SELECT * FROM journal '
                                'WHERE user_id=$user_id AND date>=$start_date AND date<$end_date', vars=locals())

        calendar = {}
        # Converts database results into dictionary
        for event in raw_calendar:
            if event.date not in calendar:
                calendar[event.date] = {
                    'date': event.date.isoformat(),
                    'events': []
                }
            calendar[event.date].events.append({
                'incdt_id': event.incident_id,
                'cost': event.cost
            })

        calendar_array = []
        # Converts calendar dictionary into array
        for date, agenda in sorted(calendar.iteritems()):
            calendar_array.append(agenda)

        return calendar_array

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
            corrected_sync_date = next_sync_date
        else:
            # Client is at an arbitrary date between next_sync_date and last_sync_date for some weird reason.
            corrected_sync_date = client_date

        cls.commit_history(user_id, corrected_sync_date)

        return corrected_sync_date