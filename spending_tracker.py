from datetime import date
from decimal import Decimal

class Purchase:
    def __init__(self, item, store, price: Decimal, quantity: int, date: date):
        self.item = item
        self.store = store
        self.price = price
        self.quantity = quantity
        self.date = date

    def calculate_total(self):
        return self.price * self.quantity

bread = Purchase("Brennans", "Lidl", Decimal("2.10"), 1, date.today())
milk = Purchase("Avonmore", "Aldi", Decimal("1.80"), 1, date(2026,11,12))
eggs = Purchase("Eggfarm", "Tesco", Decimal("1.60"), 1, date(2026,11,10))
butter = Purchase("Dairygold", "Tesco", Decimal("2.50"), 1, date(2026,11,6))

shopping_basket = []

shopping_basket.append(bread)
shopping_basket.append(bread)
shopping_basket.append(milk)
shopping_basket.append(milk)
shopping_basket.append(eggs)
shopping_basket.append(butter)

print(bread.calculate_total())
print(milk.calculate_total())

def basket_total(basket):
    amount = Decimal("0.00")
    for purchase in basket:
        amount += purchase.calculate_total()
        print(purchase.calculate_total())
    return amount

print(basket_total(shopping_basket))
print(bread.date)