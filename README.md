## AWS-SPOT-BOT
An automated tool for finding and launching the cheapest AWS spot instances.


#### !! DISCLAIMER!!
This library is something I threw together in less than day for my personal use. Its very useful so I thought I should share it. The code is not well tested and is not very configurable. Feel free to contribute.

### TODO
- add a check to report how many instances you currently have running
- setup pip
- how far back do we need to look? right now its just looking back a few hours, should we loop the callbacks
- search the project for "todo" and fix those occurrences 


#### Configuration Options
- Acceptable Regions
- Max Bid price
- Minimum time requirements
- Acceptable Instance Types
- AMI
- Use elastic IPs

The tool will find the best option for you, boot the instances and then print out their IP addresses.

#### Installation
`$ pip install aws-spot-bot`
Setup your credentials see http://boto3.readthedocs.io/en/latest/guide/quickstart.html

#### Usage
awspotbot --qty=1 --bid=0.25 --instance-type='g2.2xlarge'


### License
MIT