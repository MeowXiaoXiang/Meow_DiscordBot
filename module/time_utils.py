from datetime import datetime, timedelta

class TimeUtils:
    TIME_DELTA = timedelta(hours=+8)

    @classmethod
    def _get_current_time_utc8(cls):
        """
        取得目前 UTC+8 時區的時間。
        """
        return datetime.utcnow() + cls.TIME_DELTA

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
        格式範例：'[年-月-日 早上/下午 時:分]'
        """
        current_time = cls._get_current_time_utc8()
        str_time = cls.format_time(current_time, '%H:%M')
        hours, minutes = map(int, str_time.split(':'))
        am_or_pm = ['早上', '下午'][hours >= 12]
        return f"[{cls.format_time(current_time, '%Y-%m-%d')} {am_or_pm} {(hours - 1) % 12 + 1}:{minutes:02}]"
