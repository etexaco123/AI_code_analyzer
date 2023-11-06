import slither
import json
import pprint
import streamlit as st
from solidity_parser import parser
import ast
from graphviz import Digraph
def gen_ast_solidity(feed):
    ''' This block of code generates an AST file from the solidity file, saves it as a JSON in the directory and returns the AST as a dict'''
    ast_dict = dict(parser.parse_file(feed, loc = False))

    # Write AST dictionary to a JSON file
    with open("sol_ast.json", mode="w") as file_object:
        json.dump(ast_dict, file_object, indent=4)

    return ast_dict

def get_edges(treedict, parent=None):
    '''This block transverses the solidity AST to append the edges of the tree excludes the parent which is the file definition'''
    edges = []
    for key, value in treedict.items():
        if isinstance(value, dict):
            if parent is not None:
                edges.append((parent, key))
            edges.extend(get_edges(value, parent=key))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    if parent is not None:
                        edges.append((parent, f"{key}[{index}]"))
                    edges.extend(get_edges(item, parent=f"{key}[{index}]"))
    return edges


# def gen_dot_file(ast_dict):
# # Get edges from the AST dictionary
#         edges = get_edges(ast_dict)

#         # Visualize the AST using Graphviz DOT format in Streamlit
#         dot_format = "digraph G {\n"
#         for edge in edges:
#                 dot_format += f'  "{edge[0]}" -> "{edge[1]}" \n'
#                 dot_format += "}"
#         return dot_format
# # Display the Graphviz chart using Streamlit
# st.graphviz_chart(gen_dot_file(ast_dict), use_container_width=True)

# save the the solidity AST and the python AST to a dot file
def gen_dot_file(ast_dict):
    '''This block converts the python AST or the solidity AST to a dot file so it can be visualized by graphviz '''
    # Get edges from the AST dictionary
    edges = get_edges(ast_dict)

    # Visualize the AST using Graphviz DOT format in Streamlit
    dot_format = "digraph G {\n"
    for edge in edges:
        dot_format += f'  "{edge[0]}" -> "{edge[1]}" \n'
    dot_format += "}"
    
    return dot_format

    # Save dot_format to a DOT file
    # try:
    #     with open(output_file_path, "w") as dot_file:
    #         dot_file.write(dot_format)
    #     return f"DOT file saved successfully at: {output_file_path}"
    # except Exception as e:
    #     return f"Error saving DOT file: {e}"

#**************************************************************
#-------------Analyze python file ---------------------
#**************************************************************
def generate_ast_python(feed):
    '''This block generate the python AST using the AST python module '''
    try:
        ast_dict = ast.parse(feed)
        ast_dump = ast.dump(ast_dict, indent=4)
        # with open(feed, 'r') as file:
        #     contents = file.read()
        #     ast_dict = ast.parse(contents)
        #     ast_dump = ast.dump(ast_dict, indent=4)

        return ast_dump , ast_dict
    except SyntaxError as e:
        print("There is a Syntax error in the file")
        return None


def ast_to_dict(node):
    ''' this block converts the python AST returned from the generate_ast_python function'''
    node_dict = {'type': type(node).__name__}

    for field, value in ast.iter_fields(node):
        if isinstance(value, ast.AST):
            node_dict[field] = ast_to_dict(value)
        elif isinstance(value, list):
            node_dict[field] = [ast_to_dict(item) if isinstance(item, ast.AST) else item for item in value]
        else:
            node_dict[field] = value

    return node_dict

def print_ast(ast_dict):  # recieves the output from ast_to_dict(feed) and writes the content to a json file
    with open("py_ast.json", mode="w") as file:
         json.dump(ast_dict, file, indent=4)


#alternative for edges 
# def get_edges(treedict, parent=None):
#     edges = []
#     for key, value in treedict.items():
#         if isinstance(value, dict):
#             if parent is not None:
#                 edges.append((parent, key))
#             edges.extend(get_edges(value, parent=key))
#         elif isinstance(value, list):
#             for item in value:
#                 if isinstance(item, dict):
#                     if parent is not None:
#                         edges.append((parent, key))
#                     edges.extend(get_edges(item, parent=key))
#     return edges
	