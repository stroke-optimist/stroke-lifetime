# stroke-lifetime

[![GitHub Badge][github-img]][github-link] [![PyPI][pypi-img]][pypi-link] 
[![Open in Streamlit][streamlit-img]][streamlit-link] [![DOI][doi-img]][doi-link]

Toolkit for calculating lifetime survival probabilities and resource use for patients after stroke.

+ __Source code:__ https://github.com/stroke-optimist/stroke-lifetime
+ __Full background and methods:__ _(link to paper to be added when available)_
+ __Detailed workthrough of methods:__ https://lifetime-stroke-outcome.streamlit.app/
+ __PyPI package:__ https://pypi.org/project/stroke-lifetime/
+ __Parent project:__ <a href="https://github.com/stroke-optimist/"><img src="https://avatars.githubusercontent.com/u/77266176" alt="OPTIMIST organisation logo" height="20"></a> [stroke-optimist][github-link-stroke-optimist] Stroke OPTIMIST Project: OPTimising IMplementation of Ischaemic Stroke Thrombectomy

## ➡️ Get started

This toolkit works with Python versions 3.8 and up.

Install the package with:

    pip install stroke-lifetime

And follow the link to the code demonstration in the "External resources" section below. 

## 🏥 Motivation in brief:

Given values for a patient's age, sex, and Modified Rankin Scale (mRS) score on discharge from hospital following a stroke, we can calculate the following quantities across the remainder of that patient's lifespan:
+ The probability of survival of the patient in each year.
+ The number of Quality-Adjusted Life Years (QALYs).
+ The expected use of resources (e.g. number of admissions to A&E and number of years spent in residential care) and the cost of those resources.
+ The discounted total net benefit by change in mRS score. 

The model is described in _a paper that's not yet published. Link will be added when available_.


## 📦 Package details:

There are three main modules in the package:

+ `models.py` - Basic models.
+ `fixed_params.py` - Constants.
+ `main_calculations.py` - Gathers the basic models and calculates all of the useful outputs. 


<a href="https://lifetime-stroke-outcome.streamlit.app/"><img align="right" src="https://raw.githubusercontent.com/stroke-optimist/stroke-lifetime/main/docs/streamlit_lifetime_preview_rotated_smaller.gif" alt="Animated preview of the Streamlit app."></a>

## 👑 Example usage: Streamlit app

View a Streamlit app that uses this package and presents the methods in detail:

[![Open in Streamlit][streamlit-img]][streamlit-link] [![DOI][streamlit-doi-img]][streamlit-doi-link]

+ __Streamlit app:__ https://lifetime-stroke-outcome.streamlit.app/
+ __DOI:__ https://doi.org/10.5281/zenodo.8269389


## 📚 External resources

The following resources are not included within the package files and are accessible on the GitHub repository.

A conda environment file, `environment.yml`, is provided in the GitHub repository for use with the demonstration Jupyter notebook.

+ [![Jupyter Notebook][jupyternotebook-img]][demo-jupyternotebook-link] - [Code demonstration][demo-jupyternotebook-link] of running the main function and using the results. It also contains reference tables to describe the results categories.


[github-img]: https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white
[github-link]: https://github.com/stroke-optimist/stroke-lifetime

[pypi-img]: https://img.shields.io/pypi/v/stroke-lifetime?label=pypi%20package
[pypi-link]: https://pypi.org/project/stroke-lifetime/

[doi-img]: https://zenodo.org/badge/814086731.svg
[doi-link]: https://zenodo.org/doi/10.5281/zenodo.11637387

[github-link-stroke-optimist]: https://github.com/stroke-optimist/

[streamlit-img]: https://static.streamlit.io/badges/streamlit_badge_black_white.svg
[streamlit-link]: https://lifetime-stroke-outcome.streamlit.app/

[streamlit-doi-img]: https://zenodo.org/badge/575076706.svg
[streamlit-doi-link]: https://doi.org/10.5281/zenodo.8269389

[jupyternotebook-img]: https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white
[demo-jupyternotebook-link]: https://github.com/stroke-optimist/stroke-lifetime/blob/main/docs/demo.ipynb