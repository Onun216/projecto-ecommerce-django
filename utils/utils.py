def format_price(value):
    return f'R$ {value:.2f}'.replace('.', ',')


def cart_total_qt(cart):
    return sum([item['quantity'] for item in cart.values()])


def cart_totals(cart):
    return sum(
        [
            item.get('unit_price_promotional')
            if item.get('unit_price_promotional')
            else item.get('unit_price')
            for item
            in cart.values()
        ]
    )
