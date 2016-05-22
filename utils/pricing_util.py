from operator import attrgetter
import os
import pickle
import datetime

import boto3

from az_zone import AZZone
import aws_spot_bot.user_config as uconf


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def generate_region_AZ_dict():
    """ Generates a dict of {'region': [availability_zones, az2]} """
    print "Getting all regions and AZ's... (this may take some time)"
    region_az = {}
    for region in uconf.AWS_REGIONS:
        client = boto3.setup_default_session(region_name=region)
        client = boto3.client('ec2', aws_access_key_id=uconf.AWS_ACCESS_KEY_ID, aws_secret_access_key=uconf.AWS_SECRET_ACCESS_KEY)

        avail_zones = []
        for zone in client.describe_availability_zones()['AvailabilityZones']:
            if zone['State'] == 'available':
                avail_zones.append(zone['ZoneName'])
        region_az[region] = avail_zones
        print ">>", region

    return region_az


def get_initialized_azs():
    az_pickle_fn = "az_dict.pickle"
    az_objects_fn = 'az_objs_list.pickle'
    last_valid_AZ_time = datetime.datetime.now() - datetime.timedelta(days=uconf.AZ_PICKLE_EXPIRE_TIME_DAYS)
    last_valid_spot_time = datetime.datetime.now() - datetime.timedelta(seconds=uconf.SPOT_PRICING_PICKLE_EXPIRE_SEC)

    # Loads AZs from pickle if it exists and is less than 30 days old, else fetches them
    if os.path.isfile(az_pickle_fn) and modification_date(az_pickle_fn) > last_valid_AZ_time:
        az_dict = pickle.load(open(az_pickle_fn, "rb"))
    else:
        az_dict = generate_region_AZ_dict()
        pickle.dump(az_dict, open(az_pickle_fn, "wb"))

    # Loads AZs from pickle if it exists and is less than 30 days old, else fetches them
    if False and os.path.isfile(az_objects_fn) and modification_date(az_objects_fn) > last_valid_spot_time:
        az_objects = pickle.load(open(az_objects_fn, "rb"))
    else:
        az_objects = []
        # Get the spot pricing for each AZ
        for region, azs in az_dict.iteritems():
            for az in azs:
                az_obj = AZZone(region, az)
                az_objects.append(az_obj)

        # pickle.dump(az_objects, open(az_objects_fn, "wb"))

    return az_objects


def get_best_az():
    azs = get_initialized_azs()

    for az in azs:
        az.calculate_score(uconf.INSTANCE_TYPES, 0.65)

    # Sort the AZs by score and return the best one
    sorted_azs = sorted(azs, key=attrgetter('score'))

    for az in sorted_azs:
        print az.name
        print '>> price:', az.current_price
        print '>> mean:', az.spot_price_mean
        print '>> variance:', az.spot_price_variance
        print '>> score:', az.score

    return sorted_azs[-1]
