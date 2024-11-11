import base64
import pandas as pd
import streamlit as st

from streamlit_pdf_viewer import pdf_viewer
from streamlit_pills import pills
from streamlit_tags import st_tags

from recipes_reader import read_recipes_data
from utils import read_json, words_distance, list_flatten


def check_password():
    """
    Checks the pwd input
    :return: Whether the user had the correct password
    """
    def password_entered():
        """Checks whether a password entered by the user is correct"""
        
        if st.session_state["password"] == pwd:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Contraseña", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Contraseña", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Contraseña incorrecta")
        return False
    else:
        # Password correct.
        return True


def filter_recipes(all_recipes, to_search, strict_search):
    if not to_search:
        return []
    filtered = []
    for word_search in to_search:
        word_filter = []
        for recipe in all_recipes:
            recipe_ingredients = [el['name'].lower() for el in recipe['ingredients']]
            if any(ingredient in recipe_ingredients for ingredient in word_search):
                word_filter.append(recipe['recipe'])
        filtered.append(word_filter)
    to_return = set.intersection(*[set(x) for x in filtered]) if strict_search else list(set(list_flatten(filtered)))
    return [recipe for recipe in all_recipes if recipe['recipe'] in to_return]


def show_pdf(file_path):
    """
    Prints a pdf in the frontend
    :param file_path: PDF's path
    """
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)


def show_readme(readme_path):
    """
    Shows in Streamlit a Readme file (images included)
    :param readme_path: MD's path
    """
    with open(readme_path, 'r') as f:
        readme_line = f.readlines()
    readme_buffer = []
    #resource_files = [os.path.basename(x) for x in glob.glob('Resources/*')]
    # resource_files
    for line in readme_line :
        readme_buffer.append(line) 
        """
        for image in resource_files:
            if image in line:
                st.markdown(''.join(readme_buffer[:-1])) 
                st.image(f'Resources/{image}')
                readme_buffer.clear()
        """
    st.markdown(''.join(readme_buffer))


def show_recipes(recipes, pdf_width):
    recipes = sorted(recipes, key=lambda x: x['recipe'])
    for recipe in recipes:
        with st.expander(recipe['recipe']):
            pdf_viewer(recipe['pdf'], width=pdf_width)
            #show_pdf(recipe['pdf'])


def frontend(sorted_recipes, all_recipes, all_ingredients):
    st.header("""Recetas""")
    pdf_width = st.sidebar.slider('Ancho del pdf', min_value=100, max_value=1000, value=650, step=50)
    # Sidebar Selecbox
    input_type_dict = {'Readme': 0, 'Recetas': 1, 'Buscador': 2}
    input_type = st.sidebar.selectbox("Funciones", input_type_dict, index=0)
    # TUTORIALS
    if input_type_dict[input_type] == 0:
        show_readme('README.md')

    if input_type_dict[input_type] == 1:
        st.subheader(input_type)
        selected_recipe_type = pills("Tipo", sorted(list(sorted_recipes))) #["🍀", "🎈", "🌈"] 
        show_recipes(sorted_recipes[selected_recipe_type], pdf_width)
        
    if input_type_dict[input_type] == 2:
        st.subheader(input_type)
        ingredients = st_tags(label='Escribe tus ingredientes (si el buscador está vacío no habrán resultados)', text="Enter para añadir más")
        strict_search = st.toggle('Incluir TODOS los ingredientes')
        matches = words_distance(ingredients, all_ingredients)
        filtered_recipes = filter_recipes(all_recipes, matches, strict_search)
        show_recipes(filtered_recipes)


def main():
    st.set_page_config(page_title='RECETAS',
                       page_icon=":rice:", layout="centered",
                       initial_sidebar_state="expanded")
    #if check_password():
    sorted_recipes, all_recipes, all_ingredients = read_recipes_data()
    frontend(sorted_recipes, all_recipes, all_ingredients)


if __name__ == "__main__":
    main()
