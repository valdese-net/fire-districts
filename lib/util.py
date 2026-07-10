def format_millions(num, precision=1):
	if num == 0: return f"{num:.{precision}f}"
	magnitude = 0
	if abs(num) >= 1_000_000: magnitude = 6
	formatted_num = num / (10 ** magnitude)
	return f"{formatted_num:.{precision}f}M"

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
