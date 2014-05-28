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


"""
Blueprint for the "status" portion of the version 1 of the API.
"""
from akanda.router import utils
from akanda.router.manager import manager

blueprint = utils.blueprint_factory(__name__)

@blueprint.route('/')
@utils.json_response
def status():
    """ Return router healt status """

    retval = {}
    retval['interfaces'] = manager.get_interfaces()
    return retval
