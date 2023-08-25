from thefuzz import fuzz
from thefuzz import process


def read_txt(path):
	with open(path, 'r') as f:
		lines = f.readlines()
	return [l.replace('\n', '') for l in lines]


def get_root_ingredient(ingredient, ingredients_list):
	index = ingredients_list.index(ingredient)
	valid_elements = [el for el in ingredients_list[:index] if el [:4] == '### ']
	return valid_elements[-1]


def process_all_ingredients(md_lines):
	ingredients_lines = [line.lower() for line in md_lines if line[:3] == '###']
	all_ingredients_list = []
	for ingredient in ingredients_lines:
		if ingredient[:4] == '####':
			root_ingredient = get_root_ingredient(ingredient, ingredients_lines[:])
			processed_line = f"{root_ingredient.replace('#', '').strip()} {ingredient.replace('#', '').strip()}"
		else:
			processed_line = ingredient.replace('#', '').strip()
		all_ingredients_list.append(processed_line)
	return all_ingredients_list


def process_recipe_ingredients(txt_lines):
	return [item.lower().strip() for sublist in txt_lines for item in sublist.split(',')]


all_ingredients = process_all_ingredients(read_txt('../ingredientes.md'))
recipe_ingredients = process_recipe_ingredients(read_txt('example.txt'))

#recipe_ingredients = ['aceite', 'aceite de sesamo', 'aceite vegetal']
#all_ingredients = ['aceite', 'aceite de sesamo', 'vegetal aceite']
margin = 80

for el in recipe_ingredients:
	#match = process.extract(el, all_ingredients, scorer=fuzz.token_sort_ratio, limit=3)
	match = process.extractOne(el, all_ingredients, scorer=fuzz.token_sort_ratio)
	if match[1] > margin:
		print(match[0])

