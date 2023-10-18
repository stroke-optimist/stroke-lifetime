"""
Interactive demo for Streamlit.

This page copies most of the calculations from the main demo page
and just displays them differently and provides a download option.

This script runs through everything from receiving user inputs
for age, sex, and mRS, to calculating all the quantities we need
for tables and charts of mortality, QALYs, resource use, and
cost effectiveness.

Most of the proper calculation functions are in main_calculations.py,
and most of the calls to write to streamlit are in the scripts
named container_(something).py.
"""
# ----- Imports -----
import streamlit as st
import numpy as np
import pandas as pd
from plotly.express.colors import sample_colorscale
import plotly.graph_objs as go

# Add an extra bit to the path if we need to.
# Try importing something as though we're running this from the same
# directory as the landing page.
try:
    from utilities_lifetime.fixed_params import page_setup
except ModuleNotFoundError:
    # If the import fails, add the landing page directory to path.
    # Assume that the script is being run from the directory above
    # the landing page directory, which is called
    # streamlit_lifetime_stroke.
    import sys
    sys.path.append('./streamlit_lifetime_stroke/')
    # The following should work now:
    from utilities_lifetime.fixed_params import page_setup

# Container scripts (which will be called after the calculations):
import utilities_lifetime.container_inputs
# The home of the main calculation functions:
import utilities_lifetime.main_calculations as calc
# Function to import fixed params for either mRS or dicho model:
from utilities_lifetime.fixed_params import get_fixed_params


def main():
    # ###########################
    # ##### START OF SCRIPT #####
    # ###########################
    # Set up the tab title and emoji:
    page_setup()

    # Page title:
    st.markdown(
        '''
        # Lifetime outcomes for multiple patients

        This page runs the lifetime outcomes model for many patients
        and gives the results as a downloadable table.

        You can use the buttons below to select which model type to use
        and the age range of the patients. For each age chosen,
        the model is run for each mRS score (separate mRS model)
        or outcome type (dichotomous model) and for a male and a female
        patient. The results for all patients are given in a single
        table.
        '''
        )
    # Draw a blue information box:
    st.info(
        ':information_source: ' +  # emoji
        'For acronym reference, see the introduction page.'
        )

    # ###########################
    # ########## SETUP ##########
    # ###########################

    st.markdown('## Select the patient details.')

    cols_input = st.columns(4)
    with cols_input[0]:
        age_min = st.number_input(
            'Minimum age:',
            min_value=45.0,
            max_value=90.0,
            value=45.0,
            step=0.5,
            help='Ranges from 45 to 90.',
            key='age_min'
            )
    with cols_input[1]:
        age_max = st.number_input(
            'Maximum age:',
            min_value=45.0,
            max_value=90.0,
            value=90.0,
            step=0.5,
            help='Ranges from 45 to 90.',
            key='age_max'
            )
    with cols_input[2]:
        age_step = st.number_input(
            'Step:',
            min_value=0.5,
            max_value=10.0,
            value=5.0,
            step=0.5,
            help='Ranges from 0.5 to 10.',
            key='age_step'
            )

    with cols_input[3]:
        model_input_str = (
            utilities_lifetime.container_inputs.model_type_input())
        # model_input_str is a string, either "mRS" or "Dichotomous".

    if age_max < age_min:
        st.warning(
            '''
            :warning: The maximum age must be larger than the minimum age.
            '''
            )
        st.stop()
    age_range = np.arange(age_min, age_max+1e-3, age_step)


    # ###################################
    # ######### CREATE PATIENTS #########
    # ###################################
    # Create every combination of age/sex/mrs for the selected
    # age range and model type.

    # Decide which mRS scores to run:
    if model_input_str == 'mRS':
        mrs_to_run = range(6)
    else:
        # In the dichotomous model we give one set of parameters to
        # mRS < 3 and a second set to mRS >=3. So just run two mRS
        # values to save repeats.
        mrs_to_run = [0, 5]

    # Store patients in here:
    patient_df = pd.DataFrame(columns=[
        'age', 'sex', 'sex_label', 'mrs', 'outcome_type'])
    count = 0
    for age in age_range:
        for sex in [0, 1]:
            sex_label = 'Male' if sex == 1 else 'Female'
            for mrs in mrs_to_run:
                # Use the mRS score to label this patient as independent or
                # dependent in the dichotomous model.
                outcome_type = 'Dependent' if mrs > 2 else 'Independent'

                patient_df.loc[count] = [
                    age, sex, sex_label, mrs, outcome_type]
                count += 1

    # #####################################
    # ######### MAIN CALCULATIONS #########
    # #####################################

    # Get the fixed parameters dictionary.
    # This is found via a function because the parameters used
    # depend on whether we're using the separate-mRS or the dichotomous
    # model.
    fixed_params = get_fixed_params(model_input_str)

    # Store results dictionaries in here:
    results_dict_list = []

    # Run each patient separately:
    for p in range(len(patient_df)):
        patient = patient_df.loc[p]

        # This is the same code as in "2_Interactive_demo.py".
        results_dict = calc.main_calculations(
            patient['age'],
            patient['sex'],
            patient['sex_label'],
            patient['mrs'],
            fixed_params,
            model_input_str
            )
        # Store this dictionary in the list of dicts:
        results_dict_list.append(results_dict)

    # Turn all results dictionaries into a single data frame:
    df = pd.DataFrame(results_dict_list)

    # ###################################
    # ######### DISPLAY RESULTS #########
    # ###################################

    st.markdown('## Results')
    # Display on Streamlit:
    st.dataframe(df)
    st.download_button(
        'Download these results as .csv',
        df.to_csv(),
        file_name='lifetime_outcomes_results.csv'
    )

    st.markdown(
        '''
        ## Fixed parameters

        The following parameters are the same for all patients.

        The separate-mRS model uses only the "mRS" column
        and the dichotomous model uses only the "Dichotomous" column.

        To see how these are used in the code, please follow the
        advice in the "README" file on GitHub:
        [![][github-img]][github-data] __Source code:__
        [https://github.com/stroke-optimist/streamlit_lifetime_stroke](
            https://github.com/stroke-optimist/streamlit_lifetime_stroke
        )

        [github-img]: https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white
        [github-data]:  https://github.com/stroke-optimist/streamlit_lifetime_stroke
        '''
        )
    # Get fixed parameters from file and store in a dataframe:
    df_fixed_params = pd.DataFrame(index=fixed_params.keys())
    df_fixed_params['mRS'] = get_fixed_params('mRS').values()
    df_fixed_params['Dichotomous'] = get_fixed_params('Dichotomous').values()

    # Display on Streamlit:
    st.dataframe(df_fixed_params)
    st.download_button(
        'Download these fixed parameters as .csv',
        df_fixed_params.to_csv(),
        file_name='lifetime_outcomes_fixed_params.csv'
    )

    # ################################
    # ######### SCATTER PLOT #########
    # ################################
    st.markdown(
        '''
        ## Scatter plot of results

        The following plot shows the variation of a selected feature
        with a patient's age, sex, and mRS score.
        A subset of features from the full results are available
        to view.
        '''
        )
    # Pick out some features to plot on the y-axis:
    y_feature_options = [
        'death_in_year_1_prob',
        'survival_median_years',
        'life_expectancy',
        'year_when_zero_survival',
        'qalys_total',
        'ae_count',
        'ae_discounted_cost',
        'nel_count',
        'nel_discounted_cost',
        'el_count',
        'el_discounted_cost',
        'care_years',
        'care_years_discounted_cost',
        'total_discounted_cost',
        'net_benefit',
    ]
    # Let the user select which one to show:
    y_feature_display_name = st.selectbox(
        'Feature to plot',
        options=y_feature_options
    )
    # Draw the plot:
    if model_input_str == 'mRS':
        scatter_results(df, y_feature_display_name, 'mrs')
    else:
        scatter_results(df, y_feature_display_name, 'outcome_type')

    # ----- The end! -----


def scatter_results(df, y_feature_display_name, col):
    """
    Make a plotly scatter plot for age, sex, mrs, and a feature.

    Inputs:
    -------
    df                     - pd.DataFrame. Results of the lifetime
                             outcomes model.
    y_feature_display_name - str. Column in the dataframe to plot
                             on the y-axis.
    col                    - str. Column for either mRS scores
                             (separate mRS model) or outcome type
                             (dichotomous model).
    """

    fig = go.Figure()
    fig.update_layout(
        width=800,
        height=600,
        margin_l=0, margin_r=0, margin_b=0, margin_t=50
        )

    # Get colours from the plotly colour scale:
    colours = sample_colorscale(
        'viridis',
        np.linspace(0, 1, len(sorted(set(df[col]))))
        )
    # Iterate over outcome and sex:
    for a, val in enumerate(sorted(set(df[col]))):
        colour = colours[a]
        for s, sex_label in enumerate(sorted(set(df['sex_label']))):
            m = 'circle' if sex_label == 'Female' else 'square'
            # Reduce the dataframe to just these rows:
            df_here = df[
                (df[col] == val) &
                (df['sex_label'] == sex_label)
            ]
            # Name for this trace in the legend:
            name_str = (f'{col} {val}: {sex_label}' if col == 'mrs' else
                        f'{val}: {sex_label}')
            # Add these patients to the plot:
            fig.add_trace(go.Scatter(
                x=df_here['age'],
                y=df_here[y_feature_display_name],
                mode='lines+markers',
                marker_color=colour,
                marker_symbol=m,
                marker_line_color='black',
                marker_line_width=1.0,
                line_color=colour,
                name=name_str
            ))

    # Figure format:
    fig.update_layout(
        xaxis_title='Age (years)',
        yaxis_title=y_feature_display_name
    )
    st.plotly_chart(fig)


if __name__ == '__main__':
    main()
