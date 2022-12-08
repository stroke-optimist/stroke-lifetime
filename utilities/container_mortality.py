"""
This contains everything in the Mortality section.
"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

from utilities.fixed_params import colours_excel
from utilities.inputs import write_text_from_file


def main(
        time_list_yr, all_survival_lists,
        mRS_input, all_hazard_lists,
        pDeath_list, invalid_inds_for_pDeath, survival_times,
        time_of_death, variables_dict
        ):
    # These older plots use matplotlib instead of plotly:
    # plot_survival_vs_time(time_list_yr, all_survival_lists[mRS_input])
    # plot_hazard_vs_time(time_list_yr, all_hazard_lists, colours_excel)

    # Plot:
    plot_survival_vs_time_plotly(
        time_list_yr, all_survival_lists[mRS_input], time_of_death)
    # Plot:
    plot_hazard_vs_time_plotly(time_list_yr, all_hazard_lists)
    # Table:
    write_table_of_pDeath(pDeath_list, invalid_inds_for_pDeath, n_columns=3)
    # Table:
    write_table_of_median_survival(survival_times)

    with st.expander('Mortality during year one'):
        write_details(variables_dict, mRS_input)

    with st.expander('Mortality in subsequent years'):
        pass
        # write_details(variables_dict, mRS_input)


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
    # (I've set the upper limits slightly above the data limits so that
    # in dark mode, there's a border on the top and right sides.)
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
    st.markdown('### Probability of death')
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
                name=('Probability of death')
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
            name=('pDeath')
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
    st.markdown('### Survival')
    st.write('The survival estimates for each mRS (0 to 5): ')
    st.table(df_table.style.format("{:.2f}"))


def write_details(vd, mrs):
    """
    Read in and print a series of markdown text files.
    These are stored in the folder: pages/text_for_pages.

    When appropriate, split into two columns to show both
    the general formula and the version with variables subbed in.

    Equations will be labelled with numbers with \begin{equation},
    but that numbering doesn't carry through between tabs
    i.e. there could be multiple "Equation 1"s.
    Instead use \tag to manually label equations, e.g.
    \begin{equation}\tag{5}.

    "vd" is short for variables_dict.
    """
    # write_text_from_file(
    #     'pages/text_for_pages/calculations_mortality_1.txt',
    #     head_lines_to_skip=2
    #     )
    st.markdown('## Mortality during year one')
    # ----- Tables of constants -----
    st.markdown(
        'The following constants are used to calculate the probability ' +\
        'of death during year one.'
        )
    table_cols = st.columns(2)
    with table_cols[0]:
        st.markdown(
            r'''
            | Coefficient | Description |
            | --- | --- |
            | ''' + f'{vd["lg_coeffs"][0]}' + r'''| Constant |
            | ''' + f'{vd["lg_coeffs"][1]}' + r'''| Adjusted age |
            | ''' + f'{vd["lg_coeffs"][2]}' + r'''| Sex |
            '''
            )
    with table_cols[1]:
        st.markdown(
            r'''
            | mRS | mRS coefficient | Mean age coefficient|
            | --- | --- | --- |
            | 0 | ''' + f'{vd["lg_coeffs"][3+0]}' + r'''| ''' + \
                f'{vd["lg_mean_ages"][0]}' + r'''|
            | 1 | ''' + f'{vd["lg_coeffs"][3+1]}' + r'''| ''' + \
                f'{vd["lg_mean_ages"][1]}' + r'''|
            | 2 | ''' + f'{vd["lg_coeffs"][3+2]}' + r'''| ''' + \
                f'{vd["lg_mean_ages"][2]}' + r'''|
            | 3 | ''' + f'{vd["lg_coeffs"][3+3]}' + r'''| ''' + \
                f'{vd["lg_mean_ages"][3]}' + r'''|
            | 4 | ''' + f'{vd["lg_coeffs"][3+4]}' + r'''| ''' + \
                f'{vd["lg_mean_ages"][4]}' + r'''|
            | 5 | ''' + f'{vd["lg_coeffs"][3+5]}' + r'''| ''' + \
                f'{vd["lg_mean_ages"][5]}' + r'''|
            '''
            )

    # ----- Equation for probability -----
    st.markdown('The probability is calculated as:')
    st.latex(
        r'''
        \begin{equation}\tag{1}
        P_{\mathrm{yr1}} = \frac{1}{1+e^{-LP_{\mathrm{yr1}}}}
        \end{equation}
        '''
        )

    # ----- Equation for linear predictor -----
    st.markdown('with linear predictor')
    st.latex(
        r'''
        \begin{equation}\tag{2}
        LP_{\mathrm{yr1}} =
        \alpha_{\mathrm{yr1}} +
        \displaystyle\sum_{i=1}^{n}
        \beta_{\mathrm{yr1},\ i}
        \cdot
        X_{\mathrm{yr1},\ i}
        \end{equation}
        '''
        )

    # ----- Calculations with user input -----
    st.markdown(
        'For the current patient details, these are calculated as follows.' +\
        ' Values in red change with the patient details, and values in ' +\
        'pink use a different constant from the tables above depending ' +\
        'on the patient details.'
        )

    # ----- Calculation for linear predictor -----
    st.markdown('The linear predictor:')
    st.latex(
        r'''\begin{align*}
        LP_{\mathrm{yr1}} =&''' +
        # alpha
        f'{vd["lg_coeffs"][0]}' + r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["lg_coeffs"][1]}' + r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' + r'''}-\textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][mrs]}' +
        r'''}]\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["lg_coeffs"][2]}' + r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' + r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 3rd coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["lg_coeffs"][3+mrs]}' + r'''} \times \textcolor{red}{''' +
        f'{vd["mrs"]}' + r'''}\right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["LP_yr1"]:.2f}' +
        r'''}
        \end{align*}'''
        )
    st.write('\* This value is 0 for female patients and 1 for male.')

    # ----- Calculation for probability -----
    st.markdown('Probability:')
    st.latex(
        r'''
        \begin{align*}
        P_1 &= \frac{1}{1+e^{-
        \textcolor{red}{
        ''' +
        f'{vd["LP_yr1"]:.2f}' +
        r'''
        }
        }} \\
        &=
        \textcolor{red}{
        ''' +
        f'{100.0*vd["P_yr1"]:.2f}' +
        r'''
        \%}
        \end{align*}
        '''
        )


# #####################################################################
# The following plots use matplotlib.pyplot and have been replaced
# with the plotly versions elsewhere.
def plot_survival_vs_time(time_list_yr, survival_list):
    """
    REPLACED with plotly version.
    Plot survival vs time."""
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
