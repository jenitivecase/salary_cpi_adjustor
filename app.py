import datetime
import pandas as pd
import math
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st

cpi = pd.read_csv('CPI_data.csv')
cpi = pd.melt(cpi, id_vars='Year')
cpi['Year'] = list(map(str, cpi['Year']))
cpi['date_temp'] = cpi['Year'].str.cat(cpi['variable'], sep='-')
cpi['Date'] = list(map(lambda x: datetime.datetime.strptime(x, '%Y-%b'), cpi['date_temp']))

st.title('CPI-Adjusted Salary Graph')
st.markdown('Input five recent salaries and their corresponding months, and see what your real compensation was like.')
st.markdown('Starting values are taken from [median individual income stats](https://dqydj.com/individual-income-by-year/).')

money_now = st.sidebar.number_input('Current salary:', value=44225)

run = st.sidebar.button('Update results')
date1 = st.sidebar.date_input('Salary date 1:',
                              value=datetime.date(2000, 1, 1),
                              min_value=datetime.date(1913, 1, 1),
                              max_value=datetime.date(2022, 8, 1))
money1 = st.sidebar.number_input('Salary 1:', value=25000)

date2 = st.sidebar.date_input('Salary date 2:',
                              value=datetime.date(2005, 1, 1),
                              min_value=datetime.date(1913, 1, 1),
                              max_value=datetime.date(2022, 8, 1))
money2 = st.sidebar.number_input('Salary 2:', value=28300)

date3 = st.sidebar.date_input('Salary date 3:',
                              value=datetime.date(2010, 1, 1),
                              min_value=datetime.date(1913, 1, 1),
                              max_value=datetime.date(2022, 8, 1))
money3 = st.sidebar.number_input('Salary 3:', value=30324)

date4 = st.sidebar.date_input('Salary date 4:',
                              value=datetime.date(2015, 1, 1),
                              min_value=datetime.date(1913, 1, 1),
                              max_value=datetime.date(2022, 8, 1))
money4 = st.sidebar.number_input('Salary 4:', value=35000)

date5 = st.sidebar.date_input('Salary date 5:',
                              value=datetime.date(2020, 1, 1),
                              min_value=datetime.date(1913, 1, 1),
                              max_value=datetime.date(2022, 8, 1))
money5 = st.sidebar.number_input('Salary 5:', value=43894)


if run:
    data = pd.DataFrame(data={'date': [datetime.datetime(2022, 7, 1), date1, date2, date3, date4, date5]},
                        dtype='datetime64[M]')
    data['salary'] = [money_now, money1, money2, money3, money4, money5]
    data = data.dropna()
    data['date'] = data['date'].dt.to_period('M').dt.to_timestamp()
    data = data.sort_values('date', axis=0)

    # ref_date = data['date'].min()
    ref_date = datetime.datetime(2022, 7, 1)
    ref = cpi[cpi['Date'] == ref_date]['value'].values[0]

    def adjust_w_cpi(month: datetime, amt: float, ref: float = ref, lookup: pd.DataFrame = cpi):
        match = lookup['Date'] == month
        value = lookup['value'][match].values[0]
        if math.isnan(value):
            out = amt
        else:
            # out = ((amt * value) / ref)
            out = (ref/value)*amt
        return out


    data['adjusted'] = list(map(adjust_w_cpi, data['date'], data['salary']))
    data['pretty_date'] = list(map(lambda x: datetime.datetime.strftime(x, '%b %Y'), data['date']))

    fig = go.Figure(go.Scatter(x=data['date'], y=data['adjusted'],
                               text=data['salary'],
                               hovertemplate=
                               '<b>Adjusted Salary Trend Line<br>' +
                               '%{x}</b>' +
                               '<br>Raw Salary: $%{text:.0f}' +
                               '<br>Adjusted Salary: $%{y:.0f}'
                               ))
    fig.add_scatter(x=data['date'], y=data['salary'],
                    text=data['salary'],
                    hovertemplate=
                    '<b>Raw Salary Trend Line<br>' +
                    '%{x}</b>' +
                    '<br>Raw Salary: $%{text:.0f}' +
                    '<br>Adjusted Salary: $%{y:.0f}'
                    )
    fig.update_layout(template='plotly_white',
                      showlegend=False)

    # st.markdown('Salaries converted to July 2022 dollars.')
    st.markdown('Salaries converted to '+datetime.datetime.strftime(ref_date, '%b %Y')+' dollars.')
    st.plotly_chart(fig)
