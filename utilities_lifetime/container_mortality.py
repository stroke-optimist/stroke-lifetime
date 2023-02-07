"""
This contains everything in the Mortality section.
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utilities_lifetime.fixed_params import colours_excel
# from utilities_lifetime.inputs import write_text_from_file
# Import this function for use with user input probability:
from utilities_lifetime.models import find_survival_time_for_pDeath
# For writing formulae in the "Details" sections:
import utilities_lifetime.latex_equations


def main(
        time_list_yr, all_survival_lists,
        mRS_input, all_hazard_lists,
        pDeath_list, invalid_inds_for_pDeath, survival_times,
        time_of_death, variables_dict
        ):
    # Details on probability with time
    # Year one:
    with st.expander('Details: Mortality during year one'):
        write_details_mortality_in_year_one(variables_dict)
    with st.expander('Example: Mortality during year one'):
        write_example_mortality_in_year_one(variables_dict)

    # After year one:
    with st.expander('Details: Mortality after year one'):
        write_details_mortality_after_year_one(variables_dict)
    with st.expander('Example: Mortality after year one'):
        write_example_mortality_after_year_one(variables_dict)
    # Plot:
    plot_survival_vs_time_plotly(
        time_list_yr, all_survival_lists[mRS_input], time_of_death)
    # Write a sentence to state the 0% survival time.
    year_of_zero_survival = time_of_death // 1
    months_of_zero_survival = (time_of_death % 1)*12.0
    st.write(f'Survival falls to 0% at {year_of_zero_survival:.0f} years ',
             f'{months_of_zero_survival:.0f} months.')
    # Plot:
    plot_hazard_vs_time_plotly(time_list_yr, all_hazard_lists)

    st.markdown('### Probability of death')
    # Details on probability of death table values
    with st.expander('Details: Mortality in a chosen year'):
        write_details_mortality_in_chosen_year(variables_dict)
    # Table:
    write_table_of_pDeath(pDeath_list, invalid_inds_for_pDeath, n_columns=3)

    st.markdown('### Survival')
    # Details on median survival table values
    with st.expander('Details: Median survival'):
        write_details_median_survival(variables_dict)
    # Table:
    # Check which model we're using and draw a bespoke table:
    if st.session_state['lifetime_model_type'] == 'mRS':
        write_table_of_median_survival(survival_times)
    else:
        write_table_of_median_survival_dicho(survival_times)


def plot_survival_vs_time_plotly(
        time_list_yr, survival_list, time_of_zero_survival
        ):
    """
    Draw a line graph of survival (y) with time (x).

    Inputs:
    time_list_yr          - list or array. List of years for x-axis.
    survival_list         - list or array. List of survival rates in
                            each year. Values lie between 0 and 1.
    time_of_zero_survival - float. Year when survival=0.0.
    """
    # Don't plot values with negative survival rates.
    # Find v, the index where we want to cut off the plotted values:
    try:
        v = np.where(survival_list <= 0.0)[0][0]
    except IndexError:
        v = len(survival_list)

    # Merge the time of death into these lists:
    time_list_yr_to_plot = np.append(time_list_yr[:v], time_of_zero_survival)
    survival_list_to_plot = np.append(survival_list[:v], 0.0)

    # Combine both lists into a table.
    # Also include a column of survival x 100 to have the values in
    # percentages, as this data will appear on the hover bubble.
    table = np.transpose(np.vstack((
        time_list_yr_to_plot,
        survival_list_to_plot*100,
        survival_list_to_plot
    )))
    # Convert to dataframe for easier use of plotly:
    df = pd.DataFrame(table, columns=('year', 'survival', 'survival_frac'))

    # Plot content:
    fig = px.line(
        df,
        x='year', y='survival',
        custom_data=['survival_frac'],
        labels=dict(year='Years since discharge', survival='Survival (%)'),
        )
    # Pass survival_frac to custom_data so it is not directly plotted
    # but can be used in the hover bubble information.

    # Figure title:
    fig.update_layout(title_text='Survival', title_x=0.5)
    # Change axis:
    fig.update_yaxes(range=[0, 100])
    fig.update_xaxes(range=[0, time_list_yr[-1]],
                     constrain='domain')  # For aspect ratio.
    # Update ticks:
    fig.update_xaxes(tick0=0, dtick=5)
    fig.update_yaxes(tick0=0, dtick=25)
    # Hover settings:
    # Make it so cursor can hover over any x value to show the
    # label of the survival line for (x,y), rather than needing to
    # hover directly over the line:
    fig.update_layout(hovermode='x')
    # Remove default bulky hover messages:
    fig.update_traces(hovertemplate=None)
    # Show the survival number with two decimal places:
    fig.update_traces(
        hovertemplate=(
            '%{customdata[0]:>.2%}' +
            # Remove the contents of the secondary box:
            '<extra></extra>'
            )
        )

    # Remove the excess margins at the top and bottom by changing
    # figure height:
    fig.update_layout(height=250)
    # Changing width in the same way doesn't work when we write to
    # streamlit later with use_container_width=True.
    # Set aspect ratio:
    fig.update_yaxes(
        scaleanchor='x',
        scaleratio=0.1,
        constrain='domain'
    )

    # Disable zoom and pan:
    fig.update_layout(xaxis=dict(fixedrange=True),
                      yaxis=dict(fixedrange=True))

    # Turn off legend click events
    # (default is click on legend item, remove that item from the plot)
    fig.update_layout(legend_itemclick=False)

    # Options for the mode bar.
    # (which doesn't appear on touch devices.)
    plotly_config = {
        # Mode bar always visible:
        # 'displayModeBar': True,
        # Plotly logo in the mode bar:
        'displaylogo': False,
        # Remove the following from the mode bar:
        'modeBarButtonsToRemove': [
            'zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale',
            'lasso2d'
            ],
        # Options when the image is saved:
        'toImageButtonOptions': {'height': None, 'width': None},
        }

    # Write to streamlit:
    st.plotly_chart(fig, use_container_width=True, config=plotly_config)


def plot_hazard_vs_time_plotly(time_list_yr, all_hazard_lists):
    """
    Plot filled area of cumulative hazard (y) vs time (x).

    Inputs:
    time_list_yr     - list or array. List of years for x-axis.
    all_hazard_lists - list of arrays, one for each mRS. Each list has
                       floats of cumulative hazard for each year in
                       time_list_yr.
    """
    # Convert cumulative hazard lists into non-cumulative
    # for easier plotting with plotly.
    sub_hazard_lists = [all_hazard_lists[0]]
    # Check which model type we're using.
    model_type_used = st.session_state['lifetime_model_type']
    if model_type_used == 'mRS':
        for mRS in np.arange(1, 6):
            # For each mRS, subtract the values that came before it.
            diff_list = np.array(all_hazard_lists[mRS]-all_hazard_lists[mRS-1])
            sub_hazard_lists.append(diff_list)
    else:
        # For second outcome, subtract the values that came before it.
        diff_list = np.array(all_hazard_lists[-1]-all_hazard_lists[0])
        sub_hazard_lists.append(diff_list)
        # Reduce the length of all_hazard_lists. Only keep the first
        # and final rows of data.
        all_hazard_lists = np.array(all_hazard_lists)[[0, -1], :]

    if model_type_used == 'mRS':
        names = [f'{i}' for i in range(len(all_hazard_lists))]
        labels = [f'mRS≤{i}' for i in range(len(all_hazard_lists))]
        legend_title = 'mRS'
        colours = colours_excel
    else:
        names = ['Independent', 'Dependent']
        labels = ['Independent', 'Dependent']
        legend_title = 'Outcome'
        colours = [colours_excel[0], colours_excel[3]]

    # # Plot the data:
    fig = go.Figure()
    for i in range(len(all_hazard_lists)):
        # Extra bits for setting the hover label data:
        customdata = np.stack((
            100.0*all_hazard_lists[i],     # Cumulative probs mRS<=i
            [labels[i]]*len(all_hazard_lists[i]),  # mRS values
            ), axis=-1)
        # Line and fill:
        fig.add_trace(go.Scatter(
            x=time_list_yr,
            y=100.0*sub_hazard_lists[i],   # probabilities mRS=i
            mode='lines',
            line=dict(color=colours[i]),
            stackgroup='one',              # Makes the bands stack
            name=names[i],                   # Label for legend
            customdata=customdata,
        ))
        # The custom_data aren't directly plotted in the previous line,
        # but are loaded ready for use with the hover template later.

    # Set axis labels:
    fig.update_xaxes(title_text='Years since discharge')
    fig.update_yaxes(title_text='Cumulative hazard (%)')
    fig.update_layout(legend_title=legend_title)

    # Hover settings:
    # When hovering, highlight all mRS bins' points for chosen x:
    fig.update_layout(hovermode='x unified')
    # The line with <extra></extra> is required
    # to remove the default hover label before the rest of this.
    # Otherwise get "0 mRS=0 ...".
    fig.update_traces(
        hovertemplate=(
            '%{customdata[1]}: %{customdata[0]:6.2f}%' +
            # Remove secondary box on the hover label:
            '<extra></extra>'
            )
        )

    # Figure title:
    fig.update_layout(title_text='Hazard function for Death by mRS',
                      title_x=0.5)
    # Move legend to above plot:
    fig.update_layout(legend=dict(
        orientation='h',
        yanchor='top',
        y=1.2,
        xanchor='right',
        x=1.0
        ))
    # Change axis:
    fig.update_yaxes(range=[0, 100])

    # Give breathing room in the x-axis limits to help with viewing
    # the app on a touch screen - once the hover message appears,
    # it can only be removed by hovering (touching) a part of the plot
    # that does not generate a hover message. So add extra space for
    # clicking in this case.
    fig.update_xaxes(range=[-6, time_list_yr[-1]],
                     constrain='domain')  # For aspect ratio.
    # Update ticks:
    fig.update_xaxes(
        tickmode='array',
        tickvals=np.arange(0, time_list_yr[-1]+1e-5, 5),
        ticktext=np.arange(0, time_list_yr[-1]+1e-5, 5)
        # tick0=0, dtick=5
        )
    fig.update_yaxes(tick0=0, dtick=10)

    # Set aspect ratio:
    fig.update_yaxes(
        scaleanchor='x',
        scaleratio=0.25,
        constrain='domain'
    )

    # Disable zoom and pan:
    fig.update_layout(xaxis=dict(fixedrange=True),
                      yaxis=dict(fixedrange=True))

    # Turn off legend click events
    # (default is click on legend item, remove that item from the plot)
    fig.update_layout(legend_itemclick=False)

    # Options for the mode bar.
    # (which doesn't appear on touch devices.)
    plotly_config = {
        # Mode bar always visible:
        # 'displayModeBar': True,
        # Plotly logo in the mode bar:
        'displaylogo': False,
        # Remove the following from the mode bar:
        'modeBarButtonsToRemove': [
            'zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale',
            'lasso2d'
            ],
        # Options when the image is saved:
        'toImageButtonOptions': {'height': None, 'width': None},
        }

    # Write to streamlit:
    st.plotly_chart(fig, use_container_width=True, config=plotly_config)


def write_table_of_pDeath(pDeath_list, invalid_inds_for_pDeath, n_columns=1):
    """
    Table: probability of death.
    In Excel, this is "Yr" vs "pDeath" table.

    Is there a better way to do this? Probably.

    Inputs:
    pDeath_list             - array. Stores floats of probs of death
                              for all years (default up to 50 years).
    invalid_inds_for_pDeath - array. Stores the indices where survival
                              is below 0% and so pDeath is invalid.
    n_columns               - int. How many columns to use in the table.
    """
    # Display these years:
    years_for_prob_table = np.arange(1, 15, 1)
    # Multiply pDeath by 100 for percentage.
    pDeath_list_for_table = 100.0*pDeath_list
    # Streamlit always writes an index column. To fudge a year
    # column, add a '-' to the pDeath list for the year 0 value.
    # The unicode characters add some spaces in front of '-' to fake
    # the right-alignment.
    invalid_str = 3*'\U00002002' + '\U00002006' + '-'
    pDeath_list_for_table = np.concatenate(
        ([invalid_str], pDeath_list_for_table),
        dtype=object)
    # ^ dtype=object keeps the floats instead of converting all to str.
    # Set invalid data to '-' with a few spaces in front:
    pDeath_list_for_table[invalid_inds_for_pDeath[0]:] = invalid_str
    # Cut off the list at the required number of years:
    pDeath_list_for_table = \
        pDeath_list_for_table[:len(years_for_prob_table)+1]

    # Switch to string formatting to ensure 2 decimal places are shown.
    max_ind = np.min([invalid_inds_for_pDeath[0], len(pDeath_list_for_table)])
    for i in range(1, max_ind):
        str_here = f'{pDeath_list_for_table[i]:.2f}'
        # Whack a space on the front for aligning percentages under 10%:
        str_here = '\U00002002'*(5-len(str_here)) + str_here
        pDeath_list_for_table[i] = str_here

    # Describe the table, otherwise there's no way of explaining what
    # the first row means.
    st.write('The probability of death in each year: ')
    if n_columns > 0:
        # Split the data across the specified number of columns.
        cols = st.columns(n_columns)

        n_rows = len(pDeath_list_for_table) // n_columns
        first_row = 0
        last_row = n_rows
        for c, col in enumerate(cols):
            # Convert to a pandas series so we can give it a title:
            df_pDeath = pd.Series(
                pDeath_list_for_table[first_row:last_row],
                name=('Probability of death (%)')
            )
            # Update the index column on the left
            # so that it doesn't have to start from 0:
            df_pDeath.index = df_pDeath.index + n_rows*c
            # I've named the index but it doesn't display in Streamlit.
            df_pDeath.index.name = 'Year'

            with col:
                # Write to streamlit:
                st.table(df_pDeath)
            # Update values for the next go round the loop:
            first_row += n_rows
            last_row += n_rows
            if last_row >= len(pDeath_list_for_table):
                last_row = -1
    else:
        # One column.
        # Convert to a pandas series so we can give it a title:
        df_pDeath = pd.Series(
            pDeath_list_for_table,
            name=('Probability of death (%)')
        )
        # Write to streamlit:
        st.table(df_pDeath)


def write_table_of_median_survival(survival_times):
    """
    Table of median, IQR survival times and life expectancy (columns)
    for each mRS score (rows).

    Inputs:
    survival_times - np.array. Contains six lists, one for each mRS.
                     Each list contains [median, lower IQR, upper IQR,
                     life expectancy].
    """
    # Convert to a pandas dataframe so we can label the columns:
    df_table = pd.DataFrame(
        survival_times,
        columns=(
            'Median survival (years)',
            'Lower IQR (years)',
            'Upper IQR (years)',
            'Life expectancy (age)'
            )
    )
    # Write to streamlit with 2 decimal places:
    st.write('The survival estimates for each mRS (0 to 5): ')
    st.table(df_table.style.format("{:.2f}"))


def write_table_of_median_survival_dicho(survival_times):
    """
    Table of median, IQR survival times and life expectancy (columns)
    for each mRS score (rows).

    Inputs:
    survival_times - np.array. Contains six lists, one for each mRS.
                     Each list contains [median, lower IQR, upper IQR,
                     life expectancy].
    """
    # Only keep the first and last rows:
    survival_times = np.array(survival_times[[0, -1], :], dtype=object)
    # Add a column at the start with the outcome type labels:
    survival_times = np.hstack((
        np.array(['Independent', 'Dependent'], dtype=object).reshape(2, 1),
        survival_times
        ))

    columns = [
            ' ',  # Outcome name row
            'Median survival (years)',
            'Lower IQR (years)',
            'Upper IQR (years)',
            'Life expectancy (age)'
    ]

    # Convert to a pandas dataframe so we can label the columns:
    df_table = pd.DataFrame(
        survival_times,
        columns=columns
    )

    # Set up format dictionary for printing precision:
    format_dict = {
        columns[1]: '{:.2f}',
        columns[2]: '{:.2f}',
        columns[3]: '{:.2f}',
        columns[4]: '{:.2f}',
    }
    # Write to streamlit with 2 decimal places:
    st.write('The survival estimates for each outcome: ')
    st.table(df_table.style.format(format_dict))


def write_details_mortality_in_year_one(vd):
    """
    Write the method for calculating mortality in year one.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the probability ',
        'of death during year one.'
        ]))
    table_cols = st.columns(2)
    with table_cols[0]:
        markdown_lg_coeffs = utilities_lifetime.latex_equations.\
            table_lg_coeffs(vd)
        st.markdown(markdown_lg_coeffs)

    with table_cols[1]:
        # Check the model type to decide which table to draw.
        if st.session_state['lifetime_model_type'] == 'mRS':
            # Individual mRS table:
            markdown_lg_mrs_coeffs = utilities_lifetime.latex_equations.\
                table_lg_mrs_coeffs(vd)
        else:
            # Dichotomous table:
            markdown_lg_mrs_coeffs = utilities_lifetime.latex_equations.\
                table_lg_mrs_coeffs_dicho(vd)
        st.markdown(markdown_lg_mrs_coeffs)

    # ----- Equation for probability -----
    st.markdown(''.join([
        'The probability of death during year one, ',
        '$P_{1}$, is calculated as:'
        ]))
    latex_pDeath_yr1_generic = utilities_lifetime.latex_equations.\
        pDeath_yr1_generic()
    st.latex(latex_pDeath_yr1_generic)

    # ----- Equation for linear predictor -----
    st.markdown('with linear predictor $LP_{1}$ where:')
    latex_lp_yr1_generic = utilities_lifetime.latex_equations.lp_yr1_generic()
    st.latex(latex_lp_yr1_generic)
    st.markdown(''.join([
        r'''where $\alpha$ and $\beta$ are constants and ''',
        '$X$ are values of the patient details (i.e. age, sex, and mRS).'
        ]))

    # ----- Equation for survival -----
    st.markdown(''.join([
        'The opposite of this value is survival in year one, $S_1$:'
        ]))
    latex_survival_yr1_generic = utilities_lifetime.latex_equations.\
        survival_yr1_generic()
    st.latex(latex_survival_yr1_generic)
    st.markdown(''.join([
        'This is the quantity plotted in the survival vs. time chart.'
    ]))


def write_example_mortality_in_year_one(vd):
    """
    Write the example for calculating mortality in year one.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    # st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the tables above depending ',
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    latex_lp_yr1 = utilities_lifetime.latex_equations.lp_yr1(vd)
    st.latex(latex_lp_yr1)
    st.write('$^{*}$ This value is 0 for female patients and 1 for male.')

    # ----- Calculation for probability -----
    st.markdown('Probability:')
    latex_prob_yr1 = utilities_lifetime.latex_equations.prob_yr1(vd)
    st.latex(latex_prob_yr1)

    # ----- Calculation for survival -----
    st.markdown('Survival:')
    latex_survival_yr1 = utilities_lifetime.latex_equations.survival_yr1(vd)
    st.latex(latex_survival_yr1)


def write_details_mortality_after_year_one(vd):
    """
    Write the method for calculating mortality after year one.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the probability ',
        'of death after year one.'
        ]))
    table_cols = st.columns(2)
    with table_cols[0]:
        markdown_table_gz_coeffs = utilities_lifetime.latex_equations\
            .table_gz_coeffs(vd)
        st.markdown(markdown_table_gz_coeffs)

    with table_cols[1]:
        # Check the model type to decide which table to draw.
        if st.session_state['lifetime_model_type'] == 'mRS':
            markdown_table_gz_mRS_coeffs = utilities_lifetime.latex_equations\
                .table_gz_mRS_coeffs(vd)
        else:
            markdown_table_gz_mRS_coeffs = utilities_lifetime.latex_equations\
                .table_gz_mRS_coeffs_dicho(vd)
        st.markdown(markdown_table_gz_mRS_coeffs)

    # ----- Equation for hazard -----
    st.markdown(''.join([
        'The cumulative hazard at time $t$ ',
        '(where $t$ is the time in days ',
        'after year one), ',
        '$H_t$, is calculated as:'
        ]))
    latex_hazard_yrn_generic = utilities_lifetime.latex_equations\
        .hazard_yrn_generic()
    st.latex(latex_hazard_yrn_generic)

    # ----- Equation for linear predictor -----
    st.markdown('with linear predictor $LP_{\mathrm{H}}$ where:')
    latex_lp_yrn_generic = utilities_lifetime.latex_equations.lp_yrn_generic()
    st.latex(latex_lp_yrn_generic)

    st.markdown(''.join([
        r'''where $\alpha$ and $\beta$ are constants and ''',
        '$X$ are values of the patient details (e.g. age, sex, and mRS).'
        ]))

    # ----- Equation for probability of death -----
    st.markdown(''.join([
        'This hazard $H_t$ can be combined with the probability of '
        'death in year one, $P_{1}$ (Equation [1]), to give the '
        'cumulative probability of death by time $t$, $F_t$:'
        ]))
    latex_FDeath_yrn_generic = utilities_lifetime.latex_equations.\
        FDeath_yrn_generic()
    st.latex(latex_FDeath_yrn_generic)
    st.markdown(''.join([
        'This quantity $F_t$ is plotted in the cumulative hazard ',
        'vs. time plot. '
    ]))

    # ----- Equation for survival -----
    st.markdown(''.join([
        'The opposite of this value is survival, $S_t$:'
        ]))
    latex_survival_generic = utilities_lifetime.latex_equations.\
        survival_generic()
    st.latex(latex_survival_generic)
    st.markdown(''.join([
        'This is the quantity plotted in the survival vs. time chart.'
    ]))


def write_example_mortality_after_year_one(vd):
    """
    Write the example for calculating mortality after year one.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    # st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the tables above depending ',
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    latex_lp_yrn = utilities_lifetime.latex_equations.lp_yrn(vd)
    st.latex(latex_lp_yrn)
    st.markdown('$^{*}$ This value is 0 for female patients and 1 for male.')

    # ----- Input number of years -----
    time_input_yr = st.slider(
        'Choose a number of years for this example',
        min_value=2,
        max_value=25,
        value=2
        )
    st.markdown(''.join([
        'The following values in pink change with ',
        'the chosen time.'
        ]))

    # ----- Calculation for hazard -----
    st.markdown('Cumulative hazard $H_t$ at the chosen time $t$:')
    latex_hazard_yrn = utilities_lifetime.latex_equations.hazard_yrn(
        vd, time_input_yr)
    st.latex(latex_hazard_yrn)

    # ----- Calculation for probability -----
    st.markdown(''.join([
        'Cumulative probability of death by time $t$ ',
        '(using the previously-calculated $P_{1}$):',
    ]))


def write_details_mortality_in_chosen_year(vd):
    """
    Write the method and example for calculating mortality during any
    year after year one.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    st.markdown(''.join([
        'The probability of death during a chosen year $t$ after '
        'year one, $P_t$, ',
        'can be found by combining the cumulative probabilities ',
        'of death in that year and in the previous year. '
        ]))

    # ----- Equation for probability of death in year two -----
    st.markdown('In year 2,')
    latex_pDeath_yr2_generic = utilities_lifetime.latex_equations.\
        pDeath_yr2_generic()
    st.latex(latex_pDeath_yr2_generic)

    # ----- Equation for probability of death after year two -----
    st.markdown('In years where $t>2$,')
    latex_pDeath_yrn_generic = utilities_lifetime.latex_equations.\
        pDeath_yrn_generic()
    st.latex(latex_pDeath_yrn_generic)
    st.markdown(''.join([
        'where $F_t$ is from Equation [6] ',
        'and $P_1$ is from Equation [1].'
    ]))

    st.markdown(''.join([
        'In either case, the probability is only valid when survival is ',
        'greater than 0%.'
        ]))

    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, ',
        'and values in pink change with the chosen time.'
        ]))

    # ----- Input number of years -----
    # Put slider between two empty columns to make it skinnier.
    # cols = st.columns(3)
    # with cols[1]:
    time_input_yr = st.slider(
        'Choose t in years for this example',
        min_value=2,
        max_value=25,
        value=2
        )
    # ----- Gather some data -----
    # Probability of death in this year:
    P1 = vd["pDeath_list"][time_input_yr-1]
    # Survival in previous year:
    S0 = vd["survival_list"][time_input_yr-1]
    # Survival in this year:
    # S1 = vd["survival_list"][time_input_yr]
    # (cumulative) probabilities in the other two years:
    # Earlier year:
    if time_input_yr == 2:
        F0 = vd["P_yr1"]
    else:
        F0 = vd["hazard_list"][time_input_yr-1]
    # Later year:
    F1 = vd["hazard_list"][time_input_yr]

    # ----- Show survival -----
    st.markdown('Survival in the previous year (from Equation [3] or [7]): ')
    latex_survival_display = utilities_lifetime.latex_equations.\
        survival_display(time_input_yr-1, S0)
    st.latex(latex_survival_display)

    # ----- Calculate probability -----
    st.markdown('Probability:')
    latex_pDeath_yrn = utilities_lifetime.latex_equations.\
        pDeath_yrn(P1, F0, F1, time_input_yr, S0)
    st.latex(latex_pDeath_yrn)
    if S0 <= 0.0:
        st.markdown(''.join([
            'The probability is zero because the survival rate ',
            'in the previous year is not above zero.'
            ]))


def write_details_median_survival(vd):
    """
    Write the method and example for calculating the survival time
    for a given probability, e.g. median is P=0.5.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    st.markdown(''.join([
        'The method used to calculate a time of death depends ',
        'on whether the probability $P$ for which a time of death is ',
        'being calculated from is less than $P_1$, ',
        'the probability of death in year one (Equation [1]).'
        ]))
    st.markdown(''.join([
        'For the key times noted in the "Survival" table above, ',
        'the following probabilities are used in the calculation.'
    ]))
    st.markdown('+ Median: $P=0.5$')
    st.markdown('+ IQR lower: $P=0.25$')
    st.markdown('+ IQR upper: $P=0.75%$')
    st.markdown(''.join([
        'The life expectancy is the patient\'s age plus the median ',
        'survival time.'
        ]))

    # ----- Case 1 -----
    st.markdown('### Case 1')
    st.markdown(''.join([
        'If $P > P_1$, the time of death is based on the probability ',
        'of death after year one. The time equation '
        'has to be modified to allow for the probability of death. ',
        'Instead of $P$, we consider $P^{\prime}$ where:'
        ]))
    # ----- Prob prime -----
    latex_prob_prime_generic = utilities_lifetime.latex_equations.\
        prob_prime_generic()
    st.latex(latex_prob_prime_generic)

    # ----- Time to death (case 1) -----
    st.markdown(''.join([
        'The time of death is derived from Equation [4] ',
        'and has the form:'
        ]))
    latex_death_time_case1_generic = utilities_lifetime.latex_equations.\
        death_time_case1_generic()
    st.latex(latex_death_time_case1_generic)

    # ----- Case 2 -----
    st.markdown('### Case 2')
    st.markdown(''.join([
        'If $P \leq P_1$, the time of death is based on the probability ',
        'of death in year one (Equation 1). '
        ]))
    # ----- Time to death (case 2) -----
    latex_death_time_case2_generic = utilities_lifetime.latex_equations.\
        death_time_case2_generic()
    st.latex(latex_death_time_case2_generic)
    st.markdown(''.join([
        'This method is taken from _Decision Modelling for Health ',
        'Economic Evaluations_.'
    ]))

    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, ',
        'and values in pink change with the chosen probability of death.'
        ]))
    # ----- Show constants -----
    # Probability in year one:
    latex_Pyr1_display = utilities_lifetime.latex_equations.\
        Pyr1_display(vd['P_yr1'])
    # LP in year n:
    latex_LPyrn_display = utilities_lifetime.latex_equations.\
        LPyrn_display(vd['LP_yrn'])
    # gamma:
    latex_gammaH_display = utilities_lifetime.latex_equations.\
        gammaH_display(vd['gz_gamma'])

    st.markdown(''.join([
        'The following values from before are used ',
        '(from Equations [1] and [5]): '
        ]))
    st.latex(
        latex_Pyr1_display + ',\ ' +
        latex_LPyrn_display + ',\ ' +
        latex_gammaH_display
        )

    # To save repeating code, define a function here for printing
    # the equations and explanations for any combo of probability
    # and time of death:
    def print_survival_time_calcs(p, tDeath, vd):
        # ----- Select case -----
        if p < vd['P_yr1']:
            # Case 2
            st.markdown(''.join([
                '$P = '+f'{100.0*p:.0f}'+'$%, so '
                '$P \leq P_1$ and we use Case 2. ',
                'The time of death is:'
                ]))
            # ----- Calculate time -----
            latex_death_time_case2 = utilities_lifetime.latex_equations.\
                death_time_case2(tDeath, p, vd['P_yr1'])
            st.latex(latex_death_time_case2)

        else:
            # Case 1
            st.markdown(''.join([
                '$P = '+f'{100.0*p:.0f}'+'$%, so '
                '$P > P_1$ and we use Case 1. ',
                'First, calculate $P^{\prime}$:'
                ]))
            # ----- Calculate P` -----
            prob_prime = ((1.0 + p)/(1.0 + vd['P_yr1'])) - 1.0
            latex_prob_prime = utilities_lifetime.latex_equations.\
                prob_prime(p, prob_prime, vd['P_yr1'])
            st.latex(latex_prob_prime)
            # ----- Calculate time -----
            st.markdown('Then the time of death is: ')
            latex_death_time_case1 = utilities_lifetime.latex_equations.\
                death_time_case1(tDeath, prob_prime,
                                 vd['LP_yrn'], vd['gz_gamma'], p)
            st.latex(latex_death_time_case1)
    # --- end of function.

    # Use the function with the following values:
    # Median
    p_med = 0.5
    tDeath_med = vd['survival_meds_IQRs'][vd['mrs'], 0]
    # IQR lower
    p_iqr_low = 0.25
    tDeath_iqr_low = vd['survival_meds_IQRs'][vd['mrs'], 1]
    # IQR higher
    p_iqr_high = 0.75
    tDeath_iqr_high = vd['survival_meds_IQRs'][vd['mrs'], 2]

    tabs = st.tabs([
        'Median', 'IQR (lower)', 'IQR (higher)', 'Choose a probability'])
    with tabs[0]:
        st.markdown('__Median:__')
        print_survival_time_calcs(p_med, tDeath_med, vd)

        # Write an extra bit only for median.
        # Details about life expectancy:
        st.markdown(''.join([
            'The life expectancy is the current age plus this ',
            'median survival value:'
        ]))
        life_expectancy = vd['age'] + tDeath_med
        latex_life_expectancy = utilities_lifetime.latex_equations.\
            life_expectancy(life_expectancy, tDeath_med, vd['age'])
        st.latex(latex_life_expectancy)

    with tabs[1]:
        st.markdown('__IQR lower value:__')
        print_survival_time_calcs(p_iqr_low, tDeath_iqr_low, vd)
    with tabs[2]:
        st.markdown('__IQR upper value:__')
        print_survival_time_calcs(p_iqr_high, tDeath_iqr_high, vd)
    with tabs[3]:
        # Take the user input to find the survival time for any
        # probability they choose.
        st.markdown('__Chosen probability:__')
        prob_input_perc = st.number_input(
            'Probability (%):',
            min_value=0,
            max_value=100,
            value=50,
            step=1,
            help='Ranges from 0% to 100%.'
            )
        prob_input_frac = prob_input_perc / 100.0
        # Calculate the survival time:
        survival_time, survival_yrs, time_log, eqperc = \
            find_survival_time_for_pDeath(
                prob_input_frac, vd['P_yr1'], vd['LP_yrn'])
        print_survival_time_calcs(prob_input_frac, survival_time, vd)
