## About

This app interfaces between the Arduino board and ThorImages software to control odor delivery to mice during *in vivo* imaging experiments.

## Demo

![](https://github.com/janeswh/odor_delivery_app/blob/master/media/demo.gif)

## Getting started

### Prerequisites

* [ThorImage](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=9072#ad-image-0)
* [arduino-cli](https://github.com/arduino/arduino-cli) - packaged in the .exe

### [User Guide](https://github.com/janeswh/odor_delivery_app/blob/master/instructions.md)

### Packaging command
1. Activate conda environment imaging using Anaconda Navigator or Anaconda Prompt with command `conda activate imaging`
2. cd to `C:\Users\User\Documents\odor_delivery_app\src` and run command `flet pack main.py --add-data "arduino_sketch;arduino_sketch" --add-data "components;components" --add-data "blank_sketch;blank_sketch" --add-data "resources;resources" --name="Odor Delivery App" --icon resources/odor-delivery-app.ico`