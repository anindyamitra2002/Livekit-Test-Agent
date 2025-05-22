import streamlit as st

def update_selection():
    # Access the updated value using the widget's key
    current_value = st.session_state["selection"]
    print(current_value)
    st.write(f"Current selection: {current_value}")

# Define the selectbox with a unique key and on_change callback
st.selectbox(
    "Choose an option:",
    options=["Option 1", "Option 2", "Option 3"],
    key="selection",
    on_change=update_selection
)
