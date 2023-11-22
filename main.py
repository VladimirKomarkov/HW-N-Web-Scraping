import requests
import bs4
import time
from fake_headers import Headers
import json
from typing import Dict, Any

from requests import Response


def get_headers() -> Dict[str, Any]:
    '''
    Функция возвращает объект заголовков
    '''
    return Headers(browser="Firefox", os="win").generate()


def get_text(url: str) -> str:
    '''
    Функция выполняет GET-запрос по указанному URL, передавая заголовки,полученные из функции  get_headers()
    и возвращает текстовое содержимое ответа на запрос
    '''
    return requests.get(url, headers=get_headers()).text


def get_response(url: str) -> Response:
    '''
    Функция выполняет GET-запрос по указанному URL, передавая заголовки,полученные из функции  get_headers()
    и возвращает объект ответа целиком
    '''
    return requests.get(url, headers=get_headers())


def parce_page(url: str, num_pages: int) -> list:
    '''
    Функция парсит num_pages страниц сайта HeadHunter, начиная с переданной в URL и возвращает список словарей
    с ключами "ссылка на вакансию", "вилка зп", "работодатель", "город"
    '''
    parsing_data = []
    # парсим num_pages страниц
    for page in range(1, num_pages + 1):
        page_url = f"{url}&page={page}"
        # получаем ответ на GET-запрос
        response = get_response(page_url)
        # если код ответа 200
        if get_response(url).status_code == 200:
            # создаем объект класса BeautifulSoap
            main_soap = bs4.BeautifulSoup(response.text, 'lxml')
            # находим теги, в которых содержится заголовки вакансий
            tags = main_soap.find_all('div', class_='serp-item')
            # вытаскиваем непосредственно интересующую нас информацию из вакансий, содержащих в своём
            # описании ключевые слова "Django" и "Flask"
            for tag in tags:
                span = tag.find('span')
                if span and ('Django' in span.text or 'Flask' in span.text):
                    link = tag.find('a', class_="serp-item__title")['href']
                    salary = tag.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
                    employer = tag.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
                    city = tag.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'})
                    # добавляем полученную информацию в виде ключей в итоговый список, обрезая при этом символы
                    # "NBSP" (неразрывного пробела) и "NNBSP" (неразрывного пробела с широкими пробелами)
                    parsing_data.append({
                        'link': link,
                        'salary': salary.text.replace('\xa0', ' ').replace("\u00A0", " ").replace("\u202F",
                                                                                                  " ") if salary else None,
                        'employer': employer.text.replace('\xa0', ' ').replace("\u00A0", " ").replace("\u202F",
                                                                                                      " ") if employer else None,
                        'city': city.text.replace('\xa0', ' ').replace("\u00A0", " ").replace("\u202F",
                                                                                              " ") if city else None
                    })
                    # ставим задержку, с целью снизить вероятность бана за подозрительную активность
                    time.sleep(1)
        # если код запроса != 200 получаем сообщение об ошибке с самим кодом ошибки
        else:
            print(f"Произошла ошибка {response.status_code}!")
    # возвращаем наш список словарей с результатами
    return parsing_data


def write_to_json(data: list) -> json:
    '''
    функция записи в JSON-файл в заданном формате ("ссылка на вакансию", "вилка зп", "работодатель", "город")
    '''
    with open("C:\Python\ДЗ Нетология\Parsing\json_data.json", "w", encoding="utf-8") as json_file:
        for item in data:
            json_data = {
                'Ссылка на вакансию': item['link'],
                'Вилка зарплаты': item['salary'],
                'Компания': item['employer'],
                'Город': item['city']
            }
            json.dump(json_data, json_file, ensure_ascii=False, indent=2)
            json_file.write('\n')
    print("Данные успешно записаны в json_data.json")


if __name__ == '__main__':
    # проверям работоспособность
    url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
    parcing_data = parce_page(url, 20)

    write_to_json(parcing_data)
