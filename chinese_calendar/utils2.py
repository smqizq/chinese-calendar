# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime
from datetime import timedelta as td
from datetime import date

from chinese_calendar.constants import holidays, in_lieu_days, workdays
from chinese_calendar.solar_terms import (
    SOLAR_TERMS_C_NUMS,
    SOLAR_TERMS_DELTA,
    SOLAR_TERMS_MONTH,
    SolarTerms,
)

class WorkweekNum:
   def __init__(self, workweek_num: int) -> None:
       self.workweek_num = str(workweek_num)
       if len(self.workweek_num) != 4:
           raise Exception('not a workweek num.')
       else:
           self.year_num = 2000 + int(self.workweek_num[:2])
           self.week_num = int(self.workweek_num[2:])
   
   def __sub__(self, other: 'WorkweekNum'):
       if self.year_num < other.year_num:
           raise Exception(f'{self.year_num} is less than {other.year_num}.')
       year_offset = self.year_num - other.year_num
       print(self.year_num, other.year_num)
       for year in range(year_offset):
           print(year)
   
   def __repr__(self) -> str:
       return self.workweek_num
   
def next_day(given_date: date, weekday) -> date:
    """
    返回给定日期之后第一个符合指定星期几的日期。

    参数:
        given_date (date): 基准日期
        weekday (int/str): 目标星期几，支持数字（1-7）、中文（如"星期一"、"一"、"周一"）

    返回:
        date: 符合条件的下一个日期

    示例:
        >>> next_day(date(2023, 10, 9), "星期一")
        datetime.date(2023, 10, 16)

        >>> next_day(date(2023, 10, 9), 2)
        datetime.date(2023, 10, 10)
    """
    # 星期映射表（支持中文、数字、缩写）
    weekday_map = {
        '星期一': 1, '周一': 1, '一': 1, '1': 1,
        '星期二': 2, '周二': 2, '二': 2, '2': 2,
        '星期三': 3, '周三': 3, '三': 3, '3': 3,
        '星期四': 4, '周四': 4, '四': 4, '4': 4,
        '星期五': 5, '周五': 5, '五': 5, '5': 5,
        '星期六': 6, '周六': 6, '六': 6, '6': 6,
        '星期日': 7, '周日': 7, '星期天':7, '周天':7, '日':7, '天':7, '7':7,
    }

    # 解析目标星期几
    if isinstance(weekday, int):
        if 1 <= weekday <= 7:
            target = weekday
        else:
            raise ValueError("数字星期参数必须在 1-7 之间")
    elif isinstance(weekday, str):
        key = weekday.strip()
        if key in weekday_map:
            target = weekday_map[key]
        else:
            try:
                num = int(key)
                if 1 <= num <= 7:
                    target = num
                else:
                    raise ValueError(f"无效的星期数字: {num}")
            except ValueError:
                raise ValueError(f"无法识别的星期参数: {weekday}")
    else:
        raise TypeError("参数类型错误：weekday 应为字符串或整数")

    # 计算日期差
    current = given_date.isoweekday()
    days_ahead = target - current
    days_ahead += 7 if days_ahead <= 0 else 0

    return given_date + td(days=days_ahead)


def get_workweek_num(date=None):
    """
    将给定日期转换为两位年份 + 两位周数的格式（例如：2501 表示 2025 年第 1 周）
    
    参数:
    input_date (date): 需要判断的日期
    
    返回:
    str: 格式如 "2501" 的字符串，表示年份的后两位和周数（两位数）
    """
    curr_work_week_num = int(datetime.now().isoformat()[2:4] + '00') + datetime.now().isocalendar()[1]
    if date is None:
        return str(curr_work_week_num)
    # 获取 ISO 年份和周数（ISO 标准：每周从周一开始，第一周是包含该年第一个星期四的周）
    iso_year, week_num, _ = date.isocalendar()
    
    # 提取年份的后两位，并格式化为两位数（例如：2025 → 25，1999 → 99）
    year_short = iso_year % 100
    
    # 组合结果（年份两位数 + 周数两位数）
    return f"{year_short:02d}{week_num:02d}"

def get_workweek_range(week_str: str=None) -> tuple[date, date]:
    """
    根据四位数周号（如 '2501'）返回该周的起始日期（周一）和结束日期（周日）

    参数:
    week_str (str): 四位数周号，格式为两位年份 + 两位周数（例如：2501 表示 2025 年第 1 周）

    返回:
    tuple[date, date]: 该周的起始日期（周一）和结束日期（周日）

    异常:
    ValueError: 输入格式无效或周数超出范围
    """
    if week_str is None:
        week_str = cc.get_workweek_num()
    else:
        # 验证输入格式
        week_str = str(week_str)
        if len(week_str) != 4 or not week_str.isdigit():
            raise ValueError("输入必须为四位数字符串，例如 '2501'")

    # 解析年份后两位和周数
    year_short = int(str(week_str)[:2])
    week = int(str(week_str)[2:])

    # 处理年份后两位（00-68 → 2000-2068，69-99 → 1969-1999）
    iso_year = 1900 + year_short if year_short > 68 else 2000 + year_short

    # 构建 ISO 日期字符串（如 "2025-W01-1" 表示 2025 年第 1 周的周一）
    date_str = f"{iso_year}-W{week:02d}-1"

    try:
        # 解析周一日期（Python 3.6+ 支持 %G, %V, %u）
        start_date = datetime.strptime(date_str, "%G-W%V-%u").date()
    except ValueError as e:
        raise ValueError(f"无效的周数或年份: {e}")

    # 计算周日（周一 + 6 天）
    end_date = start_date + td(days=6)

    return start_date, end_date

def get_t_range(offset, from_week=None):
   '''
   获取from_week 周的T - offset 工作周的起始日期
   '''
   if not from_week:
       from_week=get_workweek_num()
   from_start_date = get_workweek_range(from_week)[0];''
   t_week_start_date = from_start_date - td(days=offset*7)
   t_week_num = get_workweek_num(t_week_start_date)
   return get_workweek_range(t_week_num)

def T_n(date):
   n = int(get_workweek_num()) - int(get_workweek_num(date))
#    return n
   return 'T' + str(n) if n < 0 else 'T+' + str(n)
