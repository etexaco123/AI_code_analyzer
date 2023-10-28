__version__ = "0.1.0.0"
app_name = "Code Analyzer"

# IMPORTS
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu

import os
from dotenv import load_dotenv, dotenv_values
import io
import yaml
from yaml.loader import SafeLoader

import requests

from slither import Slither
import ast
import graphviz
import openai
import subprocess
from PIL import Image
import solcx
import json
import glob 
import sys
import pprint
from solidity_parser import parser
from visualize import gen_ast_solidity , get_edges , gen_dot_file, generate_ast_python, ast_to_dict, print_ast

load_dotenv()
# openai.api_key = os.getenv('OPEN_API_KEY')
openai.api_key = os.getenv('USER_OPEN_API_KEY')
solcx.install_solc('0.8.0')
# Set the desired Solidity compiler version
solcx.set_solc_version('v0.8.0')

# # Set the SOLC_VERSION environment variable
hide_menu = """
<style>
#MainMenu {
	visibility: hidden;
}
footer{
	visibility: hidden;
}
.stDeployButton span{
        visibility: hidden;
}
</style>
"""
#hide default main menu items
st.markdown(hide_menu, unsafe_allow_html = True)


# Load YAML file for authenticating users
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# spacing for the side bar
def ui_spacer(n=2, line=False, next_n=0):
	for _ in range(n):
		st.write('')
	if line:
		st.tabs([' '])
	for _ in range(next_n):
		st.write('')

# Infomation to display on the About page
def ui_info():
	st.markdown(f"""
	# Welcome to Code Analyzer
	version {__version__}
	
	This Code Analyzer system is built on top of large language models from Open AI.
	""")
	ui_spacer(1)
	st.write("Made by [Ethelbert Uzodinma](https://www.linkedin.com/in/ethelbert-uzodinma).", unsafe_allow_html=True)
	ui_spacer(1)
	st.markdown("""
		Thank you for your interest in my application.
		Please be aware that this is only a Proof of Concept system
		and may contain bugs or unfinished features.
		If you like this app you can ❤️ [follow me](https://www.linkedin.com/in/ethelbert-uzodinma)
		on Linkedin for updates.
		""")
	ui_spacer(1)
	st.markdown('Source code can be found [here](https://github.com/etexaco123/codeanalyzer).')
    
	# ----------to generate AST from python code ---------------------
def generate_ast_python(code):
    return ast.parse(code)


# # ------------------------------to generate AST from solidity code --------------------------


#         # Get edges from the AST dictionary
# edges = get_edges(dict(sourceUnit)) 
# # Visualize the AST using Graphviz DOT format in Streamlit
# dot_format = "digraph G {\n"
# for edge in edges:
#         dot_format += f'  "{edge[0]}" -> "{edge[1]}" \n'
#         dot_format += "}"

# # -------------------------------visualize AST with graphviz----------------------------------
# def visualize_ast(ast_tree):
#     dot_data = ast.dump(ast_tree, annotate_fields=True, include_attributes=True)
#     graph = graphviz.Source(dot_data)
#     graph.render(filename="ast_tree", format="png", cleanup=True)

# #----------putting it together -----------
MAX_API_CALLS = 4
no_api_call = 3
# @st.cache_data(ttl=3600)                                 #to enable catching for the API calls
def interpret_code_with_llm(code):
    if st.session_state.user_api_key is None and st.session_state.no_api_call >= MAX_API_CALLS:
           st.warning("Please enter your API key in the Tab above")
           return None
    else:
        response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Interpret the following code and describe its functionality.\
                Also itemize the vulnerabilities in the contract \ highlight the vulnerabilities itemized in red, yellow and green respectively which maps to high, medium and low risk vulnerabilities :\n\n```{code}```\n\n:  ",
                max_tokens=2000,
                temperature = 0.0
        )
        return response.choices[0].text.strip()

# Function to set API key to environment variable and session state
def set_api_key(user_api_key):
    
    # Save API key to .env file
    with open(".env2", "w") as env_file:

        env_file.write(f"USER_OPEN_API_KEY={user_api_key}")
    
    # Set API key to environment variable
    os.environ["USER_OPEN_API_KEY"] = user_api_key
    
    # Set API key to session state
    st.session_state.user_api_key = user_api_key

# -------------------------------------- Analyze solidity contract --------------------------------------------   

def analyze_contract(contract_file_path):
       slither = Slither(contract_file_path, solc_version= os.getenv("SOLC_VERSION"))
       slither_output_dir = 'slither-report/'
       os.makedirs(slither_output_dir, exist_ok=True)
#        slither_output_file = os.path.join(slither_output_dir, 'contract.dot')
       # Get the contract's control flow graph (CFG) as a DOT format string

	   # # cfg_dot = slither.cfg()
       subprocess.run(f'slither {contract_file_path} --print cfg', shell = True)
       subprocess.run(f'slither {contract_file_path} --print call-graph', shell = True)
       subprocess.run(f'slither {contract_file_path} --print human-sumary', shell = True)
       subprocess.run(f'slither {contract_file_path} --print inheritance', shell = True)
       subprocess.run(f'slither {contract_file_path} --print inheritance-graph', shell = True)
#        subprocess.run(f'slither {contract_file_path} --print contract > contract.ast', shell = True)
    #    subprocess.run(f'dot -Tpng Voting.sol.Voting.call-graph.dot -o contract.png', shell = True)
       
	   # Save the DOT format string to a file (optional)
    #    with open('contract_cfg.dot', 'w') as dot_file:
    #           dot_file.write(cfg_dot)


# Example usage
# solidity_file_path = 'path/to/your/solidity_contract.sol'
# output_file_path = 'contract_visualization.png'
# generate_contract_visualization(solidity_file_path, output_file_path)
#--------------------------------------------- Tab section ---------------------------------------------------------------


st.session_state["no_api_call"] = no_api_call
# st.write(st.session_state)
def ui_api_key():
        # Initialize session state
        # if 'name' not in st.session_state:
        #         st.session_state.no_api_call = 0
        # else: st.info(f"API has been called {st.session_state.no_api_call} times")
        # no_api_call = 0
        # max_api_call = 4
        st.session_state.no_api_call = no_api_call
        st.write('## 1. Optional: Enter Your API key:')
        t1,t2 = st.tabs(['Trial version','enter your own API key'])
        with t1:
               pct = no_api_call * 25
               st.info("This tab allows you to use a free API key for 4 times after which you must get your own OPEN API key")
               p_text = st.write(f'Free tokens usage: :{"green" if pct < 100 else "red"}[{int(pct)}%]')
               no_of_calls = st.progress(pct , p_text)
               for i in range(0,101,25):
                      i = pct
                      no_of_calls.progress(pct, p_text)
        #        no_of_calls.empty() 
        with t2:
                user_api_key = st.text_input('OpenAI API key', type='password', label_visibility="collapsed")
                on = st.toggle('Activate API key')
                if on:
                        st.write('key Activated!')
                        set_api_key(str(user_api_key))
                elif "user_api_key" not in st.session_state:
                       # Check if API key is set in session state
                       st.session_state.user_api_key = None
            
# -----------------------------------------------Tab section end -----------------------------------------------------------------


# --------------- LAYOUT ----------------
# menu = ["About", "Login", "SignUp"]
# choice = st.sidebar.selectbox("Menu", menu)
# if choice == "About":
#         st.markdown("# Welcome to the Code Analyzer")
        	
with st.sidebar:
      choice = option_menu(
             menu_title = "Main Menu",
             options = ["Home", "Login", "SignUp"],
             icons = ["house", "key", "book" ],
             menu_icon = "cast",
             default_index = 0,
      )
if choice == "Home":
                if st.session_state["authentication_status"]:
                       pass
                else:
                        ui_info()
                        # st.write('## This is the about page')	
if choice == "Login":
        st.subheader("Login Section")
        authenticator.login('Login', 'sidebar') # name, authentication_status, username = 
        if st.session_state["authentication_status"]:
                authenticator.logout('Logout', 'main', key='unique_key')
                st.write(f'Welcome *{st.session_state["name"]}*')
                st.success("You are logged in")
                # st.title('Some content')
        elif st.session_state["authentication_status"] is False:
                st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
                st.warning('Please enter your username and password')
if choice == "SignUp":
        if st.session_state["authentication_status"]:
               pass
        else:
                st.subheader("Register your Credentials")
                try:
                        if authenticator.register_user('Register user', preauthorization=False):
                                st.success('User registered successfully')
                                with open('config.yaml', 'w') as file:
                                        yaml.dump(config, file, default_flow_style=False)
                except Exception as e:
                        st.error(e)

# abspath = 

# here is to show restricted content to authentic users
if st.session_state["authentication_status"]:
	# Text /  Title
	st.title("AuditONE\n Code Analyzer")

	#infomation about required files
	st.info("** Note this app only accepts .sol or .py files")

	# option to request user API key
	ui_api_key()

	# Header/ Subheader
	st.write('## 2. Select your Code File to Upload')
	# st.subheader("**Note this app only acepts .sol or .py files")
	# st.text("** Note this app only acepts .sol or .py files")


	uploaded_file = st.file_uploader("Upload a Solidity or Python file", type=["sol", "py"])

	# Error handling
	if uploaded_file is not None:
              st.success("File Upload Successful")

              content = uploaded_file.read().decode('utf-8')
              st.code(content)
              button1 = st.button("Analyze and Visualize" )
              button2 = st.button("Interprete")

              if button1:
                      with st.spinner(text="In progress..."):
                             if uploaded_file.name.endswith(".py"):
                                    ast_dict = generate_ast_python(os.path.abspath(uploaded_file.name))
                                    ast_dict = ast_to_dict(ast_dict)
                                    print_ast(ast_dict)
                                #     st.write(ast_dict)
                                    gen_dot_file(ast_dict, os.path.abspath("py-tree-graph.dot"))
                             else:
                                analyze_contract(os.path.abspath(uploaded_file.name))
                                ast_dict = gen_ast_solidity(uploaded_file.name)
                                gen_dot_file(ast_dict, os.path.abspath("ast-tree-graph.dot"))
                        #      st.write(ast_dict)
                #       dot = gen_dot_file(ast_dict)
                #       g = ' \'\'\' ' + dot + ' \'\'\''
                #       st.code(dot)
                        #      st.graphviz_chart(rf'''{dot}''', use_container_width=True)
              if uploaded_file.name.endswith(".py"):
                     all_files = ["py-tree-graph.dot", "py_ast.json"]
              else:
                all_files = glob.glob(os.path.abspath("*.dot")) + glob.glob(os.path.abspath("*.json"))
                
              selected_dot_file = st.selectbox("Select a .dot file", all_files, placeholder="Select a .dot file loaded",)
              with open(selected_dot_file, "r") as dot_file:
                                dot_content = dot_file.read()
                                if selected_dot_file.endswith(".dot"):
                                        st.graphviz_chart(dot_content)
                                elif selected_dot_file.endswith(".json"):
                                        ast_dict = gen_ast_solidity(uploaded_file.name) 
                                        st.write(ast_dict)
                                             
              if button2:
                      with open(uploaded_file.name, 'r', encoding = 'utf-8') as f:
                              content2 = f.read()
                              interpretation = interpret_code_with_llm(content2)

                      st.write(interpretation)




    










