from utils import pricing_util
from utils.aws_spot_instance import AWSSpotInstance
import aws_spot_bot.user_config as uconf


def launch_instances(qty):
    """Launches QTY instances and returns the instance objects."""
    best_az = pricing_util.get_best_az()
    launched_instances = []
    print "Best availability zone:", best_az.name

    for idx in range(qty):
        print '>> Launching instance #%s' % (idx)
        si = AWSSpotInstance(best_az.region, best_az.name, uconf.INSTANCE_TYPES[0], uconf.AMI_ID, uconf.BID)
        si.request_instance()
        si.get_ip()
        launched_instances.append(si)

    return launched_instances


if __name__ == '__main__':
    instances = launch_instances(uconf.QTY_INSTANCES)

    for si in instances:
        si.open_in_browser()
        si.open_ssh_term()
