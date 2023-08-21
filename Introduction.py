"""
Streamlit app for the stroke outcome model.
"""
import streamlit as st

from utilities_lifetime.fixed_params import page_setup
from utilities_lifetime.inputs import write_text_from_file

# Set up the tab title and emoji:
page_setup()

st.markdown('# Stroke lifetime mortality')
# st.markdown('## Summary')
st.markdown(''.join([
    'This app demonstrates the findings from ',
    'a lifetime economic stroke outcome model. ',
    'The model is designed to be used in either ',
    'discrete time or discrete event simulations. ',
    'The method used to develop the equations relied on ',
    'simulation and estimation techniques.'
    ]))
st.markdown(''.join([
    'Given a patient\'s age, sex and mRS score, ',
    'the demo calculates the following:'
    ]))

cols = st.columns(2)

cols[0].error('''
    Mortality
    + Mortality during year one
    + Mortality after year one
    + Mortality in a chosen year
    + Median survival in years
    ''')

cols[0].warning('''
    QALYs
    + Discounted QALYs for the median survival years
    + Change in QALYs by change in outcome
    ''')

cols[1].warning('''
    Resources and costs
    + Resource use and its discounted cost for:
        + A&E admissions
        + Non-elective bed days
        + Elective bed days
        + Average time in residential care (years)
    + Discounted total costs by change in outcome
    ''')

cols[1].error('''
    Cost-effectiveness
    + Discounted total net benefit by change in outcome
    ''')

write_text_from_file('pages/text_for_pages/1_Intro.txt',
                     head_lines_to_skip=3)
