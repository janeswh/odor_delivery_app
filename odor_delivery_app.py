import serial
import tkinter
from tkinter import *
import streamlit as st
import time
import datetime
import random
import math
import decimal
from pathlib import Path
import pdb


def set_webapp_params():
    """
    Sets the name of the Streamlit app along with intro message
    """
    st.set_page_config(page_title="Input Acquisition Settings")
    st.title("Input acquisition settings")


def initialize_states():
    """
    Initializes streamlit session state variables
    """

    if "acq_params" not in st.session_state:
        st.session_state.acq_params = False
    if "settings_saved" not in st.session_state:
        st.session_state.settings_saved = False
    if "file_name" not in st.session_state:
        st.session_state.file_name = False


def clear_fields():
    """
    Resets input fields to default values
    """
    st.session_state["text"] = ""
    st.session_state["default_roi"] = 1
    st.session_state["default_num_odors"] = 8
    st.session_state["default_num_trials"] = 3
    st.session_state["default_min_odor_time"] = 1
    st.session_state["default_max_odor_time"] = 1
    st.session_state["default_time_btw_odors"] = 10


class AcqParams:
    """
    Defines the class for holding GUI acquisition parameters
    """

    pass


def main():
    set_webapp_params()
    initialize_states()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Input Parameters", "DIY", "Random Trials", "Single Trial"]
    )

    with tab1:  # Constructs data acquisition parameters tab
        st.header("Enter Session Info")

        tab1_sessioninfo_col1, tab1_sessioninfo_col2 = st.columns(2)
        with tab1_sessioninfo_col1:
            mouse_id = st.text_input(
                label="Mouse ID", placeholder="123456-1-2", key="text"
            )
        with tab1_sessioninfo_col2:
            roi = st.number_input(
                label="ROI #", min_value=1, key="default_roi"
            )

        st.header("Set Parameters")

        tab1_top_col1, tab1_top_col2 = st.columns(2)
        with tab1_top_col1:
            num_odors = st.selectbox(
                label="Number of Odors",
                options=range(1, 9),
                index=6,
                key="default_num_odors",
            )

        with tab1_top_col2:
            num_trials = st.number_input(
                label="Number of Trials per Odor",
                min_value=1,
                # value=24,
                key="default_num_trials",
            )

        tab1_mid_col1, tab1_mid_col2, tab1_mid_col3 = st.columns(3)
        with tab1_mid_col1:
            min_odor_time = st.number_input(
                label="Min. Odor Time (s)",
                min_value=1,
                key="default_min_odor_time",
            )
        with tab1_mid_col2:
            max_odor_time = st.number_input(
                label="Max. Odor Time (s)",
                min_value=1,
                key="default_max_odor_time",
            )
        with tab1_mid_col3:
            time_btw_odors = st.number_input(
                label="Time Between Odors (s)",
                min_value=1,
                value=10,
                key="default_time_btw_odors",
            )

    buttons_col1, buttons_col2 = st.columns([0.25, 1])

    with buttons_col1:
        reset = st.button("Reset Settings", on_click=clear_fields)
    if reset:
        st.session_state.settings_saved = False
        st.session_state.acq_params = False
        st.session_state.file_name = False

    if mouse_id:  # Show save button if mouse_id isn't empty
        with buttons_col2:
            save_params = st.button("Save Settings")

        if save_params:  # Save settings to session state dict
            st.session_state.settings_saved = True
            now_date = datetime.datetime.now()
            st.session_state.acq_params = {
                "mouse": mouse_id,
                "roi": roi,
                "date": now_date.strftime("%y%m%d"),
                "num_odors": num_odors,
                "num_trials": num_trials,
                "min_odor_time": min_odor_time,
                "max_odor_time": max_odor_time,
                "time_btw_odors": time_btw_odors,
            }

            st.session_state.file_name = (
                f"{st.session_state.acq_params['date']}_"
                f"{st.session_state.acq_params['mouse']}_"
                f"ROI{st.session_state.acq_params['roi']}_Odor"
            )

            st.info(f"Settings saved for {st.session_state.file_name}.")

    if st.session_state.settings_saved:
        exp_type = st.radio(
            label="Experiment type",
            options=("DIY", "Random Trials", "Single Trial"),
        )


main()
