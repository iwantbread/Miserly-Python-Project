
from decimal import Decimal

class Purchase:
    def __init__(self, item, store, price: Decimal, quantity: int):
        self.item = item
        self.store = store
        self.price = price
        self.quantity = quantity

    def calculate_total(self):
        return self.price * self.quantity


bread = Purchase("Brennans", "Lidl", Decimal("2.10"), 2)
milk = Purchase("Avonmore", "Aldi", Decimal("1.80"), 2)

print(bread.calculate_total())
print(milk.calculate_total())
