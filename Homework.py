from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value: str):
        if not value.isdigit():
            raise ValueError("Phone must contain only digits.")
        if len(value) != 10:
            raise ValueError("Phone must contain exactly 10 digits.")
        super().__init__(value)

    def formatted(self):
        return f"+{self.value}"


class Birthday(Field):
    def __init__(self, value: str):
        if not value:
            raise ValueError("Birthday cannot be empty.")
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone: str, new_phone: str):
        for i, ph in enumerate(self.phones):
            if ph.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        return False

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def get_upcoming_birthdays(self, days_ahead: int = 7):
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if record.birthday:
                bday_date = datetime.strptime(
                    record.birthday.value, "%d.%m.%Y"
                ).date()

                next_bday = bday_date.replace(year=today.year)

                if next_bday < today:
                    next_bday = next_bday.replace(year=today.year + 1)

                if 0 <= (next_bday - today).days <= days_ahead:

                    if next_bday.weekday() >= 5:
                        next_bday += timedelta(days=(7 - next_bday.weekday()))

                    upcoming.append({
                        "name": record.name.value,
                        "birthday": next_bday.strftime("%d.%m.%Y")
                    })

        return upcoming


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Not enough arguments provided."
        except ValueError as ve:
            return str(ve)
        except KeyError:
            return "Contact not found."
        except AttributeError:
            return "Contact not found."
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)

    if record.change_phone(old_phone, new_phone):
        return "Phone updated."

    return "Old phone not found."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)

    return ", ".join(ph.formatted() for ph in record.phones)


@input_error
def add_birthday_handler(args, book: AddressBook):
    name, bday, *_ = args
    record = book.find(name)

    record.add_birthday(bday)
    return f"Birthday for {name} added."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)

    return f"{name}'s birthday: {record.birthday.value}"


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No birthdays in the next 7 days."

    return "\n".join(
        f"{item['name']} - {item['birthday']}"
        for item in upcoming
    )


@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "Address book is empty."

    result = []

    for record in book.data.values():
        phones = ", ".join(ph.formatted() for ph in record.phones)
        bday = record.birthday.value if record.birthday else "-"
        result.append(
            f"{record.name.value}: {phones} | Birthday: {bday}"
        )

    return "\n".join(result)


def parse_input(user_input: str):
    tokens = user_input.strip().split()
    if not tokens:
        return None, []
    return tokens[0], tokens[1:]


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()

        if not user_input:
            print("Please enter a command.")
            continue

        command, args = parse_input(user_input)

        if command is None:
            continue

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday_handler(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()