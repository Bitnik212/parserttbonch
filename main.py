import re
import requests as req
from bs4 import BeautifulSoup


def getCourse(facultet):
    if facultet == "56682":
        return [1, 2]
    elif facultet == 56682:
        return [1, 2]
    else:
        return [1, 2, 3, 4, 5]


def getInfoAboutLesson(lesson):  # ожидается тэг <div class="pair" weekday="2" pair="2"> с его содержимым
    predmet = {'predmet': []}
    typeLesson = {'typeLesson': []}
    studyWeeks = {'studyWeeks': []}
    teachers = {'teachers': []}
    lectureHall = {'lectureHall': []}
    try:
        predmet['predmet'].append(str(lesson.span.strong.text))
    except:
        predmet['predmet'].append({'error': 404, 'description': 'Do not have lesson name'})
    try:
        typeLesson['typeLesson'].append(
            lesson.small.find('span', attrs={'class': 'type'}).text.replace('(', '').replace(')', ''))
    except:
        typeLesson['typeLesson'].append({'error': 404, 'description': 'Do not have type lesson'})
    try:
        temp = lesson.small.find('span', attrs={'class': 'weeks'}).text.replace('(', '').replace(')', '').replace(
            ' ', '').split(',')
        for hall in temp:
            studyWeeks['studyWeeks'].append(hall)
    except:
        studyWeeks['studyWeeks'].append({'error': 404, 'description': 'Do not have study weeks'})
    try:
        temp = lesson.i.find('span', attrs={"class": "teacher"})['title'].split('; ')
        for teacher in temp:
            if teacher != "":
                teachers['teachers'].append(teacher)
    except:
        teachers['teachers'].append({'error': 404, 'description': 'Do not have teacher'})
    try:
        temp = lesson.find('span', attrs={'class': 'aud'}).text.replace(' ', '').replace('ауд.:', '').split(';')
        # print(len(temp))
        if len(temp) > 1:
            lectureHall['lectureHall'].append({'aud': temp[0], 'building': temp[1]})
        else:
            lectureHall['lectureHall'].append(temp[0])
    except:
        lectureHall['lectureHall'].append({'error': 404, 'description': 'Do not have lecture hall'})
    # data = {'data': []}
    # data['data'].append()
    data = {'data': [
        {'predmet': predmet['predmet'], 'studyWeeks': studyWeeks['studyWeeks'], 'teachers': teachers['teachers'],
         'lectureHall': lectureHall['lectureHall']}]}
    return data['data']


class timetable:
    def __init__(self):
        self.domain = "http://cabinet.sut.ru/raspisanie_all_new.php?"
        self.type_z = "&type_z="  # тип расписания
        self.facultyid = "&faculty="  # id факультета
        self.kurs = "&kurs="  # номер курса
        self.groupid = "&group="  # id группы
        self.year = "&schet="  # период обучения

    def getYears(self):
        link = self.domain
        soup = BeautifulSoup(req.get(link).text, 'html.parser')
        years = {'years': []}
        try:
            for option in soup.find('form').find('select', attrs={'id': 'schet'}).find_all('option'):
                if option['value'] != "0":
                    years['years'].append({'fulltext': option.text, 'semester': option.text.split(' ')[0],
                                           'year': option.text.split(' ')[2], 'value': option['value']})
            return years
        except:
            print("Something went wrong in getYears()!")
            return {'error': 'Something wrong'}

    def getTypeTimeTable(self):
        link = self.domain
        soup = BeautifulSoup(req.get(link).text, 'html.parser')
        TypeTimeTable = {'TypeTimeTable': []}
        try:
            for option in soup.find('form').find('select', attrs={'id': 'type_z'}).find_all('option'):
                if option['value'] != "0":
                    TypeTimeTable['TypeTimeTable'].append({'text': option.text, 'value': option['value']})
            return TypeTimeTable
        except:
            print("Something went wrong in getTypeTimeTable()!")
            return {'error': 'Something wrong'}

    def getFacultet(self, type_z, schet):
        kurs = '0'
        facultet = {'facultet': []}
        responce = req.post(self.domain, data={'choice': 1, 'type_z': str(type_z), 'schet': str(schet),
                                               'kurs': str(kurs)}).content.decode('utf-8').split(';')
        try:
            if responce == ['']:
                return {'error': 'empty request'}
            else:
                for item in responce:
                    if item != "":
                        facultet['facultet'].append({'text': item.split(',')[1], 'value': item.split(',')[0]})
                return facultet
        except:
            print("Something went wrong in getFacultet(type_z, schet)!")
            return {'error': 'Something wrong'}

    def getGroups(self, facultet, type_z, schet, kurs):
        responce = req.post(self.domain,
                            data={'faculty': str(facultet), 'choice': 1, 'type_z': str(type_z), 'schet': str(schet),
                                  'kurs': str(kurs)}).content.decode('utf-8').split(';')
        groups = {'groups': []}
        try:
            if responce == ['']:
                return {'error': 'empty request'}
            else:
                for item in responce:
                    if item != "":
                        groups['groups'].append({'text': item.split(',')[1], 'value': item.split(',')[0]})
                return groups
        except:
            print("Something went wrong in getGroups (facultet, type_z, schet, kurs)!")
            return {'error': 'Something wrong'}

    def getTimeTable(self, year, type_z, facultetid, kurs, groupid):
        link = self.domain + self.type_z + type_z + self.facultyid + facultetid + self.kurs + kurs + self.groupid + groupid + self.year + year
        soup = BeautifulSoup(req.get(link).text, 'html.parser')
        timetableresp = {"timetable": []}
        if soup.find(string=re.compile("Занятий для выбранной группы не найдено")) is not None:
            # print({"error":404, "description":'Такого расписания нет'})
            return {"error": 404, "description": 'Такого расписания нет'}
        else:
            # print(soup.find('table', attrs={'class':'simple-little-table'}))
            keys = []
            for item in soup.find('table', attrs={'class': 'simple-little-table'}).find_all('th'):
                # print(item.text)
                keys.append(item.text)
                timetableresp['timetable'].append({item.text: []})
            # print(keys)
            if type_z == "1":
                # temp = soup.find('table', attrs={'class': 'simple-little-table'}).find_all('tr')[1]
                para = []
                for item in soup.find('table', attrs={'class': 'simple-little-table'}).find_all('tr'):
                    if item.find('td') is not None:
                        temp = item.find('td').text.replace(')', '').replace(' ', '').split('(')
                        para.append({'para': temp[0], 'time': temp[1]})
                ipara = 0
                for table in soup.find('table', attrs={'class': 'simple-little-table'}).find_all(
                        'tr'):  # берем и листаем всю таблицу
                    day = 0
                    for row in table.find_all('td'):  # здесь смотрим по горизонтальным столбикам (row)
                        # print("day = "+str(keys[day]))
                        if day == 0:
                            timetableresp['timetable'][day][keys[day]].append(para[ipara])
                            # print(para[ipara])
                            ipara += 1
                        if row.text != " ":
                            for column in row.find_all('div', attrs={'class': 'pair'}):  # здесь уже смотрим саму ячейку
                                temp = getInfoAboutLesson(column)
                                # print(temp[0])
                                timetableresp['timetable'][day][keys[day]].append(
                                    {'lesson': temp[0], 'para': para[ipara - 1]})
                        else:
                            day += 1
                            continue
                        day += 1
            # возможные поддержки расписаний. Делать я это не буду но возможно подумаю. Но расписание сессий
            # когда-нибудь сделаю
            elif type_z == "2":
                msg = "Это расписание сессий"
                print(msg)
                return {'error': 404, 'description': msg}
            elif type_z == "3":
                msg = "Это расписание факультативов"
                print(msg)
                return {'error': 404, 'description': msg}
            elif type_z == "4":
                msg = "Это расписание сессий для заочников"
                print(msg)
                return {'error': 404, 'description': msg}
            elif type_z == "5":
                msg = "Это расписание ГИА"
                print(msg)
                return {'error': 404, 'description': msg}
            elif type_z == "6":
                msg = "Это расписание канфиренций и прочего"
                print(msg)
                return {'error': 404, 'description': msg}
            elif type_z == "9":
                msg = "Это расписание контроля занятий"
                print(msg)
                return {'error': 404, 'description': msg}
            else:
                msg = "Хз что это. Куда ты опять попал?!!!???! И почему это сработало??!?!?!"
                print(msg)
                return {'error': 404, 'description': msg}
        return timetableresp['timetable']


timetable = timetable()

# rasp = str(timetable.getTimeTable("205.1920/2", '1', "50554", '3', '53954'))
# rasp = rasp.replace("'", '"')
# print(rasp)
