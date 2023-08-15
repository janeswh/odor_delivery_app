## About

This app interfaces between the Arduino board and ThorImages software to control odor delivery to mice during *in vivo* imaging experiments.

## Getting started

1. Make sure ThorImage is running.
2. Open "Odor Delivery App.exe" on the Desktop, and you should see this screen:  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step2.png)

3. Click on "Open Directory" and select the folder where your acquired ThorImages will be saved to. It should be named correctly in the format YYMMDD--123456-7-8_ROIX, where 123456-7-8 is the animal ID, and X is the ROI number. Please make sure that you've selected the correct folder for each experiment, because all solenoid order/timing info will be named according to the information contained in the folder name.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step3.png)

4. Enter your experiment settings and click "Save". 
    - To test odors, select the Odor panel type, set Type of trials to single, and Select the single trial odor number (e.g. 1 is ethyl butyrate).  
    ![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step4_odorpanel.png)

    - For the odor panel, select the Odor panel type, set Type of trials to Multiple, # of odors to 8 and #Trials/odor to 3. Typically you won't change the default odor duration of 1 or the default time between odors of 10.  
    ![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step4_singleodor.png)

    The Trial order will be displayed in a table below. If you need to change any settings, click "Reset Settings", enter new settings, and "Save" again. You can also click "Randomize Again" to shuffle the trial order.
    ![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step4_trialorder.png)

    Once you're happy with all the settings, click "Start Experiment".  
    
5. As soon as you click start, the trial order will be saved to a csv file in your selected experiment folder. In the app, a new section "Experiment Progress" will appear, and a message will display briefly saying that the arduino port has been opened. This takes a few seconds. Next, it will prompt you to Start (for single trials) or Run (for a script) the experiment in ThorImage.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step5.png)

6. Once ThorImage starts image collection, the app will display a progress bar showing each step of odor delivery.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step6.png)

7. You can click on "Show output log" to see a scrollable box containing a timestamped history of the odor delivery steps.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step7.png)

8. Once the experiment is finished, the solenoid timings will be saved to a csv file in the experiment folder, and a dialogue box will display:  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step8.png)

9. You can either reset all settings to start a new experiment, or click "No" if you want to see or reuse your current experiment settings. You can click "Reset Settings" at any time.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step9.png)

10. To collect another image for the same ROI, you will need to click on "Open Directory" again. It will default to the previously selected folder, so you can just click 'Select Folder' in the bottom right. If you forgot to do this, the Save Settings button will be grayed out.

11. To collect images for an additional ROI, make sure that you select the corresponding folder for that ROI. This is important because the solenoid order csv file naming is based on the folder name.

12. To collect images for an additional mouse, ensure that you are selecting the folder for the correct mouse ID. Again, this is important for solenoid order file naming.

13. If you need to stop the odor delivery before it has completed, press "Abort Experiment", then click Yes in the confirm prompt window. All completed solenoid timings (until when experiment was stopped) will be saved to a csv file.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step13.png)

14. After you abort an experiment, you can either click "Reset Settings" to enter new settings, or just click "Start Experiment" again to rerun the experiment with unchanged settings.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step14.png)

15. Solenoid order and timing csv files will be saved in your selected experimental folder, e.g. `...solenoid_order_230810-095958.csv` means that the odor delivery experiment was started on August 10, 2023 at 09:59:58 am.  
![](https://github.com/janeswh/odor_delivery_app/blob/master/media/step15.png)
