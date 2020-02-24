from selenium import webdriver
#import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


def test_naLunch_site(URL, driver):

    df = pd.DataFrame(columns=['place_id', 'place_name', 'place_url', 'place_address', 'address_match', 'site_reached'])
    # place_id  - номер заведения (последние цифры ссылки на его страницу: /WhereTo/Place/***)
    # place_name - название заведения
    # place_url - адрес веб-страницы заведения
    # place_address - адрес заведения, как он указан на странице нашего сайта (/WhereTo/Place/***)
    # address_match - совпадение текста адреса заведения и метки на google.maps (True - указанные адреса совпадают, False -
    # адреса отличаются
    # url_reached - успех перехода на веб-страницу заведения (True - веб-страница заведения загружена успешно, False - при
    # загрузке веб-страницы заведения произошла ошибка

    driver.get(URL)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')


    #Считать номера всех заведений
    all_scripts = soup.find_all('script', attrs={'type': 'text/javascript'})
    main_script = all_scripts[-1]

    links = re.findall('a href="/WhereTo/Place/\d{3}', str(main_script))
    for link in links:
        place_URL = "https://www.nalunch.ru/WhereTo/Place/" + link[-3:]
        driver.get(place_URL)
        html_place = driver.page_source
        soup_place = BeautifulSoup(html_place, 'html.parser')
        #getting place's id
        place_id = link[-3:]

        #getting place's name
        name_div = soup_place.find('div', attrs={'class': 'point-name'})
        if name_div:
            place_name = name_div.get_text()[29:].partition("\n")[0]
            #partition("\n")[0]
            print(place_name)
        else:
            print(f"Name not found! Id: {place_id}")
            place_name = None


        #getting map address
        map_address_full = soup_place.find('a', attrs={'alt': 'Открыть карту'})
        print(place_id)
        if map_address_full:
            map_address = map_address_full['href'][26:]
            print(map_address)
        else:
            print(f"Map address not found! Id: {place_id}")
            map_address = None

        #getting text address
        text_address_div = soup_place.find('div', attrs={'class': 'point-address'})
        text_address_full = text_address_div.find('text')
        if text_address_full:
            text_address = text_address_full.get_text().partition("\n")[0]
            print(text_address)
        else:
            print(f"Text address not found! Id: {place_id}")
            text_address = None
        address_match = (str(text_address) == str(map_address))

        #getting place's site URL and checking if it can be reached
        url_div = soup_place.find('div', attrs={'class': 'point-links'})
        if url_div.find('a'):
            url = url_div.find('a')['href']
            print(url)
            driver.get(url)
            if driver.page_source:
                url_reached = True
            else:
                url_reached = False
        else:
            print(f"Site URL not found! Id: {link[-3:]}")
            url = None
            url_reached = False

        df = df.append({'place_id': place_id, 'place_name': place_name, 'place_address': text_address, 'place_url': url,
                        'address_match': address_match, 'site_reached': url_reached},
                       ignore_index=True)
        return df



URL = "https://www.nalunch.ru/whereto"
#Путь к Chrome webdriver
chromedriver_path = r"C:\Python38\chromedriver.exe"
#Инициализация webdriver
driver = webdriver.Chrome(chromedriver_path)

df = test_naLunch_site(URL, driver)

df.to_csv('nalunch_data.csv', header=True, index=False, encoding='utf-8-sig')
df.to_excel('nalunch_data.xls', header=True, index=False, encoding='utf-8-sig')

