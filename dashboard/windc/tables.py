# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
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


# TO DO: clear extra modules

import re
import logging

from django import shortcuts
from django import template
from django.core import urlresolvers
from django.template.defaultfilters import title
from django.utils.http import urlencode
from django.utils.translation import string_concat, ugettext_lazy as _

from horizon.conf import HORIZON_CONFIG
from horizon import exceptions
from horizon import messages
from horizon import tables
from horizon.templatetags import sizeformat
from horizon.utils.filters import replace_underscores

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.access_and_security \
        .floating_ips.workflows import IPAssociationWorkflow


LOG = logging.getLogger(__name__)


class CreateService(tables.LinkAction):
    name = "CreateService"
    verbose_name = _("Create Service")
    url = "horizon:project:windc:create"
    classes = ("btn-launch", "ajax-modal")

    def allowed(self, request, datum):
        return True

    def action(self, request, service):
        # FIX ME
        api.windc.services_create(request, service)


class CreateDataCenter(tables.LinkAction):
    name = "CreateDataCenter"
    verbose_name = _("Create Windows Data Center")
    url = "horizon:project:windc:create_dc"
    classes = ("btn-launch", "ajax-modal")

    def allowed(self, request, datum):
        return True

    def action(self, request, datacenter):
        api.windc.datacenters_create(request, datacenter)


class DeleteDataCenter(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Delete")
    data_type_singular = _("Data Center")
    data_type_plural = _("Data Center")
    classes = ('btn-danger', 'btn-terminate')

    def allowed(self, request, datum):
        return True

    def action(self, request, datacenter_id):
        datacenter = api.windc.datacenters_get(request, datacenter_id)
        api.windc.datacenters_delete(request, datacenter)


class DeleteService(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Delete")
    data_type_singular = _("Service")
    data_type_plural = _("Service")
    classes = ('btn-danger', 'btn-terminate')

    def allowed(self, request, datum):
        return True

    def action(self, request, service_id):
        ############## FIX ME:
        link = request.__dict__['META']['HTTP_REFERER']
        datacenter_id = re.search('windc/(\S+)', link).group(0)[6:-1]
        ##############
        datacenter = api.windc.datacenters_get(request, datacenter_id)
        
        api.windc.services_delete(request, datacenter, service_id)


class EditService(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:project:windc:update"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, instance):
        return True


class ShowDataCenterServices(tables.LinkAction):
    name = "edit"
    verbose_name = _("Services")
    url = "horizon:project:windc:services"

    def allowed(self, request, instance):
        return True


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, instance_id):
        instance = api.nova.server_get(request, instance_id)
        instance.full_flavor = api.nova.flavor_get(request,
                                                   instance.flavor["id"])
        return instance


class WinDCTable(tables.DataTable):
    name = tables.Column("name",
                         link=("horizon:project:windc:services"),
                         verbose_name=_("Name"))

    class Meta:
        name = "windc"
        verbose_name = _("Windows Data Centers")
        row_class = UpdateRow
        table_actions = (CreateDataCenter,)
        row_actions = (ShowDataCenterServices,DeleteDataCenter)


class WinServicesTable(tables.DataTable):
    name = tables.Column('dc_name', verbose_name=_('Name'))
    _type = tables.Column('type', verbose_name=_('Type'))
    status = tables.Column('status', verbose_name=_('Status'))

    class Meta:
        name = "services"
        verbose_name = _("Services")
        row_class = UpdateRow
        table_actions = (CreateService,)
        row_actions = (EditService, DeleteService)