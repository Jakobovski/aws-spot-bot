# This repository is no longer relevant given the changes to AWS spot instance pricing.

## AWS-SPOT-BOT
A tool for finding and launching the cheapest and most reliable AWS spot instances. Using an unsophisticated algorithm it launches instances in regions that have have a low price and a low price variance so that your instance is less likely to get shut down by changes in demand. It is primarily intended for machine learning researchers to be able to spawn GPU instances without incurring large costs.

### Usage
Edit `user_config.py` to your specifications then run `main.py`.   

### Ansible
For convenience Ansible is integrated into this tool. This allows one to automatically run tasks on the servers after they are launched.
This saves one from needing to rebuild AMIs every time a change is required. See `user_config.py` and `main.py` for more details. Be warned that 
hosts are not automatically removed from the Ansible `hosts` file. 


### DISCLAIMER
This library is something I threw together for my personal use. The code is not well tested and is in no way production worthy. Feel free to contribute.


### Requested contributions
- add a check to report how many instances you currently have running
- add to pypy
- search the project for "todo" and improve those items


### License
MIT
