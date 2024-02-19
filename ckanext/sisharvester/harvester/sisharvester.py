from ckanext.harvest.harvesters.ckanharvester import CKANHarvester
from __future__ import absolute_import
import six
import requests
from requests.exceptions import HTTPError, RequestException

import datetime
import re

from six.moves.urllib.parse import urlencode
from ckan import model
from ckan.logic import ValidationError, NotFound, get_action
from ckan.lib.helpers import json
from ckan.plugins import toolkit

from ckanext.harvest.model import HarvestObject
from .base import HarvesterBase

import logging
log = logging.getLogger(__name__)

def extract_contact_info(data_dict):
    return data_dict

class SisHarvester(CKANHarvester):
    '''Main plugin class of the ckanext-sisharvest extension.'''
    def _get_action_api_offset(self):
        return '/api/%d/action' % self.action_api_version

    def _get_search_api_offset(self):
        print ('IN SIS HARBESTER API OFFSET')
        #return '%s/package_search' % self._get_action_api_offset()
        return '/package_search'    

    def modify_package_dict(self, package_dict, harvest_object):
        # Add tags
        tags = package_dict['tags']

        for tag in tags:
            tag['display_name'] = tag.pop('display-name')
            name = tag['name']
            chars = ['/', '(', ')']
            for char in chars:
                if char in name:
                    tag['name'] = re.sub(char, ' ', name)        
        package_dict['tags'] = tags

        # contact information
        return package_dict
    
    def gather_stage(self, harvest_job):
        log.debug('In CKANHarvester gather_stage (%s)',
                  harvest_job.source.url)
        toolkit.requires_ckan_version(min_version='2.0')
        get_all_packages = True

        self._set_config(harvest_job.source.config)

        # Get source URL
        remote_ckan_base_url = harvest_job.source.url.rstrip('/')

        # Filter in/out datasets from particular organizations
        fq_terms = []
        org_filter_include = self.config.get('organizations_filter_include', [])
        org_filter_exclude = self.config.get('organizations_filter_exclude', [])
        if org_filter_include:
            fq_terms.append(' OR '.join(
                'organization:%s' % org_name for org_name in org_filter_include))
        elif org_filter_exclude:
            fq_terms.extend(
                '-organization:%s' % org_name for org_name in org_filter_exclude)

        groups_filter_include = self.config.get('groups_filter_include', [])
        groups_filter_exclude = self.config.get('groups_filter_exclude', [])
        if groups_filter_include:
            fq_terms.append(' OR '.join(
                'groups:%s' % group_name for group_name in groups_filter_include))
        elif groups_filter_exclude:
            fq_terms.extend(
                '-groups:%s' % group_name for group_name in groups_filter_exclude)

        # Ideally we can request from the remote CKAN only those datasets
        # modified since the last completely successful harvest.
        last_error_free_job = self.last_error_free_job(harvest_job)
        log.debug('Last error-free job: %r', last_error_free_job)
        if (last_error_free_job and
                not self.config.get('force_all', False)):
            get_all_packages = False

            # Request only the datasets modified since
            last_time = last_error_free_job.gather_started
            # Note: SOLR works in UTC, and gather_started is also UTC, so
            # this should work as long as local and remote clocks are
            # relatively accurate. Going back a little earlier, just in case.
            get_changes_since = \
                (last_time - datetime.timedelta(hours=1)).isoformat()
            log.info('Searching for datasets modified since: %s UTC',
                     get_changes_since)

            fq_since_last_time = 'metadata_modified:[{since}Z TO *]' \
                .format(since=get_changes_since)

            try:
                pkg_dicts = self._search_for_datasets(
                    remote_ckan_base_url,
                    fq_terms + [fq_since_last_time])
            except SearchError as e:
                log.info('Searching for datasets changed since last time '
                         'gave an error: %s', e)
                get_all_packages = True

            if not get_all_packages and not pkg_dicts:
                log.info('No datasets have been updated on the remote '
                         'CKAN instance since the last harvest job %s',
                         last_time)
                return []

        # Fall-back option - request all the datasets from the remote CKAN
        if get_all_packages:
            # Request all remote packages
            try:
                pkg_dicts = self._search_for_datasets(remote_ckan_base_url,
                                                      fq_terms)
            except SearchError as e:
                log.info('Searching for all datasets gave an error: %s', e)
                self._save_gather_error(
                    'Unable to search remote CKAN for datasets:%s url:%s'
                    'terms:%s' % (e, remote_ckan_base_url, fq_terms),
                    harvest_job)
                return None
        if not pkg_dicts:
            self._save_gather_error(
                'No datasets found at CKAN: %s' % remote_ckan_base_url,
                harvest_job)
            return []

        # Create harvest objects for each dataset
        try:
            package_ids = set()
            object_ids = []
            for pkg_dict in pkg_dicts:
                if pkg_dict['id'] in package_ids:
                    log.info('Discarding duplicate dataset %s - probably due '
                             'to datasets being changed at the same time as '
                             'when the harvester was paging through',
                             pkg_dict['id'])
                    continue
                package_ids.add(pkg_dict['id'])
                # SOLVE THIS!!!!
                log.debug('Creating HarvestObject for %s %s',
                          pkg_dict['id'], pkg_dict['id'])
                obj = HarvestObject(guid=pkg_dict['id'],
                                    job=harvest_job,
                                    content=json.dumps(pkg_dict))
                obj.save()
                object_ids.append(obj.id)

            return object_ids
        except Exception as e:
            self._save_gather_error('%r' % e.message, harvest_job)

class SearchError(Exception):
    pass
