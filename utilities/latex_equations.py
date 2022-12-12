"""
Store all of the LaTeX formulae that will be printed in the demo.
Each formula is pretty bulky and throws up lots of python linting
errors, so they've been banished to this file for easier reading
of the container scripts.
"""

# #####################################################################
# ####################### Container: mortality ########################
# #####################################################################

def table_lg_coeffs(vd):
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


def pDeath_yr1_generic():
    str = (
        r'''
        \begin{equation}\tag{1}
        P_{1} = \frac{1}{1+e^{-LP_{1}}}
        \end{equation}
        '''
        )
    return str


def lp_yr1_generic():
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


def survival_yr1_generic():
    str = (
        r'''
        \begin{equation}\tag{3}
        S_1 = 1 - P_{1}
        \end{equation}
        '''
    )
    return str


def lp_yr1(vd):
    str = (
        r'''\begin{align*}
        LP_{1} =&''' +
        # alpha
        f'{vd["lg_coeffs"][0]}' + r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["lg_coeffs"][1]}' + r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' + r'''}-\textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''}]\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["lg_coeffs"][2]}' + r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' + r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 3rd coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["lg_coeffs"][3+vd["mrs"]]}' + r'''} \times \textcolor{red}{''' +
        f'{vd["mrs"]}' + r'''}\right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["LP_yr1"]:.4f}' +
        r'''}
        \end{align*}'''
        )
    return str


def prob_yr1(vd):
    str = (
        r'''
        \begin{align*}
        P_{1} &= \frac{1}{1+e^{-
        \textcolor{red}{
        ''' +
        f'{vd["LP_yr1"]:.4f}' +
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
    return str


def survival_yr1(S_t, P_t):
    # Line with values in percent:
    # & = 1 - \textcolor{red}{''' +
    # f'{100.0*P_t:.2f}' + r'''\%} \\
    if S_t < 0.0:
        # Add an extra line showing an inequality.
        extra_str = r''' \\ S_1 &< \textcolor{red}{0\%} '''
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        S_1
        & = 1 - \textcolor{red}{''' +
        f'{P_t:.4f}' + r'''} \\
        & = \textcolor{red}{''' +
        f'{100.0*S_t:.2f}' + r'''\%}''' +
        extra_str + r'''
        \end{align*}
        '''
        )
    return str


def table_gz_coeffs(vd):
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


def hazard_yrn_generic():
    str = (
        r'''
        \begin{equation}\tag{4}
        H_t = \frac{e^{LP_{\mathrm{H}}}(e^{\gamma t} - 1)}{\gamma}
        \end{equation}
        '''
        )
    return str


def lp_yrn_generic():
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


def FDeath_yrn_generic():
    str = (
        r'''
        \begin{equation}\tag{6}
        F_{t} = 1 - (1-H_t)\times(1-P_{1})
        \end{equation}
        '''
        )
    return str


def survival_generic():
    str = (
        r'''
        \begin{equation}\tag{7}
        S_t = 1 - F_t
        \end{equation}
        '''
        )
    return str


def lp_yrn(vd):
    str = (
        r'''
        \begin{align*}
        LP_{\mathrm{H}} =&''' +
        # alpha
        f'{vd["gz_coeffs"][0]}' + r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["gz_coeffs"][1]}' + r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' + r'''}-''' +
        f'{vd["gz_mean_age"]}' +
        r''']\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["gz_coeffs"][2]}' + r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' + r'''}^{2}-''' +
        f'{vd["gz_mean_age"]}' +
        r'''^{2}]\right) + & \mathrm{age}^{2} \\''' +
        # 3rd coeff
        r'''& \left(''' +
        f'{vd["gz_coeffs"][3]}' + r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' + r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 4th coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["gz_coeffs"][4+vd["mrs"]]}' + r'''} \times \textcolor{red}{''' +
        f'{vd["mrs"]}' + r'''} \times [\textcolor{red}{''' +
        f'{vd["age"]}' + r'''}-''' +
        f'{vd["gz_mean_age"]}' +
        r''']\right) +
        & (\mathrm{mRS}\times\mathrm{age}) \\''' +
        # 5th coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["gz_coeffs"][10+vd["mrs"]]}' + r'''} \times \textcolor{red}{''' +
        f'{vd["mrs"]}' + r'''}\right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["LP_yrn"]:.4f}' +
        r'''}
        \end{align*}'''
    )
    return str


def hazard_yrn(vd, time_input_yr, H_t):
    if H_t > 1.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            H_{\textcolor{Fuchsia}{''' + f'{time_input_yr}' + r'''}}
            &> \textcolor{red}{100\%} '''
        )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        H_{\textcolor{Fuchsia}{''' + f'{time_input_yr}' + r'''}}
        &= \frac{1}{\gamma} \cdot
        e^{
        \textcolor{red}{
        ''' +
        f'{vd["LP_yrn"]:.4f}' +
        r'''
        }} \cdot \left(e^{\gamma \times [\textcolor{Fuchsia}{''' +
        f'{time_input_yr}' + r'''}-1] \times 365} - 1 \right) \\
        &= \textcolor{red}{
        ''' +
        f'{100.0*H_t:.2f}' +
        r'''
        \%}''' +
        extra_str + r'''
        \end{align*}
        '''
    )
    return str


def FDeath_yrn(H_t, P_yr1, P_t, time_input_yr):
    # Line with values in percent:
    # 1 - (1-\textcolor{red}{'''
    # + f'{100.0*H_t:.2f}' + r'''\%})\times(1-\textcolor{red}{'''
    # + f'{100.0*P_yr1:.2f}' + r'''\%}) \\
    if P_t > 1.0:
        # Add an extra line showing an inequality.
        extra_str = (r''' \\
            F_{\textcolor{Fuchsia}{''' + f'{time_input_yr}' + r'''}}
            &> \textcolor{red}{100\%} ''')
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        F_{\textcolor{Fuchsia}{''' + f'{time_input_yr}' + r'''}} &= '''
        r'''1 - (1-\textcolor{red}{'''
        + f'{H_t:.4f}' + r'''})\times(1-\textcolor{red}{'''
        + f'{P_yr1:.4f}' + r'''}) \\
        &= \textcolor{red}{'''
        + f'{100.0*P_t:.2f}' + r'''\%}''' +
        extra_str + r'''
        \end{align*}
        '''
    )
    return str


def survival(S_t, P_t, time_input_yr):
    # Line with values in percent:
    # & = 1 - \textcolor{red}{''' +
    # f'{100.0*P_t:.2f}' + r'''\%} \\
    if S_t < 0.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            S_{\textcolor{Fuchsia}{''' + f'{time_input_yr}' + r'''}}
            &< \textcolor{red}{0\%} '''
            )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        S_{\textcolor{Fuchsia}{''' + f'{time_input_yr}' + r'''}}
        & = 1 - \textcolor{red}{''' +
        f'{P_t:.4f}' + r'''} \\
        & = \textcolor{red}{''' +
        f'{100.0*S_t:.2f}' + r'''\%}''' +
        extra_str + r'''
        \end{align*}
        '''
        )
    return str


def pDeath_yr2_generic():
    str = (
        r'''
        \begin{equation}\tag{8}
        P_2 = 1 - \exp{(P_1 - F_2)}
        \end{equation}
        '''
        )
    return str


def pDeath_yrn_generic():
    str = (
        r'''
        \begin{equation}\tag{9}
        P_t = 1 - \exp{(F_{t-1} - F_{t})}
        \end{equation}
        '''
        )
    return str


def pDeath_yrn(P1, F0, F1, time, S1):
    # Highlight if survival is below 0%.
    if S1 <= 0.0:
        # Survival is zero, so probability is zero.
        extra_str = (
            r''' \\
            P_{\textcolor{Fuchsia}{''' + f'{time}' + r'''}}
            &= \textcolor{red}{0\%}'''
            )
    # Highlight other weird cases:
    elif P1 > 1.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            P_{\textcolor{Fuchsia}{''' + f'{time}' + r'''}}
            &> \textcolor{red}{100\%}'''
            )
    elif P1 < 0.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            P_{\textcolor{Fuchsia}{''' + f'{time}' + r'''}}
            &< \textcolor{red}{0\%}'''
            )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        P_{\textcolor{Fuchsia}{''' + f'{time}' + r'''}} &=
        1 - \exp{(
        \textcolor{red}{''' + f'{F0:.4f}' + r'''}
        -
        \textcolor{red}{''' + f'{F1:.4f}' + r'''}
        )} \\
        &= \textcolor{red}{''' + f'{100*P1:.2f}' + r'''\%}''' +
        extra_str + r'''
        \end{align*}
        '''
        )
    return str


def survival_display(time, survival):
    str = (
        r'''
        \begin{equation*}
        S_{\textcolor{Fuchsia}{''' +
        f'{time}' + r'''}} =  \textcolor{red}{''' +
        f'{100.0*survival:.2f}' + r'''\%}
        \end{equation*}
        '''
    )
    return str


def prob_prime_generic():
    str = (
        r'''
        \begin{equation*}\tag{10}
        P^{\prime} = \frac{1 + P}{1 + P_1} - 1
        \end{equation*}
        '''
    )
    return str


def death_time_case1_generic():
    str = (
        r'''
        \begin{equation*}\tag{11}
        t_{\mathrm{death}}(P) = 1 + 
        \frac{1}{\gamma \times 365} \cdot
        \log\left(
            \frac{P^{\prime} \times \gamma}{
                \exp{(LP_\mathrm{H})}} + 1.0
            \right)      
        \end{equation*}
        '''
    )
    return str


def death_time_case2_generic():
    str = (
        r'''
        \begin{equation*}\tag{12}
        t_{\mathrm{death}}(P) =
        \frac{\log{(1 - P)}}
        {\log{(1 - P_1)}}\times\frac{1}{365}
        \end{equation*}
        '''
    )
    return str


def Pyr1_display(P_yr1):
    str = (
        r'''
        P_{1} =  \textcolor{red}{''' +
        f'{100.0*P_yr1:.2f}' + r'''\%}
        '''
    )
    return str


def LPyrn_display(LP_yrn):
    str = (
        r'''
        LP_{H} =  \textcolor{red}{''' +
        f'{LP_yrn:.4f}' + r'''}
        '''
    )
    return str


def gammaH_display(gamma):
    str = (
        r'''
        \gamma = ''' + f'{gamma}' + r'''
        '''
    )
    return str


def prob_prime(p, Pprime, P_yr1):
    str = (
        r'''
        \begin{align*}
        P^{\prime} &= \frac{1 + \textcolor{Fuchsia}{''' +
        f'{p:.4f}' + r'''}}{1 + \textcolor{red}{''' +
        f'{P_yr1:.4f}' + r'''}} - 1 \\
        &= \textcolor{red}{''' + f'{100.0*Pprime:.2f}' + r'''\%}
        \end{align*}
        '''
    )
    return str


def death_time_case2(tDeath, p, P_yr1):
    str = (
        r'''
        \begin{align*}
        t_{\mathrm{death}}(\textcolor{Fuchsia}{''' + 
        f'{100.0*p:.0f}' + r'''\%}) &=
        \frac{\log{(1 - \textcolor{Fuchsia}{''' +
        f'{p:.4f}' + r'''})}}
        {\log{(1 - \textcolor{red}{''' + 
        f'{P_yr1:.4f}' + r'''})}}\times \frac{1}{365} \\
        &= \textcolor{red}{''' + 
        f'{tDeath:.2f}' + r'''} \mathrm{\ years}
        \end{align*}
        '''
    )
    return str


def death_time_case1(
        tDeath, prob_prime, LP_yrn, gamma, P):
    str = (
        r'''
        \begin{align*}
        t_{\mathrm{death}}(\textcolor{Fuchsia}{''' +
        f'{100.0*P:.0f}' + r'''\%}) &= 1 +
        \frac{1}{''' +
        f'{gamma}' + r''' \times 365} \cdot
        \log\left(
            \frac{\textcolor{red}{''' +
            f'{prob_prime:.4f}' + r'''}\times ''' +
            f'{gamma}' + r'''}{
                \exp{(\textcolor{red}{''' +
                f'{LP_yrn:.4f}' + r'''})}} + 1.0
            \right) \\
        &= \textcolor{red}{''' + 
        f'{tDeath:.2f}' + r'''} \mathrm{\ years}
        \end{align*}
        '''
    )
    return str


def life_expectancy(life_expectancy, tDeath_med, age):
    str = (
        r'''
        \begin{align*}
        \textcolor{red}{''' + f'{age}' + r'''} +
        \textcolor{red}{''' + f'{tDeath_med:.2f}' + r'''} &=
        \textcolor{red}{''' + f'{life_expectancy:.2f}' +
        r'''} \mathrm{\ years} \\
        &\approx \textcolor{red}{''' +
        f'{life_expectancy // 1:.0f}' + r'''} \mathrm{\ years\ }
        \textcolor{red}{''' +
        f'{12*(life_expectancy % 1):.0f}' + r'''} \mathrm{\ months}
        \end{align*}
        '''
    )
    return str


# #####################################################################
# ######################### Container: QALYs ##########################
# #####################################################################

def discounted_qalys_generic():
    str = (
        r'''
        \begin{equation*}\tag{13}
        Q = u +
        \frac{u}{1+d} \times
        \frac{1 - (1+d)^{-[\mathrm{yrs}-1]}}{1 - (1+d)^{-1}}
        \end{equation*}
        '''
    )
    return str


def discounted_qalys(vd):
    str = (
        r'''
        \begin{align*}
        Q &= \textcolor{Fuchsia}{''' +
        f'{vd["utility_list"][vd["mrs"]]}' + r'''} +
        \frac{\textcolor{Fuchsia}{''' +
        f'{vd["utility_list"][vd["mrs"]]}' + r'''}}{1+''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r'''} \times \frac{1 - (1+''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r''')^{-[\textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][vd["mrs"], 0]:.2f}' +
        r'''}-1]}}{1 - (1+''' +
        f'{vd["discount_factor_QALYs_perc"]/100.0:.4f}' +
        r''')^{-1}} \\
        &= \textcolor{red}{''' + f'{vd["qalys"][vd["mrs"]]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


# #####################################################################
# ####################### Container: resources ########################
# #####################################################################

def table_ae_coeffs(vd):
    str = (
        r'''
        | Description | Coefficient |
        | --- | --- |
        | Constant $\alpha_{\mathrm{AE}}$ | ''' + \
            f'{vd["A_E_coeffs"][0]}' + r'''|
        | Adjusted age | ''' + f'{vd["A_E_coeffs"][1]}' + r'''|
        | Sex | ''' + f'{vd["A_E_coeffs"][2]}' + r'''|
        | $\gamma_{\mathrm{AE}}$ (gamma) | ''' + \
            f'{vd["A_E_coeffs"][3]}' + r'''|
        '''
        )
    return str


def table_ae_mrs_coeffs(vd):
    str = (
        r'''
        | mRS | mRS coefficient | Mean age coefficient |
        | --- | --- | --- |
        | 0 | ''' + f'{vd["A_E_mRS"][0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | 1 | ''' + f'{vd["A_E_mRS"][1]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][1]}' + r'''|
        | 2 | ''' + f'{vd["A_E_mRS"][2]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][2]}' + r'''|
        | 3 | ''' + f'{vd["A_E_mRS"][3]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][3]}' + r'''|
        | 4 | ''' + f'{vd["A_E_mRS"][4]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][4]}' + r'''|
        | 5 | ''' + f'{vd["A_E_mRS"][5]}'  + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def ae_count_generic():
    # str = (
    #     r'''
    #     \begin{equation}\tag{13}
    #     \mathrm{Count} =
    #     # -
    #     # \log{\left[
    #             # \exp({-
    #     \exp{
    #         \left(\gamma_\mathrm{AE}
    #         \times 
    #         LP_{\mathrm{AE}}\right)
    #         }
    #     \times 
    #     \mathrm{yrs}^{\gamma_{\mathrm{AE}}}
    #             # })
    #     # \right] }
    #     \end{equation}
    #     '''
    # )
    str = (
        r'''
        \begin{equation}\tag{14}
        \mathrm{Count} =
        \exp{
            \left(\gamma_\mathrm{AE}
            \times 
            LP_{\mathrm{AE}}\right)
            }
        \times 
        \mathrm{yrs}^{\gamma_{\mathrm{AE}}}
        \end{equation}
        '''
    )
    return str


# def ae_lambda_generic():
#     str = (
#         r'''
#         \begin{equation}\tag{14}
#         \Lambda_\mathrm{AE} =
#         \exp{\left(\gamma_\mathrm{AE} \times LP_{\mathrm{AE}}\right)}
#         \end{equation}
#         '''
#     )
#     return str


def ae_lp_generic():
    str = (
        r'''
        \begin{equation}\tag{15}
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
    str = (
        r'''
        \begin{align*}
        LP_{\mathrm{AE}} =&''' +
        # alpha
        f'{vd["A_E_coeffs"][0]}' + r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["A_E_coeffs"][1]}' + r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' + r'''}-\textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''}]\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["A_E_coeffs"][2]}' + r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' + r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 3rd coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["A_E_mRS"][vd["mrs"]]}' + r'''}\right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["LP_A_E"]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


# def ae_lambda(vd):
#     str = (
#         r'''
#         \begin{align*}
#         \Lambda_\mathrm{AE} &=
#         \exp{\left(\textcolor{red}{''' +
#         f'{vd["A_E_coeffs"][3]}' + r'''}\times \textcolor{red}{''' +
#         f'{vd["LP_A_E"]:.4f}' + r'''}\right)} \\
#         &= \textcolor{red}{''' + f'{vd["lambda_A_E"]:.2f}' +
#         r'''}
#         \end{align*}
#         '''
#     )
#     return str


def median_survival_display(vd):
    str = (
        r'''
        \begin{equation*}
        \mathrm{yrs} = \textcolor{red}{''' + 
        f'{vd["survival_meds_IQRs"][vd["mrs"], 0]:.2f}' + r'''}
        \end{equation*}
        '''
        )
    return str


def ae_count(vd):
    str = (
        r'''
        \begin{align*}
        \mathrm{Count} &=
        \exp{
            \left( \textcolor{red}{''' +
            f'{vd["A_E_coeffs"][3]}' + r'''}
            \times \textcolor{red}{''' +
            f'{vd["LP_A_E"]:.4f}' + r'''} \right)
            }
        \times \textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][vd["mrs"], 0]:.2f}' + r'''}
        ^{\textcolor{red}{''' +
        f'{vd["A_E_coeffs"][3]}' + r'''}} \\
        &= \textcolor{red}{''' +
        f'{vd["A_E_count_list"][vd["mrs"]]:.4f}' + r'''}
        \mathrm{\ admissions}
        \end{align*}
        '''
    )
    return str


def table_nel_coeffs(vd):
    str = (
        r'''
        | Description | Coefficient |
        | --- | --- |
        | Constant $\alpha_{\mathrm{NEL}}$ | ''' + \
            f'{vd["NEL_coeffs"][0]}' + r'''|
        | Adjusted age | ''' + f'{vd["NEL_coeffs"][1]}' + r'''|
        | Sex | ''' + f'{vd["NEL_coeffs"][2]}' + r'''|
        | $\gamma_{\mathrm{NEL}}$ (gamma) | ''' + \
            f'{vd["NEL_coeffs"][3]}' + r'''|
        '''
        )
    return str


def table_nel_mrs_coeffs(vd):
    str = (
        r'''
        | mRS | mRS coefficient | Mean age coefficient |
        | --- | --- | --- |
        | 0 | ''' + f'{vd["NEL_mRS"][0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | 1 | ''' + f'{vd["NEL_mRS"][1]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][1]}' + r'''|
        | 2 | ''' + f'{vd["NEL_mRS"][2]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][2]}' + r'''|
        | 3 | ''' + f'{vd["NEL_mRS"][3]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][3]}' + r'''|
        | 4 | ''' + f'{vd["NEL_mRS"][4]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][4]}' + r'''|
        | 5 | ''' + f'{vd["NEL_mRS"][5]}'  + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def nel_bed_days_generic():
    str = (
        r'''
        \begin{equation}\tag{16}
        \mathrm{Count} =
            -\log{\left(
            \frac{1}{
                1+ [\mathrm{yrs}\times\exp{(-LP_\mathrm{NEL})} ] ^{
                    1/ \gamma_{\mathrm{NEL}}}
            }
            \right)}
        \end{equation}
        '''
    )
    return str


def nel_lp_generic():
    str = (
        r'''
        \begin{equation}\tag{17}
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
    str = (
        r'''
        \begin{align*}
        LP_{\mathrm{NEL}} =&''' +
        # alpha
        f'{vd["NEL_coeffs"][0]}' + r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["NEL_coeffs"][1]}' + r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' + r'''}-\textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''}]\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["NEL_coeffs"][2]}' + r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' + r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 3rd coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["NEL_mRS"][vd["mrs"]]}' + r'''} \right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["LP_NEL"]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


def nel_bed_days(vd):
    str = (
        r'''
        \begin{align*}
        \mathrm{Count} &=
            -\log{\left(
            \frac{1}{
                1+ [\textcolor{red}{''' +
                f'{vd["survival_meds_IQRs"][vd["mrs"], 0]:.2f}' +
                r'''} \times \exp{(-\textcolor{red}{''' +
                f'{vd["LP_NEL"]:.4f}' + r'''})} ]^{
                1/ \textcolor{red}{''' +
                f'{vd["NEL_coeffs"][3]}' +
                r'''}}}
            \right)} \\
            & = \textcolor{red}{''' +
            f'{vd["NEL_count_list"][vd["mrs"]]:.4f}' + r'''}
            \mathrm{\ days}
        \end{align*}
        '''
    )
    return str


def table_el_coeffs(vd):
    str = (
        r'''
        | Description | Coefficient |
        | --- | --- |
        | Constant $\alpha_{\mathrm{EL}}$ | ''' + \
            f'{vd["EL_coeffs"][0]}' + r'''|
        | Adjusted age | ''' + f'{vd["EL_coeffs"][1]}' + r'''|
        | Sex | ''' + f'{vd["EL_coeffs"][2]}' + r'''|
        | $\gamma_{\mathrm{EL}}$ (gamma) | ''' + \
            f'{vd["EL_coeffs"][3]}' + r'''|
        '''
        )
    return str

def table_el_mrs_coeffs(vd):
    str = (
        r'''
        | mRS | mRS coefficient | Mean age coefficient |
        | --- | --- | --- |
        | 0 | ''' + f'{vd["EL_mRS"][0]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][0]}' + r'''|
        | 1 | ''' + f'{vd["EL_mRS"][1]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][1]}' + r'''|
        | 2 | ''' + f'{vd["EL_mRS"][2]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][2]}' + r'''|
        | 3 | ''' + f'{vd["EL_mRS"][3]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][3]}' + r'''|
        | 4 | ''' + f'{vd["EL_mRS"][4]}' + r'''| ''' + \
            f'{vd["lg_mean_ages"][4]}' + r'''|
        | 5 | ''' + f'{vd["EL_mRS"][5]}'  + r'''| ''' + \
            f'{vd["lg_mean_ages"][5]}' + r'''|
        '''
        )
    return str


def el_bed_days_generic():
    str = (
        r'''
        \begin{equation}\tag{18}
        \mathrm{Count} =
            -\log{\left(
            \frac{1}{
                1+ [\mathrm{yrs} \times \exp{(-LP_\mathrm{EL})} ] ^{
                    1/ \gamma_{\mathrm{EL}}}
            }
            \right)}
        \end{equation}
        '''
    )
    return str


def el_lp_generic():
    str = (
        r'''
        \begin{equation}\tag{19}
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
    str = (
        r'''
        \begin{align*}
        LP_{\mathrm{EL}} =&''' +
        # alpha
        f'{vd["EL_coeffs"][0]}' + r''' + & \mathrm{constant} \\''' +
        # 1st coeff
        r'''& \left(''' +
        f'{vd["EL_coeffs"][1]}' + r'''\times [\textcolor{red}{''' +
        f'{vd["age"]}' + r'''}-\textcolor{Fuchsia}{''' +
        f'{vd["lg_mean_ages"][vd["mrs"]]}' +
        r'''}]\right) + & \mathrm{age} \\''' +
        # 2nd coeff
        r'''& \left(''' +
        f'{vd["EL_coeffs"][2]}' + r'''\times \textcolor{red}{''' +
        f'{vd["sex"]}' + r'''}\right) + & \mathrm{sex}^{*} \\''' +
        # 3rd coeff
        r'''& \left(\textcolor{Fuchsia}{''' +
        f'{vd["EL_mRS"][vd["mrs"]]}' + r'''} \right) & \mathrm{mRS} \\''' +
        # Next line, value equal to:
        r'''=& \textcolor{red}{''' +
        f'{vd["LP_EL"]:.4f}' +
        r'''}
        \end{align*}
        '''
    )
    return str


def el_bed_days(vd):
    str = (
        r'''
        \begin{align*}
        \mathrm{Count} &=
            -\log{\left(
            \frac{1}{
                1+ [\textcolor{red}{''' +
                f'{vd["survival_meds_IQRs"][vd["mrs"], 0]:.2f}' +
                r'''} \times \exp{(-\textcolor{red}{''' +
                f'{vd["LP_EL"]:.4f}' + r'''})} ]^{
                1/ \textcolor{red}{''' +
                f'{vd["EL_coeffs"][3]}' +
                r'''}}}
            \right)} \\
            & = \textcolor{red}{''' +
            f'{vd["EL_count_list"][vd["mrs"]]:.4f}' + r'''}
            \mathrm{\ days}
        \end{align*}
        '''
    )
    return str


def table_time_in_care_coeffs(vd):
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
            f'{100.0*vd["perc_care_home_not_over70"][4]:.4f}' + r'''\%
        | 5 | ''' + 
            f'{100.0*vd["perc_care_home_over70"][5]:.4f}' + \
            r'''\% | ''' + \
            f'{100.0*vd["perc_care_home_not_over70"][5]:.4f}' + r'''\%
        '''
        )
    return str


def tic_generic():
    str = (
        r'''
        \begin{equation}\tag{20}
        \mathrm{Count} =
        95\% \times c \times \mathrm{yrs}
        \end{equation}
        '''
    )
    return str


def tic(vd):
    if vd["age"] > 70:
        perc = vd["perc_care_home_over70"][vd["mrs"]]
    else:
        perc = vd["perc_care_home_not_over70"][vd["mrs"]]
    str = (
        r'''
        \begin{align*}
        \mathrm{Count} &=
        95\% \times \textcolor{Fuchsia}{''' + 
        f'{100.0*perc:.4f}' + r'''\%} \times \textcolor{red}{''' +
        f'{vd["survival_meds_IQRs"][vd["mrs"], 0]:.2f}' + r'''} \\
        &= \textcolor{red}{''' + 
        f'{vd["care_years_list"][vd["mrs"]]:.4f}' +r'''} \mathrm{\ years}
        \end{align*}
        '''
    )
    return str
