import datetime
import numpy as np
import boto3

import aws_spot_bot.user_config as uconf


class AZZone():

    def __init__(self, region, name):
        self.region = region
        self.name = name
        self.client = boto3.setup_default_session(region_name=self.region)
        self.client = boto3.client('ec2', aws_access_key_id=uconf.AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=uconf.AWS_SECRET_ACCESS_KEY)
        self.spot_pricing_history = None
        self.score = None

    @property
    def spot_price_variance(self):
        prices = [float(record['SpotPrice']) for record in self.spot_pricing_history]
        return np.var(prices)

    @property
    def spot_price_mean(self):
        prices = [float(record['SpotPrice']) for record in self.spot_pricing_history]
        return np.mean(prices)

    @property
    def current_price(self):
        if self.spot_pricing_history:
            return float(self.spot_pricing_history[0]['SpotPrice'])
        elif self.spot_pricing_history == []:
            return None
        else:
            raise Exception("You must fetch the history before calling this property")

    def get_spot_pricing_history(self, instance_types, product_descriptions=['Linux/UNIX']):
        """ Returns the spot price history given a specified AZ and region."""
        print "Getting spot prices for", self.name

        response = self.client.describe_spot_price_history(
            DryRun=False,
            StartTime=datetime.datetime.now() - datetime.timedelta(days=7),
            EndTime=datetime.datetime.now(),
            InstanceTypes=instance_types,
            AvailabilityZone=self.name,
            ProductDescriptions=product_descriptions)

        self.spot_pricing_history = response.get('SpotPriceHistory', [])
        return response

    def calculate_score(self, instance_types, bid, update=False):
        if self.spot_pricing_history is None:
            self.get_spot_pricing_history(instance_types)
        elif update:
            self.get_spot_pricing_history(instance_types)

        # TODO: This should be removed but I am lazy and this is easier than catching exceptions
        # @jgre can you fix?
        if self.spot_pricing_history == []:
            return -1e10

        # We are not interested in this AZ if its more than the bid, so lets just return
        if self.current_price > bid:
            return 0

        # Here we multiply each item by a weight.
        # These weights are arbitrary and probably not ideal.
        # There is much room for improvement on this scoring algorithm, but this algorithm
        # works for most light use cases. Feel free to contribute!
        current_price_s = bid - self.current_price
        variance_s = -5 * (self.spot_price_variance * self.spot_price_mean)
        mean_s = 0.5 * (bid - self.spot_price_mean)

        self.score = current_price_s + variance_s + mean_s
        return self.score
