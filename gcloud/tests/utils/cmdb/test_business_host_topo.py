# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from mock import MagicMock, patch

from django.test import TestCase

from gcloud.utils.cmdb import get_business_host_topo, get_filter_business_host_topo


class GetBusinessHostTopoTestCase(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_client.cc.list_biz_hosts_topo = "list_biz_hosts_topo"
        self.get_client_by_user_patcher = patch(
            "gcloud.utils.cmdb.get_client_by_user", MagicMock(return_value=self.mock_client)
        )
        self.get_client_by_user_patcher.start()

        self.username = "user_token"
        self.bk_biz_id = "biz_id_token"
        self.supplier_account = "supplier_account_token"
        self.host_fields = ["host_fields_token"]
        self.ip_list = "ip_list_token"
        self.ip_str = "ip_str_token"
        self.ip_strs = "ip1_str_token, ip2_str_token"
        self.host_id = "225"
        self.host_ids = "225,286"
        self.list_biz_hosts_topo_return = [
            {
                "host": {
                    "bk_cloud_id": 0,
                    "bk_host_id": 1,
                    "bk_host_innerip": "127.0.0.1",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
                "topo": [
                    {"bk_set_id": 11, "bk_set_name": "set1", "module": [{"bk_module_id": 56, "bk_module_name": "m1"}]}
                ],
            },
            {
                "host": {
                    "bk_cloud_id": 0,
                    "bk_host_id": 3,
                    "bk_host_innerip": "127.0.0.3",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
                "topo": [
                    {
                        "bk_set_id": 10,
                        "bk_set_name": "空闲机池",
                        "module": [
                            {"bk_module_id": 54, "bk_module_name": "空闲机"},
                            {"bk_module_id": 55, "bk_module_name": "空闲机1"},
                        ],
                    },
                    {"bk_set_id": 11, "bk_set_name": "set1", "module": [{"bk_module_id": 56, "bk_module_name": "m1"}]},
                ],
            },
        ]
        self.list_biz_hosts_page_topo_return = {
            "result": True,
            "data": {
                "info": [
                    {
                        "host": {
                            "bk_cloud_id": 0,
                            "bk_host_id": 1,
                            "bk_host_innerip": "127.0.0.1",
                            "bk_mac": "",
                            "bk_os_type": None,
                        },
                        "topo": [
                            {
                                "bk_set_id": 11,
                                "bk_set_name": "set1",
                                "module": [{"bk_module_id": 56, "bk_module_name": "m1"}],
                            }
                        ],
                    },
                    {
                        "host": {
                            "bk_cloud_id": 0,
                            "bk_host_id": 3,
                            "bk_host_innerip": "127.0.0.3",
                            "bk_mac": "",
                            "bk_os_type": None,
                        },
                        "topo": [
                            {
                                "bk_set_id": 10,
                                "bk_set_name": "空闲机池",
                                "module": [
                                    {"bk_module_id": 54, "bk_module_name": "空闲机"},
                                    {"bk_module_id": 55, "bk_module_name": "空闲机1"},
                                ],
                            },
                            {
                                "bk_set_id": 11,
                                "bk_set_name": "set1",
                                "module": [{"bk_module_id": 56, "bk_module_name": "m1"}],
                            },
                        ],
                    },
                ],
                "count": 2,
            },
        }
        self.get_business_host_topo_expect_return = [
            {
                "host": {
                    "bk_cloud_id": 0,
                    "bk_host_id": 1,
                    "bk_host_innerip": "127.0.0.1",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
                "set": [{"bk_set_id": 11, "bk_set_name": "set1"}],
                "module": [{"bk_module_id": 56, "bk_module_name": "m1"}],
            },
            {
                "host": {
                    "bk_cloud_id": 0,
                    "bk_host_id": 3,
                    "bk_host_innerip": "127.0.0.3",
                    "bk_mac": "",
                    "bk_os_type": None,
                },
                "set": [{"bk_set_id": 10, "bk_set_name": "空闲机池"}, {"bk_set_id": 11, "bk_set_name": "set1"}],
                "module": [
                    {"bk_module_id": 54, "bk_module_name": "空闲机"},
                    {"bk_module_id": 55, "bk_module_name": "空闲机1"},
                    {"bk_module_id": 56, "bk_module_name": "m1"},
                ],
            },
        ]
        self.get_filter_business_host_topo_expect_return = (
            [
                {
                    "host": {
                        "bk_cloud_id": 0,
                        "bk_host_id": 1,
                        "bk_host_innerip": "127.0.0.1",
                        "bk_mac": "",
                        "bk_os_type": None,
                    },
                    "set": [{"bk_set_id": 11, "bk_set_name": "set1"}],
                    "module": [{"bk_module_id": 56, "bk_module_name": "m1"}],
                },
                {
                    "host": {
                        "bk_cloud_id": 0,
                        "bk_host_id": 3,
                        "bk_host_innerip": "127.0.0.3",
                        "bk_mac": "",
                        "bk_os_type": None,
                    },
                    "set": [{"bk_set_id": 10, "bk_set_name": "空闲机池"}, {"bk_set_id": 11, "bk_set_name": "set1"}],
                    "module": [
                        {"bk_module_id": 54, "bk_module_name": "空闲机"},
                        {"bk_module_id": 55, "bk_module_name": "空闲机1"},
                        {"bk_module_id": 56, "bk_module_name": "m1"},
                    ],
                },
            ],
            2,
        )

    def tearDown(self):
        self.get_client_by_user_patcher.stop()

    def test__list_biz_hosts_topo_return_empty(self):
        mock_batch_request = MagicMock(return_value=[])
        with patch("gcloud.utils.cmdb.batch_request", mock_batch_request):
            hosts_topo = get_business_host_topo(self.username, self.bk_biz_id, self.supplier_account, self.host_fields)

        self.assertEqual(hosts_topo, [])
        mock_batch_request.assert_called_once_with(
            "list_biz_hosts_topo",
            {"bk_biz_id": self.bk_biz_id, "bk_supplier_account": self.supplier_account, "fields": self.host_fields},
        )

    def test__get_with_ip_list(self):
        mock_batch_request = MagicMock(return_value=self.list_biz_hosts_topo_return)
        with patch("gcloud.utils.cmdb.batch_request", mock_batch_request):
            hosts_topo = get_business_host_topo(
                self.username, self.bk_biz_id, self.supplier_account, self.host_fields, self.ip_list
            )

        self.assertEqual(hosts_topo, self.get_business_host_topo_expect_return)
        mock_batch_request.assert_called_once_with(
            "list_biz_hosts_topo",
            {
                "bk_biz_id": self.bk_biz_id,
                "bk_supplier_account": self.supplier_account,
                "fields": self.host_fields,
                "host_property_filter": {
                    "condition": "AND",
                    "rules": [{"field": "bk_host_innerip", "operator": "in", "value": self.ip_list}],
                },
            },
        )

    def test__get_without_ip_list(self):
        mock_batch_request = MagicMock(return_value=self.list_biz_hosts_topo_return)
        with patch("gcloud.utils.cmdb.batch_request", mock_batch_request):
            hosts_topo = get_business_host_topo(self.username, self.bk_biz_id, self.supplier_account, self.host_fields)

        self.assertEqual(hosts_topo, self.get_business_host_topo_expect_return)
        mock_batch_request.assert_called_once_with(
            "list_biz_hosts_topo",
            {"bk_biz_id": self.bk_biz_id, "bk_supplier_account": self.supplier_account, "fields": self.host_fields},
        )

    def test__get_contains_with_ip_list(self):
        self.mock_client.cc.list_biz_hosts_topo = MagicMock(return_value=self.list_biz_hosts_page_topo_return)
        hosts_topo = get_filter_business_host_topo(
            self.username,
            self.bk_biz_id,
            self.supplier_account,
            self.host_fields,
            start="0",
            limit="10",
            ip_str=self.ip_str,
        )

        self.assertEqual(hosts_topo, self.get_filter_business_host_topo_expect_return)
        self.mock_client.cc.list_biz_hosts_topo.assert_called_once_with(
            {
                "bk_biz_id": self.bk_biz_id,
                "bk_supplier_account": self.supplier_account,
                "fields": self.host_fields,
                "host_property_filter": {
                    "condition": "OR",
                    "rules": [{"field": "bk_host_innerip_v6", "operator": "contains", "value": self.ip_str}]
                    + [{"field": "bk_host_innerip", "operator": "contains", "value": self.ip_str}],
                },
                "page": {"start": 0, "limit": 10},
            },
        )

    def test__get_many_contains_with_ip_list(self):
        self.mock_client.cc.list_biz_hosts_topo = MagicMock(return_value=self.list_biz_hosts_page_topo_return)
        hosts_topo = get_filter_business_host_topo(
            self.username,
            self.bk_biz_id,
            self.supplier_account,
            self.host_fields,
            start="0",
            limit="10",
            ip_str=self.ip_strs,
        )

        self.assertEqual(hosts_topo, self.get_filter_business_host_topo_expect_return)
        self.mock_client.cc.list_biz_hosts_topo.assert_called_once_with(
            {
                "bk_biz_id": self.bk_biz_id,
                "bk_supplier_account": self.supplier_account,
                "fields": self.host_fields,
                "host_property_filter": {
                    "condition": "OR",
                    "rules": [
                        {"field": "bk_host_innerip_v6", "operator": "contains", "value": self.ip_str}
                        for self.ip_str in self.ip_strs.split(",")
                    ]
                    + [
                        {"field": "bk_host_innerip", "operator": "contains", "value": self.ip_str}
                        for self.ip_str in self.ip_strs.split(",")
                    ],
                },
                "page": {"start": 0, "limit": 10},
            },
        )

    def test__get_with_page_list(self):
        self.mock_client.cc.list_biz_hosts_topo = MagicMock(return_value=self.list_biz_hosts_page_topo_return)
        hosts_topo = get_filter_business_host_topo(
            self.username, self.bk_biz_id, self.supplier_account, self.host_fields, start="0", limit="10"
        )

        self.assertEqual(hosts_topo, self.get_filter_business_host_topo_expect_return)
        self.mock_client.cc.list_biz_hosts_topo.assert_called_once_with(
            {
                "bk_biz_id": self.bk_biz_id,
                "bk_supplier_account": self.supplier_account,
                "fields": self.host_fields,
                "page": {"start": 0, "limit": 10},
            }
        )

    def test_get_equal_host_list(self):
        self.mock_client.cc.list_biz_hosts_topo = MagicMock(return_value=self.list_biz_hosts_page_topo_return)
        hosts_topo = get_filter_business_host_topo(
            self.username,
            self.bk_biz_id,
            self.supplier_account,
            self.host_fields,
            start="0",
            limit="10",
            host_id=self.host_id,
        )

        self.assertEqual(hosts_topo, self.get_filter_business_host_topo_expect_return)
        self.mock_client.cc.list_biz_hosts_topo.assert_called_once_with(
            {
                "bk_biz_id": self.bk_biz_id,
                "bk_supplier_account": self.supplier_account,
                "fields": self.host_fields,
                "host_property_filter": {
                    "condition": "OR",
                    "rules": [{"field": "bk_host_id", "operator": "in", "value": [int(self.host_id)]}],
                },
                "page": {"start": 0, "limit": 10},
            }
        )

    def test_get_many_equal_host_list(self):
        self.mock_client.cc.list_biz_hosts_topo = MagicMock(return_value=self.list_biz_hosts_page_topo_return)
        hosts_topo = get_filter_business_host_topo(
            self.username,
            self.bk_biz_id,
            self.supplier_account,
            self.host_fields,
            start="0",
            limit="10",
            host_id=self.host_ids,
        )

        self.assertEqual(hosts_topo, self.get_filter_business_host_topo_expect_return)
        self.mock_client.cc.list_biz_hosts_topo.assert_called_once_with(
            {
                "bk_biz_id": self.bk_biz_id,
                "bk_supplier_account": self.supplier_account,
                "fields": self.host_fields,
                "host_property_filter": {
                    "condition": "OR",
                    "rules": [
                        {
                            "field": "bk_host_id",
                            "operator": "in",
                            "value": [int(host_id) for host_id in self.host_ids.split(",")],
                        }
                    ],
                },
                "page": {"start": 0, "limit": 10},
            }
        )
