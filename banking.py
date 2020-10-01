import random
import sqlite3

conn = sqlite3.connect('card.s3db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS card (
                number TEXT NOT NULL,
                pin TEXT NOT NULL,
                balance INTEGER DEFAULT 0 NOT NULL
);""")


class Card:
    card_n = None
    pin_num = None
    balance = None

    def __init__(self):
        self.card_n = "400000" + str(random.randint(10**9, 10**10 - 1))
        self.card_creator()
        self.pin_num = random.randint(10**3, 10**4-1)
        self.balance = 0

    def card_creator(self):
        card_list = list(str(self.card_n))
        del card_list[-1]
        total = 0
        for i in range(15):
            if i % 2 == 0:
                card_list[i] = str(int(card_list[i]) * 2)
                if int(card_list[i]) > 9:
                    card_list[i] = str(int(card_list[i]) - 9)
            total += int(card_list[i])
        checksum = ((total//10 + 1) * 10) - total
        card_list = list(str(self.card_n))
        card_list[-1] = str(checksum)
        self.card_n = "".join(card_list)


def luhn_checker(cardnum):
    cardlist = list(str(cardnum))
    total = 0
    i = None
    for i in range(15):
        if i % 2 == 0:
            cardlist[i] = str(int(cardlist[i]) * 2)
            if int(cardlist[i]) > 9:
                cardlist[i] = str(int(cardlist[i]) - 9)
        total += int(cardlist[i])
    checksum = ((total//10 + 1) * 10) - total
    # print(checksum, cardlist[-1])
    if checksum == int(cardlist[-1]):
        return 0
    else:
        return -1


def money_transfer(card_input, balance):
    print("Transfer\nEnter card number:")
    trn_card = int(input())
    if luhn_checker(trn_card) == -1:
        print("Probably you made mistake in the card number. Please try again!")
        return -1
    elif luhn_checker(trn_card) == 0:
        if c.execute("""SELECT number
                        FROM card
                        WHERE 
                        number = ?""", (str(trn_card),)).fetchone() is None:
            print("Such a card does not exist.\n")
            return -1
        else:
            money_trn = int(input("Enter how much money you want to transfer:\n"))
            print(money_trn, balance)
            if money_trn < balance:
                c.execute("""UPDATE card SET balance = balance - ? WHERE number = ?""", (money_trn, str(card_input)))
                c.execute("""UPDATE card SET balance = balance + ? WHERE number = ?""", (money_trn, str(trn_card)))
                conn.commit()
                print("Success!")
                print(c.execute("SELECT * FROM card").fetchall())
                return 0
            else:
                print("Not enough money!\n")


def account_checker():
    card_input = int(input("\nEnter your card number:\n"))
    pin_input = int(input("Enter your PIN:\n"))
    if c.execute("""SELECT number, pin
                        FROM card
                        WHERE 
                        number = ? AND 
                        pin = ?""", (str(card_input), pin_input)).fetchone() is None:
        print("\nWrong card number or PIN!\n")
    else:
        print("\nYou have successfully logged in:")
        while True:
            c.execute("""SELECT balance
                         FROM card
                         WHERE
                         number = ?""", ((str(card_input)),))
            balance = c.fetchone()[0]
            account_input = int(input("""
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit\n"""))

            if account_input == 1:
                print("Balance:", balance)

            elif account_input == 2:
                income = int(input("Enter income:"))
                c.execute("""UPDATE card 
                             SET balance = balance + ? 
                             WHERE
                             number = ?""", (income, str(card_input)))
                conn.commit()
                print("Income was added!")

            elif account_input == 3:
                money_transfer(card_input, balance)

            elif account_input == 4:
                c.execute("DELETE FROM card WHERE number = ?", ((str(card_input)), ))
                print("The account has been closed!\n")
                conn.commit()
                return 0

            elif account_input == 5:
                print("You have successfully logged out!")
                return 0
            else:
                return -1


def main():
    user_card = None
    while True:
        user_input = int(input("1. Create an account\n2. Log into account\n0. Exit\n"))
        if user_input == 1:
            user_card = Card()
            c.execute("INSERT INTO card (number, pin) VALUES(?, ?);", (user_card.card_n, user_card.pin_num))
            conn.commit()
            print("\nYour card has been created\nYour card number:\n{}\nYour card PIN:\n{}\n".format(user_card.card_n, user_card.pin_num))
        elif user_input == 2:
            response = account_checker()
            if response == -1:
                print("Bye!")
                break
        else:
            print("Bye!")
            return 0


main()
conn.close()
