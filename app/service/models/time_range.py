from datetime import datetime


class TimeRange:
    def __init__(self, start_at: datetime, end_at: datetime):
        self.__start_at = start_at
        self.__end_at = end_at

        if not self.__is_hourly(start_at):
            raise ValueError("Start time must be set at the beginning of an hour.")
        if not self.__is_hourly(end_at):
            raise ValueError("End time must be set at the beginning of an hour.")
        if start_at >= end_at:
            raise ValueError("start_at must be before end_at.")

    def start_at(self) -> datetime:
        return self.__start_at

    def end_at(self) -> datetime:
        return self.__end_at

    @staticmethod
    def __is_hourly(d: datetime) -> bool:
        return d.minute == 0 and d.second == 0 and d.microsecond == 0

    def __repr__(self):
        return f"{self.__start_at} ~ {self.__end_at}"
