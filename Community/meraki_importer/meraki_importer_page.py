# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
# -*- coding: utf-8 -*-
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
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2020-03-31
# Gateway Version: 20.1.1
# Description: CISCO Meraki Importer page.py

import os
import sys
import codecs

from flask import request, url_for, redirect, render_template, flash, g, jsonify
from wtforms.validators import URL, DataRequired
from wtforms import StringField, BooleanField, SubmitField

from bluecat.wtform_extensions import GatewayForm
from bluecat import route, util
import config.default_config as config
from main_app import app

from .meraki_importer import MerakiImporter

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

def get_configuration():
    configuration = None
    if g.user:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
    return configuration
    

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'meraki_importer'
    workflow_permission = 'meraki_importer_page'
    
    text=util.get_text(module_path(), config.language)
    require_message=text['require_message']
    
    api_key = StringField(
        label=text['label_api_key'],
        validators=[DataRequired(message=require_message)]
    )
    org_name = StringField(
        label=text['label_org_name'],
        validators=[DataRequired(message=require_message)]
    )
    network_name = StringField(
        label=text['label_network_name'],
        validators=[DataRequired(message=require_message)]
    )
    dashboard_url = StringField(
        label=text['label_dashboard_url'],
        validators=[DataRequired(message=require_message)],
        render_kw={"placeholder": "https://<Dashboard Instance>.meraki.com/<Network Name>/n/<ID>"}
    )
    
    include_matches = BooleanField(
        label='',
        default='checked'
    )
    
    include_ipam_only = BooleanField(
        label='',
        default='checked'
    )
    
    submit = SubmitField(label=text['label_submit'])

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/meraki_importer/meraki_importer_endpoint')
@util.workflow_permission_required('meraki_importer_page')
@util.exception_catcher
def meraki_importer_meraki_importer_page():
    form = GenericFormTemplate()
    
    meraki_importer = MerakiImporter.get_instance(debug=True)
    
    value = meraki_importer.get_value('api_key')
    if value is not None:
        form.api_key.data = value
    value = meraki_importer.get_value('org_name')
    if value is not None:
        form.org_name.data = value
    value = meraki_importer.get_value('network_name')
    if value is not None:
        form.network_name.data = value
    value = meraki_importer.get_value('dashboard_url')
    if value is not None:
        form.dashboard_url.data = value
    value = meraki_importer.get_value('include_matches')
    if value is not None:
        form.include_matches.data = value
    value = meraki_importer.get_value('include_ipam_only')
    if value is not None:
        form.include_ipam_only.data = value
    
    return render_template(
        'meraki_importer_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/meraki_importer/load_col_model')
@util.workflow_permission_required('meraki_importer_page')
@util.exception_catcher
def load_col_model():
    text=util.get_text(module_path(), config.language)
    
    links = '<img src="{icon}" title="{title}" width="16" height="16">'
    value_table = {
        'UNKNOWN': links.format(icon='img/help.gif', title=text['label_state_unknown']),
        'MATCH': links.format(icon='img/check.gif', title=text['label_state_match']),
        'MISMATCH': links.format(icon='img/about.gif', title=text['label_state_mismatch']),
        'RECLAIM': links.format(icon='img/data_delete.gif', title=text['label_state_reclaim'])
    }

    col_model = [
        {'index':'id', 'name':'id', 'hidden':True, 'sortable':False},
        {'index':'network_id', 'name':'network_id', 'hidden':True, 'sortable':False},
        {'index':'order', 'name':'order', 'hidden':True, 'sortable':False},
        {'index':'name', 'name':'name', 'hidden':True, 'sortable':False},
        {'index':'system', 'name':'system', 'hidden':True, 'sortable':False},
        {'index':'detail_link', 'name':'detail_link', 'hidden':True, 'sortable':False},
        {
            'label': text['label_col_ipaddr'], 'index':'ipaddr', 'name':'ipaddr',
            'width':100, 'align':'center', 'sortable':False
        },
        {
            'label': text['label_col_macaddr'], 'index':'macaddr', 'name':'macaddr',
            'width':130, 'align':'center', 'sortable':False
        },
        {
            'label': text['label_col_name'], 'index':'linked_name', 'name':'linked_name',
            'width':140, 'sortable':False, 'formatter': 'link'
        },
        {
            'label': text['label_col_system'], 'index':'system', 'name':'system',
            'width':240, 'sortable':False
        },
        {
            'label': text['label_col_state'], 'index':'state', 'name':'state',
            'width':50, 'align':'center', 'sortable':False,
            'formatter': 'select',
            'formatoptions': {
                'value': value_table
            }
        },
        {
            'label': text['label_col_lastfound'], 'index':'last_found', 'name':'last_found',
            'width':140, 'align':'center', 'sortable':False,
            'formatter': 'date',
            'formatoptions': {
                'srcformat': 'ISO8601Long',
                'newformat': 'Y-m-d H:i:s',
                'userLocalTime': True
            }
        }
    ]
    return jsonify(col_model)

@route(app, '/meraki_importer/get_clients')
@util.workflow_permission_required('meraki_importer_page')
@util.exception_catcher
def get_clients():
    clients = []
    configuration = get_configuration()
    if configuration is not None:
        meraki_importer = MerakiImporter.get_instance()
        meraki_importer.collect_clients(configuration)
        clients = meraki_importer.get_clients()
    return jsonify(clients)

@route(app, '/meraki_importer/load_clients')
@util.workflow_permission_required('meraki_importer_page')
@util.exception_catcher
def load_clients():
    meraki_importer = MerakiImporter.get_instance()
    clients = meraki_importer.get_clients()
    return jsonify(clients)

@route(app, '/meraki_importer/update_config', methods=['POST'])
@util.workflow_permission_required('meraki_importer_page')
@util.exception_catcher
def update_config():
    config = request.get_json()
    meraki_importer = MerakiImporter.get_instance()
    meraki_importer.set_value('api_key', config['api_key'])
    meraki_importer.set_value('org_name', config['org_name'])
    meraki_importer.set_value('network_name', config['network_name'])
    meraki_importer.set_value('dashboard_url', config['dashboard_url'])
    meraki_importer.set_value('include_matches', config['include_matches'])
    meraki_importer.set_value('include_ipam_only', config['include_ipam_only'])
    meraki_importer.save()
    return jsonify(success=True)

@route(app, '/meraki_importer/push_selected_clients', methods=['POST'])
@util.workflow_permission_required('meraki_importer_page')
@util.exception_catcher
def push_selected_clients():
    new_clients = []
    client_ids = request.get_json()
    meraki_importer = MerakiImporter.get_instance()
    
    for client in meraki_importer.get_clients():
        if client['id'] in client_ids:
            new_clients.append(client)
            
    meraki_importer.set_clients(new_clients)
    return jsonify(success=True)

@route(app, '/meraki_importer/clear_clients', methods=['POST'])
@util.workflow_permission_required('meraki_importer_page')
@util.exception_catcher
def clear_clients():
    meraki_importer = MerakiImporter.get_instance()
    meraki_importer.clear_clients()
    return jsonify(success=True)

@route(app, '/meraki_importer/form', methods=['POST'])
@util.workflow_permission_required('meraki_importer_page')
@util.exception_catcher
def meraki_importer_meraki_importer_page_form():
    form = GenericFormTemplate()
    text=util.get_text(module_path(), config.language)
    if form.validate_on_submit():
        meraki_importer = MerakiImporter.get_instance()
        meraki_importer.set_value('api_key', form.api_key.data)
        meraki_importer.set_value('org_name', form.org_name.data)
        meraki_importer.set_value('network_name', form.network_name.data)
        meraki_importer.set_value('dashboard_url', form.dashboard_url.data)
        meraki_importer.set_value('include_matches', form.include_matches.data)
        meraki_importer.set_value('include_ipam_only', form.include_ipam_only.data)
        meraki_importer.save()
        
        configuration = get_configuration()
        meraki_importer.import_clients(configuration)
        meraki_importer.collect_clients(configuration)
        
        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash(text['imported_message'], 'succeed')
        return redirect(url_for('meraki_importermeraki_importer_meraki_importer_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'meraki_importer_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )

