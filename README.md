## AWS-SPOT-BOT
A tool for automating the finding and launching of the cheapest and most reliable AWS spot instances. It is primarily intended for machine learning researchers to be able to spawn multiple GPU instances without incurring large costs.


#### Configuration Options
- Acceptable Regions
- Max Bid price
- Minimum time requirements
- Acceptable Instance Types
- AMI
- Use elastic IPs


#### Ansible
For convenience Ansible is integrated into this tool. This allows one to automatically run tasks on the servers after they are launched.
This saves one from needing to rebuild AMIs every time a change is required. See `userconfig.py` and `main.py` for more details. Be warned that 
hosts are not automatically removed from the Ansible `hosts` file. 


#### DISCLAIMER
This library is something I threw together for my personal use. The code is not well tested and is in no way production worthy. Feel free to contribute.


### Requested contributions
- add a check to report how many instances you currently have running
- add to pypy
- search the project for "todo" and improve those items 


#### Usage
Edit `user_config.py` to your specifications then run `main.py`.   

### License
MIT