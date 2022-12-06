"""
This contains everything in the Cost Effectiveness section.
"""
import streamlit as st
import numpy as np
import pandas as pd


def main(table_cost_effectiveness):
    write_table_cost_effectiveness(table_cost_effectiveness)


def write_table_cost_effectiveness(table_cost_effectiveness):
    # Use this function to colour values in the table:
    def color_negative_red(val):
        colour = 'black'
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
            diff_val = table_cost_effectiveness[row][column]
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
    st.markdown('### Discounted total Net Benefit by change in outcome')
    st.table(df_table.style.applymap(color_negative_red))
    st.write('Changes in outcome from column value to row value.')
    st.write('Net Benefit is QALYs valued at Willingness to pay ',
             'threshold plus any cost savings')
