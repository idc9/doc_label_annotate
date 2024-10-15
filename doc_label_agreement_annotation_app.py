"""
This script creates a streamlit app for users to annotate if they agree/disagree with provided document/label pairs.

This code was written with assistance from ChatGPT.
"""
import streamlit as st
import pandas as pd
import io

from streamlit_shortcuts import button


st.set_page_config(layout="wide")


# Initialize session state
def initialize_session_state():
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'annotations' not in st.session_state:
        st.session_state.annotations = []
    if 'notes' not in st.session_state:
        st.session_state.notes = []
    if 'user_note' not in st.session_state:
        st.session_state.user_note = ""
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'reset_trigger' not in st.session_state:
        st.session_state.reset_trigger = 0

# Function to reset the session state
def reset_session():
    # Clear specific session state variables
    st.session_state.current_index = 0
    st.session_state.annotations = []
    st.session_state.notes = []
    st.session_state.user_note = ""
    st.session_state.uploaded_file = None
    # Increment the reset trigger to reload the page
    st.session_state.reset_trigger += 1

# Function to load and check the file
def load_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    if len(df.columns) < 2:
        st.error("The file must have at least 2 columns.")
        return None
    return df

# Function to display document navigation and content
def display_document(df):
    total_docs = len(df)
    doc_name = df.iloc[st.session_state.current_index, 0] if len(df.columns) == 3 else st.session_state.current_index
    st.write(f"Document {doc_name} ({st.session_state.current_index + 1}/{total_docs})")
    
    # Determine the indices based on the number of columns
    if len(df.columns) == 3:
        text, label = df.iloc[st.session_state.current_index, 1], df.iloc[st.session_state.current_index, 2]
        text_column, label_column = df.columns[1], df.columns[2]
    else:
        text, label = df.iloc[st.session_state.current_index, 0], df.iloc[st.session_state.current_index, 1]
        text_column, label_column = df.columns[0], df.columns[1]

    # col1, col2 = st.columns([3, 1])
    col1, col2 = st.columns([5, 1.5])
    with col1:
        st.markdown(f"<h5 style='text-decoration: underline;'>{text_column}</h5>", unsafe_allow_html=True)
        # st.subheader(text_column)
        st.write(f"<div style='height: 50px; overflow-y: auto; color: red;'>{text}</div>", unsafe_allow_html=True)


    with col2:
        # st.subheader(label_column)
        st.markdown(f"<h5 style='text-decoration: underline;'>{label_column}</h5>", unsafe_allow_html=True)
        st.write(f"<div style='height: 50px; overflow-y: auto; color: red;'>{label}</div>", unsafe_allow_html=True)

    # Add this line after displaying the document text and label in display_document function
    st.markdown("---")
    # st.markdown("<hr style='border:1px solid #333; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)


# Function to handle feedback buttons
def feedback_buttons(df):
    total_docs = len(df)
    is_done = st.session_state.current_index >= total_docs

    # Place the prompt text before the buttons
    # st.write("")

    correct_col, wrong_col, unsure_col = st.columns([1, 1, 1])
    with correct_col:
        st.button("Correct", on_click=update_feedback, args=("Correct",), disabled=is_done)
    with wrong_col:
        st.button("Wrong", on_click=update_feedback, args=("Wrong",), disabled=is_done)
    with unsure_col:
        st.button("Unsure", on_click=update_feedback, args=("Unsure",), disabled=is_done)


# Function to handle feedback buttons with keyboard shortcuts
def feedback_buttons(df):
    total_docs = len(df)
    is_done = st.session_state.current_index >= total_docs

    # Display the prompt text above the buttons
    st.write("Is the label provided for this document correct? Keyboard shortcuts: c, w, u.")

    # Use keyboard shortcuts with the custom button function
    correct_col, wrong_col, unsure_col = st.columns([1, 1, 1])
    with correct_col:
        if button("Correct", "c", on_click=update_feedback, args=("Correct",), disabled=is_done):
            st.write("You selected Agree.")
    with wrong_col:
        if button("Wrong", "w", on_click=update_feedback, args=("Wrong",), disabled=is_done):
            st.write("You selected Disagree.")
    with unsure_col:
        if button("Unsure", "u", on_click=update_feedback, args=("Unsure",), disabled=is_done):
            st.write("You selected Unsure.")


# Update feedback and move to next document
def update_feedback(annotation):
    st.session_state.annotations.append(annotation)
    st.session_state.notes.append(st.session_state.user_note)
    st.session_state.current_index += 1
    st.session_state.user_note = ""

# Function to go back to the previous document
def go_back_button():
    st.write(" ")
    st.write(" ")
    st.write(" ")
    if st.button("Go back to previous"):
        if st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.session_state.annotations.pop()
            st.session_state.notes.pop()
            st.session_state.user_note = ""

# Function to download annotations
def download_annotations(df):
    annotated_df = df.copy()
    annotated_df["user_annotation"] = pd.Series(st.session_state.annotations)
    annotated_df["user_notes"] = pd.Series(st.session_state.notes)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        annotated_df.to_excel(writer, index=False)
    st.download_button(
        label="Download user annotations",
        data=output.getvalue(),
        file_name="annotations.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Main app function
def main():
    initialize_session_state()
    
    st.title("Is the label provided for each document correct?")
    
    # File uploader with reset check
    uploaded_file = st.\
        file_uploader("Upload an Excel file. Press the x to reset the application.",
                      type=["xlsx"])
    if uploaded_file is None and st.session_state.uploaded_file is not None:
        reset_session()
    
    # Update session state with uploaded file
    st.session_state.uploaded_file = uploaded_file

    if st.session_state.uploaded_file is not None:
        df = load_file(st.session_state.uploaded_file)

        st.markdown("---")

        if df is not None:
            if st.session_state.current_index < len(df):
                display_document(df)
                feedback_buttons(df)
            else:
                st.write("All documents have been annotated. Thank you!")
                feedback_buttons(df)  # Buttons are still shown but are disabled

            # Notes input box (using `text_input` for single-line input)
            st.text_input("Notes",
                          key="user_note",
                          placeholder="Enter any notes here (ignore instructions about press enter to apply)")
            
            # Go back button
            go_back_button()

            st.markdown("---")

            # Download button
            if len(st.session_state.annotations) > 0:
                download_annotations(df)

        # # Reset button
        # if st.button("Reset"):
        #     reset_session()
    else:
        st.write("Please upload an Excel file. Each row should be a document. There should be either two (text, label) or three (name, text, label) columns.")

if __name__ == "__main__":
    main()
