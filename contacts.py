import json
import re
from datetime import datetime
from collections import UserDict

class Field:
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid value")
        self.__value = value

    def __str__(self):
        return str(self.__value)

    def is_valid(self, value):
        return True

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid value")
        self.__value = value


class Name(Field):
    pass


class Phone(Field):
    def is_valid(self, value):
        return len(value) == 10 and value.isdigit()


class Email(Field):
    def validate_email_format(self, email):
        regex = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+")
        return bool(regex.fullmatch(email))

    def is_valid(self, value):
        return self.validate_email_format(value)


class Birthday(Field):    
    def __init__(self, value=None):
        if value:
            self._validate_birthday_format(value)
        super().__init__(value)

    def _validate_birthday_format(self, value):
        if value.lower() != 'none':  
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                raise ValueError 


class Record:
    def __init__(self, name, birthday=None, email=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)
        self.email = Email(email)

    def add_phone(self, phone):
        self.phones.append(str(phone))

    def remove_phone(self, phone):
        self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        index = self.phones.index(old_phone)
        self.phones[index] = new_phone

    def find_phone(self, phone):
        return phone in self.phones

    def days_to_birthday(self):
        try:
            if self.birthday and self.birthday.value:
                today = datetime.now().date()
                next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day).date()
                if today > next_birthday:
                    next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day).date()
                days_until_birthday = (next_birthday - today).days
                if days_until_birthday == 0:
                    return "Birthday today!"
                elif days_until_birthday == 1:
                    return "Tomorrow is your birthday!"
                else:
                    return f"The birthday of {self.name.value} is {days_until_birthday} days away."
        except Exception as e:
            print(f"Error calculating days to birthday for {self.name.value}: {e}")
        return None

    def __str__(self):
        birthday_info = f", Birthday: {self.birthday}" if self.birthday.value else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(self.phones)}{birthday_info}"


class AddressBook(UserDict):
    def __init__(self, filename):
        self.filename = filename
        super().__init__()
        self.load_from_json()

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __iter__(self):
        return self.iterator()

    def iterator(self, part_record=1):
        records = list(self.data.values())
        num_records = len(records)
        current_index = 0
        while current_index < num_records:
            yield records[current_index:current_index + part_record]
            current_index += part_record

    def save_to_json(self):
        with open(self.filename, "w") as fh:
            json.dump([{"name": record.name.value,
                        "phones": record.phones,
                        "email" : str(record.email), 
                        "birthday": str(record.birthday)} for record in self.data.values()], fh, indent=4)

    def load_from_json(self):
        try:
            with open(self.filename, "r") as fh:
                data = json.load(fh)
                if not data:
                    raise ValueError("The JSON file is empty.")
                else:
                    self.data.clear()
                    for item in data:
                        record = Record(item['name'])
                        for phone in item['phones']:
                            record.add_phone(phone)
                        record.birthday = Birthday(item['birthday'])
                        record.email = Email(item['email'])
                        self.add_record(record)
        except FileNotFoundError:
            print("File not found. Creating a new address book.")
        except json.JSONDecodeError as e:
            print(f"Error loading data from JSON: {e}")
        except Exception as e:
            print(f"Unexpected error occurred while loading data: {e}")


if __name__ == "__main__":
    address_book = AddressBook("address_book.json")

  
    print("All contacts:")
    print(address_book)

    
    address_book.save_to_json()