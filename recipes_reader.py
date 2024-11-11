import glob
import pdfplumber
import pandas as pd
import re
import streamlit as st

from pdfplumber.utils import extract_text

from utils import list_flatten


def get_pdf_data(path):
    extracted_text = process_pdf(path)
    recipe_data = {'ingredients': []}
    ingredients = False
    instructions = False
    instructions_lines = []
    for line in extracted_text:
        if 'Receta' in line and not recipe_data.get('recipe'):
            recipe_data['recipe'] = process_text(line.replace('Receta', '').split('Porciones')[0])
            recipe_data['sides'] = process_text(line.split('Porciones')[-1])
        elif 'Ingredientes' in line:
            ingredients = True
        elif ingredients:
            if 'Instrucciones' not in line:
                tmp_ingredients = [el for el in line.split(';') if el]
                for el in tmp_ingredients:
                    splitted_line = el.split(':')
                    recipe_data['ingredients'].append({'name': process_text(splitted_line[0]), 'quantity': process_text(splitted_line[1]) if len(splitted_line) > 1 else ''})
            else:
                ingredients = False
                instructions = True        
        elif instructions:
            instructions_lines.append(line)
        recipe_data['instructions'] = process_instructions_text(instructions_lines)

    return recipe_data


def process_instructions_text(lines):
    processed_lines = process_text('\n'.join(lines).replace('\n+', ' ')).split('•')
    return [el.strip() for el in lines]


def process_pdf(pdf_path):
    pdf = pdfplumber.open(pdf_path)
    all_text = []

    for page in pdf.pages:
        filtered_page = page
        chars = filtered_page.chars
        page_text = extract_text(chars, layout=True)
        all_text.extend(page_text.split('\n'))

    all_text = [p for p in all_text if any(c.isalpha() for c in p)]

    pdf.close()
    return all_text


def process_text(text):
    return re.sub(' +', ' ', text).strip()


def read_recipes():
    files = [file for file in glob.glob('static' + '/**/*.pdf', recursive=True) if 'template' not in file.lower()]
    data = {}
    for pdf_path in files:

        file_class = pdf_path.split('/')[-2]

        pdf_data = get_pdf_data(pdf_path)
        pdf_data['pdf'] = pdf_path

        if file_class not in data:
            data[file_class] = []
        data[file_class].append(pdf_data)

    return data


@st.cache_data
def read_recipes_data():
    sorted_recipes = read_recipes()
    all_recipes = list_flatten([sorted_recipes[recipe_type] for recipe_type in sorted_recipes])
    all_ingredients = list(set([ingredient['name'] for recipe in all_recipes for ingredient in recipe['ingredients']]))
    return sorted_recipes, all_recipes, all_ingredients
