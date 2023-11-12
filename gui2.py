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
from tempfile import NamedTemporaryFile

from slither import Slither
import ast
import graphviz
from graphviz import Digraph
import openai
import subprocess
from PIL import Image
import solcx
import json
import glob 
import sys
import pprint
from solidity_parser import parser
from visualize import gen_ast_solidity , get_edges , gen_dot_file, generate_ast_python, ast_to_dict

load_dotenv()

# initialize openAPI access
# openai.api_key = os.getenv('OPEN_API_KEY')
openai.api_key = os.getenv('USER_OPEN_API_KEY')
subprocess.run(f'solc-select install 0.8.0 ', shell=True)
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
.viewerBadge_container__r5tak styles_viewerBadge__CvC9N{
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


# # ------------------------------to generate AST from solidity code --------------------------

# # -------------------------------visualize AST with graphviz----------------------------------
# #----------putting it together -----------
MAX_API_CALLS = 4
no_api_call = 3
@st.cache_data                                 #to enable catching for the API calls
def interpret_code_with_llm(code):
    if st.session_state.user_api_key is None and st.session_state.no_api_call >= MAX_API_CALLS:
           st.warning("Please enter your API key in the Tab above")
           return None
    else:
        response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Interpret the following code and describe in details its functionality.\
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
@st.cache_data
def analyze_contract(uploaded_file):
    # Path to save the uploaded file temporarily
    # temp_file_path = os.path.join("slitter_output", uploaded_file)
    temp_file_path = os.path.abspath(uploaded_file)
    
    slither = Slither(temp_file_path, solc_version= os.getenv("SOLC_VERSION"))
    # List to store generated files
    analysis_reports = {}
    
    # Run Slither subprocess commands and parse the output
    slither_output1 = subprocess.run(f'slither {temp_file_path} --print cfg --json -', shell=True, capture_output=True, text=True)
    
    slither_output2 = subprocess.run(f'slither {temp_file_path} --print call-graph --json -', shell=True, capture_output=True, text=True)
     
#     slither_output3 = subprocess.run(f'slither {temp_file_path} --print human-summary --json -', shell=True, capture_output=True, text=True)
    
    slither_output4 = subprocess.run(f'slither {temp_file_path} --print inheritance-graph --json -', shell=True, capture_output=True, text=True)

    # slither_output5 = subprocess.run(f'solc {temp_file_path} --ast-compact-json', shell=True, capture_output=True, text=True)


    analysis_reports["cfg"] = slither_output1.stdout
    analysis_reports["call-graph"] = slither_output2.stdout
#     analysis_reports["human-summary"] = slither_output3.stdout
    analysis_reports["inheritance-graph"] = slither_output4.stdout
    # generated_files["json-ast"] = slither_output5.stdout

    return analysis_reports

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
            
# -----------------------------------------------python AST section -----------------------------------------------------------------

# Create a Graphviz Digraph object
dot = Digraph()

# Define a function to get additional details for the node (customize this as needed)
def get_node_details(node):
    if isinstance(node, ast.FunctionDef):
        args = ", ".join(arg.arg for arg in node.args.args)
        return f"Name: {node.name}\nArguments: {args}"
    elif isinstance(node, ast.Assign):
        targets = ", ".join(target.id for target in node.targets)
        return f"Assign Targets: {targets}"
    elif isinstance(node, ast.If):
        return "If Statement"
    elif isinstance(node, ast.For):
        return f"For Loop: {node.target.id}"
    elif isinstance(node, ast.While):
        return "While Loop"
    elif isinstance(node, ast.Call):
        return f"Function Call: {node.func.id}"
    # Add more conditions and details for other node types as needed
    return ""
# Define a function to recursively add nodes to the Digraph
def add_node(node, parent=None):
    node_name = str(node.__class__.__name__)
    node_details = get_node_details(node)  # Get additional details for the node
    full_node_label = f"{node_name}\n{node_details}"
    dot.node(str(id(node)), full_node_label)
    if parent:
        dot.edge(str(id(parent)), str(id(node)))
    for child in ast.iter_child_nodes(node):
        add_node(child, node)

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
py_analyzed = {}
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

	# Upload & Error handling
	if uploaded_file is not None:
              f = NamedTemporaryFile(suffix=".sol", delete=False) # Create temporary file
              f.write(uploaded_file.getvalue())
              f.close()
        #       with open(f.name, 'r') as temp_file:
        #                 contents = temp_file.read()
        #       st.code(contents)
              st.success("File Upload Successful")

              content = uploaded_file.read().decode('utf-8')
              st.code(content)
              button1 = st.button("Analyze and Visualize" )
              button2 = st.button("Interprete")

              # Initialize session state
              if "analyze_state" not in st.session_state:
                        st.session_state.analyze_state = False
              if "interpret_state" not in st.session_state:
                        st.session_state.interpret_state = False

              if button1 or st.session_state.analyze_state:
                      st.session_state.analyze_state = True
                      with st.spinner(text="In progress..."):
                             if uploaded_file.name.endswith(".py"):
                                    ast_dict = generate_ast_python(content)
                                    py_analyzed.update({"AST": ast_dict[0], "AST-Graph":ast_dict[1] }) 
                                    add_node(py_analyzed["AST-Graph"])
                                    # Render the Digraph as a PNG file
                                    dot.format = 'png'
                             else:
                                analyzed_files = analyze_contract(f.name)
                                # analyze_contract(os.path.abspath(uploaded_file.name))
                                ast_dict = gen_ast_solidity(f.name) # from here
                                ast_graph = gen_dot_file(ast_dict)
                                # ast_str = json.dumps(ast_dict)
                                analyzed_files.update({"AST": ast_dict, "AST-Graph":ast_graph})
                                # gen_dot_file(ast_dict, os.path.abspath("ast-tree-graph.dot")) # to here
                        #      st.write(ast_dict)
                #       dot = gen_dot_file(ast_dict)
                #       g = ' \'\'\' ' + dot + ' \'\'\''
                #       st.code(dot)
                        #      st.graphviz_chart(rf'''{dot}''', use_container_width=True)
                      if uploaded_file.name.endswith(".py"):
                                all_files = py_analyzed.keys()
                      else:
                                all_files = analyzed_files.keys()
                                
                      option = st.selectbox("Select a Task", all_files, placeholder="Select a .dot file loaded")
                      if option == "cfg" or option == "call-graph" or option == "inheritance-graph" :
                                data = json.loads(analyzed_files[option])
                                st.graphviz_chart(data["results"]["printers"][0]["elements"][0]["name"]["content"]) # this works
                      elif option == "AST" and uploaded_file.type == 'text/x-python': st.code(py_analyzed[option])
                      elif option == "AST-Graph" and uploaded_file.type == 'text/x-python': st.graphviz_chart(dot)
                      elif option == "AST": st.write(analyzed_files[option])
                      else : st.graphviz_chart(analyzed_files[option])
                                             
              if button2 or st.session_state.interpret_state:
                #       with open(uploaded_file.name, 'r', encoding = 'utf-8') as f:
                #               content2 = f.read()
                      try:
                        interpretation = interpret_code_with_llm(content)
                        st.write('### Check the AI description of your code')
                        st.write(interpretation)

                      except Exception as e:
                        st.error("Please enter your API key")
                                     

                      




    










