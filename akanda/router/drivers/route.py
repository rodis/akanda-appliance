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

from akanda.router.drivers import base


LOG = logging.getLogger(__name__)


class RouteManager(base.Manager):
    EXECUTABLE = '/sbin/route'

    def __init__(self, root_helper='sudo'):
        super(RouteManager, self).__init__(root_helper)

    def update_default(self, config):
        for net in config.networks:
            if not net.is_external_network:
                continue

            for subnet in net.subnets:
                if subnet.gateway_ip:
                    self._set_default_gateway(subnet.gateway_ip)

    def _get_default_gateway(self, version):
        current = None
        try:
            cmd_out = self.sudo('-n', 'get', version, 'default')
        except:
            # assume the route is missing and use defaults
            pass
        else:
            if 'no such process' in cmd_out.lower():
                # There is no gateway
                return None
            for l in cmd_out.splitlines():
                l = l.strip()
                if l.startswith('gateway:'):
                    return l.partition(':')[-1].strip()
        return current

    def _set_default_gateway(self, gateway_ip):
        version = '-inet'
        if gateway_ip.version == 6:
            version += '6'
        current = self._get_default_gateway(version)
        desired = str(gateway_ip)

        if not current:
            # Set the gateway
            return self.sudo('add', version, 'default', desired)
        if current != desired:
            # Update the current gateway
            return self.sudo('change', version, 'default', desired)
        # Nothing to do
        return ''
