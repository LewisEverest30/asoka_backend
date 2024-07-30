import datetime
from lunar import Lunar


bdt = datetime.datetime.fromisoformat("2001-07-16T12:35:00")

eightchar = Lunar(bdt)

gender = 0
eightchar_dic = {
    '农历': '%s %s[%s]年 %s%s' % (eightchar.lunarYearCn, eightchar.year8Char, eightchar.chineseYearZodiac, eightchar.lunarMonthCn, eightchar.lunarDayCn),
    '性别': '男' if gender==0 else '女',
    '今日节日': (eightchar.get_legalHolidays(), eightchar.get_otherHolidays(), eightchar.get_otherLunarHolidays()),
    '八字': ' '.join([eightchar.year8Char, eightchar.month8Char, eightchar.day8Char, eightchar.twohour8Char]),
    '今日节气': eightchar.todaySolarTerms,
    '今日时辰': eightchar.twohour8CharList,
    '时辰凶吉': eightchar.get_twohourLuckyList(),
    '生肖冲煞': eightchar.chineseZodiacClash,
    '星座': eightchar.starZodiac,
    '星次': eightchar.todayEastZodiac,
    '彭祖百忌': eightchar.get_pengTaboo(),
    '彭祖百忌精简': eightchar.get_pengTaboo(long=4, delimit='<br>'),
    '十二神': eightchar.get_today12DayOfficer(),
    '廿八宿': eightchar.get_the28Stars(),
    '今日三合': eightchar.zodiacMark3List,
    '今日六合': eightchar.zodiacMark6,
    '今日五行': eightchar.get_today5Elements(),
    '纳音': eightchar.get_nayin(),
    '九宫飞星': eightchar.get_the9FlyStar(),
    '吉神方位': eightchar.get_luckyGodsDirection(),
    '今日胎神': eightchar.get_fetalGod(),
    '神煞宜忌': eightchar.angelDemon,
    '今日吉神': eightchar.goodGodName,
    '今日凶煞': eightchar.badGodName,
    '宜忌等第': eightchar.todayLevelName,
    '宜': eightchar.goodThing,
    '忌': eightchar.badThing,
    '时辰经络': eightchar.meridians
}


print(eightchar_dic)