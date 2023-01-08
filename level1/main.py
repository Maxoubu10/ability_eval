import json
from typing import Dict, Union
from datetime import datetime

JSON_INPUT_FILE_PATH = r'level1/data/input.json'


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

    def get_rental_price(self, car: Car):
        price = self.duration * car.price_per_day + self.distance * car.price_per_km
        return price

    def get_rental_price_info(self, car: Car):
        rental_info = {
            "id": self.id,
            "price": self.get_rental_price(car)
        }

        return rental_info

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
        rental.get_rental_price_info(all_cars_data[rental.car_id])
        for rental in all_rentals
    ]

    return rentals_price_details


if __name__ == '__main__':
    rentals_price_detail = main()
    final_output = {"rentals": rentals_price_detail}

    with open(r'level1/data/generated_output.json', 'w') as output_file:
        json.dump(final_output, output_file, indent=2)
