from django import template

register = template.Library()

@register.filter
def outtoip(value):
	if value == None:
		return 0
	whole = round(value/3)
	frac = float(value%3)/10
	val =  whole+frac
	return val


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
