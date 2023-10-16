"""
Store all of the LaTeX formulae and markdown tables that will be
printed in the demo.

Each formula is pretty bulky and throws up lots of python linting
errors, so they've been banished to this file for easier reading
of the container scripts.

The order on this page is more or less the order that the functions
are called during the Interactive Demo.
Moved some related functions to have their generic versions next to
their versions with variables subbed in.

Equations will be labelled with numbers with \begin{equation},
but that numbering doesn't carry through between tabs
i.e. there could be multiple "Equation 1"s.
Instead use \tag to manually label equations, e.g.
\begin{equation*}\tag{5}.

LaTeX is flexible with spacing in the strings, but the markdown
tables will throw a wobbly if you edit the spacing in these functions
much. Leave the markdown alone!

Terms used in this script:
"vd"      - is short for variables_dict from main_calculations.py.
"generic" - means an equation with only symbols and constants,
            i.e. no calculated variables.
"display" - means we're just showing the current value of some
            variable, as opposed to showing a formula for it.
"""

# #####################################################################
# ############################ Mortality ##############################
# #####################################################################


# ##### Mortality in year one #####
def table_lg_coeffs(vd):
    """Table of logistic regression coefficients."""
    str = (
        r'''
        | Description | Coefficient |
        | --- | --- |
        | Constant $\alpha_{1}$ | ''' + f'{vd["lg_coeffs"][0]}' + r'''|
        | Adjusted age | ''' + f'{vd["lg_coeffs"][1]}' + r'''|
        | Sex | ''' + f'{vd["lg_coeffs"][2]}' + r'''|
        '''
        )
    return str


def table_lg_mrs_coeffs(vd):
    """Table of logistic regression mRS coefficients."""
    str = (
        r'''
        | mRS | mRS coefficient | Mean age coefficient |
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
    return str



def table_lg_mrs_coeffs_dicho(vd):
    """
    Table of logistic regression mRS coefficients.

    This uses the first and final row of the individual mRS table
    with the rows and column headings re-labelled.
    """
    str = (
        r'''
        | Outcome | Outcome coefficient | Mean age coefficient |
        | --- | --- | --- |
        | Independent | ''' + f'{vd["lg_coeffs"][3+0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | Dependent | ''' + f'{vd["lg_coeffs"][3+5]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def pDeath_year1_generic():
    """Probability of death in year one."""
    str = (
        r'''
        \begin{equation}\tag{1}
        P_{1} = \frac{1}{1+e^{-LP_{1}}}
        \end{equation}
        '''
        )
    return str


def prob_year1(vd):
    """
    Probability of death in year one, with symbols
    replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        P_{1} &= \frac{1}{1+e^{-
        \textcolor{red}{
        ''' +
        f'{vd["lp_year1"]:.4f}' +
        r'''
        }
        }} \\
        &=
        \textcolor{red}{
        ''' +
        f'{100.0*vd["P_year1"]:.2f}' +
        r'''
        \%}
        \end{align*}
        '''
        )
    return str


def Pyear1_display(P_year1):
    """
    Shows the current value of probability of death in year one.
    """
    str = (
        r'''
        P_{1} = \textcolor{red}{
        ''' +
        f'{100.0*P_year1:.2f}' +
        r'''
        \%}
        '''
    )
    return str


def lp_year1_generic():
    """Linear predictor for probability of death in year one."""
    str = (
        r'''
        \begin{equation}\tag{2}
        LP_{1} =
        \alpha_{1} +
        \displaystyle\sum_{i=1}^{n}
        \beta_{1,\ i}
        \cdot
        X_{1,\ i}
        \end{equation}
        '''
        )
    return str


def lp_year1(vd):
    """
    Linear predictor for probability of death in year one, with symbols
    replaced with variables from the calculations.
    """
    str = (
        r'''\begin{align*}
        LP_{1} =&''' +
        # alpha
        f'{vd["lg_coeffs"][0]}' +
        r'''
         +& \mathrm{constant} \\
        ''' +
        # 1st coeff
        r'''
        & \left(
        ''' +
        f'{vd["lg_coeffs"][1]}' +
        r'''
        \times [\textcolor{red}{
        ''' +
        f'{vd["age"]}' +
        r'''
        } - \textcolor{Fuchsia}{
        ''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''
        }]\right) + & \mathrm{age} \\
        ''' +
        # 2nd coeff
        r'''
        & \left(
        ''' +
        f'{vd["lg_coeffs"][2]}' +
        r'''
        \times \textcolor{red}{
        ''' +
        f'{vd["sex"]}' +
        r'''
        }\right) + & \mathrm{sex}^{*} \\
        ''' +
        # 3rd coeff
        r'''
        & \left(\textcolor{Fuchsia}{
        ''' +
        f'{vd["lg_coeffs"][3+vd["mrs"]]}' +
        r'''
        } \right) & \mathrm{mRS} \\
        ''' +
        # Next line, value equal to:
        r'''
        =& \textcolor{red}{
        ''' +
        f'{vd["lp_year1"]:.4f}' +
        r'''
        }
        \end{align*}'''
        )
    return str


def survival_year1_generic():
    """Survival in year one."""
    str = (
        r'''
        \begin{equation}\tag{3}
        S_1 = 1 - P_{1}
        \end{equation}
        '''
    )
    return str


def survival_year1(vd):
    """
    Survival percentage in year one, with symbols
    replaced with variables from the calculations.
    """
    if vd["survival_year1"] < 0.0:
        # Add an extra line showing an inequality.
        extra_str = r''' \\ S_1 &< \textcolor{red}{0\%} '''
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        S_1
        & = 1 - \textcolor{red}{
        ''' +
        f'{vd["P_year1"]:.4f}' +
        r'''
        } \\
        & = \textcolor{red}{
        ''' +
        f'{100.0*vd["survival_year1"]:.2f}' +
        r'''
        \%}
        ''' +
        extra_str +
        r'''
        \end{align*}
        '''
        )
    return str


# ##### Mortality after year one #####
def table_gz_coeffs(vd):
    """Table of coefficients for Gompertz predictor."""
    str = (
        r'''
        | Description | Coefficient |
        | --- | --- |
        | Constant $\alpha_\mathrm{H}$ | ''' + f'{vd["gz_coeffs"][0]}' + r'''|
        | Adjusted age | ''' + f'{vd["gz_coeffs"][1]}' + r'''|
        | (Adjusted age)$^{2}$ | ''' + f'{vd["gz_coeffs"][2]}' + r'''|
        | Sex | ''' + f'{vd["gz_coeffs"][3]}' + r'''|
        | $\gamma$ (gamma) | ''' + f'{vd["gz_gamma"]}' + r'''|
        | Mean age | ''' + f'{vd["gz_mean_age"]}' + r'''|
        '''
        )
    return str


def table_gz_mRS_coeffs(vd):
    """Table of mRS coefficients for Gompertz predictor."""
    str = (
        r'''
        | mRS | mRS coefficient | (mRS $\times$ adjusted age) coefficient|
        | --- | --- | --- |
        | 0 | ''' + f'{vd["gz_coeffs"][10+0]}' + r'''| ''' + \
            f'{vd["gz_coeffs"][4+0]}' + r'''|
        | 1 | ''' + f'{vd["gz_coeffs"][10+1]}' + r'''| ''' + \
            f'{vd["gz_coeffs"][4+1]}' + r'''|
        | 2 | ''' + f'{vd["gz_coeffs"][10+2]}' + r'''| ''' + \
            f'{vd["gz_coeffs"][4+2]}' + r'''|
        | 3 | ''' + f'{vd["gz_coeffs"][10+3]}' + r'''| ''' + \
            f'{vd["gz_coeffs"][4+3]}' + r'''|
        | 4 | ''' + f'{vd["gz_coeffs"][10+4]}' + r'''| ''' + \
            f'{vd["gz_coeffs"][4+4]}' + r'''|
        | 5 | ''' + f'{vd["gz_coeffs"][10+5]}' + r'''| ''' + \
            f'{vd["gz_coeffs"][4+5]}' + r'''|
        '''
        )
    return str


def table_gz_mRS_coeffs_dicho(vd):
    """
    Table of mRS coefficients for Gompertz predictor.

    This uses the first and bottom row of the individual mRS table
    with the rows and column headings re-labelled.
    """
    str = (
        r'''
        | Outcome | Outcome coefficient | (Outcome $\times$ adjusted age) coefficient|
        | --- | --- | --- |
        | Independent | ''' + f'{vd["gz_coeffs"][10+0]}' + r'''| ''' + \
            f'{vd["gz_coeffs"][4+0]}' + r'''|
        | Dependent | ''' + f'{vd["gz_coeffs"][10+5]}' + r'''| ''' + \
            f'{vd["gz_coeffs"][4+5]}' + r'''|
        '''
        )
    return str


def gammaH_display(gamma):
    """
    Shows the current value of the Gompertz gamma coefficient.
    """
    str = (
        r'''
        \gamma = ''' + f'{gamma}' + r'''
        '''
    )
    return str


def hazard_yearn_generic():
    """Cumulative hazard by year n."""
    str = (
        r'''
        \begin{equation}\tag{4}
        H_t = \frac{e^{LP_{\mathrm{H}}}(e^{\gamma t} - 1)}{\gamma}
        \end{equation}
        '''
        )
    return str


def hazard_yearn(vd, time_input_year):
    """
    Cumulative hazard by year n, with symbols
    replaced with variables from the calculations.
    """
    if vd["fhazard_list"][time_input_year] > 1.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r'''
            \\
            H_{\textcolor{Fuchsia}{
            ''' +
            f'{time_input_year}' +
            r'''
            }} &> \textcolor{red}{100\%}
            '''
        )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        H_{\textcolor{Fuchsia}{
        ''' +
        f'{time_input_year}' +
        r'''
        }} &= \frac{1}{\textcolor{red}{
        ''' +
        f'{vd["gz_gamma"]}' +
        r'''}} \cdot
        e^{
        \textcolor{red}{
        ''' +
        f'{vd["lp_yearn"]:.4f}' +
        r'''
        }} \cdot \left(e^{\textcolor{red}{
        ''' +
        f'{vd["gz_gamma"]}' +
        r'''} \times [\textcolor{Fuchsia}{
        ''' +
        f'{time_input_year}' +
        r'''
        }-1] \times 365} - 1 \right) \\
        &= \textcolor{red}{
        ''' +
        f'{100.0*vd["fhazard_list"][time_input_year]:.2f}' +
        r'''
        \%}
        ''' +
        extra_str +
        r'''
        \end{align*}
        '''
    )
    return str


def lp_yearn_generic():
    """Linear predictor for cumulative hazard by year n."""
    str = (
        r'''
        \begin{equation}\tag{5}
    LP_{\mathrm{H}} =
            \alpha_{\mathrm{H}} +
            \displaystyle\sum_{i=1}^{n}
            \beta_{\mathrm{H},\ i}
            \cdot
            X_{\mathrm{H},\ i}
        \end{equation}
        '''
        )
    return str


def lp_yearn(vd):
    """
    Linear predictor for cumulative hazard by year n, with symbols
    replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        LP_{\mathrm{H}} =&
        ''' +
        # alpha
        f'{vd["gz_coeffs"][0]}' +
        r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["gz_coeffs"][1]}' +
        r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' +
        r'''}-''' +
        f'{vd["gz_mean_age"]}' +
        r''']\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["gz_coeffs"][2]}' +
        r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' +
        r'''}^{2}-''' +
        f'{vd["gz_mean_age"]}' +
        r'''^{2}]\right) + & \mathrm{age}^{2} \\''' +
        # 3rd coeff
        r'''& \left(''' +
        f'{vd["gz_coeffs"][3]}' +
        r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' +
        r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 4th coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["gz_coeffs"][4+vd["mrs"]]}' +
        r'''} \times [\textcolor{red}{''' +
        f'{vd["age"]}' +
        r'''}-''' +
        f'{vd["gz_mean_age"]}' +
        r''']\right) + & (\mathrm{mRS}\times\mathrm{age}) \\''' +
        # 5th coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["gz_coeffs"][10+vd["mrs"]]}' +
        r'''}\right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["lp_yearn"]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


def LPyearn_display(lp_yearn):
    """
    Shows the current value of the linear predictor for death after
    year one.
    """
    str = (
        r'''
        LP_{H} =  \textcolor{red}{''' +
        f'{lp_yearn:.4f}' + r'''}
        '''
    )
    return str


def FDeath_yearn_generic():
    """Cumulative probability of death by year n."""
    str = (
        r'''
        \begin{equation}\tag{6}
        F_{t} = 1 - (1-P_{1})\times(1-H_t)
        \end{equation}
        '''
        )
    return str


def FDeath_yearn(vd, time_input_year):
    """
    Cumulative probability of death by year n, with symbols
    replaced with variables from the calculations.
    """
    if vd["hazard_list"][time_input_year] > 1.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            F_{\textcolor{Fuchsia}{''' +
            f'{time_input_year}' +
            r'''}} &> \textcolor{red}{100\%}
            '''
            )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        F_{\textcolor{Fuchsia}{''' +
        f'{time_input_year}' +
        r'''}} &= 1 - (1-\textcolor{red}{''' +
        f'{vd["P_year1"]:.4f}' +
        r'''})\times(1-\textcolor{red}{''' +
        f'{vd["fhazard_list"][time_input_year]:.4f}' +
        r'''}) \\
        &= \textcolor{red}{''' +
        f'{100.0*vd["hazard_list"][time_input_year]:.2f}' +
        r'''\%}''' +
        extra_str +
        r'''
        \end{align*}
        '''
    )
    return str


def survival_generic():
    "Survival in year n."
    str = (
        r'''
        \begin{equation}\tag{7}
        S_t = 1 - F_t
        \end{equation}
        '''
        )
    return str


def survival(vd, time_input_year):
    """
    Survival by year n, with symbols
    replaced with variables from the calculations.
    """
    if vd["survival_list"][time_input_year] < 0.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            S_{\textcolor{Fuchsia}{''' +
            f'{time_input_year}' +
            r'''}} &< \textcolor{red}{0\%} '''
            )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        S_{\textcolor{Fuchsia}{''' +
        f'{time_input_year}' +
        r'''}} & = 1 - \textcolor{red}{''' +
        f'{vd["hazard_list"][time_input_year]:.4f}' +
        r'''} \\
        & = \textcolor{red}{''' +
        f'{100.0*vd["survival_list"][time_input_year]:.2f}' +
        r'''\%}''' +
        extra_str +
        r'''
        \end{align*}
        '''
        )
    return str


def pDeath_year2_generic():
    """
    Probability of death during year 2.

    (There is no non-generic version of this.)
    """
    str = (
        r'''
        \begin{equation}\tag{8}
        P_2 = 1 - \exp{(P_1 - F_2)}
        \end{equation}
        '''
        )
    return str


def pDeath_yearn_generic():
    """
    Probability of death during year n.
    """
    str = (
        r'''
        \begin{equation}\tag{9}
        P_t = 1 - \exp{(F_{t-1} - F_{t})}
        \end{equation}
        '''
        )
    return str


def pDeath_yearn(P1, F0, F1, time, S1):
    """
    Probability of death during year n, with symbols
    replaced with variables from the calculations.
    """
    # Highlight if survival is below 0%.
    if S1 <= 0.0:
        # Survival is zero, so probability is zero.
        extra_str = (
            r''' \\
            P_{\textcolor{Fuchsia}{''' +
            f'{time}' +
            r'''}} &= \textcolor{red}{0\%}'''
            )
    # Highlight other weird cases:
    # (expecting these to be caught in the actual calculations
    # before we get to displaying the values like this.)
    elif P1 > 1.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            P_{\textcolor{Fuchsia}{''' +
            f'{time}' +
            r'''}} &> \textcolor{red}{100\%}'''
            )
    elif P1 < 0.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            P_{\textcolor{Fuchsia}{''' +
            f'{time}' +
            r'''}} &< \textcolor{red}{0\%}'''
            )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        P_{\textcolor{Fuchsia}{''' +
        f'{time}' +
        r'''}} &= 1 - \exp{(\textcolor{red}{''' +
        f'{F0:.4f}' +
        r'''} - \textcolor{red}{''' +
        f'{F1:.4f}' +
        r'''} )} \\
        &= \textcolor{red}{''' +
        f'{100*P1:.2f}' +
        r'''\%}''' +
        extra_str +
        r'''
        \end{align*}
        '''
        )
    return str


def survival_display(time, survival):
    """
    Show the value of survival by year n, with symbols
    replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{equation*}
        S_{\textcolor{Fuchsia}{''' +
        f'{time}' +
        r'''}} =  \textcolor{red}{''' +
        f'{100.0*survival:.2f}' +
        r'''\%}
        \end{equation*}
        '''
    )
    return str


# ##### Survival #####
def median_survival_display(vd):
    """Show the number of years when survival is 50%."""
    str = (
        r'''
        \begin{equation*}
        \mathrm{years} = \textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][0]:.2f}' +
        r'''}
        \end{equation*}
        '''
        )
    return str


def prob_prime_generic():
    """
    P`, prob prime, or time_log.
    Probability of death during year n, modified to account for the
    chance of death during year 1.
    """
    str = (
        r'''
        \begin{equation*}\tag{10}
        P^{\prime} = \frac{1 + P}{1 + P_1} - 1
        \end{equation*}
        '''
    )
    return str


def prob_prime(p, Pprime, P_year1):
    """
    P`, prob prime, or time_log. Probability of death during year n,
    modified by the probability of death during year one. This version
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        P^{\prime} &= \frac{1 + \textcolor{Fuchsia}{''' +
        f'{p:.4f}' +
        r'''}}{1 + \textcolor{red}{''' +
        f'{P_year1:.4f}' +
        r'''}} - 1 \\
        &= \textcolor{red}{''' +
        f'{100.0*Pprime:.2f}' +
        r'''\%}
        \end{align*}
        '''
    )
    return str


def death_time_case1_generic():
    """
    Time of death for Case 1 (Pdeath in year n > Pdeath in year one).
    """
    str = (
        r'''
        \begin{equation*}\tag{11}
        t_{\mathrm{death}}(P) = 1 +
        \frac{1}{\gamma \times 365} \cdot
        \ln\left(
            \frac{P^{\prime} \times \gamma}{
                \exp{(LP_\mathrm{H})}} + 1
            \right)
        \end{equation*}
        '''
    )
    return str


def death_time_case2_generic():
    """
    Time of death for Case 2 (Pdeath in year n <= Pdeath in year one).
    """
    str = (
        r'''
        \begin{equation*}\tag{12}
        t_{\mathrm{death}}(P) =
        \frac{\ln{(1 - P)}}
        {\ln{(1 - P_1)}}\times\frac{1}{365}
        \end{equation*}
        '''
    )
    return str


def death_time_case2(tDeath, p, P_year1):
    """
    Time of death for Case 2 (Pdeath by year n <= Pdeath in year one),
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        t_{\mathrm{death}}(\textcolor{Fuchsia}{''' +
        f'{100.0*p:.0f}' +
        r'''\%}) &=
        \frac{\ln{(1 - \textcolor{Fuchsia}{''' +
        f'{p:.4f}' +
        r'''})}}
        {\ln{(1 - \textcolor{red}{''' +
        f'{P_year1:.4f}' +
        r'''})}}\times \frac{1}{365} \\
        &= \textcolor{red}{''' +
        f'{tDeath:.2f}' +
        r'''} \mathrm{\ years}
        \end{align*}
        '''
    )
    return str


def death_time_case1(tDeath, prob_prime, lp_yearn, gamma, P):
    """
    Time of death for Case 1 (Pdeath by year n > Pdeath in year one),
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        t_{\mathrm{death}}(\textcolor{Fuchsia}{''' +
        f'{100.0*P:.0f}' +
        r'''\%}) &= 1 + \frac{1}{''' +
        f'{gamma}' +
        r''' \times 365} \cdot \ln\left(\frac{\textcolor{red}{''' +
        f'{prob_prime:.4f}' +
        r'''}\times ''' +
        f'{gamma}' +
        r'''}{\exp{(\textcolor{red}{''' +
        f'{lp_yearn:.4f}' +
        r'''})}} + 1.0 \right) \\
        &= \textcolor{red}{''' +
        f'{tDeath:.2f}' +
        r'''} \mathrm{\ years}
        \end{align*}
        '''
    )
    return str


def life_expectancy(life_expectancy, tDeath_med, age):
    """
    Find the life expectancy by adding the current age to the
    median survival years. Variables from the calculations
    are subbed in in place of the symbols.
    """
    str = (
        r'''
        \begin{align*}
        \textcolor{red}{''' +
        f'{age}' +
        r'''} +
        \textcolor{red}{''' +
        f'{tDeath_med:.2f}' +
        r'''} &=
        \textcolor{red}{''' +
        f'{life_expectancy:.2f}' +
        r'''} \mathrm{\ years} \\
        &\approx \textcolor{red}{''' +
        f'{life_expectancy // 1:.0f}' +
        r'''} \mathrm{\ years\ } \textcolor{red}{''' +
        f'{12*(life_expectancy % 1):.0f}' +
        r'''} \mathrm{\ months}
        \end{align*}
        '''
    )
    return str


# #####################################################################
# ############################## QALYs ################################
# #####################################################################


def table_qaly_coeffs(vd):
    """Table of coefficients for QALY linear predictor."""
    str = (
        r'''
        | Description | Coefficient |
        | --- | --- |
        | Adjusted age | ''' + f'{vd["qaly_age_coeff"]}' + r'''|
        | (Adjusted age)$^{2}$ | ''' + f'{vd["qaly_age2_coeff"]:.7f}' + r'''|
        | Sex | ''' + f'{vd["qaly_sex_coeff"]}' + r'''|
        '''
        )
    return str


def table_mean_age_coeffs(vd):
    """
    Table of mean age coefficients (as in year 1).
    """
    str = (
        r'''
        | mRS | Utility, $u$ | Mean age coefficient|
        | --- | --- | --- |
        | 0 | ''' +
            f'{vd["utility_list"][0]}' + r'''| ''' +
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | 1 | '''  +
            f'{vd["utility_list"][1]}' + r'''| ''' +
            f'{vd["lg_mean_ages"][1]}' + r'''|
        | 2 | '''  +
            f'{vd["utility_list"][2]}' + r'''| ''' +
            f'{vd["lg_mean_ages"][2]}' + r'''|
        | 3 | '''  +
            f'{vd["utility_list"][3]}' + r'''| ''' +
            f'{vd["lg_mean_ages"][3]}' + r'''|
        | 4 | '''  +
            f'{vd["utility_list"][4]}' + r'''| ''' +
            f'{vd["lg_mean_ages"][4]}' + r'''|
        | 5 | ''' +
            f'{vd["utility_list"][5]}' + r'''| ''' +
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def table_mean_age_coeffs_dicho(vd):
    """
    Table of mean age coefficients (as in year 1)

    First and final rows of the individual mRS table
    with rows re-labelled for the dichotomous model.
    """
    str = (
        r'''
        | Outcome | Utility, $u$ | Mean age coefficient|
        | --- | --- | --- |
        | Independent | ''' +
            f'{vd["utility_list"][0]}' + r'''| ''' +
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | Dependent | ''' +
            f'{vd["utility_list"][5]}' + r'''| ''' +
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def discounted_raw_qalys_generic():
    """
    QALYs from utility, discount factor, and years.

    Similar format to other linear predictors.
    """
    str = (
        r'''
        \begin{equation}\tag{13}
        Q_{y, \mathrm{raw}} =
            u +
            \displaystyle\sum_{i=1}^{n}
            \beta_{\mathrm{Q},\ i}
            \cdot
            X_{\mathrm{Q},\ i,\ y}
        \end{equation}
        '''
        )
    return str


def discounted_raw_qalys_symbols_generic():
    """
    Version of the QALYs linear predictor that's more explicit.
    Changed to the usual LP equation to avoid defining more symbols.

    QALYs from utility, discount factor, and years.
    """
    str = (
        r'''
        \begin{align*}#\tag{15}
        Q_{y, \mathrm{raw}} =& u + \\
        & ([a + y] - \beta_{\mathrm{av\ age}})
            \times \beta_{\mathrm{age}} - \\
        & ([a + y]^2 - \beta_{\mathrm{av\ age}}^2)
            \times \beta_{\mathrm{age\ sq}} + \\
        & s \times \beta_{\mathrm{sex}}
        \end{align*}
        '''
    )
    return str


def discounted_qalys_generic():
    """QALYs from utility, discount factor, and years."""
    str = (
        r'''
        \begin{equation*}\tag{14}
        Q_{y} = Q_{y,\mathrm{raw}} \times \frac{1}{(1 + d)^{y}}
        \end{equation*}
        '''
    )
    return str


def discounted_qalys_total_generic():
    """Sum discounted resources in all years to get total use."""
    str = (
        r'''
        \begin{equation*}\tag{15}
        Q = \displaystyle\sum_{y=1}^{m} Q_{y}
        \end{equation*}
        '''
    )
    return str


def discounted_raw_qalys(vd, year, qaly_raw):
    """
    Version of the QALYs linear predictor that's more explicit.
    Changed to the usual LP equation to avoid defining more symbols.

    QALYs from utility, discount factor, and years.
    """
    str = (
        r'''
        \begin{align*}
        Q_{\textcolor{Fuchsia}{''' +
        f'{year}' +
        r'''}, \mathrm{raw}} =& \textcolor{Fuchsia}{'''
        f'{vd["utility_list"][vd["mrs"]]}' +
        r'''} + & \mathrm{utility} \\
        & ([\textcolor{red}{''' +
        f'{vd["age"]}' + r'''} +
        \textcolor{Fuchsia}{''' +
        f'{year}' +
        r'''}] - \textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''}) \times ''' +
        f'{vd["qaly_age_coeff"]}' +
        r''' - & \mathrm{age} \\
        & ([\textcolor{red}{''' +
        f'{vd["age"]}' + r'''} +
        \textcolor{Fuchsia}{''' +
        f'{year}' +
        r'''}]^{2} - \textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''}^{2}) \times ''' +
        f'{vd["qaly_age2_coeff"]:.7f}' +
        r''' + & \mathrm{age}^{2} \\
        & \textcolor{red}{''' +
        f'{vd["sex"]}' +
        r'''} \times ''' +
        f'{vd["qaly_sex_coeff"]}' +
        r''' & \mathrm{sex}^{*} \\
        =& \textcolor{red}{''' +
        f'{qaly_raw:.3f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


def discounted_qalys(vd, qaly_raw, year, qaly, frac):
    """QALYs from utility, discount factor, and years."""
    # Check if this is the final year.
    # If it is, add an extra string to explain that we reduce
    # the value to match the fraction of the year that is lived in.
    if frac == 0:
        extra_str = ''
    else:
        extra_str = r'''\times \textcolor{red}{''' + f'{frac:.2f}' + r'''}'''

    str = (
        r'''
        \begin{align*}
        Q_{\textcolor{Fuchsia}{''' +
        f'{year}' +
        r'''}} &= \textcolor{red}{''' +
        f'{qaly_raw:.3f}' +
        r'''} \times \frac{1}{(1 + ''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r''')^{\textcolor{Fuchsia}{''' +
        f'{year}' +
        r'''}}} ''' +
        extra_str +
        r'''\\
        &= \textcolor{red}{''' +
        f'{qaly:.3f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


def build_table_str_qalys(
        qalys_yearaw, qalys_y, discounted_sum
        ):
    """
    Table of raw and discounted QALYs in each year 
    up to the median survival year.

    For each year, add another row to the table.
    If the table is long, cut out the middle and replace with "...".
    """
    # ----- Function for tables -----
    # Set up header:
    table_rows = (
        r'''
        | Year | $Q_{y, \mathrm{raw}}$ | $Q_{y}$ |
        | --- | --- | --- |
        '''
    )

    max_year = len(qalys_y)+1
    # When the max_year is large, end up with a hugely long table.
    # Instead only show the first four and final four rows,
    # with a separating row of "..." in the middle.
    # Set the conditions for the rows to skip:
    if max_year > 10:
        # Long table:
        skip_min = 5
        skip_max = max_year - 5
    else:
        # Table is short enough that we can show the whole thing:
        # Set to values we'll never reach:
        skip_min = max_year + 10
        skip_max = max_year + 10

    for i, year in enumerate(range(1, max_year)):
        if year < skip_min or year > skip_max:
            # Valid entry, so add a row of values to the table:
            row = r'''| ''' + f'{year}' + r''' |  ''' + \
                f'{qalys_yearaw[i]:.4f}' + r''' | ''' +\
                f'{qalys_y[i]:.4f}' + r''' |
        '''
            # ^ don't move these quote marks!!!
            # it looks silly but is necessary for the markdown table,
            # so that each row starts on a new line but is not indented.
            table_rows += row
        else:
            # Either do nothing, or...
            if year == skip_min:
                # Add this row of ... to the table:
                table_rows += r'''| ... | ... | ... |
        '''
        # ^ don't move these quote marks either!!
    # Add a final row to show the sum of the discounted resource values:
    table_rows += r'''| | Sum: | ''' + f'{discounted_sum:.4f}' + r'''|'''
    return table_rows


def discounted_qalys_v7(vd):
    """
    QALYs from utility, discount factor, and years,
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        Q &= \textcolor{Fuchsia}{''' +
        f'{vd["utility_list"][vd["mrs"]]}' +
        r'''} + \frac{\textcolor{Fuchsia}{''' +
        f'{vd["utility_list"][vd["mrs"]]}' +
        r'''}}{1+''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r'''} \times \frac{1 - (1+''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r''')^{-[\textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][0]:.2f}' +
        r'''}-1]}}{1 - (1+''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r''')^{-1}} \\
        &= \textcolor{red}{''' +
        f'{vd["qalys"]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


def discounted_qalys_generic_v7():
    """
    QALYs from utility, discount factor, and years.

    This was used for an older version of the Excel sheet, NHCT v7.0.
    It now goes unused in Streamlit.
    """
    str = (
        r'''
        \begin{equation*}#\tag{13}
        Q = u +
        \frac{u}{1+d} \times
        \frac{1 - (1+d)^{-[\mathrm{years}-1]}}{1 - (1+d)^{-1}}
        \end{equation*}
        '''
    )
    return str


def discounted_qalys_v7(vd):
    """
    QALYs from utility, discount factor, and years,
    with symbols replaced with variables from the calculations.

    This was used for an older version of the Excel sheet, NHCT v7.0.
    It now goes unused in Streamlit.
    """
    str = (
        r'''
        \begin{align*}
        Q &= \textcolor{Fuchsia}{''' +
        f'{vd["utility_list"][vd["mrs"]]}' +
        r'''} + \frac{\textcolor{Fuchsia}{''' +
        f'{vd["utility_list"][vd["mrs"]]}' +
        r'''}}{1+''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r'''} \times \frac{1 - (1+''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r''')^{-[\textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][0]:.2f}' +
        r'''}-1]}}{1 - (1+''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r''')^{-1}} \\
        &= \textcolor{red}{''' +
        f'{vd["qalys"]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


# #####################################################################
# ########################### Resource use ############################
# #####################################################################

# ##### A&E #####
def table_ae_coeffs(vd):
    """Table of coefficients for A&E admissions model."""
    str = (
        r'''
        | Description | Coefficient |
        | --- | --- |
        | Constant $\alpha_{\mathrm{AE}}$ | ''' + \
            f'{vd["ae_coeffs"][0]}' + r'''|
        | Adjusted age | ''' + f'{vd["ae_coeffs"][1]}' + r'''|
        | Sex | ''' + f'{vd["ae_coeffs"][2]}' + r'''|
        | $\gamma_{\mathrm{AE}}$ (gamma) | ''' + \
            f'{vd["ae_coeffs"][3]}' + r'''|
        '''
        )
    return str


def table_ae_mrs_coeffs(vd):
    """Table of mRS coefficients for A&E admissions model."""
    str = (
        r'''
        | mRS | mRS coefficient | Mean age coefficient |
        | --- | --- | --- |
        | 0 | ''' + f'{vd["ae_mRS"][0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | 1 | ''' + f'{vd["ae_mRS"][1]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][1]}' + r'''|
        | 2 | ''' + f'{vd["ae_mRS"][2]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][2]}' + r'''|
        | 3 | ''' + f'{vd["ae_mRS"][3]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][3]}' + r'''|
        | 4 | ''' + f'{vd["ae_mRS"][4]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][4]}' + r'''|
        | 5 | ''' + f'{vd["ae_mRS"][5]}'  + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def table_ae_mrs_coeffs_dicho(vd):
    """
    Table of outcome coefficients for A&E admissions model.

    This uses the first and final rows of the table for the
    individual mRS model, with some re-labelling.
    """
    str = (
        r'''
        | Outcome | Outcome coefficient | Mean age coefficient |
        | --- | --- | --- |
        | Independent | ''' + f'{vd["ae_mRS"][0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | Dependent | ''' + f'{vd["ae_mRS"][5]}'  + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def ae_count_generic():
    """Model for number of A&E admissions."""
    str = (
        r'''
        \begin{equation}\tag{16}
        \mathrm{Count (years)} =
        \exp{
            \left(\gamma_\mathrm{AE}
            \times
            LP_{\mathrm{AE}}\right)
            }
        \times
        \mathrm{years}^{\gamma_{\mathrm{AE}}}
        \end{equation}
        '''
    )
    return str


def ae_lp_generic():
    """Linear predictor for A&E admissions model."""
    str = (
        r'''
        \begin{equation}\tag{17}
        LP_{\mathrm{AE}} =
        \alpha_{\mathrm{AE}} +
        \displaystyle\sum_{i=1}^{n}
        \beta_{\mathrm{AE},\ i}
        \cdot
        X_{\mathrm{AE},\ i}
        \end{equation}
        '''
    )
    return str


def ae_lp(vd):
    """
    Linear predictor for A&E admissions model,
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        LP_{\mathrm{AE}} =&''' +
        # alpha
        f'{vd["ae_coeffs"][0]}' +
        r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["ae_coeffs"][1]}' +
        r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' +
        r'''}-\textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''}]\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["ae_coeffs"][2]}' +
        r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' +
        r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 3rd coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["ae_mRS"][vd["mrs"]]}' +
        r'''}\right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["lp_ae"]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


def ae_count(vd):
    """
    A&E admissions model
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        \mathrm{Count (years=\textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][0]:.2f}' +
        r'''})} &=
        \exp{
            \left( ''' +
            f'{vd["ae_coeffs"][3]}' +
            r''' \times \textcolor{red}{''' +
            f'{vd["lp_ae"]:.4f}' +
            r'''} \right)
            }
        \times \textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][0]:.2f}' +
        r'''}^{''' +
        f'{vd["ae_coeffs"][3]}' +
        r'''} \\
        &= \textcolor{red}{''' +
        f'{vd["ae_count"]:.4f}' +
        r'''}
        \mathrm{\ admissions}
        \end{align*}
        '''
    )
    return str


# ##### Non-elective bed-days #####
def table_nel_coeffs(vd):
    """Table of coefficients for the NEL count model."""
    str = (
        r'''
        | Description | Coefficient |
        | --- | --- |
        | Constant $\alpha_{\mathrm{NEL}}$ | ''' + \
            f'{vd["nel_coeffs"][0]}' + r'''|
        | Adjusted age | ''' + f'{vd["nel_coeffs"][1]}' + r'''|
        | Sex | ''' + f'{vd["nel_coeffs"][2]}' + r'''|
        | $\gamma_{\mathrm{NEL}}$ (gamma) | ''' + \
            f'{vd["nel_coeffs"][3]}' + r'''|
        '''
        )
    return str


def table_nel_mrs_coeffs(vd):
    """Table of mRS coefficients for the NEL count model."""
    str = (
        r'''
        | mRS | mRS coefficient | Mean age coefficient |
        | --- | --- | --- |
        | 0 | ''' + f'{vd["nel_mRS"][0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | 1 | ''' + f'{vd["nel_mRS"][1]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][1]}' + r'''|
        | 2 | ''' + f'{vd["nel_mRS"][2]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][2]}' + r'''|
        | 3 | ''' + f'{vd["nel_mRS"][3]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][3]}' + r'''|
        | 4 | ''' + f'{vd["nel_mRS"][4]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][4]}' + r'''|
        | 5 | ''' + f'{vd["nel_mRS"][5]}'  + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def table_nel_mrs_coeffs_dicho(vd):
    """
    Table of mRS coefficients for the NEL count model.

    This uses the first and final rows of the table for the
    individual mRS model, with some re-labelling.
    """
    str = (
        r'''
        | Outcome | Outcome coefficient | Mean age coefficient |
        | --- | --- | --- |
        | Independent | ''' + f'{vd["nel_mRS"][0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | Dependent | ''' + f'{vd["nel_mRS"][5]}'  + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def nel_bed_days_generic():
    """NEL count model."""
    str = (
        r'''
        \begin{equation}\tag{18}
        \mathrm{Count (years)} =
            -\ln{\left(
            \frac{1}{
                1+ [\mathrm{years}\times\exp{(-LP_\mathrm{NEL})} ] ^{
                    1/ \gamma_{\mathrm{NEL}}}
            }
            \right)}
        \end{equation}
        '''
    )
    return str


def nel_lp_generic():
    """Linear predictor for the NEL count model."""
    str = (
        r'''
        \begin{equation}\tag{19}
        LP_{\mathrm{NEL}} =
        \alpha_{\mathrm{NEL}} +
        \displaystyle\sum_{i=1}^{n}
        \beta_{\mathrm{NEL},\ i}
        \cdot
        X_{\mathrm{NEL},\ i}
        \end{equation}
        '''
    )
    return str


def nel_lp(vd):
    """
    Linear predictor for the NEL count model,
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        LP_{\mathrm{NEL}} =&''' +
        # alpha
        f'{vd["nel_coeffs"][0]}' +
        r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["nel_coeffs"][1]}' +
        r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' +
        r'''}-\textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''}]\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["nel_coeffs"][2]}' +
        r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' +
        r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 3rd coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["nel_mRS"][vd["mrs"]]}' +
        r'''} \right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["lp_nel"]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


def nel_bed_days(vd):
    """
    Number of NEL bed days from the model,
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        \mathrm{Count (years=\textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][0]:.2f}' +
        r'''})} &=
            -\ln{\left(
            \frac{1}{
                1+ [\textcolor{red}{''' +
                f'{vd["survival_meds_IQRs"][0]:.2f}' +
                r'''} \times \exp{(-\textcolor{red}{''' +
                f'{vd["lp_nel"]:.4f}' +
                r'''})} ]^{
                1/ ''' +
                f'{vd["nel_coeffs"][3]}' +
                r'''}}
            \right)} \\
            & = \textcolor{red}{''' +
            f'{vd["nel_count"]:.4f}' +
            r'''} \mathrm{\ days}
        \end{align*}
        '''
    )
    return str


# ##### Elective bed-days #####
def table_el_coeffs(vd):
    """Table of coefficients for the EL bed days model."""
    str = (
        r'''
        | Description | Coefficient |
        | --- | --- |
        | Constant $\alpha_{\mathrm{EL}}$ | ''' + \
            f'{vd["el_coeffs"][0]}' + r'''|
        | Adjusted age | ''' + f'{vd["el_coeffs"][1]}' + r'''|
        | Sex | ''' + f'{vd["el_coeffs"][2]}' + r'''|
        | $\gamma_{\mathrm{EL}}$ (gamma) | ''' + \
            f'{vd["el_coeffs"][3]}' + r'''|
        '''
        )
    return str


def table_el_mrs_coeffs(vd):
    """Table of mRS coefficients for the EL bed days model."""
    str = (
        r'''
        | mRS | mRS coefficient | Mean age coefficient |
        | --- | --- | --- |
        | 0 | ''' + f'{vd["el_mRS"][0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | 1 | ''' + f'{vd["el_mRS"][1]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][1]}' + r'''|
        | 2 | ''' + f'{vd["el_mRS"][2]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][2]}' + r'''|
        | 3 | ''' + f'{vd["el_mRS"][3]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][3]}' + r'''|
        | 4 | ''' + f'{vd["el_mRS"][4]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][4]}' + r'''|
        | 5 | ''' + f'{vd["el_mRS"][5]}'  + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def table_el_mrs_coeffs_dicho(vd):
    """
    Table of mRS coefficients for the EL bed days model.

    This uses the first and final rows of the table for the
    individual mRS model, with some re-labelling.
    """
    str = (
        r'''
        | Outcome | Outcome coefficient | Mean age coefficient |
        | --- | --- | --- |
        | Independent | ''' + f'{vd["el_mRS"][0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | Dependent | ''' + f'{vd["el_mRS"][5]}'  + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def el_bed_days_generic():
    """Model for counting EL bed days."""
    str = (
        r'''
        \begin{equation}\tag{20}
        \mathrm{Count (years)} =
            -\ln{\left(
            \frac{1}{
                1+ [\mathrm{years} \times \exp{(LP_\mathrm{EL})} ] ^{
                    1/ \gamma_{\mathrm{EL}}}
            }
            \right)}
        \end{equation}
        '''
    )
    return str


def el_lp_generic():
    """Linear predictor for the EL bed days model."""
    str = (
        r'''
        \begin{equation}\tag{21}
        LP_{\mathrm{EL}} =
        \alpha_{\mathrm{EL}} +
        \displaystyle\sum_{i=1}^{n}
        \beta_{\mathrm{EL},\ i}
        \cdot
        X_{\mathrm{EL},\ i}
        \end{equation}
        '''
    )
    return str


def el_lp(vd):
    """
    Linear predictor for the EL bed days model,
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        LP_{\mathrm{EL}} =&''' +
        # alpha
        f'{vd["el_coeffs"][0]}' +
        r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["el_coeffs"][1]}' +
        r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' +
        r'''}-\textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''}]\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["el_coeffs"][2]}' +
        r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' +
        r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 3rd coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["el_mRS"]}' +
        r'''} \right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["lp_el"]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


def el_bed_days(vd):
    """
    The number of EL bed days from the model,
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        \mathrm{Count (years=\textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][0]:.2f}' +
        r'''})} &=
            -\ln{\left(
            \frac{1}{
                1+ [\textcolor{red}{''' +
                f'{vd["survival_meds_IQRs"][0]:.2f}' +
                r'''} \times \exp{(-\textcolor{red}{''' +
                f'{vd["lp_el"]:.4f}' +
                r'''})} ]^{
                1/ ''' +
                f'{vd["el_coeffs"][3]}' +
                r'''}}
            \right)} \\
            & = \textcolor{red}{''' +
            f'{vd["el_count"]:.4f}' +
            r'''} \mathrm{\ days}
        \end{align*}
        '''
    )
    return str


# ##### Time in care #####
def table_time_in_care_coeffs(vd):
    """
    Table of coefficients for the time in residential care model.

    The unicode characters \U00002002 are used to fudge right-alignment
    of the values by providing an extra space in front of coefficients
    with fewer digits before the decimal point.
    """
    str = (
        r'''
        | mRS | Age over 70 | Age not over 70 |
        | --- | --- | --- |
        | 0 | ''' +
            f'\U00002002{100.0*vd["perc_care_home_over70"][0]:.4f}' + \
            r'''\% | ''' + \
            f'\U00002002{100.0*vd["perc_care_home_not_over70"][0]:.4f}'
            + r'''\%
        | 1 | ''' +
            f'\U00002002{100.0*vd["perc_care_home_over70"][1]:.4f}' + \
            r'''\% | ''' + \
            f'\U00002002{100.0*vd["perc_care_home_not_over70"][1]:.4f}'
            + r'''\%
        | 2 | ''' +
            f'\U00002002{100.0*vd["perc_care_home_over70"][2]:.4f}' + \
            r'''\% | ''' + \
            f'\U00002002{100.0*vd["perc_care_home_not_over70"][2]:.4f}'
            + r'''\%
        | 3 | ''' +
            f'{100.0*vd["perc_care_home_over70"][3]:.4f}' + \
            r'''\% | ''' + \
            f'\U00002002{100.0*vd["perc_care_home_not_over70"][3]:.4f}'
            + r'''\%
        | 4 | ''' +
            f'{100.0*vd["perc_care_home_over70"][4]:.4f}' + \
            r'''\% | ''' + \
            f'{100.0*vd["perc_care_home_not_over70"][4]:.4f}'
            + r'''\%
        | 5 | ''' +
            f'{100.0*vd["perc_care_home_over70"][5]:.4f}' + \
            r'''\% | ''' + \
            f'{100.0*vd["perc_care_home_not_over70"][5]:.4f}' + r'''\%
        '''
        )
    return str


def table_time_in_care_coeffs_dicho(vd):
    """
    Table of coefficients for the time in residential care model.

    This uses the first and final rows of the table for the
    individual mRS model, with some re-labelling.

    The unicode characters \U00002002 are used to fudge right-alignment
    of the values by providing an extra space in front of coefficients
    with fewer digits before the decimal point.
    """
    str = (
        r'''
        | Outcome | Age over 70 | Age not over 70 |
        | --- | --- | --- |
        | Independent | ''' +
            f'\U00002002{100.0*vd["perc_care_home_over70"][0]:.4f}' + \
            r'''\% | ''' + \
            f'\U00002002{100.0*vd["perc_care_home_not_over70"][0]:.4f}'
            + r'''\%
        | Dependent | ''' +
            f'{100.0*vd["perc_care_home_over70"][5]:.4f}' + \
            r'''\% | ''' + \
            f'{100.0*vd["perc_care_home_not_over70"][5]:.4f}' + r'''\%
        '''
        )
    return str


def tic_generic():
    """Model for time spent in residential care."""
    str = (
        r'''
        \begin{equation}\tag{22}
        \mathrm{Count (years)} =
        95\% \times c \times \mathrm{years}
        \end{equation}
        '''
    )
    return str


def tic(vd):
    """
    Model for time spent in residential care,
    with symbols replaced with variables from the calculations.
    """
    if vd["age"] > 70:
        perc = vd["perc_care_home_over70"][vd["mrs"]]
    else:
        perc = vd["perc_care_home_not_over70"][vd["mrs"]]
    str = (
        r'''
        \begin{align*}
        \mathrm{Count (years=\textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][0]:.2f}' +
        r'''})} &=
        95\% \times \textcolor{Fuchsia}{''' +
        f'{100.0*perc:.4f}' +
        r'''\%} \times \textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][0]:.2f}' +
        r'''} \\
        &= \textcolor{red}{''' +
        f'{vd["care_years"]:.4f}' +
        r'''} \mathrm{\ years}
        \end{align*}
        '''
    )
    return str


# ##### Discounted resource use #####
def count_yeari_generic():
    """
    The amount of resource use in year i, found by taking the
    difference between cumulative resource uses in year i and i-1.
    """
    str = (
        r'''
        \begin{equation*}\tag{23}
        \mathrm{Count}_i =
        \mathrm{Count}(\mathrm{years}=i) -
        \mathrm{Count}(\mathrm{years}=[i-1])
        \end{equation*}
        '''
    )
    return str


def discounted_resource_generic(vd):
    """Converting resource use to discounted resource use."""
    str = (
        r'''
        \begin{equation*}\tag{24}
        D_i = \mathrm{Count}_i \times \frac{1}{\left(
            1 + ''' +
            f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
            r'''\right)^{i - 1}
        }
        \end{equation*}
        '''
    )
    return str


def discounted_resource_total_generic():
    """Sum discounted resources in all years to get total use."""
    str = (
        r'''
        \begin{equation*}\tag{25}
        D =
        c \times \displaystyle\sum_{i=1}^{m}
        D_i
        \end{equation*}
        '''
    )
    return str


def table_cost_factors_1(vd):
    """
    Table of coefficients for converting resource use to cost.

    Table is split into two parts for use with columns.
    """
    str = (
        r'''
        | Category | Cost factor $c$ |
        | --- | --- |
        | A&E | ''' + f'£{vd["cost_ae_gbp"]:.2f}' + r'''|
        | Time in care | ''' + \
            f'£{vd["cost_residential_day_gbp"]:.2f}' + r''' $\times$ 365 |
        '''
        )
    return str


def table_cost_factors_2(vd):
    """
    Table of coefficients for converting resource use to cost.

    Table is split into two parts for use with columns.
    """
    str = (
        r'''
        | Category | Cost factor $c$ |
        | --- | --- |
        | Non-elective bed days | ''' + \
            f'£{vd["cost_non_elective_bed_day_gbp"]:.2f}' + r'''|
        | Elective bed days | ''' + \
            f'£{vd["cost_elective_bed_day_gbp"]:.2f}' + r'''|
        '''
        )
    return str


def build_table_str_resource_count(
        counts_years, counts_i, discounted_i, discounted_sum
        ):
    """
    Table of resource use in each year up to the median survival year.

    For each year, add another row to the table.
    If the table is long, cut out the middle and replace with "...".
    """
    # ----- Function for tables -----
    # Set up header:
    table_rows = (
        r'''
        | Year | $\mathrm{Count}(\mathrm{years})$ | ''' +
        r'''$\mathrm{Count}_i$ | Discounted use |
        | --- | --- | --- | --- |
        '''
    )

    max_year = len(counts_i)+1
    # When the max_year is large, end up with a hugely long table.
    # Instead only show the first four and final four rows,
    # with a separating row of "..." in the middle.
    # Set the conditions for the rows to skip:
    if max_year > 10:
        # Long table:
        skip_min = 5
        skip_max = max_year - 5
    else:
        # Table is short enough that we can show the whole thing:
        # Set to values we'll never reach:
        skip_min = max_year + 10
        skip_max = max_year + 10

    for i, year in enumerate(range(1, max_year)):
        if year < skip_min or year > skip_max:
            # Valid entry, so add a row of values to the table:
            row = r'''| ''' + f'{year}' + r''' | ''' + \
                f'{counts_years[i]:.4f}' +\
                r''' | ''' + f'{counts_i[i]:.4f}' + r''' | ''' +\
                f'{discounted_i[i]:.4f}' + r''' |
        '''
            # ^ don't move these quote marks!!!
            # it looks silly but is necessary for the markdown table,
            # so that each row starts on a new line but is not indented.
            table_rows += row
        else:
            # Either do nothing, or...
            if year == skip_min:
                # Add this row of ... to the table:
                table_rows += r'''| ... | ... | ... | ... |
        '''
        # ^ don't move these quote marks either!!
    # Add a final row to show the sum of the discounted resource values:
    table_rows += r'''| | | Sum: | ''' + f'{discounted_sum:.4f}' + r'''|'''
    return table_rows


def discounted_resource(vd, count_i, year, D_i):
    """
    Convert resource to discounted resource for year i,
    with symbols replaced with variables from the calculations.
    """
    str = (
        r'''
        \begin{align*}
        D_{\textcolor{Fuchsia}{''' +
        f'{year}' +
        r'''}} &= \textcolor{red}{''' +
        f'{count_i:.4f}' +
        r'''} \times \frac{1}{\left(
            1 + ''' +
            f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
            r'''\right)^{\textcolor{Fuchsia}{''' +
            f'{year}' +
            r'''} - 1}} \\
        &= \textcolor{red}{''' +
        f'{D_i:.4f}' + r'''}
        \end{align*}
        '''
    )
    return str


def discounted_cost(vd, discounted_sum, cost_str, discounted_cost_str,
                    care=0):
    """
    Convert discounted resource use to the cost of this use,
    with symbols replaced with variables from the calculations.
    """
    if care != 0:
        extra_str = r''' \times 365'''
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        D &= ''' +
        f'£{vd[cost_str]:.2f}' +
        extra_str +
        r''' \times \textcolor{red}{''' +
        f'{discounted_sum:.4f}' +
        r'''} \\
        &= \textcolor{red}{''' +
        f'£{vd[discounted_cost_str]:.2f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


# #####################################################################
# ####################### Cost-effectiveness ##########################
# #####################################################################

def cost_effectiveness(vd, qaly, cost, total):
    """
    Example of calculating net benefit in cost for this QALY and
    associated cost that are associated with a change in outcome.
    """
    str = (
        r'''
        \begin{equation*}
        \left(''' +
        f'£{vd["wtp_qaly_gpb"]:.0f}' +
        r'''\times \textcolor{red}{''' +
        f'{qaly:.4f}' +
        r'''}\right) + \textcolor{red}{''' +
        f'£{cost:.0f} ' +
        r'''} = \textcolor{red}{''' +
        f'£{total:.0f}' +
        r'''}
        \end{equation*}
        '''
    )
    return str
