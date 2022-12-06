"""
This contains everything in the QALYs section.
"""
import streamlit as st
import numpy as np
import pandas as pd

from utilities.fixed_params import utilities


def main(survival_times, qalys, qalys_table):
    write_table_discounted_qalys(survival_times, qalys)
    write_table_discounted_qalys_outcome(qalys_table)


def write_table_discounted_qalys(survival_times, qalys):
    """
    Use the non-removable index column as the mRS column.
    """
    qaly_table = []
    for i, mRS in enumerate(range(6)):
        qaly_table.append([
            utilities[i],
            # mRS,
            survival_times[i][0],
            survival_times[i][1],
            survival_times[i][2],
            qalys[i]
        ])

    # Convert to a pandas dataframe so we can label the columns:
    qaly_table = np.array(qaly_table)
    df_table = pd.DataFrame(
        qaly_table,
        columns=(
            'Utility',
            # 'mRS',
            'Median survival (years)',
            'Lower IQR (years)',
            'Upper IQR (years)',
            'QALYs'
            )
    )
    format_dict = {
        'Utility': '{:4.2f}',
        # 'mRS': '{:1.0f}',
        'Median survival (years)': '{:4.2f}',
        'Lower IQR (years)': '{:4.2f}',
        'Upper IQR (years)': '{:4.2f}',
        'QALYs': '{:4.2f}'
        }
    # Write to streamlit:
    st.markdown('### Discounted QALYs')
    st.table(df_table.style.format(format_dict))


def write_table_discounted_qalys_outcome(qaly_table):

    # Change the table values to formatted strings:
    table = []
    for row in range(6):
        row_vals = []
        for column in range(6):
            val = qaly_table[row][column]
            if type(val) == np.float64:
                # Format the number as a nice string:
                row_vals.append(f'{val:4.2f}')
            elif column == row:
                row_vals.append('-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table)

    df_table = pd.DataFrame(table)

    # Write to streamlit:
    st.markdown('### Discounted QALYs by change in outcome')
    st.write('Change in outcome from column value to row value.')
    st.table(df_table)
    # Notes from the Excel FrontSheet:
    st.write('Stroke. 2018;49:965-971')
    st.write(
        'Note: QALY shorfalls compared to lifetime QALYs can be ',
        'weighted 85%-95% shortfall valued @ 120%, ',
        '95% shortfall valued @ 170%')
    st.write('**** NICE health technology evaluations: the manual (Jan 2022)')
    return
