
# =============== Default configs ==================
AWS_REGIONS = ['us-east-1', 'us-west-2', 'us-west-1', 'eu-west-1', 'eu-central-1', 'ap-southeast-1',
               'ap-northeast-1', 'ap-northeast-2', 'ap-southeast-2', 'sa-east-1']
AZ_PICKLE_EXPIRE_TIME_DAYS = 30
SPOT_PRICING_PICKLE_EXPIRE_SEC = 30 * 60


# =============== Personal config ==================
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
KEY_NAME = 'main_key'
SECURITY_GROUP_ID = ''
SECURITY_GROUP = 'gpu-security-group'
AMI_ID = 'ami-622eda0f'
INSTANCE_TYPES = ['g2.2xlarge']
BID = 0.25
SSH_USER_NAME = 'ubuntu'
QTY_INSTANCES = 1
