"""
Store all of the LaTeX formulae that will be printed in the demo.
Each formula is pretty bulky and throws up lots of python linting
errors, so they've been banished to this file for easier reading
of the container scripts.
"""
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
        | mRS | mRS coefficient | Mean age coefficient|
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
    str = r'''S_1 = 1 - P_{1}'''
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
        f'{vd["LP_yr1"]:.2f}' +
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
        f'{vd["LP_yr1"]:.2f}' +
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
        \begin{equation}\tag{3}
        H_t = \frac{e^{LP_{\mathrm{H}}}(e^{\gamma t} - 1)}{\gamma}
        \end{equation}
        '''
        )
    return str


def lp_yrn_generic():
    str = (
        r'''
        \begin{equation}\tag{4}
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
        \begin{equation}\tag{5}
        F_{t} = 1 - (1-H_t)\times(1-P_{1})
        \end{equation}
        '''
        )
    return str


def survival_generic():
    str = (
        r'''S_t = 1 - F_t'''
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
        f'{vd["LP_yrn"]:.2f}' +
        r'''}
        \end{align*}'''
    )
    return str


def hazard_yrn(vd, time_input_yr, H_t):
    if H_t > 1.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            H_{\textcolor{red}{''' + f'{time_input_yr}' + r'''}}
            &> \textcolor{red}{100\%} '''
        )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        H_{\textcolor{red}{''' + f'{time_input_yr}' + r'''}}
        &= \frac{1}{\gamma} \cdot
        e^{
        \textcolor{red}{
        ''' +
        f'{vd["LP_yrn"]:.2f}' +
        r'''
        }} \cdot \left(e^{\gamma \times [\textcolor{red}{''' +
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
            F_{\textcolor{red}{''' + f'{time_input_yr}' + r'''}}
            &> \textcolor{red}{100\%} ''')
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        F_{\textcolor{red}{''' + f'{time_input_yr}' + r'''}} &= '''
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
            S_{\textcolor{red}{''' + f'{time_input_yr}' + r'''}}
            &< \textcolor{red}{0\%} '''
            )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        S_{\textcolor{red}{''' + f'{time_input_yr}' + r'''}}
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
        \begin{equation}\tag{6}
        P_2 = 1 - \exp{(P_1 - F_2)}
        \end{equation}
        '''
        )
    return str


def pDeath_yrn_generic():
    str = (
        r'''
        \begin{equation}\tag{6}
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
            P_{\textcolor{red}{''' + f'{time}' + r'''}}
            &= \textcolor{red}{0\%}'''
            )
    # Highlight other weird cases:
    elif P1 > 1.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            P_{\textcolor{red}{''' + f'{time}' + r'''}}
            &> \textcolor{red}{100\%}'''
            )
    elif P1 < 0.0:
        # Add an extra line showing an inequality.
        extra_str = (
            r''' \\
            P_{\textcolor{red}{''' + f'{time}' + r'''}}
            &< \textcolor{red}{0\%}'''
            )
    else:
        extra_str = ''
    str = (
        r'''
        \begin{align*}
        P_{\textcolor{red}{''' + f'{time}' + r'''}} &=
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
        S_{\textcolor{red}{''' +
        f'{time}' + r'''}} =  \textcolor{red}{''' +
        f'{100.0*survival:.2f}' + r'''\%}
        \end{equation*}
        '''
    )
    return str


def prob_prime_generic():
    str = (
        r'''
        \begin{equation*}
        P^{\prime} = \frac{1 + P}{1 + P_1} - 1
        \end{equation*}
        '''
    )
    return str


def death_time_case1_generic():
    str = (
        r'''
        \begin{equation*}
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
        \begin{equation*}
        t_{\mathrm{death}}(P) =
        \frac{\log{(1 - P)}}
        {\log{(1 - P_1)}\cdot 365}
        \end{equation*}
        '''
    )
    return str
