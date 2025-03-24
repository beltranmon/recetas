import base64
import pandas as pd
import streamlit as st

from streamlit_pdf_viewer import pdf_viewer
from streamlit_pills import pills
from streamlit_tags import st_tags

from recipes_reader import read_recipes_data
from utils import read_json, words_distance, list_flatten

from streamlit_js_eval import streamlit_js_eval


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
            if any(ingredient.lower() in recipe_ingredients for ingredient in word_search):
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


def show_recipes(recipes, pdf_width, input_type):
    recipes = sorted(recipes, key=lambda x: x['recipe'])
    for recipe in recipes:
        with st.expander(recipe['recipe']):
            pdf_viewer(recipe['pdf'], width=pdf_width, key=f"{recipe['recipe']}-{input_type}")
            #show_pdf(recipe['pdf'])


def frontend(sorted_recipes, all_recipes, all_ingredients, pdf_width):
    st.header("""Recetas""")
    tab1, tab2, tab3 = st.tabs(['Instructivos' , 'Recetas', 'Buscador'])
    # TUTORIALS
    with tab1:
        show_readme('README.md')

    with tab2:
        selected_recipe_type = pills("Tipo", sorted(list(sorted_recipes)))
        show_recipes(sorted_recipes[selected_recipe_type], pdf_width, 'list')
    
    with tab3:
        ingredients = st_tags(label='Escribe tus ingredientes', text="Enter para añadir más")
        strict_search = st.toggle('Incluir TODOS los ingredientes')
        matches = words_distance(ingredients, all_ingredients)
        filtered_recipes = filter_recipes(all_recipes, matches, strict_search)
        show_recipes(filtered_recipes, pdf_width, 'search')


def main():
    st.set_page_config(page_title='RECETAS',
                       page_icon=":rice:", layout="centered",
                       initial_sidebar_state="expanded")
    #if check_password():
    sorted_recipes, all_recipes, all_ingredients = read_recipes_data()
    screen_width = streamlit_js_eval(js_expressions='screen.width', key='SCRW')
    screen_height = streamlit_js_eval(js_expressions='screen.height', key='SCRH')#
    screen_prop =  screen_width / screen_height if (screen_width and screen_height) else 0
    pdf_width = 650 if screen_prop > 1 else 300
    frontend(sorted_recipes, all_recipes, all_ingredients, pdf_width)


if __name__ == "__main__":
    main()
