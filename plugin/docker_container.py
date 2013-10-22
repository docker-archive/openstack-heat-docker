# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013 dotCloud, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import time

from heat.engine import resource
from heat.openstack.common.gettextutils import _
from heat.openstack.common import log as logging

import docker


logger = logging.getLogger(__name__)


class Docker(resource.Resource):

    properties_schema = {
        'DockerEndpoint': {
            'Type': 'String',
            'Default': None,
            'Description': _('Docker daemon endpoint (by default the local '
                             'docker daemon will be used)')
        },
        'Hostname': {
            'Type': 'String',
            'Default': '',
            'Description': _('Hostname of the container')
        },
        'User': {
            'Type': 'String',
            'Default': '',
            'Description': _('Username or UID')
        },
        'Memory': {
            'Type': 'Integer',
            'Default': 0,
            'Description': _('Memory limit (Bytes)')
        },
        'AttachStdin': {
            'Type': 'Boolean',
            'Default': False,
        },
        'AttachStdout': {
            'Type': 'Boolean',
            'Default': True
        },
        'AttachStderr': {
            'Type': 'Boolean',
            'Default': True
        },
        'PortSpecs': {
            'Type': 'List',
            'Default': None
        },
        'Privileged': {
            'Type': 'Boolean',
            'Default': False
        },
        'Tty': {
            'Type': 'Boolean',
            'Default': False
        },
        'OpenStdin': {
            'Type': 'Boolean',
            'Default': False
        },
        'StdinOnce': {
            'Type': 'Boolean',
            'Default': False
        },
        'Env': {
            'Type': 'List',
            'Default': None
        },
        'Cmd': {
            'Type': 'List',
            'Default': [],
            'Description': _('Command to run after spawning the container')
        },
        'Dns': {
            'Type': 'List',
            'Default': None
        },
        'Image': {
            'Type': 'String',
            'Required': True,
            'Description': _('Image name')
        },
        'Volumes': {
            'Type': 'Map',
            'Default': {}
        },
        'VolumesFrom': {
            'Type': 'String',
            'Default': ""
        },
        'Privileged': {
            'Type': 'Boolean',
            'Default': False
        },
    }

    attributes_schema = {
        'Info': _('Container info'),
        'NetworkInfo': _('Container network info'),
        'NetworkIp': _('Container ip address'),
        'NetworkTcpPorts': _('Container TCP ports'),
        'NetworkUdpPorts': _('Container UDP ports'),
        'Logs': _('Container logs'),
        'LogsHead': _('Container first logs line'),
        'LogsTail': _('Container last logs line')
    }

    def __init__(self, *args, **kwargs):
        super(Docker, self).__init__(*args, **kwargs)
        self._client_class = kwargs.get('client_class', docker.Client)
        self._client = self._client_class()

    def get_client(self):
        client = self._client
        endpoint = self.properties.get('DockerEndpoint')
        if endpoint:
            client = self._client_class(endpoint)
        return client

    def _container_networkinfo(self, client, resource_id):
        info = client.inspect_container(self.resource_id)
        networkinfo = info['NetworkSettings']
        tcp = ','.join(networkinfo['PortMapping']['Tcp'].values())
        udp = ','.join(networkinfo['PortMapping']['Udp'].values())
        networkinfo['TcpPorts'] = tcp
        networkinfo['UdpPorts'] = udp
        return networkinfo

    def _resolve_attribute(self, name):
        if not self.resource_id:
            return
        client = self.get_client()
        if name == 'Info':
            return client.inspect_container(self.resource_id)
        networkinfo = self._container_networkinfo(client, self.resource_id)
        if name == 'NetworkInfo':
            return networkinfo
        if name == 'NetworkIp':
            return networkinfo['Gateway']
        if name == 'NetworkTcpPorts':
            return networkinfo['TcpPorts']
        if name == 'NetworkUdpPorts':
            return networkinfo['UdpPorts']
        logs = self._wait_logs(client, self.resource_id)
        if name == 'Logs':
            return logs
        if name == 'LogsHead':
            return logs.split('\n')[0]
        if name == 'LogsTail':
            return logs.split('\n').pop()

    def _wait_logs(self, client, container_id, wait=10):
        # NOTE(samalba): Give maximum 10 seconds to the containers to display
        # logs, so we assumed it started
        wait = float(wait)
        step = 0.3
        count = 0.0
        logs = None
        while not logs and count < (wait / step):
            logs = client.logs(container_id)
            time.sleep(step)
            count += step
        return logs

    def handle_create(self):
        args = {
            'image': self.properties['Image'],
            'command': self.properties['Cmd'],
            'hostname': self.properties['Hostname'],
            'user': self.properties['User'],
            'stdin_open': self.properties['OpenStdin'],
            'tty': self.properties['Tty'],
            'mem_limit': self.properties['Memory'],
            'ports': self.properties['PortSpecs'],
            'environment': self.properties['Env'],
            'dns': self.properties['Dns'],
            'volumes': self.properties['Volumes'],
            'volumes_from': self.properties['VolumesFrom'],
            'privileged': self.properties['Privileged'],
        }
        client = self.get_client()
        result = client.create_container(**args)
        container_id = result['Id']
        client.start(container_id)
        self._wait_logs(client, container_id)
        self.resource_id_set(container_id)

    def handle_delete(self):
        if self.resource_id is None:
            return
        client = self.get_client()
        try:
            client.kill(self.resource_id)
        except RuntimeError as e:
            logger.warning(_('Cannot kill the container: %s'), e)
        finally:
            self.resource_id_set(None)

    def handle_suspend(self):
        if not self.resource_id:
            return
        client = self.get_client()
        client.stop(self.resource_id)

    def handle_resume(self):
        if not self.resource_id:
            return
        client = self.get_client()
        client.start(self.resource_id)


def resource_mapping():
    return {
        'OS::Heat::Docker': Docker
    }
