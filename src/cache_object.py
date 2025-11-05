import datetime as datetime

class AlertCache:
    def __init__(self):
        self._last_alerted_threshold = 0
        self._last_alerted_week = None

    @property
    def last_alerted_threshold(self):
        self.reset_week()
        return self._last_alerted_threshold

    @last_alerted_threshold.setter
    def last_alerted_threshold(self, value):
        self._last_alerted_threshold = value

    def reset_week(self):
        # Check if the current week has changed since the last alert.
        # If a new week is detected, reset the last alerted threshold.
        # This allows alerts to be sent again for the same thresholds each new week.
        if self.current_week() != self._last_alerted_week:
            print('New week detected, resetting last alerted threshold')
            self._last_alerted_week = self.current_week()
            self._last_alerted_threshold = 0

    @staticmethod
    def current_week():
        # Returns the current year and week number as a tuple. For example: (2025, 34)
        today = datetime.datetime.now(datetime.timezone.utc)
        return today.isocalendar()[:2]
