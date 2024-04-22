#!/usr/bin/env python3
from re import search
from math import inf
from json import dumps
from typing import Any, TypedDict
from decimal import Decimal
from datetime import date
from argparse import ArgumentParser

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

DEFAULT_URL = 'https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1C.aspx'


class Rate(TypedDict):
    kWh: float
    name: str
    price: Decimal
    

class SummerMonth(TypedDict):
    month: int
    rates: list[Rate]


class Summer(TypedDict):
    start: int
    months: list[SummerMonth]


class Data(TypedDict):
    year: int
    summers: list[Summer]


class Scraper:
    def __init__(self, url: str, /) -> None:
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')

        self._url = url
        self._driver = Chrome(options=options)
        
    def scrap(self, year: int, /) -> Data:
        data: Data = {
            'year': year,
            'summers': [],
        }
        try:
            self._driver.get(self._url)
            self._select_year(year)
            for summer_start in range(2, 5):
                self._select_summer(summer_start)
                summer: Summer = {
                    'start': summer_start,
                    'months': [],
                }
                for month in range(1, 13):
                    self._select_month(month)
                    summer_month: SummerMonth = {
                        'month': month,
                        'rates': self._get_rates() 
                    }
                    summer['months'].append(summer_month)
                data['summers'].append(summer)
        finally:
            self._driver.quit()
        return data

    def _get_rates(self) -> list[Rate]:
        rates: list[Rate] = []
        tbody = self._driver.find_element(By.XPATH, '//b[contains(text(), "Consumo básico")]/../../..')
        for tr in tbody.find_elements(By.XPATH, './tr'):
            name, price, kWh = tr.find_elements(By.XPATH, './td')

            kWh = search(r'\d+', kWh.text)
            if kWh:
                kWh = int(kWh.group())
            else:
                kWh = inf
            name = name.text.strip()
            price = Decimal(price.text.strip())
            
            rates.append(
                {
                    'kWh': kWh,
                    'name': name,
                    'price': price,
                }
            )
        return rates
    
    def _select_year(self, year: int, /) -> None:
        xpath = '//span[contains(text(), "Consultar tarifas de:")]/../following-sibling::td/select'
        self._select(xpath, year)
    
    def _select_summer(self, summer_month: int, /) -> None:
        xpath = '//td[contains(text(), "Elige el mes en que comienza el verano en tu localidad")]/following-sibling::td/select'
        self._select(xpath, summer_month)
        
    def _select_month(self, month: int, /) -> None:
        xpath = '//td[contains(text(), "Elige el mes que deseas consultar")]/following-sibling::td/select'
        self._select(xpath, month)
    
    def _select(self, xpath: str, value: Any, /) -> None:
        select = self._get_select(xpath)
        select.select_by_value(str(value))
    
    def _get_select(self, xpath: str, /) -> Select:
        element = self._driver.find_element(By.XPATH, xpath)
        return Select(element)


if __name__ == '__main__':
    parser = ArgumentParser()
    
    parser.add_argument('--url', type=str, default=DEFAULT_URL)
    parser.add_argument('--year', type=int, default=date.today().year)

    args = parser.parse_args()
    
    url = args.url
    year = args.year

    scraper = Scraper(url)
    
    print(dumps(scraper.scrap(year), default=str, indent=4))
