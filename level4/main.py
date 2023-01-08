import json
import numpy as np
from typing import Dict, Union
from datetime import datetime

JSON_INPUT_FILE_PATH = r'level4/data/input.json'
ACTORS_DEB_OR_CRED = {
    "driver": "debit",
    "owner": "credit",
    "insurance": "credit",
    "assistance": "credit",
    "drivy": "credit"
}


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

    def get_rental_price(self, car: Car):
        rental_price = int(self._get_rental_distance_price(car) + self._get_rental_duration_price(car))
        return rental_price

    def _get_owner_and_driver_rental_data(self, car: Car, commission: float = 0.30):
        owner_driver_data = {
            "driver": self.get_rental_price(car),
            "owner": int(self.get_rental_price(car) * (1 - commission))
        }
        return owner_driver_data

    def _get_commission_data(
            self,
            car: Car,
            commission: float = 0.30,
            insurance_share: float = 0.50,
            roadside_assistance_daily_fee: int = 100
    ):
        rental_price = self.get_rental_price(car)
        commission_amount = commission * rental_price
        insurance_fee = insurance_share * commission_amount
        roadside_assistance_fee = self.duration * roadside_assistance_daily_fee
        drivy_fee = commission_amount - insurance_fee - roadside_assistance_fee

        commission_data = {
            "insurance": int(insurance_fee),
            "assistance": int(roadside_assistance_fee),
            "drivy": int(drivy_fee)
        }

        return commission_data

    def _get_all_actions(self, car: Car):
        commission_data = self._get_commission_data(car)
        owner_driver_data = self._get_owner_and_driver_rental_data(car)

        overall_data = owner_driver_data |commission_data

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
    all_rentals = [
        Rental.from_dict(rental) for rental in input_info["rentals"]
    ]

    rentals_price_details = [
        rental.get_rental_actions_info(all_cars_data[rental.car_id])
        for rental in all_rentals
    ]

    return rentals_price_details


if __name__ == '__main__':
    rentals_price_detail = main()
    final_output = {"rentals": rentals_price_detail}

    with open(r'level4/data/generated_output.json', 'w') as output_file:
        json.dump(final_output, output_file, indent=2)
        