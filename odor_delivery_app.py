import serial
import tkinter
from tkinter import *
import streamlit as st
import pandas as pd
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
    st.set_page_config(page_title="Odor Delivery App")
    st.title("Odor Delivery")


def initialize_states():
    """
    Initializes streamlit session state variables
    """

    if "acq_params" not in st.session_state:
        st.session_state.acq_params = False
    if "saved_acq_params" not in st.session_state:
        st.session_state.saved_acq_params = False
    if "saved_params_compare" not in st.session_state:
        st.session_state.saved_params_compare = False
    if "settings_saved" not in st.session_state:
        st.session_state.settings_saved = False
    if "file_name" not in st.session_state:
        st.session_state.file_name = False
    if "randomize_trials" not in st.session_state:
        st.session_state.randomize_trials = False
    if "exp_type_selected" not in st.session_state:
        st.session_state.exp_type_selected = False
    if "experiment_started" not in st.session_state:
        st.session_state.experiment_started = False


def clear_settings_fields():
    """
    Resets input fields to default values
    """
    st.session_state["text"] = ""
    st.session_state["default_roi"] = 1
    st.session_state["default_num_odors"] = 1
    st.session_state["default_num_trials"] = 1
    st.session_state["default_odor_duration"] = 1
    st.session_state["default_min_odor_time"] = 1
    st.session_state["default_max_odor_time"] = 1
    st.session_state["default_time_btw_odors"] = 10
    st.session_state["default_exp_type"] = "Yes"


def get_setting_inputs():
    """
    Creates input fields for experiment settings and saves to AcqParams object
    """
    st.header("Settings")

    mouse_id = False  # Set to false before user input

    (
        settings_r1_c1,
        settings_r1_c2,
        settings_r1_c3,
        settings_r1_c4,
    ) = st.columns(4)

    sessioninfo_col1, sessioninfo_col2 = st.columns(2)
    with settings_r1_c1:
        mouse_id = st.text_input(
            label="Mouse ID", placeholder="123456-1-2", key="text"
        )
    with settings_r1_c2:
        roi = st.number_input(label="ROI #", min_value=1, key="default_roi")

    with settings_r1_c3:
        num_odors = st.selectbox(
            label="Number of Odors",
            options=range(1, 9),
            # index=7,
            key="default_num_odors",
        )

    with settings_r1_c4:
        num_trials = st.number_input(
            label="Number of Trials per Odor",
            min_value=1,
            # value=24,
            key="default_num_trials",
        )

    (
        settings_r2_c1,
        settings_r2_c2,
        settings_r2_c3,
        settings_r2_c4,
    ) = st.columns(4)

    with settings_r2_c1:
        odor_duration = st.number_input(
            label="Odor Duration (s)",
            min_value=1,
            key="default_odor_duration",
        )

    with settings_r2_c2:
        time_btw_odors = st.number_input(
            label="Time Between Odors (s)",
            min_value=1,
            value=10,
            key="default_time_btw_odors",
        )

    now_date = datetime.datetime.now()

    with settings_r2_c3:
        st.session_state.randomize_trials = st.radio(
            label="Shuffle trials?",
            options=(
                "Yes",
                "No",
            ),
            key="default_exp_type",
        )

    return (
        mouse_id,
        roi,
        num_odors,
        num_trials,
        odor_duration,
        time_btw_odors,
        now_date,
    )


def save_settings(settings_dict):
    """
    Saves experiment settings to AcqParams object
    """
    st.session_state.settings_saved = True
    st.session_state.saved_params_compare = settings_dict

    st.session_state.saved_acq_params = AcqParams(
        settings_dict["date"],
        settings_dict["mouse"],
        settings_dict["roi"],
        settings_dict["num_odors"],
        settings_dict["num_trials"],
        settings_dict["odor_duration"],
        settings_dict["time_btw_odors"],
        settings_dict["randomize_trials"],
    )

    st.session_state.file_name = (
        f"{st.session_state.acq_params['date']}_"
        f"{st.session_state.acq_params['mouse']}_"
        f"ROI{st.session_state.acq_params['roi']}_Odor"
    )

    st.info(f"Settings saved for {st.session_state.file_name}.")


def make_settings_fields():
    """
    Creates layout for experiment settings
    """
    (
        mouse_id,
        roi,
        num_odors,
        num_trials,
        odor_duration,
        time_btw_odors,
        now_date,
    ) = get_setting_inputs()

    st.session_state.acq_params = {
        "mouse": mouse_id,
        "roi": roi,
        "date": now_date.strftime("%y%m%d"),
        "num_odors": num_odors,
        "num_trials": num_trials,
        "odor_duration": odor_duration,
        "time_btw_odors": time_btw_odors,
        "randomize_trials": st.session_state.randomize_trials,
    }

    buttons_col1, buttons_col2 = st.columns([0.25, 1])

    with buttons_col1:
        reset = st.button("Reset Settings", on_click=clear_settings_fields)
    if reset:
        st.session_state.settings_saved = False
        st.session_state.acq_params = False
        st.session_state.file_name = False

    if (
        mouse_id  # Mouse id has been entered
        # If any values were changed, prompt to save settings again
        and st.session_state.acq_params
        != st.session_state.saved_params_compare
    ):
        with buttons_col2:
            save_params = st.button("Save Settings")

        if save_params:  # Save dict to AcqParams object
            save_settings(st.session_state.acq_params)


def randomize_trials():
    """
    Randomizes the order of odor delivery
    """
    trials = (
        list(range(1, st.session_state.saved_acq_params.num_odors + 1))
        * st.session_state.saved_acq_params.num_trials
    )

    random.shuffle(trials)

    return trials


def get_trial_order():
    """
    Displays the order in which odors are delivered for every trial in a table
    """
    if st.session_state.randomize_trials == "Yes":
        trials = randomize_trials()

    if st.session_state.randomize_trials == "No":
        trials = (
            list(range(1, st.session_state.saved_acq_params.num_odors + 1))
            * st.session_state.saved_acq_params.num_trials
        )

    trial_labels = list(range(1, len(trials) + 1))
    trials_df = pd.DataFrame({"Trial": trial_labels, "Odor #": trials})

    st.markdown("**Odor order by trials:**")

    # CSS to inject contained in a string, to hide df indices
    hide_table_row_index = """
                <style>
                thead tr th {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

    st.table(trials_df.T)

    # Make randomize and start experiment buttons
    buttons2_col1, buttons2_col2 = st.columns([0.4, 1])

    if st.session_state.experiment_started == False:
        if st.session_state.randomize_trials == "Yes":
            randomize = buttons2_col1.button("Randomize Trials Again")
            if randomize:
                trials = randomize_trials()
                st.session_state.experiment_started = False

            start_exp = buttons2_col2.button("Start Experiment")

        else:
            start_exp = buttons2_col1.button("Start Experiment")

        if start_exp:
            st.session_state.experiment_started = True
            # Immediately re-runs script to hide setting input fields
            st.experimental_rerun()


def show_exp_summary():
    """
    Creates layout for experiment settings summary
    """
    st.markdown("""---""")
    st.header("Trial info")
    st.markdown(
        f"""
        **Total # of trials:** {st.session_state.saved_acq_params.num_trials*st.session_state.saved_acq_params.num_odors}
        -- {st.session_state.saved_acq_params.num_trials} trial(s) for each
        of {st.session_state.saved_acq_params.num_odors} odors
        
        **Odor duration:** {st.session_state.saved_acq_params.odor_duration}s

        **Time between odors:** {st.session_state.saved_acq_params.time_btw_odors}s
        """
    )

    get_trial_order()


class AcqParams:
    """
    Defines the class for holding GUI acquisition parameters
    """

    def __init__(
        self,
        date,
        mouse_id,
        roi,
        num_odors,
        num_trials,
        odor_duration,
        time_btw_odors,
        randomize_trials,
    ):
        self.date = date
        self.mouse_id = mouse_id
        self.roi = roi
        self.num_odors = num_odors
        self.num_trials = num_trials
        self.odor_duration = odor_duration
        self.time_btw_odors = time_btw_odors
        self.randomize_trials = randomize_trials


def main():
    set_webapp_params()
    initialize_states()

    # If experiment hasn't started, display setting fields
    if st.session_state.experiment_started == False:
        make_settings_fields()

    # Otherwise show message that experiment is in progress
    else:
        st.warning("Experiment in progress...")

    # Always show summary of settings
    if (
        st.session_state.settings_saved
        and st.session_state.acq_params
        == st.session_state.saved_params_compare
    ):
        show_exp_summary()


main()
