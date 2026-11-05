
from decimal import Decimal

class Purchase:
    def __init__(self, item, store, price: Decimal, quantity: int):
        self.item = item
        self.store = store
        self.price = price
        self.quantity = quantity

    def calculate_total(self):
        return self.price * self.quantity

bread = Purchase("Brennans", "Lidl", Decimal("2.10"), 1)
milk = Purchase("Avonmore", "Aldi", Decimal("1.80"), 1)
eggs = Purchase("Eggfarm", "Tesco", Decimal("1.60"), 1)
butter = Purchase("Dairygold", "Tesco", Decimal("2.50"), 1)

shopping_basket = []

shopping_basket.append(bread)
shopping_basket.append(bread)
shopping_basket.append(milk)
shopping_basket.append(milk)
shopping_basket.append(eggs)
shopping_basket.append(butter)

print(bread.calculate_total())
print(milk.calculate_total())

amount = 0

for purchase in shopping_basket:
    amount = amount + purchase.calculate_total()
    print(purchase.calculate_total())

total = amount