import streamlit as st
import pandas as pd


def write_text_from_file(filename, head_lines_to_skip=0):
    """
    Write text from 'filename' into streamlit.
    Skip a few lines at the top of the file using head_lines_to_skip.
    """
    # Open the file and read in the contents,
    # skipping a few lines at the top if required.
    with open(filename, 'r', encoding="utf-8") as f:
        text_to_print = f.readlines()[head_lines_to_skip:]

    # Turn the list of all of the lines into one long string
    # by joining them up with an empty '' string in between each pair.
    text_to_print = ''.join(text_to_print)

    # Write the text in streamlit.
    st.markdown(f"""{text_to_print}""")


def import_animal_data(filename, index_col=None, header='infer'):
    """
    Import an Animals dataframe from file.

    This example is simple, but for a more complicated case
    it can be easier to have a separate import function for each
    data file type. For example, perhaps the data file contains
    data for many different scenarios and we want to extract
    the rows or columns for just one scenario.
    """
    # Load mRS distributions from file:
    df = pd.read_csv(
        filename,
        index_col=index_col,
        header=header)

    return df
