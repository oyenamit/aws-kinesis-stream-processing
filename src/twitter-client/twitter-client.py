# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (C) 2020 Namit Bhalla (oyenamit@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>
#
# ***** END LICENSE BLOCK *****



import boto3
import json
import os
import sys
from TwitterAPI import TwitterAPI

# Environment variable names
strTwitterApiConsumerKey    = 'TWITTER_API_CONSUMER_KEY'
strTwitterApiConsumerSecret = 'TWITTER_API_CONSUMER_SECRET'
strTwitterApiTokenKey       = 'TWITTER_API_TOKEN_KEY'
strTwitterApiTokenSecret    = 'TWITTER_API_TOKEN_SECRET'
strAwsAccessKeyId           = 'AWS_ACCESS_KEY_ID'
strAwsSecretKey             = 'AWS_SECRET_KEY'
strAwsRegion                = 'AWS_REGION'
strAwsStreamName            = 'AWS_STREAM_NAME'

# Ensure environment variables have been set
try:
    # Twitter OAuth Tokens
    consumer_key        = os.environ[strTwitterApiConsumerKey]
    consumer_secret     = os.environ[strTwitterApiConsumerSecret]
    access_token_key    = os.environ[strTwitterApiTokenKey]
    access_token_secret = os.environ[strTwitterApiTokenSecret]

    # AWS Credentials
    aws_access_key      = os.environ[strAwsAccessKeyId]
    aws_secret_key      = os.environ[strAwsSecretKey]

    # AWS Region and Kinesis Stream Name
    aws_region          = os.environ[strAwsRegion]
    aws_stream_name     = os.environ[strAwsStreamName]

except KeyError:
    print('Error! One or more of the following environment variables are not set:')
    print(strTwitterApiConsumerKey)
    print(strTwitterApiConsumerSecret)
    print(strTwitterApiTokenKey)
    print(strTwitterApiTokenSecret)
    print(strAwsAccessKeyId)
    print(strAwsSecretKey)
    print(strAwsRegion)
    print(strAwsStreamName)
    sys.exit(1)


# Ensure filterText is provided as a command-line argument
if len(sys.argv) < 2:
    print('Error! Filter keyword for tweets not provided as a command-line argument');
    sys.exit(1);


# Setting up Twitter and Kinesis objects
api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
kinesis = boto3.client('kinesis', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)

# Filter and track tweets by specific keyword
filterText = sys.argv[1]
r = api.request('statuses/filter', {'track': filterText})

# Write new tweets into Kinesis
for item in r:
   if 'text' in item:
        kinesis.put_record(StreamName=aws_stream_name, Data=json.dumps(item), PartitionKey=item['user']['screen_name'])
        print(item['text'])
        print('---------------------------')

