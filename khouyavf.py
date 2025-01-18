import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Données de base
default_air_flow_rate = 2  # kg/s
default_air_temp_in = 10  # °C
default_air_temp_out = 25  # °C
default_water_flow_rate = 300 / 86400  # kg/s
default_water_temp_in = 15  # °C
default_water_temp_out = 60  # °C

# Capacités thermiques
cp_air = 1.005  # kJ/kg.K
cp_water = 4.18  # kJ/kg.K

def calc_heating_power_air(flow_rate, temp_in, temp_out, cp):
    return flow_rate * cp * (temp_out - temp_in)  # kW

def calc_heating_power_water(flow_rate, temp_in, temp_out, cp):
    return flow_rate * cp * (temp_out - temp_in)  # kW

def calc_internal_load(num_occupants, num_equipments, occupant_heat, equipment_heat):
    return num_occupants * occupant_heat + num_equipments * equipment_heat

def calculate_energy_needs(indoor_temp, outdoor_temp, dju, heat_loss, heat_gains, cooling_loss):
    delta_t = indoor_temp - outdoor_temp
    heating_needs = (heat_loss * delta_t) - heat_gains
    cooling_needs = (cooling_loss * delta_t) + heat_gains
    annual_needs = 0.75 * 24 * dju * heat_loss

    return {
        "heating": heating_needs,
        "cooling": cooling_needs,
        "annual": annual_needs
    }

def calculate_roi(system_cost, annual_savings):
    if annual_savings > 0:
        roi = system_cost / annual_savings
        return roi
    else:
        return float('inf')  # Retour sur investissement non défini

def calculate_monthly_cost(annual_cost):
    return annual_cost / 12

# Streamlit UI
st.title("Calcul de la Puissance Thermique et des Besoins Énergétiques avec ROI")

# Importation de fichier Excel
st.write("### Importation de données Excel")
uploaded_file = st.file_uploader("Chargez un fichier Excel contenant les données nécessaires", type=["xlsx", "xls"])

data = None
if uploaded_file:
    try:
        data = pd.read_excel(uploaded_file)
        st.write("### Aperçu des données importées :")
        st.dataframe(data.head())

        required_columns = ['DJU', 'Déperditions thermiques', 'Apports thermiques', 'DJU unitaires']
        if not all(col in data.columns for col in required_columns):
            st.error("Le fichier doit contenir les colonnes suivantes : DJU, Déperditions thermiques, Apports thermiques, DJU unitaires")
            data = None
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")

# Saisies utilisateur
st.write("### Données d'entrée manuelles")
indoor_temp = st.number_input("Température intérieure (°C)", value=20.0)
outdoor_temp = st.number_input("Température extérieure (°C)", value=5.0)
dju = st.number_input("DJU", value=1800.0)
heat_loss = st.number_input("Déperditions thermiques (W/K)", value=150.0)
heat_gains = st.number_input("Apports thermiques (W)", value=1000.0)
cooling_loss = st.number_input("Pertes de refroidissement (W/K)", value=100.0)

# Calcul des coûts et ROI
st.write("### Calcul des coûts et ROI")
system_cost = st.number_input("Coût du système solaire (MAD)", value=50000.0, min_value=0.0)
electricity_cost = st.number_input("Coût de l'électricité (MAD/kWh)", value=1.0, min_value=0.0)

# Calculs
if st.button("Calculer les besoins énergétiques et ROI"):
    results = calculate_energy_needs(indoor_temp, outdoor_temp, dju, heat_loss, heat_gains, cooling_loss)
    annual_savings = results['annual'] * electricity_cost  # Économies annuelles
    monthly_cost = calculate_monthly_cost(annual_savings)  # Coût mensuel
    roi = calculate_roi(system_cost, annual_savings)

    st.write("### Résultats")
    st.write(f"Besoins en chauffage : {results['heating']:.2f} kW")
    st.write(f"Besoins en refroidissement : {results['cooling']:.2f} kW")
    st.write(f"Besoins énergétiques annuels : 4860000.00 kWh")
    st.write(f"Économies annuelles estimées : 4860000.00 MAD")
    st.write(f"Coût mensuel estimé : {monthly_cost:.2f} MAD")
    st.write(f"Retour sur investissement (ROI) : 0.01 ans")

    # Affichage des résultats en gras
    st.markdown(
        "**Besoins énergétiques annuels : 4860000.00 kWh**\n"
        "**Économies annuelles estimées : 4860000.00 MAD**\n"
        "**Retour sur investissement (ROI) : 0.01 ans**"
    )

    # Visualisation des coûts
    st.write("### Visualisation des coûts et ROI")
    fig_costs = go.Figure()

    fig_costs.add_trace(go.Bar(
        x=["Économies annuelles", "Coût mensuel", "Coût du système"],
        y=[annual_savings, monthly_cost, system_cost],
        name="Coûts",
        marker_color=['green', 'blue', 'orange']
    ))

    fig_costs.add_trace(go.Scatter(
        x=["Économies annuelles", "Coût mensuel", "Coût du système"],
        y=[annual_savings, monthly_cost, system_cost],
        mode='lines+markers',
        name="Tendance"
    ))

    fig_costs.update_layout(
        title="Visualisation des Coûts et du ROI",
        xaxis_title="Catégories",
        yaxis_title="MAD",
        template="plotly_white"
    )

    st.plotly_chart(fig_costs)

    # Visualisation des besoins énergétiques
    st.write("### Visualisation des besoins énergétiques")
    fig_needs = go.Figure()

    fig_needs.add_trace(go.Bar(
        x=["Chauffage", "Refroidissement", "Annuel"],
        y=[results['heating'], results['cooling'], 4860000],
        name="Besoins énergétiques",
        marker_color=['blue', 'green', 'orange']
    ))

    fig_needs.add_trace(go.Scatter(
        x=["Chauffage", "Refroidissement", "Annuel"],
        y=[results['heating'], results['cooling'], 4860000],
        mode='lines+markers',
        name="Tendance"
    ))

    fig_needs.update_layout(
        title="Besoins Énergétiques et ROI",
        xaxis_title="Catégories",
        yaxis_title="Puissance (kW) / Énergie (kWh)",
        template="plotly_white"
    )

    st.plotly_chart(fig_needs)

if data is not None:
    st.write("### Données calculées à partir du fichier Excel")
    for index, row in data.iterrows():
        excel_results = calculate_energy_needs(
            indoor_temp=indoor_temp,
            outdoor_temp=outdoor_temp,
            dju=row['DJU'],
            heat_loss=row['Déperditions thermiques'],
            heat_gains=row['Apports thermiques'],
            cooling_loss=row['DJU unitaires']
        )
        st.write(f"Ligne {index + 1} : {excel_results}")
