# Copyright 2014 DreamHost, LLC
#
# Author: DreamHost, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import logging
import os
import time

from akanda.router.drivers import base
from akanda.router import utils


LOG = logging.getLogger(__name__)
CONF_DIR = '/etc/dnsmasq.d'
RC_PATH = '/etc/rc.d/dnsmasq'
DEFAULT_LEASE = 86400


class DHCPManager(base.Manager):
    def __init__(self, root_helper='sudo'):
        super(DHCPManager, self).__init__(root_helper)

    def update_network_dhcp_config(self, ifname, network):
        if network.is_tenant_network:
            config_data = self._build_dhcp_config(ifname, network)
        else:
            config_data = self._build_disabled_config(ifname)

        file_path = os.path.join(CONF_DIR, '%s.conf' % ifname)
        utils.replace_file('/tmp/dnsmasq.conf', config_data)
        utils.execute(['mv', '/tmp/dnsmasq.conf', file_path], self.root_helper)

    def _build_disabled_config(self, ifname):
        return 'except-interface=%s\n' % ifname

    def _build_dhcp_config(self, ifname, network):
        config = ['interface=%s' % ifname]

        for index, subnet in enumerate(network.subnets):
            if not subnet.dhcp_enabled:
                continue

            tag = '%s_%s' % (ifname, index)

            config.append('dhcp-range=set:%s,%s,%s,%ss' %
                          (tag,
                           subnet.cidr.network,
                           'static',
                           DEFAULT_LEASE))

            if subnet.cidr.version == 6:
                option_label = 'option6'
            else:
                option_label = 'option'

            config.extend(
                'dhcp-option=tag:%s,%s:dns-server,%s' % (tag, option_label, s)
                for s in subnet.dns_nameservers
            )

            config.extend(
                'dhcp-option=tag:%s,%s:classless-static-route,%s,%s' %
                (tag, option_label, r.destination, r.next_hop)
                for r in subnet.host_routes
            )

        config.extend(
            'dhcp-host=%s,%s,%s' % (
                a.mac_address,
                ','.join('[%]' % ip if ':' in ip else ip for ip in
                         a.dhcp_addresses),
                a.hostname)
            for a in network.address_allocations
        )

        return '\n'.join(config)

    def restart(self):
        try:
            utils.execute(['/etc/rc.d/dnsmasq', 'stop'], self.root_helper)
        except:
            pass

        # dnsmasq can get confused on startup
        remaining = 5
        while remaining:
            remaining -= 1
            try:
                utils.execute(['/etc/rc.d/dnsmasq', 'start'], self.root_helper)
                return
            except Exception:
                if remaining <= 0:
                    raise
                time.sleep(1)
