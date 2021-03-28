# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0020_auto_20190906_1119"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pipelineinstance",
            name="execution_snapshot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="execution_snapshot_instances",
                to="pipeline.Snapshot",
                verbose_name="\u7528\u4e8e\u5b9e\u4f8b\u6267\u884c\u7684\u7ed3\u6784\u6570\u636e",
            ),
        ),
        migrations.AlterField(
            model_name="pipelineinstance",
            name="snapshot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="snapshot_instances",
                to="pipeline.Snapshot",
                verbose_name="\u5b9e\u4f8b\u7ed3\u6784\u6570\u636e\uff0c\u6307\u5411\u5b9e\u4f8b\u5bf9\u5e94\u7684\u6a21\u677f\u7684\u7ed3\u6784\u6570\u636e",
            ),
        ),
        migrations.AlterField(
            model_name="pipelineinstance",
            name="tree_info",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tree_info_instances",
                to="pipeline.TreeInfo",
                verbose_name="\u63d0\u524d\u8ba1\u7b97\u597d\u7684\u4e00\u4e9b\u6d41\u7a0b\u7ed3\u6784\u6570\u636e",
            ),
        ),
    ]
