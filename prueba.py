import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

path = 'Accidentes_Vehiculares_NYC_2013-2019.csv'

st.title("Accidentes de vehículos motorizados en Nueva York 2012-2019")
st.markdown("### Este dashboard analiza los accidentes vehiculares en Nueva York")

@st.cache(persist=True)
def cargar_data(nrows):
    data = pd.read_csv(path, nrows=nrows, parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time':'fecha/hora'}, inplace=True)
    return data

data = cargar_data(100000)
original_data = data

st.header("Lugares donde se ocasionan cierto número de heridos")
injured_people = st.slider("Número de heridos", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how="any"))


st.header("Accidentes que ocurren durante cierta hora del día")
hour = st.slider("Hora a analizar", 0, 23)
data['fecha/hora'] = pd.to_datetime(data['fecha/hora'], format='%m/%d/%Y %H:%M', errors='coerce')) 
data = data[data['fecha/hora'].dt.hour == hour]
num_acc = len(data)

st.markdown("Número de accidentes vehiculares entre %i:00 y %i:00" % (hour, (hour + 1) % 24) + " = " + "**_" + str(num_acc) + "_**")
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50},
    layers=[pdk.Layer("HexagonLayer",
                    data=data[['fecha/hora','latitude','longitude']],
                    get_position=['longitude','latitude'],
                    radius=100,
                    extruded=True,
                    pickeable=True,
                    elevation_scale=4,
                    elevation_range=[0,1000])]
))

st.subheader("Breakdown por minuto entre %i:00 and %i:00" % (hour, (hour +1) %24))
filtered = data[
    (data['fecha/hora'].dt.hour >= hour) & (data['fecha/hora'].dt.hour < (hour+1))]

hist = np.histogram(filtered['fecha/hora'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute','crashes'], height=400)
st.write(fig)

st.header("Top 5 calles más peligrosas por tipo de afectado")
select = st.selectbox('Tipo de persona afectada', ['Pedestrians','Cyclists','Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:5].reset_index(drop=True))

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name","injured_cyclists"]].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:5].reset_index(drop=True))

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name","injured_motorists"]].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:5].reset_index(drop=True))


if st.checkbox("Mostrar datos sin procesar", False):
    st.subheader('Datos')
    st.write(data)
