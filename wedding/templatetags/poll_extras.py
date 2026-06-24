from django import template

register = template.Library()


@register.filter(name='get_by_index')
def get_by_index(indexable, i):
    try:
        return indexable[i]
    except IndexError:
        return None


@register.filter(name='price_currency')
def price_currency(price, currency):
    return round(float(price)*float(currency))


@register.filter(name='discount_percent')
def discount_percent(price, percent):
    return price-(price*percent/100)


@register.filter(name='discount_amount')
def discount_amount(price, amount):
    return price-amount


@register.filter(name='get_by_key')
def get_by_key(indexable, i):
    try:
        return indexable[str(i)]
    except:
        return None


@register.filter(name='multiply')
def multiply(a, b):
    a = str(a).replace(',', '')
    b = str(b).replace(',', '')
    return f'{int(round(float(a) * float(b))):,}'


@register.filter(name='multiply_without_separator')
def multiply_without_separator(a, b):
    a = str(a).replace(',', '')
    b = str(b).replace(',', '')
    return int(round(float(a) * float(b)))


@register.filter(name='to_str')
def to_str(val):
    return str(val)


@register.filter(name='division')
def division(a, b):
    return round(a/b, 2)


@register.filter(name='plus')
def plus(a, b):
    try:
        int(a) + int(b)
        return int(a)+int(b)
    except:
        return 0


@register.filter(name='debugger')
def debugger(pos):
    print("I m in {} ".format(pos))
