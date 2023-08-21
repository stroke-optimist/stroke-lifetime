# Lifetime stroke outcome model


[![Open in Streamlit][streamlit-img]][streamlit-link] [![DOI][doi-img]][doi-link]

This repository contains the code behind the Streamlit app for the lifetime stroke model.

+ __Streamlit app:__ https://lifetime-stroke-outcome.streamlit.app/
+ __DOI:__ https://doi.org/10.5281/zenodo.8269389

The model is described in _a paper that's not yet published. Link will be added when available_.

The app takes user inputs to select the age, sex, and Modified Rankin Scale (mRS) score on discharge from hospital following a stroke, and these are used to calculate the following quantities across the remainder of that patient's lifespan:
+ The probability of survival of the patient in each year.
+ The number of Quality-Adjusted Life Years (QALYs).
+ The expected use of resources (e.g. number of admissions to A&E and number of years spent in residential care) and the cost of those resources.
+ The discounted total net benefit by change in mRS score. 

## Layout of the code

The `.py` file behind each page is kept as short as possible so that it is easier to change the layout of the displayed page.

Generally the necessary calculations are stored in functions in `utilities/main_calculations.py`, and most of the formatting and displaying of objects is in the "container" scripts e.g. `utilities/container_X.py` (named for [Streamlit's way of grouping objects](https://docs.streamlit.io/library/api-reference/layout/st.container) but actually just `.py` scripts with all of the code needed to populate that chunk of the page).

### Which scripts do you need?

If you want to use the models but aren't interested in the Streamlit parts, you will just need:

+ `utilities_lifetime/models.py` - Basic models
+ `utilities_lifetime/fixed_params.py` - Constants
+ `utilities_lifetime/main_calculations.py` - Gathers the basic models and calculates all of the useful outputs. 

To work out how to piece it all together, it might be helpful to look at the "Calculations" section of `Interactive_demo.py`


### Pages 

The Streamlit landing page is `1: Introduction.py`. In the sidebar there are a series of other pages to choose, and these are stored in the `pages/` directory:

+ `2: Interactive_demo.py` - the main page. The user can select the values of the patient's age, sex, and mRS score, and these are used to populate a series of charts and tables about that patient's expected mortality, QALYs, resource use, and cost-effectiveness.
+ `3: Advanced_options.py` - currently empty.
+ `4: Project.py` - information about the project and people behind this project.
+ `5: Cite_this_work.py` - Zenodo citation. 
+ `6: Resources.py` - links to further useful materials. 

The page topics follow the recommendations of [Tom Monks and Alison Harper (in Proceedings of the Operational Research Society Simulation Workshop 2023 (SW23))](https://doi.org/10.36819/SW23.030). 

When these pages display a large amount of markdown text in one go, that text is imported from a `.txt` file in `pages/text_for_pages/` to prevent constant re-spacing to keep the lines below 79 characters. 

### Utilities
The `utilities_lifetime` directory contains the bulk of the useful code. 

| File | Contents | 
| --- | --- | 
| `container_costeffectiveness.py` | Gathers everything under the "Cost-effectiveness" tab.
| `container_inputs.py` | Gathers the user input widgets.
| `container_mortality.py` | Gathers everything under the "Mortality" tab.
| `container_qalys.py` | Gathers everything under the "QALYs" tab.
| `container_resources.py` | Gathers everything under the "Resource use" tab.
| `fixed_params.py` | Stores constants and coefficients. |
| `inputs.py` | Contains a function for reading markdown text from a file and writing to Streamlit. |
| `latex_equations.py` | Stores many functions that return a string containing a LaTeX-formatted function or a markdown-formatted table that can be written to Streamlit. Some of these are "generic" static formulae and others replace certain symbols in the formula with variables. |
| `main_calculations.py` | Contains more complicated functions with much python jiggery-pokery for calculating lots of quantities in one go. Typically uses the functions in `models.py` but wrapped in a "for" loop. |
| `models.py` | Contains functions for calculating the simpler quantities, i.e. those that can be described by a short formula rather than lots of python jiggery-pokery.  |

`utilities_lifetime/` also contains an empty `__init__.py` file that allows the container scripts to import functions directly from the latex equations script. 

#

[streamlit-img]: https://static.streamlit.io/badges/streamlit_badge_black_white.svg
[streamlit-link]: https://lifetime-stroke-outcome.streamlit.app/

[doi-img]: https://zenodo.org/badge/575076706.svg
[doi-link]: https://doi.org/10.5281/zenodo.8269389