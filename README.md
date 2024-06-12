# stroke-lifetime

[![GitHub Badge][github-img]][github-link]


Toolkit for calculating lifetime survival probabilities and resource use for patients after stroke.

+ __Source code:__ https://github.com/stroke-optimist/stroke-lifetime
+ __Parent project:__ <a href="https://github.com/stroke-optimist/"><img src="https://avatars.githubusercontent.com/u/77266176" alt="OPTIMIST organisation logo" height="20"></a> [stroke-optimist][github-link-stroke-optimist] Stroke OPTIMIST Project: OPTimising IMplementation of Ischaemic Stroke Thrombectomy

## ➡️ Get started

This toolkit works with Python versions 3.8 and up.

Install the package with:

    pip install stroke-lifetime

## 🏥 Motivation in brief:

Given values for a patient's age, sex, and Modified Rankin Scale (mRS) score on discharge from hospital following a stroke, we can calculate the following quantities across the remainder of that patient's lifespan:
+ The probability of survival of the patient in each year.
+ The number of Quality-Adjusted Life Years (QALYs).
+ The expected use of resources (e.g. number of admissions to A&E and number of years spent in residential care) and the cost of those resources.
+ The discounted total net benefit by change in mRS score. 

The model is described in _a paper that's not yet published. Link will be added when available_.


## 📦 Package details:

+ `models.py` - Basic models
+ `fixed_params.py` - Constants
+ `main_calculations.py` - Gathers the basic models and calculates all of the useful outputs. 


## Example usage: Streamlit app

View a Streamlit app that uses this package:

[![Open in Streamlit][streamlit-img]][streamlit-link] [![DOI][streamlit-doi-img]][streamlit-doi-link]

+ __Streamlit app:__ https://lifetime-stroke-outcome.streamlit.app/
+ __DOI:__ https://doi.org/10.5281/zenodo.8269389


[github-img]: https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white
[github-link]: https://github.com/stroke-optimist/stroke-lifetime

[github-link-stroke-optimist]: https://github.com/stroke-optimist/

[streamlit-img]: https://static.streamlit.io/badges/streamlit_badge_black_white.svg
[streamlit-link]: https://lifetime-stroke-outcome.streamlit.app/

[streamlit-doi-img]: https://zenodo.org/badge/575076706.svg
[streamlit-doi-link]: https://doi.org/10.5281/zenodo.8269389