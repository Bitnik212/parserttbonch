from bs4 import BeautifulSoup
import requests as req
import json, re



class timetable:
    domain = "http://cabinet.sut.ru/raspisanie_all_new.php?"
    type_z = "&type_z=" # тип расписания
    facultyid = "&faculty=" # id факультета
    kurs = "&kurs=" # номер курса
    groupid = "&group=" # id группы
    year = "&schet="
    def getYears () :
        link = timetable.domain
        soup = BeautifulSoup(req.get(link).text, 'html.parser')
        years = {'years': [] }
        try:
            for option in soup.find('form').find('select', attrs={'id':'schet'}).find_all('option'):
                if option['value'] != "0":
                    years['years'].append({'fulltext':option.text, 'semester': option.text.split(' ')[0], 'year': option.text.split(' ')[2], 'value':option['value']})
            return years

        except:
            print("Something went wrong in getYears()!")
            return {'error':'Something wrong'}

    def getTypeTimeTable ():
        link = timetable.domain
        soup = BeautifulSoup(req.get(link).text, 'html.parser')
        TypeTimeTable = {'TypeTimeTable': []}
        try:
            for option in soup.find('form').find('select', attrs={'id':'type_z'}).find_all('option'):
                if option['value'] != "0":
                    TypeTimeTable['TypeTimeTable'].append({'text':option.text, 'value':option['value']})
            return TypeTimeTable
        except:
            print("Something went wrong in getTypeTimeTable()!")
            return {'error':'Something wrong'}

    def getFacultet(type_z, schet):
        kurs = '0'
        facultet = {'facultet': []}
        responce = req.post( timetable.domain, data={'choice':1, 'type_z': str(type_z), 'schet': str(schet), 'kurs':str(kurs)}).content.decode('utf-8').split(';')
        try:
            if responce == ['']:
                return {'error':'empty request'}
            else:
                for item in responce:
                    if item != "":
                        facultet['facultet'].append({'text':item.split(',')[1], 'value':item.split(',')[0]})
                return facultet
        except:
            print("Something went wrong in getFacultet(type_z, schet)!")
            return {'error':'Something wrong'}
    def getCourse (facultet):
        if facultet == "56682":
            return [1, 2]
        else:
            return [1, 2, 3, 4, 5]
    def getGroups (facultet, type_z, schet, kurs):
        responce = req.post(timetable.domain, data={'faculty':str(facultet), 'choice':1, 'type_z': str(type_z), 'schet': str(schet), 'kurs':str(kurs)}).content.decode('utf-8').split(';')
        groups = {'groups': []}
        try:
            if responce == ['']:
                return {'error':'empty request'}
            else:
                for item in responce:
                    if item != "":
                        groups['groups'].append({'text':item.split(',')[1], 'value':item.split(',')[0]})
                return groups
        except:
            print("Something went wrong in getGroups (facultet, type_z, schet, kurs)!")
            return {'error':'Something wrong'}
    def getTimeTable(year, type_z, facultetid, kurs, groupid):
        link = timetable.domain+timetable.type_z+type_z+timetable.facultyid+facultetid+timetable.kurs+kurs+timetable.groupid+groupid+timetable.year+year
        soup = BeautifulSoup(req.get(link).text, 'html.parser')
        timetableresp = {"timetable": []}
        if soup.find(string=re.compile("Занятий для выбранной группы не найдено")) != None:
            print({"error":404, "description":'Такого расписания нет'})
            return {"error":404, "description":'Такого расписания нет'}
        else:
            # print({"error":"Расписания есть"})
            # print(soup.find('table', attrs={'class':'simple-little-table'}))
            keys = []
            for item in soup.find('table', attrs={'class':'simple-little-table'}).find_all('th'):
                # print(item.text)
                keys.append(item.text)
                timetableresp['timetable'].append({item.text: []})
            print(keys)
            if type_z == "1":
                # timetableresp['timetable'][1][keys[1]].append( "meme")
                # print(timetableresp['timetable'])
                temp = soup.find('table', attrs={'class':'simple-little-table'}).find_all('tr')[1] #.find_all('td')[0] #.find_all('div', attrs={'class':'pair'})[0]
                # print(temp.find_all('td')[0].text[0:1].isdigit())
                para = []
                for item in soup.find('table', attrs={'class':'simple-little-table'}).find_all('tr'):
                    if item.find('td') != None:
                        temp = item.find('td').text.replace(')', '').replace(' ', '').split('(')
                        para.append({'para':temp[0], 'time': temp[1]})
                        # print(item.find('td').text.replace(')', '').replace(' ', '').split('('))
                print(para)
                ipara = 0
                for table in soup.find('table', attrs={'class':'simple-little-table'}).find_all('tr'): # берем и листаем всю таблицу
                    day = 0
                    for row in table.find_all('td'): # здесь смотрим по горизонтальным столбикам (row)
                        print("day = "+str(keys[day]))
                        if day == 0:
                            print(para[ipara])
                            ipara+=1
                        day+=1
                        for column in row.find_all('div', attrs={'class':'pair'}): # здесь уже смотрим саму ячейку
                            print(timetable.getInfoAboutLesson(column))


                # print(timetable.getInfoAboutLesson(temp))
                # print(json.loads(str(timetable.getInfoAboutLesson(temp)).replace("'",'"')))

            # возможные поддержки расписаний
            elif type_z == "2":
                print("Это расписание сессий")
            elif type_z == "3":
                print("Это расписание факультативов")
            elif type_z == "4":
                print("Это расписание сессий для заочников")
            elif type_z == "5":
                print("Это расписание ГИА")
            elif type_z == "6":
                print("Это расписание канфиренций и прочего")
            elif type_z == "9":
                print("Это расписание контроля занятий")
            else:
                print("Хз что это. Куда ты опять попал?!!!???! И почему это сработало??!?!?!")

    def getInfoAboutLesson(lesson): # ожидается тэг <div class="pair" weekday="2" pair="2"> с его содержимым
        predmet = {'predmet': []}
        typeLesson = {'typeLesson': []}
        studyWeeks = {'studyWeeks':[]}
        teachers = {'teachers': []}
        lectureHall = {'lectureHall': []}
        try:
            predmet['predmet'].append(str(lesson.span.strong.text))
        except:
            predmet['predmet'].append({'error':404, 'description': 'Do not have lesson name'})
        try:
            typeLesson['typeLesson'].append(lesson.small.find('span', attrs={'class': 'type'}).text.replace('(', '').replace(')', ''))
        except:
            typeLesson['typeLesson'].append({'error':404, 'description':'Do not have type lesson'})
        try:
            temp = lesson.small.find('span', attrs={'class': 'weeks'}).text.replace('(', '').replace(')', '').replace(' ', '').split(',')
            for hall in temp:
                studyWeeks['studyWeeks'].append(hall)
        except:
            studyWeeks['studyWeeks'].append({'error':404, 'description':'Do not have study weeks'})
        try:
            temp = lesson.i.find('span', attrs={"class": "teacher"})['title'].split('; ')
            for teacher in temp:
                if teacher != "":
                    teachers['teachers'].append(teacher)
        except:
            teachers['teachers'].append({'error':404, 'description':'Do not have teacher'})
        try:
            temp = lesson.find('span', attrs={'class': 'aud'}).text.replace(' ', '').replace('ауд.:', '').split(';')
            # print(len(temp))
            if len(temp) > 1:
                lectureHall['lectureHall'].append({'aud':temp[0], 'building': temp[1]})
            else:
                lectureHall['lectureHall'].append(temp[0])
        except:
            lectureHall['lectureHall'].append({'error': 404, 'description':'Do not have lecture hall'})
        # data = {'data': []}
        # data['data'].append()
        return [predmet, typeLesson, studyWeeks, teachers, lectureHall]
timetable.getTimeTable("205.1920/2", '1', "50554", '3', '53954')
#http://cabinet.sut.ru/raspisanie_all_new.php?&type_z=1&faculty=50029&kurs=2&group=53776&schet=205.1920/1