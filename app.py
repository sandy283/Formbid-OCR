import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import time


# Function to get the Gemini model response
def get_gemini_response(input_text, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    if input_text != "":
        response = model.generate_content([input_text, image])
    else:
        response = model.generate_content(image)
    return response.text

# Function to save properties to a file
def save_properties(properties, filename):
    with open(filename, "w") as file:
        for prop, value in properties.items():
            file.write(f"{prop}: {value}\n")

# Initialize Streamlit app
st.set_page_config(page_title="Certificate Checker", page_icon=":gem:")
st.markdown(
    """
    <style>
    .main {
        background-color: #4682B4;
    }
    h1, h2, h3, h4, h5, h6, p, label {
        color: #333333;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        font-size: 16px;
        padding: 10px 24px;
        margin: 10px 0;
    }
    .stTextInput>div>div>input {
        border: 2px solid #4CAF50;
        border-radius: 12px;
        color: #333333;
    }
    .stFileUploader>label {
        color: #4CAF50;
        font-weight: bold;
    }
    .uploadedFile, .fileText {
        color: #4CAF50 !important;
        background-color: #ffffff !important;
        font-weight: bold !important;
    }
    .stFileUploader {
        border: 2px solid #4CAF50;
        border-radius: 12px;
        padding: 5px;
    }
    .property-table {
        margin-top: 20px;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        background-color: #ffffff;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .scroll-box {
        max-height: 150px; /* Reduced height */
        overflow-y: auto; /* Vertical scroll */
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        background-color: #f9f9f9;
        font-size: 12px;
        line-height: 1.5;
        font-family: monospace;
        color: #000000;  /* Set text color to black */
    }
    .scroll-box-image {
        max-height: 15px; /* Reduced height */
        overflow-y: auto; /* Vertical scroll */
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        background-color: #f9f9f9;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.header("Test Certificates")
api_key = st.text_input("Enter your API key", type="password")
genai.configure(api_key=api_key)
input_text = "Extract All Tables from given image"
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], label_visibility="visible", help="Upload your image file here.")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Resize the image to 30% of its original dimensions
    new_width = int(image.width * 0.3)
    new_height = int(image.height * 0.3)
    resized_image = image.resize((new_width, new_height))
    
    st.markdown('<div class="scroll-box-image">', unsafe_allow_html=True)
    st.image(resized_image, caption="Uploaded Image", use_column_width=False)  # Set to False for manual resizing
    st.markdown('</div>', unsafe_allow_html=True)

# Default values
default_properties_values = {
    "Si(%)": 0.016,
    "Fe(%)": 0.021,
    "Cu(%)": 0.04,
    "Mn(%)": 0.056,
    "Mg(%)": 0.012,
    "Cr(%)": 0.011,
    "Zn(%)": 0.013,
    "Ti(%)": 0.041,
    "Al(%)": 0.075,
    "Ultimate tensile strength(Mpa)": 31.0,
    "Tensile yield strength(Mpa)": 27.6,
    "Modulus of Elasticity(Gpa)": 68.9,
    "Shear strength(Mpa)": 20.7
}

# Load default values if available
if os.path.exists("default_values.txt"):
    with open("default_values.txt", "r") as file:
        default_properties_values = {line.split(": ")[0]: float(line.split(": ")[1]) for line in file}

# Ensure properties values are initialized in session state
if 'properties_values' not in st.session_state:
    st.session_state.properties_values = default_properties_values.copy()

# Display properties in a table-like format with styling
st.subheader("Properties Table")
st.markdown('<div class="property-table">', unsafe_allow_html=True)

# Use default values or initialize new ones
properties_values = st.session_state.properties_values

cols = st.columns(4)
for i, (prop, value) in enumerate(properties_values.items()):
    col = cols[i % 4]
    with col:
        new_value = st.number_input(f"{prop}", value=value, key=prop)
        properties_values[prop] = new_value
st.markdown('</div>', unsafe_allow_html=True)

# Save values button
if st.button("Save Values"):
    save_properties(properties_values, "values.txt")

# Set as default button
if st.button("Set as Default"):
    # Save the current properties to values.txt
    save_properties(default_properties_values, "values.txt")

    st.session_state.properties_values = default_properties_values.copy()

# Button to submit and generate test certificate
submit = st.button("Test Certificate")

# If the submit button is clicked

def get_gemini_response_text(question):
    response = chat.send_message(question, stream=True)
    return response

if submit:
    response = get_gemini_response(input_text, image)
    st.write(response)

    with open("temp.txt", "w") as file:
        file.write(response)

    with open('values.txt', 'r') as file:
        defalut_values = file.read()

    with open('temp.txt', 'r') as file:
        file_content = file.read()


    st.write("Processing your certificate. Please wait...")

    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = model.start_chat(history=[])

    input_text = f"""
    Compare the following certificate values against the default values to determine if the certificate passes. A certificate passes if all values are greater than or equal to their corresponding default values. If any default value is missing in the certificate, exclude it from the comparison.
    \n
    Instructions:

    Comparison: Ensure each certificate value is greater than or equal to the default value.
    Result: Output "Pass" if all present values meet or exceed the defaults. Output "Fail" and specify the failing features if any values are below the default.
    \n
    Provide results as follows:

    Pass or
    Fail with specific failing features.
    \n
    Default Values:

    {defalut_values}
    \n
    Certificate Values:

    {file_content}
    """

    if submit and input_text:
        response = get_gemini_response_text(input_text)
        time.sleep(2.5)

        for chunk in response:
            st.write(chunk.text)
