from datetime import datetime, timedelta, timezone

class TimeUtils:
    TIME_DELTA = timedelta(hours=+8)

    @classmethod
    def _get_current_time_utc8(cls):
        """
        取得目前 UTC+8 時區的時間。
        """
        return datetime.now(timezone.utc) + cls.TIME_DELTA

    @staticmethod
    def format_time(time_obj, format_str):
        """
        將時間物件根據指定的格式進行格式化。
        
        Args:
            time_obj (datetime): 要格式化的時間物件。
            format_str (str): 指定的時間格式字符串。

        Returns:
            str: 格式化後的時間字串。
        """
        return time_obj.strftime(format_str)

    @classmethod
    def get_utc8(cls):
        """
        取得目前 UTC+8 時區的時間，並以 '%Y-%m-%d %H:%M:%S' 格式返回。
        """
        return cls.format_time(cls._get_current_time_utc8(), '%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_utc8_ch(cls):
        """
        取得目前 UTC+8 時區的時間，並以中文格式返回。
        格式範例：'[年-月-日 早上/下午 時:分:秒]'
        """
        current_time = cls._get_current_time_utc8()
        str_time = cls.format_time(current_time, '%H:%M:%S')
        hours, minutes, seconds = map(int, str_time.split(':'))
        am_or_pm = ['早上', '下午'][hours >= 12]
        return f"[{cls.format_time(current_time, '%Y-%m-%d')} {am_or_pm} {(hours - 1) % 12 + 1}：{minutes:02}：{seconds:02}]"

    @staticmethod
    def parse_time(time_str, format_str):
        """
        從字符串解析出時間物件。

        Args:
            time_str (str): 時間字符串。
            format_str (str): 解析格式。

        Returns:
            datetime: 解析後的時間物件。
        """
        return datetime.strptime(time_str, format_str)

    @staticmethod
    def calculate_time_difference(start_time, end_time):
        """
        計算兩個時間之間的差異。

        Args:
            start_time (datetime): 開始時間。
            end_time (datetime): 結束時間。

        Returns:
            timedelta: 時間差。
        """
        return end_time - start_time

    @staticmethod
    def convert_timezone(time_obj, target_timezone):
        """
        在不同時區之間進行時間轉換。

        Args:
            time_obj (datetime): 原始時間物件。
            target_timezone (timezone): 目標時區。

        Returns:
            datetime: 轉換後的時間物件。
        """
        return time_obj.astimezone(target_timezone)

    @classmethod
    def countdown_to(cls, target_time):
        """
        計算到特定時間的倒計時。

        Args:
            target_time (datetime): 目標時間。

        Returns:
            str: 倒計時。
        """
        current_time = cls._get_current_time_utc8()
        time_diff = target_time - current_time
        return str(time_diff)

    @classmethod
    def is_daylight_savings(cls):
        """
        檢查是否為夏令時間。

        Returns:
            bool: 是否為夏令時間。
        """
        return bool(datetime.now(timezone.utc).astimezone().dst())