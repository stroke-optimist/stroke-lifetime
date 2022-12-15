"""
This contains everything in the Mortality section.
"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

from utilities.fixed_params import colours_excel
# from utilities.inputs import write_text_from_file
from utilities.models import find_FDeath_yrn, find_survival_time_for_pDeath
import utilities.latex_equations


def main(
        time_list_yr, all_survival_lists,
        mRS_input, all_hazard_lists,
        pDeath_list, invalid_inds_for_pDeath, survival_times,
        time_of_death, variables_dict
        ):
    # These older plots use matplotlib instead of plotly:
    # plot_survival_vs_time(time_list_yr, all_survival_lists[mRS_input])
    # plot_hazard_vs_time(time_list_yr, all_hazard_lists, colours_excel)

    # Details on probability with time
    with st.expander('Details: Mortality during year one'):
        write_details_mortality_in_year_one(variables_dict)
    with st.expander('Details: Mortality after year one'):
        write_details_mortality_after_year_one(variables_dict)
    # Plot:
    plot_survival_vs_time_plotly(
        time_list_yr, all_survival_lists[mRS_input], time_of_death)
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
    write_table_of_median_survival(survival_times)


def plot_survival_vs_time_plotly(
        time_list_yr, survival_list, time_of_zero_survival
        ):
    # Don't plot values with negative survival rates.
    try:
        v = np.where(survival_list <= 0.0)[0][0]
    except IndexError:
        v = len(survival_list)

    # Merge the time of death into these lists:
    time_list_yr_to_plot = np.append(time_list_yr[:v], time_of_zero_survival)
    survival_list_to_plot = np.append(survival_list[:v], 0.0)

    # # Put the lists in order:
    # sorted_inds = time_list_yr_to_plot.argsort()
    # time_list_yr_to_plot = time_list_yr_to_plot[sorted_inds]
    # survival_list_to_plot = survival_list_to_plot[sorted_inds]

    # Combine both lists into a table:
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
        # hover_data={'survival_frac': ':.2f'}
        )

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
    # fig.update_traces(yhoverformat='.2%')
    fig.update_traces(
        hovertemplate=(
            # 'mRS=%{customdata[1]}: %{y:>6.2f}' +
            # 5 * '\U00002002' +
            '%{customdata[0]:>.2%}' +
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

    # Write to streamlit:
    st.plotly_chart(fig, use_container_width=True)
    year_of_zero_survival = time_of_zero_survival // 1
    months_of_zero_survival = (time_of_zero_survival % 1)*12.0
    st.write(f'Survival falls to 0% at {year_of_zero_survival:.0f} years ',
             f'{months_of_zero_survival:.0f} months.')


def plot_hazard_vs_time_plotly(time_list_yr, all_hazard_lists):
    """Plot hazard vs time."""
    # Convert cumulative hazard lists into non-cumulative
    # for easier plotting with plotly.
    sub_hazard_lists = [all_hazard_lists[0]]
    for mRS in np.arange(1, 6):
        # For each mRS, subtract the values that came before it.
        diff_list = np.array(all_hazard_lists[mRS]-all_hazard_lists[mRS-1])
        # # Attempted fix for weird mRS 5 line for age > 83 or so.
        # # If any difference is negative, set it to zero:
        # diff_list[np.where(diff_list < 0)] = 0.0
        sub_hazard_lists.append(diff_list)

    # Build this data into a big dataframe for plotly.
    # It wants each row in the table to have [mRS, year, hazard].
    for i in range(6):
        # The symbol for less than / equal to: ≤
        mRS_list = [  # 'mRS='+f'{i}'
            f'{i}' for year in time_list_yr]
        hazard_list = 100.0*sub_hazard_lists[i]
        cum_hazard_list = 100.0*all_hazard_lists[i]

        # Use dtype=object to keep the mixed strings (mRS),
        # integers (years) and floats (hazards).
        data_here = np.transpose(np.array(
            [mRS_list, time_list_yr, hazard_list, cum_hazard_list],
            dtype=object))

        if i == 0:
            data_to_plot = data_here
        else:
            data_to_plot = np.vstack((data_to_plot, data_here))

    # Pop this data into a dataframe:
    df_to_plot = pd.DataFrame(
        data_to_plot,
        columns=['mRS', 'year', 'hazard', 'cumhazard']
        )

    # Plot the data:
    fig = px.area(
        df_to_plot,
        x='year', y='hazard', color='mRS',
        custom_data=['cumhazard', 'mRS'],
        color_discrete_sequence=colours_excel
        )
    # The custom_data aren't directly plotted in the previous, but are
    # loaded ready for use with the hover template later.

    # Set axis labels:
    fig.update_xaxes(title_text='Years since discharge')
    fig.update_yaxes(title_text='Cumulative hazard (%)')
    # fig.update_layout(legend_title='mRS', title_x=0.5)

    # Hover settings:
    # When hovering, highlight all mRS bins' points for chosen x:
    fig.update_layout(hovermode='x unified')
    # Remove default bulky hover messages:
    fig.update_traces(hovertemplate=None)
    # I don't know why, but the line with <extra></extra> is required
    # to remove the default hover label before the rest of this.
    # Otherwise get "0 mRS=0 ..."
    fig.update_traces(
        hovertemplate=(
            # 'mRS=%{customdata[1]}: %{y:>6.2f}' +
            # 5 * '\U00002002' +
            'mRS≤%{customdata[1]}: %{customdata[0]:>6.2f}' +
            '<extra></extra>'
            )
        )
    # # The followings adds 'Year X' to the hover label,
    # # but annoyingly also adds it to every xtick.
    # fig.update_xaxes(tickprefix='Year ')

    # Figure title:
    fig.update_layout(title_text='Hazard function for Death by mRS',
                      title_x=0.5)
    # Change axis:
    fig.update_yaxes(range=[0, 100])
    fig.update_xaxes(range=[0, time_list_yr[-1]],
                     constrain='domain')  # For aspect ratio.
    # Update ticks:
    fig.update_xaxes(tick0=0, dtick=5)
    fig.update_yaxes(tick0=0, dtick=10)

    # # Remove the excess margins at the top and bottom by changing
    # # figure height:
    # fig.update_layout(height=450)
    # # Changing width in the same way doesn't work when we write to
    # # streamlit later with use_container_width=True.
    # Set aspect ratio:
    fig.update_yaxes(
        scaleanchor='x',
        scaleratio=0.25,
        constrain='domain'
    )

    # Write to streamlit:
    st.plotly_chart(fig, use_container_width=True)


def write_table_of_pDeath(pDeath_list, invalid_inds_for_pDeath, n_columns=1):
    """
    Table: probability of death.
    In Excel, this is "Yr" vs "pDeath" table.

    Is there a better way to do this? Probably.
    """
    # Display these years:
    years_for_prob_table = np.arange(1, 15, 1)
    # Multiply pDeath by 100 for percentage.
    pDeath_list_for_table = 100.0*pDeath_list
    # Round the values for printing nicely:
    # pDeath_list_for_table = np.round(pDeath_list_for_table, 2)
    # Streamlit always writes an index column. To fudge this into a year
    # column, add a '-' to the pDeath list for the year 0 value.
    pDeath_list_for_table = np.concatenate(
        ([3*'\U00002002' + '\U00002006' + '-'], pDeath_list_for_table),
        dtype=object)
    # ^ dtype=object keeps the floats instead of converting all to str.
    # Set invalid data to '-' with a few spaces in front:
    pDeath_list_for_table[invalid_inds_for_pDeath[0]:] = \
        3*'\U00002002' + '\U00002006' + '-'
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
            df_pDeath.index = df_pDeath.index + n_rows*c
            df_pDeath.index.name = 'Year'

            with col:
                # Write to streamlit:
                st.table(df_pDeath)
            first_row += n_rows
            last_row += n_rows
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


def write_details_mortality_in_year_one(vd):
    """
    "vd" is short for variables_dict.
    """
    # write_text_from_file(
    #     'pages/text_for_pages/calculations_mortality_1.txt',
    #     head_lines_to_skip=2
    #     )
    # st.markdown('## Mortality during year one')
    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the probability ',
        'of death during year one.'
        ]))
    table_cols = st.columns(2)
    with table_cols[0]:
        markdown_lg_coeffs = utilities.latex_equations.table_lg_coeffs(vd)
        st.markdown(markdown_lg_coeffs)

    with table_cols[1]:
        markdown_lg_mrs_coeffs = utilities.latex_equations.\
            table_lg_mrs_coeffs(vd)
        st.markdown(markdown_lg_mrs_coeffs)

    # ----- Equation for probability -----
    st.markdown(''.join([
        'The probability of death during year one, ',
        '$P_{1}$, is calculated as:'
        ]))
    latex_pDeath_yr1_generic = utilities.latex_equations.pDeath_yr1_generic()
    st.latex(latex_pDeath_yr1_generic)

    # ----- Equation for linear predictor -----
    st.markdown('with linear predictor $LP_{1}$ where:')
    latex_lp_yr1_generic = utilities.latex_equations.lp_yr1_generic()
    st.latex(latex_lp_yr1_generic)
    st.markdown(''.join([
        r'''where $\alpha$ and $\beta$ are constants and ''',
        '$X$ are values of the patient details (i.e. age, sex, and mRS).'
        ]))

    # ----- Equation for survival -----
    st.markdown(''.join([
        'The opposite of this value is survival in year one, $S_1$:'
        ]))
    latex_survival_yr1_generic = utilities.latex_equations.\
        survival_yr1_generic()
    st.latex(latex_survival_yr1_generic)
    st.markdown(''.join([
        'This is the quantity plotted in the survival vs. time chart.'
    ]))

    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the tables above depending ',
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    latex_lp_yr1 = utilities.latex_equations.lp_yr1(vd)
    st.latex(latex_lp_yr1)
    st.write('$^{*}$ This value is 0 for female patients and 1 for male.')

    # ----- Calculation for probability -----
    st.markdown('Probability:')
    latex_prob_yr1 = utilities.latex_equations.prob_yr1(vd)
    st.latex(latex_prob_yr1)

    # ----- Calculation for survival -----
    S_1 = 1.0 - vd["P_yr1"]
    st.markdown(''.join([
        'Survival:'
    ]))
    latex_survival_yr1 = utilities.latex_equations.\
        survival_yr1(S_1, vd["P_yr1"])
    st.latex(latex_survival_yr1)


def write_details_mortality_after_year_one(vd):
    """
    "vd" is short for variables_dict.
    """
    # write_text_from_file(
    #     'pages/text_for_pages/calculations_mortality_1.txt',
    #     head_lines_to_skip=2
    #     )
    # st.markdown('## Mortality after year one')
    # ----- Tables of constants -----
    st.markdown(''.join([
        'The following constants are used to calculate the probability ',
        'of death after year one.'
        ]))
    table_cols = st.columns(2)
    with table_cols[0]:
        markdown_table_gz_coeffs = utilities.latex_equations\
            .table_gz_coeffs(vd)
        st.markdown(markdown_table_gz_coeffs)

    with table_cols[1]:
        markdown_table_gz_mRS_coeffs = utilities.latex_equations\
            .table_gz_mRS_coeffs(vd)
        st.markdown(markdown_table_gz_mRS_coeffs)

    # ----- Equation for hazard -----
    st.markdown(''.join([
        'The cumulative hazard at time $t$ ',
        '(where $t$ is the time in days ',
        'after year one), ',
        '$H_t$, is calculated as:'
        ]))
    latex_hazard_yrn_generic = utilities.latex_equations\
        .hazard_yrn_generic()
    st.latex(latex_hazard_yrn_generic)

    # ----- Equation for linear predictor -----
    st.markdown('with linear predictor $LP_{\mathrm{H}}$ where:')
    latex_lp_yrn_generic = utilities.latex_equations.lp_yrn_generic()
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
    latex_FDeath_yrn_generic = utilities.latex_equations.FDeath_yrn_generic()
    st.latex(latex_FDeath_yrn_generic)
    st.markdown(''.join([
        'This quantity $F_t$ is plotted in the cumulative hazard ',
        'vs. time plot. '
    ]))

    # ----- Equation for survival -----
    st.markdown(''.join([
        'The opposite of this value is survival, $S_t$:'
        ]))
    latex_survival_generic = utilities.latex_equations.survival_generic()
    st.latex(latex_survival_generic)
    st.markdown(''.join([
        'This is the quantity plotted in the survival vs. time chart.'
    ]))

    # ##### EXAMPLE #####
    # ----- Calculations with user input -----
    st.markdown('### Example')
    st.markdown(''.join([
        'For the current patient details, these are calculated as follows.',
        ' Values in red change with the patient details, and values in ',
        'pink use a different constant from the tables above depending ',
        'on the patient details.'
        ]))

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    latex_lp_yrn = utilities.latex_equations.lp_yrn(vd)
    st.latex(latex_lp_yrn)
    st.markdown('$^{*}$ This value is 0 for female patients and 1 for male.')

    # ----- Input number of years -----
    # Put slider between two empty columns to make it skinnier.
    # cols = st.columns(3)
    # with cols[1]:
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

    # Calculate the hazard and probability of death:
    # (hazard is currently not stored in main_calculations
    # so have to find it specially here.)
    H_t, P_t = find_FDeath_yrn(
        vd["age"], vd["sex"], vd["mrs"], time_input_yr, p1=vd["P_yr1"])
    # Survival:
    S_t = 1.0 - P_t

    # ----- Calculation for hazard -----
    st.markdown('Cumulative hazard $H_t$ at the chosen time $t$:')
    latex_hazard_yrn = utilities.latex_equations.hazard_yrn(
        vd, time_input_yr, H_t)
    st.latex(latex_hazard_yrn)

    # ----- Calculation for probability -----
    st.markdown(''.join([
        'Cumulative probability of death by time $t$ ',
        '(using the previously-calculated $P_{1}$):',
    ]))
    latex_FDeath_yrn = utilities.latex_equations.FDeath_yrn(
        H_t, vd["P_yr1"], P_t, time_input_yr)
    st.latex(latex_FDeath_yrn)

    # ----- Calculation for survival -----
    st.markdown(''.join([
        'Survival at time $t$:'
    ]))
    latex_survival = utilities.latex_equations.\
        survival(S_t, P_t, time_input_yr)
    st.latex(latex_survival)


def write_details_mortality_in_chosen_year(vd):
    # st.markdown('## Mortality in a chosen year')
    st.markdown(''.join([
        'The probability of death during a chosen year $t$ after '
        'year one, $P_t$, ',
        'can be found by combining the cumulative probabilities ',
        'of death in that year and in the previous year. '
        ]))

    # ----- Equation for probability of death in year two -----
    st.markdown('In year 2,')
    latex_pDeath_yr2_generic = utilities.latex_equations.pDeath_yr2_generic()
    st.latex(latex_pDeath_yr2_generic)

    # ----- Equation for probability of death after year two -----
    st.markdown('In years where $t>2$,')
    latex_pDeath_yrn_generic = utilities.latex_equations.pDeath_yrn_generic()
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
        H0, F0 = find_FDeath_yrn(
            vd["age"], vd["sex"], vd["mrs"], time_input_yr-1, p1=vd["P_yr1"])
    # Later year:
    H1, F1 = find_FDeath_yrn(
        vd["age"], vd["sex"], vd["mrs"], time_input_yr, p1=vd["P_yr1"])

    # ----- Show survival -----
    st.markdown('Survival in the previous year (from Equation [3] or [7]): ')
    latex_survival_display = utilities.latex_equations.\
        survival_display(time_input_yr-1, S0)
    st.latex(latex_survival_display)

    # ----- Calculate probability -----
    st.markdown('Probability:')
    latex_pDeath_yrn = utilities.latex_equations.\
        pDeath_yrn(P1, F0, F1, time_input_yr, S0)
    st.latex(latex_pDeath_yrn)
    if S0 <= 0.0:
        st.markdown(''.join([
            'The probability is zero because the survival rate ',
            'in the previous year is not above zero.'
            ]))


def write_details_median_survival(vd):
    # st.markdown('## Median survival time')

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
    latex_prob_prime_generic = utilities.latex_equations.prob_prime_generic()
    st.latex(latex_prob_prime_generic)

    # ----- Time to death (case 1) -----
    st.markdown(''.join([
        'The time of death is derived from Equation [4] ',
        'and has the form:'
        ]))
    latex_death_time_case1_generic = utilities.latex_equations.\
        death_time_case1_generic()
    st.latex(latex_death_time_case1_generic)

    # ----- Case 2 -----
    st.markdown('### Case 2')
    st.markdown(''.join([
        'If $P \leq P_1$, the time of death is based on the probability ',
        'of death in year one (Equation 1). '
        ]))
    # ----- Time to death (case 2) -----
    latex_death_time_case2_generic = utilities.latex_equations.\
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
    latex_Pyr1_display = utilities.latex_equations.\
        Pyr1_display(vd['P_yr1'])
    # LP in year n: 
    latex_LPyrn_display = utilities.latex_equations.\
        LPyrn_display(vd['LP_yrn'])
    # gamma:
    latex_gammaH_display = utilities.latex_equations.\
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

    def print_survival_time_calcs(p, tDeath, vd):
        # ----- Select case -----
        if p < vd['P_yr1']:
            # Case 2
            st.markdown(''.join([
                '$P = '+f'{100.0*p:.0f}'+'$%, so'
                '$P \leq P_1$ and we use Case 2. ',
                'The time of death is:'
                ]))
            # ----- Calculate time -----
            latex_death_time_case2 = utilities.latex_equations.\
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
            latex_prob_prime = utilities.latex_equations.\
                prob_prime(p, prob_prime, vd['P_yr1'])
            st.latex(latex_prob_prime)
            # ----- Calculate time -----
            st.markdown('Then the time of death is: ')
            latex_death_time_case1 = utilities.latex_equations.\
                death_time_case1(tDeath, prob_prime, 
                                 vd['LP_yrn'], vd['gz_gamma'], p)
            st.latex(latex_death_time_case1)

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
        st.markdown(''.join([
            'The life expectancy is the current age plus this ',
            'median survival value:'
        ]))
        life_expectancy = vd['age'] + tDeath_med
        latex_life_expectancy = utilities.latex_equations.\
            life_expectancy(life_expectancy, tDeath_med, vd['age'])
        st.latex(latex_life_expectancy)

    with tabs[1]:
        st.markdown('__IQR lower value:__')
        print_survival_time_calcs(p_iqr_low, tDeath_iqr_low, vd)
    with tabs[2]:
        st.markdown('__IQR upper value:__')
        print_survival_time_calcs(p_iqr_high, tDeath_iqr_high, vd)
    with tabs[3]:
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




# #####################################################################
# The following plots use matplotlib.pyplot and have been replaced
# with the plotly versions elsewhere.
def plot_survival_vs_time(time_list_yr, survival_list):
    """
    REPLACED with plotly version.
    Plot survival vs time.
    """
    fig, ax = plt.subplots()

    # Plot content:
    ax.plot(time_list_yr, survival_list*100.0)

    # Plot setup:
    ax.set_title('Survival')
    ax.set_xlabel('Years since discharge')
    ax.set_ylabel('Survival (%)')

    # Change axis ticks:
    ax.set_xlim(0, time_list_yr[-1])
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 25))
    ax.set_yticks(np.arange(0, 101, 5), minor=True)
    ax.set_xticks(np.arange(0, time_list_yr[-1]+5, 5))
    ax.set_xticks(np.arange(0, time_list_yr[-1]+1, 1), minor=True)
    ax.grid(color='k', alpha=0.2)

    # Change how squat or skinny the plot is, where the smaller the
    # fraction, the squatter the plot:
    ax.set_aspect(1.0/10.0)

    # Write to streamlit:
    st.pyplot(fig)


def plot_hazard_vs_time(time_list_yr, all_hazard_lists, colours):
    """
    REPLACED with plotly version.
    Plot hazard vs time.
    """
    fig, ax = plt.subplots()

    # Plot content:
    # Create an array of zeroes for use with fill_between
    # on the first go round the "for" loop.
    y_before = np.zeros(len(all_hazard_lists[0]))

    for mRS in np.arange(6):
        # Get data from the big list
        # and multiply by 100 for percent:
        y_vals = all_hazard_lists[mRS] * 100.0

        # Colour the gap between this line and the previous:
        ax.fill_between(
            time_list_yr, y_vals, y_before,
            color=colours[mRS],
            label=mRS
            )

        # Update the y-values of the previous line
        # for the next go round the loop.
        y_before = y_vals

    # Plot setup:
    ax.set_title('Hazard function for Death by mRS')
    ax.set_xlabel('Years since discharge')
    ax.set_ylabel('Cumulative hazard (%)')

    # Change axis ticks:
    ax.set_xlim(0, time_list_yr[-1])
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_yticks(np.arange(0, 101, 5), minor=True)
    ax.set_xticks(np.arange(0, time_list_yr[-1]+5, 5))
    ax.set_xticks(np.arange(0, time_list_yr[-1]+1, 1), minor=True)
    ax.grid(color='k', alpha=0.2)

    # Change how squat or skinny the plot is, where the smaller the
    # fraction, the squatter the plot:
    ax.set_aspect(1.0/5.0)

    # Add legend below the axis:
    ax.legend(title='mRS', bbox_to_anchor=[0.5, -0.2],
              loc='upper center', ncol=6)

    # Write to streamlit:
    st.pyplot(fig)
