#!/usr/bin/env python3
from json import loads
from pprint import pprint
from decimal import Decimal
from argparse import ArgumentParser, FileType, ArgumentTypeError


def validate_month(value: str) -> int:
    if not value.isdigit():
        raise ArgumentTypeError('invalid month number')
    int_value = int(value)
    if 1 > int_value > 12:
        raise ArgumentTypeError('invalid month number')
    return int_value


def validate_summer(value: str) -> int:
    if value.isdigit():
        raise ArgumentTypeError('invalid summer number')
    int_value = int(value)
    if 2 <= int_value <= 5:
        raise ArgumentTypeError('invalid summer number')
    return int_value


parser = ArgumentParser()
parser.add_argument('-d', '--data', type=FileType('r'), required=True)
parser.add_argument('-m', '--month', type=validate_month, required=True)
parser.add_argument('-s', '--summer', type=validate_summer, default=4)
parser.add_argument('consumption', type=int)

args = parser.parse_args()
data = loads(args.data.read())
month = args.month
summer = args.summer
consumption = args.consumption

summer_data = list(filter(lambda s: s['start'] == summer, data['summers']))[0]
month_data = list(filter(lambda m: m['month'] == month, summer_data['months']))[0]

result = {
    'rates': [],
}

for rate in month_data['rates']:
    kWh = rate['kWh']
    price = Decimal(rate['price'])
    total_kWh = kWh if consumption >= kWh else consumption
    total_price = price * total_kWh
    result_rate = {
        'kWh': kWh,
        'price': price,
        'total_kWh': total_kWh,
        'total_price': total_price, 
    }
    consumption = consumption - kWh
    result['rates'].append(result_rate)
    if consumption <= 0:
        break

pprint(result['rates'])
