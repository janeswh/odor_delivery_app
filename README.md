## About

This app interfaces between the Arduino board and ThorImages software to control odor delivery to mice during *in vivo* imaging experiments.

## Getting started

1. Make sure ThorImages is running.
2. Open "Odor Delivery App.exe" on the Desktop, and you should see this screen:  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/start.png)

3. Click on "Open Directory" and select the folder where your acquired ThorImages will be saved to. It should be named correctly in the format YYMMDD--123456-7-8_ROIX, where 123456-7-8 is the animal ID, and X is the ROI number. Please make sure that you've selected the correct folder for each experiment, because all solenoid order/timing info will be named according to the information contained in the folder name.
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/pick_folder.png)

4. Enter your experiment settings and click "Save". The Trial order will be displayed in a table below. If you need to change any settings, click "Reset Settings", enter new settings, and "Save" again. You can also click "Randomize Again" to shuffle the trial order. Once you're happy with all the settings, click "Start Experiment".
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/trial_order.png)

5. As soon as you click start, the trial order will be saved to a csv file in your selected experiment folder. In the app, a new section "Experiment Progress" will appear, and a message will display briefly saying that the arduino port has been opened. Next, it will prompt you to Start or Run the experiment on ThorImages.
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/press_start.png)

6. Once ThorImages starts, the app will display a progress bar showing each step of odor delivery.
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/progress.png)

7. You can click on "Show output log" to see a scrollable box containing a timestamped history of the odor delivery steps.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/log.png)

8. Once the experiment is finished, the solenoid timings will be saved to a csv file in the experime folder, and a dialogue box will display:  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/complete.png)

9. You can either reset all settings to start a new experiment, or click "No" if you want to see your current experiment settings. You can click "Reset Settings" at any time.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/complete_screen.png)

10. If you need to stop the odor delivery before it has completed, press "Abort Experiment", then click Yes in the confirm prompt window. All completed solenoid timings (until when experiment was stopped) will be saved to a csv file.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/abort.png)

11. After you abort an experiment, you can either click "Reset Settings" to enter new settings, or just click "Start Experiment" again to rerun the experiment with unchanged settings.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/aborted.png)

12. Solenoid order and timing csv files will be saved in your selected experimental folder, e.g. ...solenoid_order_230718-131507.csv" means that the odor delivery experiment was started on July 18, 2023 at 13:15:07 pm.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/csv_files.png)
