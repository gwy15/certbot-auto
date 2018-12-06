#! /usr/bin/python3
import json
import os
from pathlib import Path

from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import AddDomainRecordRequest


class Hook(object):
    def __init__(self):
        # base = Path(Path(__file__).absolute()).parent
        base = Path(__file__).resolve().parent
        config = base / 'config.json'

        if not config.exists():
            raise RuntimeError('setup config.json first.')

        config = json.load(open(config))

        self.client = AcsClient(
            config['access-key-id'],
            config['access-key-secret'],
            config['region-id']
        )

    @staticmethod
    def getBaseDomain(domain):
        return '.'.join(domain.split('.')[-2:])

    def setDomainRRAsValue(self, domain, RR, value):
        print('Set RR {} as value {} for domain {}.'.format(RR, value, domain))
        request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
        request.set_DomainName(self.getBaseDomain(domain))
        response = json.loads(
            self.client.do_action_with_exception(request).decode())

        for record in response['DomainRecords']['Record']:
            if record['Type'] == 'TXT' and record['RR'] == RR and record['Value'] == value:
                print('value already exists.')
                return

        print('Create a new record.')
        request = AddDomainRecordRequest.AddDomainRecordRequest()
        request.set_DomainName(self.getBaseDomain(domain))

        request.set_Type('TXT')
        request.set_RR(RR)
        request.set_Value(value)
        response = json.loads(
            self.client.do_action_with_exception(request).decode())
        print(response)


def main():
    domain = '.'.join(os.environ['CERTBOT_DOMAIN'].split('.')[-2:])
    value = os.environ['CERTBOT_VALIDATION']
    rr = '.'.join(
        ('_acme-challenge.' + os.environ['CERTBOT_DOMAIN']).split('.')[:-2])

    hook = Hook()
    hook.setDomainRRAsValue(domain, rr, value)


if __name__ == '__main__':
    main()
