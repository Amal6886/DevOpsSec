from products.models import Supplement, ProteinBar


def cart(request):
    cart_items = []
    cart_total = 0

    if 'cart' in request.session:

        for item in request.session['cart']:
            product_type = item.get('type')
            product_id = item.get('id')
            quantity = item.get('quantity', 1)

            if product_type == 'supplement':
                try:
                    product = Supplement.objects.get(id=product_id)
                    item_total = float(product.price) * quantity
                    cart_items.append({
                        'product': product,
                        'type': 'supplement',
                        'quantity': quantity,
                        'total': item_total
                    })
                    cart_total += item_total
                except Supplement.DoesNotExist:
                    continue
            elif product_type == 'protein_bar':
                try:
                    product = ProteinBar.objects.get(id=product_id)
                    item_total = float(product.price) * quantity
                    cart_items.append({
                        'product': product,
                        'type': 'protein_bar',
                        'quantity': quantity,
                        'total': item_total
                    })
                    cart_total += item_total
                except ProteinBar.DoesNotExist:
                    continue

    return {
        'cart_items': cart_items,
        'cart_total': round(cart_total, 2),
        'cart_count': len(cart_items)
    }





