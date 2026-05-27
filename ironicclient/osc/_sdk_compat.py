#   Copyright 2025 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""Backward-compatibility managers for the openstacksdk migration.

During migration from ironicclient.v1.client.Client to
openstack.baremetal.v1._proxy.Proxy, these managers are attached to the live
proxy instance by attach_compat_managers() so that existing command code that
calls client.chassis.get(), client.node.set_provision_state(), etc. continues
to work unchanged.

Each per-resource migration commit removes the corresponding manager class and
its line from attach_compat_managers(). The final cleanup commit deletes this
module entirely.
"""

from __future__ import annotations

from typing import Any

import openstack.exceptions

from ironicclient import exc
from ironicclient.common.i18n import _


class _CompatResource:
    """Wraps an openstacksdk Resource to expose ._info for backward compat."""

    def __init__(self, resource: Any) -> None:
        self._sdk_resource = resource
        self._info: dict[str, Any] = dict(resource._body)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._sdk_resource, name)


def _filter_none(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


def _reraise(e: Exception) -> None:
    raise exc.ClientException(str(e)) from e


class _AllocationManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, allocation_id: str) -> _CompatResource:
        return _CompatResource(self._proxy.get_allocation(allocation_id))

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_allocation(**kwargs))

    def delete(self, allocation_id: str) -> None:
        try:
            self._proxy.delete_allocation(allocation_id, ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def wait(self, allocation_id: str,
             timeout: int | None = None) -> _CompatResource:
        return _CompatResource(
            self._proxy.wait_for_allocation(allocation_id, timeout=timeout))

    def list(self, **kwargs: Any) -> Any:
        return self._proxy.allocations(**_filter_none(kwargs))

    def update(self, allocation_id: str, patch: list[Any]) -> None:
        self._proxy.patch_allocation(allocation_id, patch)


class _ChassisManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, chassis_id: str,
            fields: list[str] | None = None) -> _CompatResource:
        return _CompatResource(
            self._proxy.get_chassis(chassis_id, fields=fields))

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_chassis(**kwargs))

    def delete(self, chassis_id: str) -> None:
        try:
            self._proxy.delete_chassis(chassis_id, ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def list(self, detail: bool = False, **kwargs: Any) -> Any:
        return self._proxy.chassis(details=detail, **_filter_none(kwargs))

    def update(self, chassis_id: str, patch: list[Any]) -> _CompatResource:
        return _CompatResource(self._proxy.patch_chassis(chassis_id, patch))


class _ConductorManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, conductor_id: str) -> _CompatResource:
        return _CompatResource(self._proxy.get_conductor(conductor_id))

    def list(self, **kwargs: Any) -> Any:
        return self._proxy.conductors(**_filter_none(kwargs))


class _DeployTemplateManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, template_id: str,
            fields: list[str] | None = None) -> _CompatResource:
        return _CompatResource(
            self._proxy.get_deploy_template(template_id, fields=fields))

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_deploy_template(**kwargs))

    def delete(self, template_id: str) -> None:
        try:
            self._proxy.delete_deploy_template(template_id,
                                               ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def list(self, **kwargs: Any) -> Any:
        return self._proxy.deploy_templates(**_filter_none(kwargs))

    def update(self, template_id: str, patch: list[Any]) -> None:
        self._proxy.patch_deploy_template(template_id, patch)


class _DriverManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, driver_name: str,
            fields: list[str] | None = None) -> _CompatResource:
        return _CompatResource(self._proxy.get_driver(driver_name))

    def list(self, detail: bool = False, **kwargs: Any) -> Any:
        return self._proxy.drivers(details=detail, **_filter_none(kwargs))

    def properties(self, driver_name: str) -> dict[str, Any]:
        return dict(
            self._proxy.get(f'/v1/drivers/{driver_name}/properties').json())

    def raid_logical_disk_properties(
            self, driver_name: str) -> dict[str, Any]:
        return dict(
            self._proxy.get(
                f'/v1/drivers/{driver_name}/raid/logical_disk_properties'
            ).json())

    def get_vendor_passthru_methods(self, driver_name: str) -> Any:
        return self._proxy.list_driver_vendor_passthru(driver_name)

    def vendor_passthru(self, driver_name: str, method: str,
                        http_method: str = 'POST',
                        args: dict[str, Any] | None = None) -> Any:
        return self._proxy.call_driver_vendor_passthru(
            driver_name, http_method, method, body=args)


class _InspectionRuleManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, rule_id: str) -> _CompatResource:
        return _CompatResource(self._proxy.get_inspection_rule(rule_id))

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_inspection_rule(**kwargs))

    def delete(self, rule_id: str) -> None:
        try:
            self._proxy.delete_inspection_rule(rule_id, ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def list(self, **kwargs: Any) -> Any:
        return self._proxy.inspection_rules(**_filter_none(kwargs))

    def update(self, rule_id: str, patch: list[Any]) -> None:
        self._proxy.patch_inspection_rule(rule_id, patch)


class _PortManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, port_id: str,
            fields: list[str] | None = None) -> _CompatResource:
        return _CompatResource(self._proxy.get_port(port_id, fields=fields))

    def get_by_address(self, address: str,
                       fields: list[str] | None = None) -> _CompatResource:
        ports = list(self._proxy.ports(address=address, details=True))
        if not ports:
            raise exc.ClientException(
                _('No port found with address %s') % address)
        return _CompatResource(ports[0])

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_port(**kwargs))

    def delete(self, port_id: str) -> None:
        try:
            self._proxy.delete_port(port_id, ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def list(self, **kwargs: Any) -> Any:
        return self._proxy.ports(**_filter_none(kwargs))

    def update(self, port_id: str, patch: list[Any]) -> None:
        self._proxy.patch_port(port_id, patch)


class _PortgroupManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, portgroup_id: str,
            fields: list[str] | None = None) -> _CompatResource:
        return _CompatResource(
            self._proxy.get_port_group(portgroup_id, fields=fields))

    def get_by_address(self, address: str,
                       fields: list[str] | None = None) -> _CompatResource:
        portgroups = list(
            self._proxy.port_groups(address=address, details=True))
        if not portgroups:
            raise exc.ClientException(
                _('No portgroup found with address %s') % address)
        return _CompatResource(portgroups[0])

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_port_group(**kwargs))

    def delete(self, portgroup_id: str) -> None:
        try:
            self._proxy.delete_port_group(portgroup_id, ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def list(self, **kwargs: Any) -> Any:
        return self._proxy.port_groups(**_filter_none(kwargs))

    def update(self, portgroup_id: str, patch: list[Any]) -> None:
        self._proxy.patch_port_group(portgroup_id, patch)


class _RunbookManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, runbook_id: str) -> _CompatResource:
        return _CompatResource(self._proxy.get_runbook(runbook_id))

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_runbook(**kwargs))

    def delete(self, runbook_id: str) -> None:
        try:
            self._proxy.delete_runbook(runbook_id, ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def list(self, **kwargs: Any) -> Any:
        return self._proxy.runbooks(**_filter_none(kwargs))

    def update(self, runbook_id: str, patch: list[Any]) -> None:
        self._proxy.patch_runbook(runbook_id, patch)

    def get_traits(self, runbook_id: str) -> list[str]:
        return self._proxy.get(
            f'/v1/runbooks/{runbook_id}/traits').json().get('traits', [])

    def add_trait(self, runbook_id: str, trait: str) -> None:
        self._proxy.put(f'/v1/runbooks/{runbook_id}/traits/{trait}')

    def remove_trait(self, runbook_id: str, trait: str) -> None:
        self._proxy.delete(f'/v1/runbooks/{runbook_id}/traits/{trait}')

    def remove_all_traits(self, runbook_id: str) -> None:
        self._proxy.delete(f'/v1/runbooks/{runbook_id}/traits')


class _ShardManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def list(self) -> list[Any]:
        return self._proxy.get('/v1/shards').json().get('shards', [])


class _VolumeConnectorManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, vc_id: str) -> _CompatResource:
        return _CompatResource(self._proxy.get_volume_connector(vc_id))

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_volume_connector(**kwargs))

    def delete(self, vc_id: str) -> None:
        try:
            self._proxy.delete_volume_connector(vc_id, ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def list(self, **kwargs: Any) -> Any:
        return self._proxy.volume_connectors(**_filter_none(kwargs))

    def update(self, vc_id: str, patch: list[Any]) -> None:
        self._proxy.patch_volume_connector(vc_id, patch)


class _VolumeTargetManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, vt_id: str) -> _CompatResource:
        return _CompatResource(self._proxy.get_volume_target(vt_id))

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_volume_target(**kwargs))

    def delete(self, vt_id: str) -> None:
        try:
            self._proxy.delete_volume_target(vt_id, ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def list(self, **kwargs: Any) -> Any:
        return self._proxy.volume_targets(**_filter_none(kwargs))

    def update(self, vt_id: str, patch: list[Any]) -> None:
        self._proxy.patch_volume_target(vt_id, patch)


class _NodeManager:
    def __init__(self, proxy: Any) -> None:
        self._proxy = proxy

    def get(self, node_id: str,
            fields: list[str] | None = None) -> _CompatResource:
        return _CompatResource(self._proxy.get_node(node_id, fields=fields))

    def get_by_instance_uuid(self, instance_uuid: str) -> _CompatResource:
        return _CompatResource(self._proxy.find_node(instance_uuid))

    def create(self, **kwargs: Any) -> _CompatResource:
        return _CompatResource(self._proxy.create_node(**kwargs))

    def delete(self, node_id: str) -> None:
        try:
            self._proxy.delete_node(node_id, ignore_missing=False)
        except openstack.exceptions.SDKException as e:
            _reraise(e)

    def list(self, detail: bool = False, **kwargs: Any) -> Any:
        return self._proxy.nodes(details=detail, **_filter_none(kwargs))

    def update(self, node_id: str, patch: list[Any]) -> Any:
        return self._proxy.patch_node(node_id, patch)

    def set_provision_state(self, node_id: str, state: str,
                            **kwargs: Any) -> None:
        self._proxy.set_node_provision_state(node_id, state, **kwargs)

    def wait_for_provision_state(self, nodes: Any, **kwargs: Any) -> None:
        self._proxy.wait_for_nodes_provision_state(nodes, **kwargs)

    def set_boot_device(self, node_id: str, device: str,
                        persistent: bool = False) -> None:
        self._proxy.set_node_boot_device(node_id, device, persistent)

    def get_boot_device(self, node_id: str) -> dict[str, Any]:
        return self._proxy.get_node_boot_device(node_id)

    def get_supported_boot_devices(self, node_id: str) -> dict[str, Any]:
        return self._proxy.get_node_supported_boot_devices(node_id)

    def set_boot_mode(self, node_id: str, mode: str) -> None:
        self._proxy.set_node_boot_mode(node_id, mode)

    def set_secure_boot(self, node_id: str, mode: str) -> None:
        self._proxy.set_node_secure_boot(node_id, mode)

    def set_maintenance(self, node_id: str, state: bool,
                        maint_reason: str | None = None) -> None:
        if state:
            self._proxy.set_node_maintenance(node_id, reason=maint_reason)
        else:
            self._proxy.unset_node_maintenance(node_id)

    def set_power_state(self, node_id: str, state: str,
                        **kwargs: Any) -> None:
        self._proxy.set_node_power_state(node_id, state, **kwargs)

    def set_console_mode(self, node_id: str, enabled: bool) -> None:
        if enabled:
            self._proxy.enable_node_console(node_id)
        else:
            self._proxy.disable_node_console(node_id)

    def get_console(self, node_id: str) -> dict[str, Any]:
        return self._proxy.get_node_console(node_id)

    def inject_nmi(self, node_id: str) -> None:
        self._proxy.inject_nmi_to_node(node_id)

    def vif_attach(self, node_id: str, vif_id: str, **kwargs: Any) -> None:
        self._proxy.attach_vif_to_node(node_id, vif_id, **kwargs)

    def vif_detach(self, node_id: str, vif_id: str) -> None:
        self._proxy.detach_vif_from_node(node_id, vif_id)

    def vif_list(self, node_id: str) -> list[Any]:
        return self._proxy.list_node_vifs(node_id)

    def add_trait(self, node_id: str, trait: str) -> None:
        self._proxy.add_node_trait(node_id, trait)

    def remove_trait(self, node_id: str, trait: str) -> None:
        self._proxy.remove_node_trait(node_id, trait)

    def remove_all_traits(self, node_id: str) -> None:
        self._proxy.set_node_traits(node_id, [])

    def get_traits(self, node_id: str) -> list[str]:
        return self._proxy.get_node(node_id).traits

    def set_traits(self, node_id: str, traits: list[str]) -> None:
        self._proxy.set_node_traits(node_id, traits)

    def get_vendor_passthru_methods(self, node_id: str) -> Any:
        return self._proxy.list_node_vendor_passthru(node_id)

    def vendor_passthru(self, node_id: str, method: str,
                        http_method: str = 'POST',
                        args: dict[str, Any] | None = None) -> Any:
        return self._proxy.call_node_vendor_passthru(
            node_id, http_method, method, body=args)

    def get_inventory(self, node_id: str) -> Any:
        return self._proxy.get_node_inventory(node_id)

    def get_history_list(self, node_id: str,
                         detail: bool = False) -> list[Any]:
        url = '/v1/nodes/%s/history' % node_id
        if detail:
            url += '?detail=True'
        return self._proxy.get(url).json().get('history', [])

    def get_history_event(self, node_id: str,
                          event_uuid: str) -> dict[str, Any]:
        return self._proxy.get(
            '/v1/nodes/%s/history/%s' % (node_id, event_uuid)).json()

    def list_firmware_components(self, node_id: str) -> Any:
        return self._proxy.list_node_firmware(node_id)

    def get_bios_setting(self, node_id: str,
                         setting: str) -> dict[str, Any]:
        return self._proxy.get(
            '/v1/nodes/%s/bios/%s' % (node_id, setting)).json()

    def list_bios_settings(self, node_id: str,
                           fields: list[str] | None = None) -> dict[str, Any]:
        return self._proxy.get(
            '/v1/nodes/%s/bios' % node_id).json().get('bios', {})

    def validate(self, node_id: str) -> Any:
        result = self._proxy.validate_node(node_id)

        class _ValidateResult:
            _info: dict[str, Any]

        vr = _ValidateResult()
        vr._info = dict(result)
        return vr

    def set_target_raid_config(self, node_id: str,
                               config: dict[str, Any] | None) -> None:
        self._proxy.put(
            '/v1/nodes/%s/states/raid' % node_id,
            json={'target_raid_config': config})

    def list_children_of_node(self, parent_node_id: str) -> list[Any]:
        return list(
            self._proxy.nodes(details=False, parent_node=parent_node_id))


def attach_compat_managers(proxy: Any) -> None:
    """Attach backward-compat managers to a baremetal proxy instance.

    Enables command modules that still use the old manager API
    (client.chassis.get(), client.node.set_provision_state(), etc.) to
    work against the openstacksdk proxy without modification.  Remove each
    entry here once the corresponding command module has been migrated.
    """
    proxy.allocation = _AllocationManager(proxy)
    proxy.chassis = _ChassisManager(proxy)
    proxy.conductor = _ConductorManager(proxy)
    proxy.deploy_template = _DeployTemplateManager(proxy)
    proxy.driver = _DriverManager(proxy)
    proxy.inspection_rule = _InspectionRuleManager(proxy)
    proxy.node = _NodeManager(proxy)
    proxy.port = _PortManager(proxy)
    proxy.portgroup = _PortgroupManager(proxy)
    proxy.runbook = _RunbookManager(proxy)
    proxy.shard = _ShardManager(proxy)
    proxy.volume_connector = _VolumeConnectorManager(proxy)
    proxy.volume_target = _VolumeTargetManager(proxy)
