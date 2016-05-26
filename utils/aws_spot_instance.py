import os
import random
import time
import webbrowser
import socket
import datetime

import appscript
import boto3

import aws_spot_bot.user_config as uconf


class AWSSpotInstance():

    def __init__(self, region, az_zone, instance_type, ami_id, bid):
        self.random_id = str(random.random() * 1000)
        self.az_zone = az_zone
        self.region = region
        self.instance_type = instance_type
        self.ip = None
        self.bid = bid
        self.ami_id = ami_id
        self.key_name = uconf.KEY_NAME
        self.security_group_id = uconf.SECURITY_GROUP_ID

        # == Boto3 related tools ==
        boto3.setup_default_session(region_name=self.region)
        self.client = boto3.client('ec2', aws_access_key_id=uconf.AWS_ACCESS_KEY_ID, aws_secret_access_key=uconf.AWS_SECRET_ACCESS_KEY)
        session = boto3.session.Session(aws_access_key_id=uconf.AWS_ACCESS_KEY_ID, aws_secret_access_key=uconf.AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
        self.ec2_instance = session.resource('ec2')

        # == Values that we need to wait to get from AWS ==
        self.spot_instance_request_id = None
        self.instance_id = None
        self.status_code = None
        self.ip = None

    def request_instance(self):
        """Boots the instance on AWS"""
        print ">> Requesting instance"
        response = self.client.request_spot_instances(
            SpotPrice=str(self.bid),
            ClientToken=self.random_id,
            InstanceCount=1,
            Type='one-time',
            # ValidUntil=datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 100),
            LaunchSpecification={
                'ImageId': self.ami_id,
                'KeyName': self.key_name,
                'InstanceType': self.instance_type,
                'Placement': {
                    'AvailabilityZone': self.az_zone,
                },
                'EbsOptimized': False,
                'SecurityGroupIds': [
                    self.security_group_id
                ]
            }
        )
        self.spot_instance_request_id = response.get('SpotInstanceRequests')[0].get('SpotInstanceRequestId')
        return response

    def get_spot_request_status(self):
        print ">> Checking instance status"
        response = self.client.describe_spot_instance_requests(
            SpotInstanceRequestIds=[self.spot_instance_request_id],
        )
        self.status_code = response.get('SpotInstanceRequests')[0].get('Status').get('Code')
        self.instance_id = response.get('SpotInstanceRequests')[0].get('InstanceId')
        return {'status_code': self.status_code, 'instance_id': self.instance_id}

    def get_ip(self):
        if self.ip:
            return self.ip

        if not self.status_code:
            self.get_spot_request_status()

        for idx in range(100):
            if not self.instance_id and 'pending' in self.status_code:
                time.sleep(3)
                self.get_spot_request_status()
            else:
                self.ip = self.ec2_instance.Instance(self.instance_id).public_ip_address
                break

        # TODO: improve this
        if not self.ip:
            raise Exception('There is no public IP address for this instance... Maybe the bid failed..')

        return self.ip

    def terminate(self):
        """Terminates the instance on AWS"""
        pass

    def open_ssh_term(self):
        """Opens your default terminal and starts SSH session to the instance"""
        # TODO. This wont work on non osx machines.
        appscript.app('Terminal').do_script('ssh ' + uconf.SSH_USER_NAME + '@' + self.get_ip())

    def open_in_browser(self, port='80'):
        """Opens the instance in your browser to the specified port.
        Default port is Jupyter server
        """
        webbrowser.open_new_tab('http://' + self.ip + ':' + port)

    def add_to_ansible_hosts(self):
        path = os.path.dirname(os.path.dirname(__file__))
        with open(path + '/ansible/hosts', 'a') as file:
            file.write(str(self.ip) + '\n')

    def wait_for_http(self, port=80, timeout=uconf.SERVER_TIMEOUT):
        """Waits until port 80 is open on this instance.
        This is a useful way to check if the system has booted.
        """
        self.wait_for_port(port, timeout)

    def wait_for_ssh(self, port=22, timeout=uconf.SERVER_TIMEOUT):
        """Waits until port 22 is open on this instance.
        This is a useful way to check if the system has booted.
        """
        self.wait_for_port(port, timeout)

    def wait_for_port(self, port, timeout=uconf.SERVER_TIMEOUT):
        """Waits until port is open on this instance.
        This is a useful way to check if the system has booted and the HTTP server is running.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start = datetime.datetime.now()
        print ">> waiting for port", port

        if not self.get_ip():
            raise Exception("Error getting IP for this instance. Instance must have an IP before calling this method.")

        while True:
            # We need this try block because depending on the parameters the system will cause the connection
            # to timeout early.
            try:
                if sock.connect_ex((self.get_ip(), port)):
                    # we got a connection, lets return
                    return
                else:
                    time.sleep(3)
            except:
                # TODO: catch the timeout exception and ignore that, but every other exception should be raised
                # The system timeout, no problem
                pass

            if (datetime.datetime.now() - start).seconds > timeout:
                print (datetime.datetime.now() - start).seconds
                raise Exception("Connection timed out. Try increasing the timeout amount, or fix your server.")

        print ">> port %s is live" % (port)

if __name__ == '__main__':
    import pricing_util
    # best_az = pricing_util.get_best_az()
    # print best_az.region
    # print best_az.name
    region = 'us-east-1'
    az_zone = 'us-east-1d'
    instance_type = uconf.INSTANCE_TYPES[0]
    si = AWSSpotInstance(region, az_zone, instance_type, uconf.AMI_ID, uconf.BID)
    response = si.request_instance()
    print si.get_ip()
    si.wait_for_ssh()
    si.wait_for_http()

    si.open_in_browser()
    si.open_ssh_term()
