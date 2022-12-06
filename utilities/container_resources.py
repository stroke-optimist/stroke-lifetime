"""
This contains everything in the Resources and Costs section.
"""
import streamlit as st
import numpy as np
import pandas as pd


def main(
        A_E_count_list, NEL_count_list, EL_count_list, care_years_list,
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost,
        table_discounted_cost
        ):
    write_table_resource_use(
        A_E_count_list, NEL_count_list,
        EL_count_list, care_years_list
        )
    write_table_discounted_resource_use(
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        )
    write_table_discounted_change(table_discounted_cost)


def write_table_resource_use(
        A_E_count_list, NEL_count_list,
        EL_count_list, care_years_list
        ):
    headings = [
        # 'mRS',
        'A&E',
        'NEL Days',
        'EL Days',
        'Average time in residential care (years)'
    ]
    # Combine lists into a grid
    table = np.transpose(np.vstack((
        A_E_count_list,
        NEL_count_list,
        EL_count_list,
        care_years_list
        )))
    # Change into a dataframe with column headings:
    df_table = pd.DataFrame(table, columns=headings)

    # Write to streamlit:
    st.write('### Resource use')
    st.table(df_table.style.format("{:4.2f}"))


def write_table_discounted_resource_use(
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        ):
    headings = [
        # 'mRS',
        'A&E',
        'NEL Days',
        'EL Days',
        'Cost of residental care',
        'Total cost'
    ]

    # Combine lists into a grid
    table = np.transpose(np.vstack((
        A_E_discounted_cost,
        NEL_discounted_cost,
        EL_discounted_cost,
        care_years_discounted_cost,
        total_discounted_cost
        )))

    # # Round pounds up (away from zero if -ve) to match Excel.
    # table_round = np.zeros_like(table)
    # inds_neg = np.where(table < 0.0)
    # inds_pos = np.where(table >= 0.0)
    # table_round[inds_neg] = np.floor(table[inds_neg])
    # table_round[inds_pos] = np.ceil(table[inds_pos])
    table_round = table

    # Change into a dataframe with column headings:
    df_table = pd.DataFrame(table_round, columns=headings)

    # Write to streamlit:
    st.write('### Discounted Cost of Resource use')
    st.table(df_table.style.format('£{:.0f}'))


def write_table_discounted_change(table_discounted_cost):
    # Use this function to colour values in the table:
    def color_negative_red(val):
        colour = None
        if len(val) > 0:
            if val[0] == '-' and val[-1] != '-':
                # Also check final character to check it's not a
                # string of one character, '-'.
                colour = 'red'
        return f'color: {colour}'

    # Change the table values to formatted strings:
    table = []
    for row in range(6):
        row_vals = []
        for column in range(6):
            diff_val = table_discounted_cost[row][column]
            if type(diff_val) == np.float64:
                # Either add a minus sign or a bit of empty space.
                sign = '-' if diff_val < 0 else '\U00002004'
                # Round pounds up (away from zero if -ve) to match Excel.
                # diff = sign+f'£{np.ceil(np.abs(diff_val)):.0f}'
                diff = sign+f'£{np.abs(diff_val):.0f}'
                # Add extra spaces at the start for right-alignment
                # cheat:
                extra_spaces = 10 - len(diff)
                diff = (
                    diff.split('£')[0] + '£' +
                    extra_spaces * '\U00002002' +
                    diff.split('£')[1]
                )
                row_vals.append(diff)
            elif column == row:
                row_vals.append('-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table)

    df_table = pd.DataFrame(table)

    # Write to streamlit:
    st.write('### Discounted total costs by change in outcome')
    st.table(df_table.style.applymap(color_negative_red))
    st.write('Changes in outcome from column value to row value.')
    st.write('Numbers in red are increased costs to the NHS, ',
             'numbers in black represent savings to the NHS')
