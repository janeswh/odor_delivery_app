import serial
import tkinter
from tkinter import *
import streamlit as st
from stqdm import stqdm
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

    # Initialize arduino variables
    if "arduino_initialized" not in st.session_state:
        st.session_state.arduino_initialized = False
    if "arduino" not in st.session_state:
        st.session_state.arduino = False

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
    if "trial_order" not in st.session_state:
        st.session_state.trial_order = False
    if "exp_type_selected" not in st.session_state:
        st.session_state.exp_type_selected = False
    if "experiment_started" not in st.session_state:
        st.session_state.experiment_started = False

    if "prelim_trials" not in st.session_state:
        st.session_state.prelim_trials = False

    if "trial_order_saved" not in st.session_state:
        st.session_state.trial_order_saved = False

    if "rand_btn_clicked" not in st.session_state:
        st.session_state.rand_btn_clicked = False


def initialize_arduino():
    """
    Initiate the Arduino
    """
    arduino = serial.Serial()

    # pdb.set_trace()
    arduino.port = "COM8"  # Change COM PORT if COMPort error occurs
    arduino.baudrate = 9600
    arduino.timeout = 2
    arduino.setRTS(FALSE)
    time.sleep(2)
    # two seconds for arduino to reset and port to open
    arduino.open()

    st.session_state.arduino_initialized = True
    st.session_state.arduino = arduino


def close_arduino():
    """
    Closes the arduino connection
    """
    st.session_state.arduino.close()
    st.session_state.arduino_initialized = False


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


def save_trial_order(trials):
    """
    Saves the prelim odor trial orders
    """
    st.session_state.trial_order = trials
    st.session_state.trial_order_saved = True

    start_experiment()
    # st.experimental_rerun()


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


def randomize_trials(button=False):
    """
    Randomizes the order of odor delivery
    """
    trials = (
        list(range(1, st.session_state.saved_acq_params.num_odors + 1))
        * st.session_state.saved_acq_params.num_trials
    )

    random.shuffle(trials)

    if button:
        st.session_state.rand_btn_clicked = True

    st.session_state.prelim_trials = trials


def get_trial_order():
    """
    Displays the order in which odors are delivered for every trial in a table
    """

    if st.session_state.trial_order_saved is False:
        if (
            st.session_state.randomize_trials == "Yes"
            and st.session_state.rand_btn_clicked is False
        ):
            randomize_trials()

        if st.session_state.randomize_trials == "No":
            st.session_state.prelim_trials = (
                list(range(1, st.session_state.saved_acq_params.num_odors + 1))
                * st.session_state.saved_acq_params.num_trials
            )

        print_trial_order(st.session_state.prelim_trials)

        # Make randomize and start experiment buttons
        buttons2_col1, buttons2_col2 = st.columns([0.4, 1])

        if st.session_state.randomize_trials == "Yes":
            buttons2_col1.button(
                "Randomize Trials Again",
                on_click=randomize_trials,
                args=((True,)),
            )

            buttons2_col2.button(
                "Start Experiment",
                on_click=save_trial_order,
                args=((st.session_state.prelim_trials,)),
            )

        else:
            buttons2_col1.button(
                "Start Experiment",
                on_click=save_trial_order,
                args=((st.session_state.prelim_trials,)),
            )
    else:
        print_trial_order(st.session_state.trial_order)


def start_experiment():
    """
    Initializes arduino and starts experiment. Takes the odor odor sequence
    has input.
    """
    st.session_state.experiment_started = True

    # Initialize Arduino
    if st.session_state.arduino_initialized == False:
        initialize_arduino()
    if st.session_state.arduino_initialized == True:
        st.info("Arduino initialized and on stand-by")

        arduino_session = ArduinoSession(
            st.session_state.saved_acq_params, st.session_state.trial_order
        )

        arduino_session.save_solenoid_order_csv()

        if arduino_session.trig_signal is False:
            while (
                arduino_session.trig_signal is False
                and arduino_session.sequence_complete is False
            ):
                # Check whether arduino is connected
                new_arduino_message = arduino_session.get_arduino_msg()
                if "y" in new_arduino_message:
                    print("Arduino is connected")
                    arduino_session.trig_signal = True

                    arduino_session.generate_arduino_str()

                    arduino_session.save_solenoid_timing_csv()

                    arduino_session.trig_signal = False

                else:
                    pass

                # arduino_session.make_str_signals()

    pdb.set_trace()
    close_arduino()
    pdb.set_trace()


def make_trials_df(trials):
    """
    Puts odor trials into a df
    """
    trial_labels = list(range(1, len(trials) + 1))
    trials_df = pd.DataFrame({"Trial": trial_labels, "Odor #": trials})

    return trials_df


def print_trial_order(trials):
    """
    Prints a table listing the trial number and odor used for each trial
    """

    trials_df = make_trials_df(trials)

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


class ArduinoSession:
    """
    Defines the class for holding signals sent to the arduino per session
    """

    def __init__(self, session_params, odor_sequence):
        self.acq_params = session_params

        self.trig_signal = False  # Whether Arduino has triggered microscope
        self.delay_time = 0  # Time btw odors? don't think I need

        self.sequence_complete = (
            False  # Whether odor delivery sequence has finished
        )

        self.solenoid_order = odor_sequence  # Double check

        ###For predicted timings:
        self.trigger = 100  # in milliseconds   what is this??
        self.iniStart = datetime.datetime.now()
        self.iniHour = (self.iniStart).hour
        self.iniMinute = (self.iniStart).minute
        self.iniSec = (self.iniStart).second
        self.iniMicroSec = (self.iniStart).microsecond
        self.iniMilliSec = (
            self.iniMicroSec
        ) / 1000  # only has microseconds, which is 1/1000 milliseconds

        # Testing new format to directly go into miliseconds
        self.init_time = datetime.datetime.now().isoformat(
            "|", timespec="milliseconds"
        )

        ###Keep track of when the solenoids were activated
        self.time_solenoid_on = (
            []
        )  # Contains times that solenoids were activated
        self.time_solenoid_off = (
            []
        )  # Contains times that solenoids were closed
        self.sent = 0  # if sent = 1, then that means a string has been sent to the arduino and we need to wait for it to be done
        self.timeTTLName = "TTL to microscope sent at: "
        self.time_scope_TTL = []

    def get_arduino_msg(self):
        """
        Gets message back from arduino after sending it str
        """

        # if st.session_state.arduino.in_waiting:
        if st.session_state.arduino.isOpen():
            sent_info = st.session_state.arduino.readline().strip()
            # sent_info = st.session_state.arduino.read()
            decode_info = sent_info.decode("utf-8")
        else:
            decode_info = None

        return decode_info

    def parse_arduino_msg(self, solenoid, placeholder):
        """
        Translates the message sent back from arduino into informative
        timestamps. Prints the info into placeholder textbox
        """
        arduino_msg_received = self.get_arduino_msg()

        if (
            arduino_msg_received is None or "y" in arduino_msg_received
        ):  ##update: check if y is anywhere in the messageReceived in case arduino sends too many at once
            pass
        elif arduino_msg_received == "9":
            # Time when microscope has been triggered via TTL
            time_TTL = datetime.datetime.now().isoformat(
                "|", timespec="milliseconds"
            )
            self.time_scope_TTL.append(time_TTL)

            placeholder.info(
                f"odor {solenoid} microscope triggered at {time_TTL}"
            )

            time.sleep(2)

        elif arduino_msg_received == "1":
            time_solenoid_on = datetime.datetime.now().isoformat(
                "|", timespec="milliseconds"
            )
            self.time_solenoid_on.append(time_solenoid_on)
            placeholder.info(f"odor {solenoid} released at {time_solenoid_on}")

            time.sleep(2)
        elif arduino_msg_received == "2":
            time_solenoid_off = datetime.datetime.now().isoformat(
                "|", timespec="milliseconds"
            )
            self.time_solenoid_off.append(time_solenoid_off)
            placeholder.info(f"odor {solenoid} stopped at {time_solenoid_off}")

            time.sleep(2)
        elif arduino_msg_received == "3":
            self.sent = 0
            placeholder.info("delay stopped, send next solenoid info")

            time.sleep(2)

    def generate_arduino_str(self):
        """
        Generates arduino execution strs in format "x, y, z" where
        x = solenoid number
        y = odor duration (s)
        z = time between odors (s)
        """

        # Adds progress bar
        bar = stqdm(range(len(self.solenoid_order)), desc=f"Executing Trial")

        # Creates plateholder container for arduino progress msgs
        arduino_output_placeholder = st.empty()

        # for solenoid in self.solenoid_order:
        for trial in bar:
            bar.set_description(f"Executing Trial {trial+1}", refresh=True)
            to_be_sent = (
                # f"{solenoid},{self.acq_params.odor_duration},"
                f"{self.solenoid_order[trial]},{self.acq_params.odor_duration},"
                f"{self.acq_params.time_btw_odors}"
            )
            # to_be_sent = "5"

            self.sent = 1
            time.sleep(2)  # Two seconds for arduino to reset

            # Send the information to arduino and wait for something to come back
            st.session_state.arduino.write(to_be_sent.encode())

            while self.sent == 1:
                # self.parse_arduino_msg(solenoid, arduino_output_placeholder)
                self.parse_arduino_msg(
                    self.solenoid_order[trial], arduino_output_placeholder
                )

                # Mark end after last trial
                if trial + 1 == len(bar):
                    arduino_output_placeholder.info(
                        "Odor delivery sequence complete."
                    )
                    self.sequence_complete = True

    def save_solenoid_order_csv(self):
        """
        Creates the solenoid .csv file containing solenoid info and timings
        Columns: Trial, Odor #, Frame #, Date, Trigger Timestamp, release timestamp,
        stopped timestamp

        """
        csv_name = (
            f"{self.acq_params.date}_{self.acq_params.mouse_id}_ROI"
            f"{self.acq_params.roi}_solenoid_order.csv"
        )
        trials_df = make_trials_df(self.solenoid_order)
        trials_df.to_csv(csv_name, index=False)

    def save_solenoid_timing_csv(self):
        """
        Saves the timestamps for when each solenoid was triggered, opened,
        and closed to a .csv file.
        """
        csv_name = (
            f"{self.acq_params.date}_{self.acq_params.mouse_id}_ROI"
            f"{self.acq_params.roi}_solenoid_timing.csv"
        )

        trial_labels = list(range(1, len(self.solenoid_order) + 1))
        timings_df = pd.DataFrame(
            {
                "Trial": trial_labels,
                "Odor #": self.solenoid_order,
                "Microscope Triggered": self.time_scope_TTL,
                "Solenoid opened": self.time_solenoid_on,
                "Solenoid closed": self.time_solenoid_off,
            }
        )

        timings_df.to_csv(csv_name, index=False)

    def make_str_signals(self):
        """
        Compile a string to be sent to Arduino to execute
        """
        for solenoid in self.solenoid_order:
            print(solenoid)


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
        get_trial_order()


main()
