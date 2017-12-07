# Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 07-12-17
# Gateway Version: 17.12.1
# Description: Example Gateway workflows

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField
from bluecat.wtform_fields import CustomSearchButtonField
from bluecat.wtform_fields import PlainHTML
from bluecat.wtform_fields import CustomSelectField
from bluecat.wtform_fields import TableField

from component_logic import find_objects_by_type_endpoint
from component_logic import server_table_data_endpoint
from component_logic import get_object_types
from component_logic import raw_table_data


class GenericFormTemplate(GatewayForm):
    workflow_name = 'table_component'
    workflow_permission = 'table_component_page'

    object_type = CustomSelectField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label = 'Object Type',
        choices_function=get_object_types,
        required=True,
        is_disabled_on_start=False

    )

    keyword = CustomStringField(
        label='Keyword',
        is_disabled_on_start=False,
        required=True
    )

    search = CustomSearchButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        default='Search Objects',
        inputs = {
            'keyword': 'keyword',
            'object_type': 'object_type'
        },
        server_side_method=find_objects_by_type_endpoint,
        message_field='search_message',
        on_complete=['call_output_table', 'call_server_table'],
        is_disabled_on_start=False
    )
    plain_html = PlainHTML('<div id="search_message"></div>')

    output_table = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='',
        data_function=raw_table_data,
        on_complete=['custom_js_table_loaded']
    )

    server_table = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Server table',
        data_function=raw_table_data,
        server_side_method=server_table_data_endpoint,
        table_features={
            'searching': False,
            'paging': False,
            'ordering': False,
            'info': False
        },
        inputs = {'keyword': 'keyword', 'object_type': 'object_type'}
    )
