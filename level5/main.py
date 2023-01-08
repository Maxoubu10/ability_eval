import json
import numpy as np
from enum import Enum
from typing import Dict, Union
from datetime import datetime

JSON_INPUT_FILE_PATH = r'level5/data/input.json'
ACTORS_DEB_OR_CRED = {
    "driver": "debit",
    "owner": "credit",
    "insurance": "credit",
    "assistance": "credit",
    "drivy": "credit"
}
OWNER_ADDITIONAL_OPTIONS = ['gps', 'baby_seat']


class Options(Enum):

    gps = 500
    baby_seat = 200
    additional_insurance = 1000


class Car:
    def __init__(self, id: int, price_per_day: int, price_per_km: int):
        self.id = id
        self.price_per_day = price_per_day
        self.price_per_km = price_per_km

    @classmethod
    def from_dict(cls, car_info: Dict[str, int]):
        car = cls(
            id=car_info["id"],
            price_per_day=car_info["price_per_day"],
            price_per_km=car_info["price_per_km"]
        )
        return car


class Rental:
    def __init__(self, id: int, car_id: int, start_date: str, end_date: str, distance: int):
        self.id = id
        self.car_id = car_id
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.distance = distance
        self.duration = (self.end_date - self.start_date).days + 1
        self._options = []

    def update_options(self, option: str):
        self._options.append(option)

    def _get_rental_distance_price(self, car: Car):
        distance_price = self.distance * car.price_per_km
        return distance_price

    def _get_rental_duration_price(self, car: Car):
        discounts = np.ones(self.duration)
        discounts[1:] = 0.9
        discounts[4:] = 0.7
        discounts[10:] = 0.5
        duration_price = np.sum(car.price_per_day * discounts)

        return duration_price

    def get_rental_price_no_additional_charges(self, car: Car):
        rental_price = int(self._get_rental_distance_price(car) + self._get_rental_duration_price(car))
        return rental_price

    def get_options_price_for_driver(self):
        if not self._options:
            return 0
        return self._get_additional_price_for_drivy() + self._get_additional_price_for_owner()

    def _get_additional_price_for_drivy(self):
        if 'additional_insurance' in self._options:
            return Options.additional_insurance.value * self.duration
        return 0

    def _get_additional_price_for_owner(self):
        owner_options_taken = list(set(self._options) & set(OWNER_ADDITIONAL_OPTIONS))
        if not owner_options_taken:
            return 0
        return sum([Options.__getattr__(option).value * self.duration for option in owner_options_taken])

    def _get_owner_and_driver_rental_data(self, car: Car, commission: float = 0.30):
        owner_driver_data = {
            "driver": self.get_rental_price_no_additional_charges(car) + self.get_options_price_for_driver(),
            "owner": int(self.get_rental_price_no_additional_charges(car) * (1 - commission)) + self._get_additional_price_for_owner()
        }
        return owner_driver_data

    def _get_commission_data(
            self,
            car: Car,
            commission: float = 0.30,
            insurance_share: float = 0.50,
            roadside_assistance_daily_fee: int = 100
    ):
        rental_price = self.get_rental_price_no_additional_charges(car)
        commission_amount = commission * rental_price
        insurance_fee = insurance_share * commission_amount
        roadside_assistance_fee = self.duration * roadside_assistance_daily_fee
        drivy_fee = commission_amount - insurance_fee - roadside_assistance_fee + self._get_additional_price_for_drivy()

        commission_data = {
            "insurance": int(insurance_fee),
            "assistance": int(roadside_assistance_fee),
            "drivy": int(drivy_fee)
        }

        return commission_data

    def _get_all_actions(self, car: Car):
        commission_data = self._get_commission_data(car)
        owner_driver_data = self._get_owner_and_driver_rental_data(car)

        overall_data = owner_driver_data | commission_data

        actions = [
            {
                "who": person,
                "type": ACTORS_DEB_OR_CRED[person],
                "amount": amount
            }
            for person, amount in overall_data.items()
        ]

        return actions

    def get_rental_actions_info(self, car):
        actions_info = {
            "id": self.id,
            "options": self._options,
            "actions": self._get_all_actions(car)
        }
        return actions_info

    @classmethod
    def from_dict(cls, rental: Dict[str, Union[str, int]]):
        rental = Rental(
            id=rental["id"],
            car_id=rental["car_id"],
            start_date=rental["start_date"],
            end_date=rental["end_date"],
            distance=rental["distance"]
        )
        return rental


def main():
    with open(JSON_INPUT_FILE_PATH, 'r') as input_file:
        input_info = json.load(input_file)

    all_cars_data = {
        car["id"]: Car.from_dict(car) for car in input_info['cars']
    }
    all_rentals = {
        rental["id"]: Rental.from_dict(rental) for rental in input_info["rentals"]
    }

    all_options = input_info['options']

    for option in all_options:
        all_rentals[option['rental_id']].update_options(option["type"])

    rentals_price_details = [
        rental.get_rental_actions_info(all_cars_data[rental.car_id])
        for rental in all_rentals.values()
    ]

    return rentals_price_details


if __name__ == '__main__':
    rentals_price_detail = main()
    final_output = {"rentals": rentals_price_detail}

    with open(r'level5/data/generated_output.json', 'w') as output_file:
        json.dump(final_output, output_file, indent=2)
