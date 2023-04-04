import datapane as dp
import pdb


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
    ):
        self.date = date
        self.mouse_id = mouse_id
        self.roi = roi
        self.num_odors = num_odors
        self.num_trials = num_trials
        self.odor_duration = odor_duration
        self.time_btw_odors = time_btw_odors


# def save_params(
#     mouse: str,
#     roi: int,
#     num_odors: int,
#     num_trials: int,
#     odor_dur: int,
#     time_btw_odor: int,
#     exp_type: str,
# ):
def save_params(params):
    # acq_params = AcqParams()
    # pdb.set_trace()
    # dp.Text(params["mouse"])

    if params["exp_type"] == "Single Trial":
        display = dp.Text("Single trial")
    else:
        display = dp.Text("Random Trials")

    return dp.View(display)


controls = dict(
    mouse=dp.TextBox(label="Mouse ID"),
    roi=dp.NumberBox(label="ROI #", initial=1),
    num_odors=dp.NumberBox(label="# of odors", initial=8),
    num_trials=dp.NumberBox(label="# of trials", initial=1),
    odor_dur=dp.NumberBox(label="Odor duration (s)", initial=1),
    time_btw_odor=dp.NumberBox(label="Time between odors (s)", initial=10),
    exp_type=dp.Choice(
        label="Experiment type", options=["Single Trial", "Random Trials"]
    ),
)

if __name__ == "__main__":
    view = dp.View(
        dp.Group(
            dp.Group(name="placeholder1"),
            dp.Group(
                dp.Text("## Experiment settings"),
                dp.Form(
                    controls=controls, on_submit=save_params, target="saved"
                ),
            ),
            dp.Group(dp.Text("## Trial order"), dp.Group(name="saved")),
            dp.Group(name="placeholder2"),
            # valign=VAlign.Center,
            widths=[1, 2, 2, 1],
            columns=4,
        ),
        # pdb.set_trace(),
    )

    dp.serve_app(view)
