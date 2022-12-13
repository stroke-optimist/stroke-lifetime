"""
This contains everything in the Cost Effectiveness section.
"""
import streamlit as st
import numpy as np
import pandas as pd


def main(table_cost_effectiveness, variables_dict):
    st.markdown('### Discounted total Net Benefit by change in outcome')
    write_details_cost_effectiveness(variables_dict)
    write_table_cost_effectiveness(table_cost_effectiveness)


def write_table_cost_effectiveness(table_cost_effectiveness):
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
                # Show only a dash on the right-hand-side of the cell.
                row_vals.append(9*'\U00002002' + '-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table)

    df_table = pd.DataFrame(table)

    # Write to streamlit:
    st.table(df_table.style.applymap(color_negative_red))
    st.caption('Changes in outcome from column value to row value.')


def write_details_cost_effectiveness(vd):
    st.markdown(''.join([
        'Net Benefit is QALYs valued at Willingness to pay (WTP) ',
        'threshold, which is '
        f'£{vd["WTP_QALY_gpb"]:.2f}, '
        'plus any cost savings.'
        ]))
    qaly = vd["qalys"][1]-vd["qalys"][2]
    cost = vd["total_discounted_cost"][2]-vd["total_discounted_cost"][1]
    total = vd["WTP_QALY_gpb"]*qaly + cost
    st.markdown(''.join([
        'For example, the change from outcome mRS=1 to mRS=2 ',
        'has a discounted QALY of ',
        f'{qaly:.4f} ',
        'and a discounted total cost of ',
        f'£{cost:.0f}, ',
        'giving a net benefit of: '
    ]))
    st.latex(''.join([
        r'''\begin{equation*} \left(''',
        f'£{vd["WTP_QALY_gpb"]:.0f}', r'''\times''',
        f'{qaly:.4f}', r'''\right)''', f'+ £{cost:.0f} ',
        f'= £{total:.0f}',
        r'''\end{equation*}'''
    ]))