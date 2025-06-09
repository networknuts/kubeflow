import os
import streamlit as st
import requests
import pandas as pd

# UI Title
st.title("Insurance Fraud Detection")

# Define input fields
def user_input_features():
    months_as_customer = st.number_input('Months as Customer', min_value=0, value=0)
    age = st.number_input('Age', min_value=0, value=30)
    policy_state = st.selectbox('Policy State', ['OH', 'IN', 'SC', 'NY', 'WV', 'VA', 'NC', 'WI', 'MO', 'LA', 'OK', 'AR', 'AZ', 'IL', 'FL', 'NM', 'TX', 'KY', 'GA', 'PA'])
    policy_csl = st.selectbox('Policy CSL', ['100/300', '250/500', '500/1000'])
    policy_deductable = st.number_input('Policy Deductable', min_value=0, value=500)
    policy_annual_premium = st.number_input('Annual Premium', min_value=0.0, value=1000.0)
    umbrella_limit = st.number_input('Umbrella Limit', min_value=0, value=0)
    insured_zip = st.text_input('Insured Zip', '00000')
    insured_sex = st.selectbox('Insured Sex', ['MALE', 'FEMALE'])
    insured_education_level = st.selectbox('Education Level', ['MD', 'PhD', 'High School', 'College', 'Masters'])
    insured_occupation = st.text_input('Occupation', 'craft-repair')
    insured_hobbies = st.text_input('Hobbies', 'sleeping')
    insured_relationship = st.selectbox('Relationship', ['Husband', 'Wife', 'Unmarried', 'Children'])
    capital_gains = st.number_input('Capital Gains', min_value=0, value=0)
    capital_loss = st.number_input('Capital Loss', min_value=0, value=0)
    incident_type = st.selectbox('Incident Type', ['Single Vehicle Collision', 'Multi-vehicle Collision', 'Parked Car'])
    collision_type = st.selectbox('Collision Type', ['Side Collision', 'Rear Collision', 'Front Collision'])
    incident_severity = st.selectbox('Incident Severity', ['Minor Damage', 'Major Damage', 'Total Loss'])
    authorities_contacted = st.selectbox('Authorities Contacted', ['Police', 'Fire', 'Other', 'NA'])
    incident_state = st.selectbox('Incident State', ['OH', 'IN', 'SC', 'NY', 'WV', 'VA', 'NC', 'WI', 'MO', 'LA', 'OK', 'AR', 'AZ', 'IL', 'FL', 'NM', 'TX', 'KY', 'GA', 'PA'])
    incident_city = st.text_input('Incident City', 'Columbus')
    incident_hour = st.slider('Incident Hour of the Day', 0, 23, 12)
    num_vehicles = st.number_input('Number of Vehicles Involved', min_value=1, value=1)
    property_damage = st.selectbox('Property Damage', ['YES', 'NO'])
    bodily_injuries = st.number_input('Bodily Injuries', min_value=0, value=0)
    witnesses = st.number_input('Witnesses', min_value=0, value=0)
    police_report_available = st.selectbox('Police Report Available', ['YES', 'NO'])
    total_claim_amount = st.number_input('Total Claim Amount', min_value=0.0, value=0.0)
    injury_claim = st.number_input('Injury Claim', min_value=0.0, value=0.0)
    property_claim = st.number_input('Property Claim', min_value=0.0, value=0.0)
    vehicle_claim = st.number_input('Vehicle Claim', min_value=0.0, value=0.0)
    auto_make = st.text_input('Auto Make', 'Saab')
    auto_model = st.text_input('Auto Model', '92x')
    auto_year = st.number_input('Auto Year', min_value=1900, max_value=2100, value=2004)

    data = {
        'months_as_customer': months_as_customer,
        'age': age,
        'policy_state': policy_state,
        'policy_csl': policy_csl,
        'policy_deductable': policy_deductable,
        'policy_annual_premium': policy_annual_premium,
        'umbrella_limit': umbrella_limit,
        'insured_zip': insured_zip,
        'insured_sex': insured_sex,
        'insured_education_level': insured_education_level,
        'insured_occupation': insured_occupation,
        'insured_hobbies': insured_hobbies,
        'insured_relationship': insured_relationship,
        'capital-gains': capital_gains,
        'capital-loss': capital_loss,
        'incident_type': incident_type,
        'collision_type': collision_type,
        'incident_severity': incident_severity,
        'authorities_contacted': authorities_contacted,
        'incident_state': incident_state,
        'incident_city': incident_city,
        'incident_hour_of_the_day': incident_hour,
        'number_of_vehicles_involved': num_vehicles,
        'property_damage': property_damage,
        'bodily_injuries': bodily_injuries,
        'witnesses': witnesses,
        'police_report_available': police_report_available,
        'total_claim_amount': total_claim_amount,
        'injury_claim': injury_claim,
        'property_claim': property_claim,
        'vehicle_claim': vehicle_claim,
        'auto_make': auto_make,
        'auto_model': auto_model,
        'auto_year': auto_year
    }
    return pd.DataFrame([data])

# Collect user input into DataFrame
input_df = user_input_features()
st.write("### Input Data", input_df)

# Predict button
PREDICTOR_URL = os.getenv("PREDICTOR_URL", "http://localhost:8080/v1/models/insurance-fraud-custom:predict")
if st.button("Predict Fraud"):
    instances = input_df.to_dict(orient='records')
    payload = {"instances": instances}
    response = requests.post(
        PREDICTOR_URL,
        json=payload
    )
    if response.status_code == 200:
        result = response.json()
        st.success(f"Prediction: {result['predictions'][0]}")
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
