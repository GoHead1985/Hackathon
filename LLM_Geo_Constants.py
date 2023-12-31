import configparser
config = configparser.ConfigParser()
config.read('config.ini')

# use your KEY.
OpenAI_key = config.get('API_Key', 'OpenAI_key')
# print("OpenAI_key:", OpenAI_key)


# carefully change these prompt parts!   

#--------------- constants for graph generation  ---------------
graph_role = r'A professional Geo-information scientist and developer good at Python.'

graph_task_prefix = r'Generate a graph (data structure) only, whose nodes are (1) a series of consecutive steps and (2) data to solve this question: '

graph_reply_exmaple = r"""
```python
import networkx as nx
G = nx.DiGraph()
# Add nodes and edges for the graph
# 1 Load hazardous waste site shapefile
G.add_node("haz_waste_shp_url", node_type="data", path="https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/Hazardous_Waste_Sites.zip", description="Hazardous waste facility shapefile URL")
G.add_node("load_haz_waste_shp", node_type="operation", description="Load hazardous waste facility shapefile")
G.add_edge("haz_waste_shp_url", "load_haz_waste_shp")
G.add_node("haz_waste_gdf", node_type="data", description="Hazardous waste facility GeoDataFrame")
G.add_edge("load_haz_waste_shp", "haz_waste_gdf")
...
```
"""
graph_requirement = [   
                        'Think step by step.',
                        'Steps and data (both input and output) form a graph stored in NetworkX. Disconnected components are NOT allowed.',
                        'Each step is a data process operation: the input can be data paths or variables, and the output can be data paths or variables.',
                        'There are two types of nodes: a) operation node, and b) data node (both input and output data). These nodes are also input nodes for the next operation node.',
                        'The input of each operation is the output of the previous operations, except the those need to load data from a path or need to collect data.',
                        'You need to carefully name the output data node.',
                        'The data and operation form a graph.',
                        'The first operations are data loading or collection, and the output of the last operation is the final answer to the task.'
                        'Operation nodes need to connect via output data nodes, DO NOT connect the operation node directly.',
                        'The node attributes include: 1) node_type (data or operation), 2) data_path (data node only, set to "" if not given ), and description. E.g., {‘name’: “County boundary”, “data_type”: “data”, “data_path”: “D:\Test\county.shp”,  “description”: “County boundary for the study area”}.',
                        'The connection between a node and an operation node is an edge.', 
                        'Add all nodes and edges, including node attributes to a NetworkX instance, DO NOT change the attribute names.',
                        'DO NOT generate code to implement the steps.',
                        'Join the attribute to the vector layer via a common attribute if necessary.',
                        'Put your reply into a Python code block, NO explanation or conversation outside the code block(enclosed by ```python and ```).',
                        'Note that GraphML writer does not support class dict or list as data values.',
                        'You need spatial data (e.g., vector or raster) to make a map.',
                        'Do not put the GraphML writing process as a step in the graph.',
                        'Keep the graph concise, DO NOT use too many operation nodes.',
                        # 'Keep the graph concise, DO NOT over-split task into too many small steps, especially for simple problems. For example, data loading and data transformation/preprocessing should be in one operation node.',

                         ]

# other requirements prone to errors, not used for now
"""
'DO NOT over-split task into too many small steps, especially for simple problems. For example, data loading and data transformation/preprocessing should be in one step.',
"""



#--------------- constants for operation generation  ---------------
operation_role = graph_role

operation_task_prefix = r'You need to generate a Python function to do: '

operation_reply_exmaple = """
```python',
def Load_csv(tract_population_csv_url="https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/NC_tract_population.csv"):
# Description: Load a CSV file from a given URL
# tract_population_csv_url: Tract population CSV file URL
tract_population_df = pd.read_csv(tract_population_csv_url)
return tract_population_df
```
"""

operation_requirement = [                         
                        'DO NOT change the given variable names and paths.',
                        'Put your reply into a Python code block(enclosed by ```python and ```), NO explanation or conversation outside the code block.',
                        'If using GeoPandas to load a zipped ESRI shapefile from a URL, the correct method is "gpd.read_file(URL)". DO NOT download and unzip the file.',
                        "Generate descriptions for input and output arguments.",
                        "You need to receive the data from the functions, DO NOT load in the function if other functions have loaded the data and returned it in advance.",
                        "Note module 'pandas' has no attribute 'StringIO'",
                        "Use the latest Python module methods.",
                        "When doing spatial analysis, convert the involved spatial layers into the same map projection.",
                        "DO NOT reproject or set spatial data(e.g., GeoPandas Dataframe) if only one layer involved.",
                        "Map projection conversion is only conducted for spatial data layers such as GeoDataFrame. DataFrame loaded from a CSV file does not have map projection information.",
                        "If join DataFrame and GeoDataFrame, using common columns, DO NOT convert DataFrame to GeoDataFrame.",
                        "When joining tables, convert the involved columns to string type without leading zeros. ",
                        "When doing spatial joins, remove the duplicates in the results. Or please think about whether it needs to be removed.",
                        "If using colorbar for GeoPandas or Matplotlib visulization, set the colorbar's height or length as the same as the plot.",
                        "Graphs or maps need to show the unit.",
                        "Keep the needed table columns for the further steps.",
                        "Remember the variable, column, and file names used in ancestor functions when using them, such as joining tables or calculating.",
                        # "Show a progressbar (e.g., tqdm in Python) if loop more than 200 times, also add exception handling for loops to make sure the loop can run.",
                        "When crawl the webpage context to ChatGPT, using Beautifulsoup to crawl the text only, not all the HTML file.",
                        "If using GeoPandas for spatial joining, the arguements are: geopandas.sjoin(left_df, right_df, how='inner', predicate='intersects', lsuffix='left', rsuffix='right', **kwargs), how: default ‘inner’, use intersection of keys from both dfs; retain only left_df geometry column; ‘left’: use keys from left_df, retain only left_df geometry column. ",
                        "GEOID in US Census data and FIPS in Census boundaries are integer with leading zeros. If use pandas.read_csv() to GEOID or FIPS (or 'fips') columns from read CSV files, set the dtype as 'str'.",
                        # "Drop rows with NaN cells, i.e., df.dropna(),  before using Pandas or GeoPandas columns for processing (e.g. join or calculation).",
                        "DO NOT use 'if __name__ == '__main__:' statement because this program needs to be executed by exec().",
                        "Use the built-in functions or attribute, if you do not remember, DO NOT make up fake ones, just use alternative methods.",
                        "Pandas library has no attribute 'StringIO', so 'pd.compat.StringIO' is wrong, you need to use 'io.StringIO' instead.",

                        ]
# other requirements prone to errors, not used for now
"""
If joining FIPS or GEOID, need to fill the leading zeros (digits: state: 2, county: 5, tract: 11, block group: 12.
"Create a copy or use .loc to avoid SettingWithCopyWarning when using pandas DataFrames."
"When creating maps or graphs, make them looks beautiful and professional. Carefuly select color, and show the layout, aspect, size, legend, scale bar, colorbar, background, annotation, axis ticks, title, font size, and label appropriately, but not overloaded."
"""


#--------------- constants for assembly prompt generation  ---------------
assembly_role = graph_role
assembly_requirement = ['You can think step by step. ',
                    f"Each function is one step to solve the question. ",
                    f"The output of the final function is the question to the question.",
                    f"Put your reply in a code block(enclosed by ```python and ```), NO explanation or conversation outside the code block.",              
                    f"Save final  maps, if any. If use matplotlib, the function is: matplotlib.pyplot.savefig(*args, **kwargs).",  
                    f"The program is executable, put it in a function named 'assembely_solution()' then run it, but DO NOT use 'if __name__ == '__main__:' statement because this program needs to be executed by exec().",
                    "Use the built-in functions or attribute, if you do not remember, DO NOT make up fake ones, just use alternative methods.",
                    # "Drop rows with NaN cells, i.e., df.dropna(),  before using Pandas or GeoPandas columns for processing (e.g. join or calculation).",
                    ]

#--------------- constants for direct request prompt generation  ---------------
direct_request_role = graph_role

direct_request_task_prefix = r'Write a Python program'

direct_request_reply_exmaple = """
```python',

```
"""

direct_request_requirement = [
                        'DO NOT change the given variable names and paths.',
                        'Put your reply into a Python code block(enclosed by ```python and ```), NO explanation or conversation outside the code block.',
                        'If using GeoPandas to load a zipped ESRI shapefile from a URL, the correct method is "gpd.read_file(URL)". DO NOT download and unzip the file.',
                        "Generate descriptions for input and output arguments.",
                        "Note module 'pandas' has no attribute 'StringIO'",
                        "Use the latest Python module methods.",
                        "When doing spatial analysis, convert the involved spatial layers into the same map projection.",
                        "DO NOT reproject or set spatial data(e.g., GeoPandas Dataframe) if only one layer involved.",
                        "Map projection conversion is only conducted for spatial data layers such as GeoDataFrame. DataFrame loaded from a CSV file does not have map projection information.",
                        "If join DataFrame and GeoDataFrame, using common columns, DO NOT convert DataFrame to GeoDataFrame.",
                        "When joining tables, convert the involved columns to string type without leading zeros. ",
                        "When doing spatial joins, remove the duplicates in the results. Or please think about whether it needs to be removed.",
                        "If using colorbar for GeoPandas or Matplotlib visulization, set the colorbar's height or length as the same as the plot.",
                        "Graphs or maps need to show the unit.",
                        "Remember the variable, column, and file names used in ancestor functions when using them, such as joining tables or calculating.",
                        # "Show a progressbar (e.g., tqdm in Python) if loop more than 200 times, also add exception handling for loops to make sure the loop can run.",
                        "When crawl the webpage context to ChatGPT, using Beautifulsoup to crawl the text only, not all the HTML file.",
                        "If using GeoPandas for spatial joining, the arguements are: geopandas.sjoin(left_df, right_df, how='inner', predicate='intersects', lsuffix='left', rsuffix='right', **kwargs), how: default ‘inner’, use intersection of keys from both dfs; retain only left_df geometry column; ‘left’: use keys from left_df, retain only left_df geometry column. ",
                        "GEOID in US Census data and FIPS (or 'fips') in Census boundaries are integer with leading zeros. If use pandas.read_csv() to GEOID or FIPS (or 'fips') columns from read CSV files, set the dtype as 'str'.",
                        # "Drop rows with NaN cells, i.e., df.dropna(), before using Pandas or GeoPandas columns for processing (e.g. join or calculation).",
                        "The program is executable, put it in a function named 'direct_solution()' then run it, but DO NOT use 'if __name__ == '__main__:' statement because this program needs to be executed by exec().",

                        ]

#--------------- constants for debugging prompt generation  ---------------
debug_role = graph_role

debug_task_prefix = r'You need to correct the code of a program, then return the complete corrected code. '

debug_requirement = [
                        'Correct the code. Revise the buggy parts, but need to keep program structure, i.e., the function name, its arguments, and returns.',
                        'Elaborate your reasons for revision.',
                        'You must return the complete corrected program in only one Python code block(enclosed by ```python and ```); DO NOT return the revised part only.',
                        'If using GeoPandas to load a zipped ESRI shapefile from a URL, the correct method is "gpd.read_file(URL)". DO NOT download and unzip the file.',
                        "Note module 'pandas' has no attribute 'StringIO'",
                        "When doing spatial analysis, convert the involved spatial layers into the same map projection.",
                        "DO NOT reproject or set spatial data(e.g., GeoPandas Dataframe) if only one layer involved.",
                        "Map projection conversion is only conducted for spatial data layers such as GeoDataFrame. DataFrame loaded from a CSV file does not have map projection information.",
                        "If join DataFrame and GeoDataFrame, using common columns, DO NOT convert DataFrame to GeoDataFrame.",
                        "Remember the variable, column, and file names used in ancestor functions when using them, such as joining tables or calculating.",
                        "When joining tables, convert the involved columns to string type without leading zeros. ",
                        "When doing spatial joins, remove the duplicates in the results. Or please think about whether it needs to be removed.",
                        "If using colorbar for GeoPandas or Matplotlib visulization, set the colorbar's height or length as the same as the plot.",
                        "Graphs or maps need to show the unit.",
                        # "Show a progressbar (e.g., tqdm in Python) if loop more than 200 times, also add exception handling for loops to make sure the loop can run.",
                        "When crawl the webpage context to ChatGPT, using Beautifulsoup to crawl the text only, not all the HTML file.",
                        "If using GeoPandas for spatial joining, the arguements are: geopandas.sjoin(left_df, right_df, how='inner', predicate='intersects', lsuffix='left', rsuffix='right', **kwargs), how: default ‘inner’, use intersection of keys from both dfs; retain only left_df geometry column; ‘left’: use keys from left_df, retain only left_df geometry column. ",
                        "GEOID in US Census data and FIPS (or 'fips') in Census boundaries are integer with leading zeros. If use pandas.read_csv() to GEOID or FIPS (or 'fips') columns from read CSV files, set the dtype as 'str'.",
                        # "Drop rows with NaN cells, i.e., df.dropna(),  before using Pandas or GeoPandas columns for processing (e.g. join or calculation).",
                        # "Drop rows with NaN cells, i.e., df.dropna(),  if the error information reports NaN related errors."
                        #
                        ]

#--------------- constants for operation review prompt generation  ---------------
operation_review_role = graph_role

operation_review_task_prefix = r'Review the code of a function to determine whether the code meets its associated requirements. If not, correct it then return the complete corrected code. '

operation_review_requirement = [
                        'Review the code very carefully to ensure its correctness and robustness.',
                        'Elaborate your reasons for revision.',
                        'If the code has no error, and you do not need to modify the code, DO NOT return code, return "PASS" only, without any other explanation or description.',
                        'If you modified the code, return the complete corrected function. All returned code need to be inside only one Python code block (enclosed by ```python and ```).',
                        'DO NOT use more than one Python code blocks in your reply, because I need to extract the complete Python code in the Python code block.',
                        'Pay extra attention on file name, table field name, spatial analysis parameters, map projections, and NaN cells removal, in the used Pandas columns.',
                        'Pay extra attention on the common field names when joining Pandas DataFrame.',
                        'The given code might has error in mapping or visualization when using GeoPandas or Matplotlib packages.',
                        'Revise the buggy parts, but DO NOT rewrite the entire function, MUST keep the function name, its arguments, and returns.',
                 #
                        ]

#--------------- constants for assembly program review prompt generation  ---------------
assembly_review_role = graph_role

assembly_review_task_prefix = r'Review the code of a program to determine whether the code meets its associated requirements. If not, correct it then return the complete corrected code. '

assembly_review_requirement = [
                        'Review the code very carefully to ensure its correctness and robustness.',
                        'Elaborate your reasons for revision.',
                        'If the code has no error, and you do not need to modify the code, DO NOT return code, return "PASS" only, without any other explanation or description.',
                        'If you modified the code, DO NOT reture the revised part only; instead, return the complete corrected program. All returned code need to be inside only one Python code block (enclosed by ```python and ```)',
                        'DO NOT use more than one Python code blocks in your reply, because I need to extract the complete Python code in the Python code block.',
                        'Pay extra attention on file name, table field name, spatial analysis parameters, map projections, and NaN cells removal in the used Pandas columns.',
                        'Pay extra attention on the common field names when joining Pandas DataFrame.',
                        'The given code might has error in mapping or visualization when using GeoPandas or Matplotlib packages.',
                        'Revise the buggy parts, but DO NOT rewrite the entire program or functions, MUST keep the function name, its arguments, and returns.',

                        #
                        ]

#--------------- constants for direct program review prompt generation  ---------------
direct_review_role = graph_role

direct_review_task_prefix = r'Review the code of a program to determine whether the code meets its associated requirements. If not, correct it then return the complete corrected code. '

direct_review_requirement = [
                        'Review the code very carefully to ensure its correctness and robustness.',
                        'Elaborate your reasons for revision.',
                        'If the code has no error, and you do not need to modify the code, DO NOT return code, return "PASS" only, without any other explanation or description.',
                        'If you modified the code, return the complete corrected program. All returned code need to be inside only one Python code block (enclosed by ```python and ```)',
                        'DO NOT use more than one Python code blocks in your reply, because I need to extract the complete Python code in the Python code block.',
                        'Pay extra attention on file name, table field name, spatial analysis parameters, map projections, and NaN cells removal in the used Pandas columns.',
                        'Pay extra attention on the common field names when joining Pandas DataFrame.',
                        'The given code might has error in mapping or visualization when using GeoPandas or Matplotlib packages.',
                        #
                        ]


#--------------- constants for sampling data prompt generation  ---------------
sampling_data_role = graph_role

sampling_task_prefix = r"Given a function, write a program to run this function, then sample the returned data of the function. The program needs to be run by another Python program via exec() function, and the sampled data will be stored in a variable."

sampling_data_requirement = [
                        'Return all sampled data in a string variable named "sampled_data", i.e., sampled_data=given_function().',
                        'The data usually are tables or vectors. You need to sample the top 5 record of the table (e.g., CSV file or vector attritube table) If the data is a vector, return the map projection information.',
                        'The sampled data format is: "Map projection: XXX. Sampled data: XXX',
 
                        #
                        ]

