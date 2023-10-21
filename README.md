# ckanext-sisharvester

[![Tests](https://github.com/berlinonline/ckanext-sisharvester/workflows/Tests/badge.svg?branch=master)](https://github.com/berlinonline/ckanext-sisharvester/actions)
[![Code Coverage](http://codecov.io/github/berlinonline/ckanext-sisharvester/coverage.svg?branch=master)](http://codecov.io/github/berlinonline/ckanext-sisharvester?branch=master)

This plugin belongs to a set of plugins for the _Datenregister_ – the non-public [CKAN](https://ckan.org) instance that is part of Berlin's open data portal [daten.berlin.de](https://daten.berlin.de).
_ckanext-sisharvester_ provides a harvester for Berlin's [Sozial-Informations-System](https://www.sozial-informations-system.de) (SIS), a separate dataportal by the [Senatsverwaltung für Arbeit, Soziales, Gleichstellung, Integration, Vielfalt und Antidiskriminierung](https://www.berlin.de/sen/asgiva/) .

The plugin implements the following CKAN interfaces:

- … not sure yet

It also implements IHarvester, which is defined in the [ckanext-harvest](https://github.com/ckan/ckanext-harvest) extension. (probably)

- [IHarvester](https://github.com/ckan/ckanext-harvest#the-harvesting-interface)

## Notes

- Das SIS ist kein CKAN, sondern [Piveau](https://www.piveau.eu).
- Bietet aber eine eingeschränkte CKAN-API:
  - `package_search`: https://www.sozial-informations-system.de/api/search/ckan/package_search/
    - `&q=metadata_modified:[2000-07-01T00:00:0.000Z%20TO%202023-09-01T08:42:37Z]` scheint ignoriert zu werden (wahrscheinlich kein Solr im Einsatz)
    - Gibt es eine andere Möglichkeit, nach Datum zu filtern?
  - `package_show`: https://www.sozial-informations-system.de/api/search/ckan/package_show?id=ts1300199000202306-xlsx
- Evtl. könnte man also einfach den generischen CKAN-Harvester (https://github.com/ckan/ckanext-harvest#the-ckan-harvester) nehmen und erweitern.


## Requirements

This plugin has been tested with CKAN 2.9.9 (which requires Python 3).

## License

This material is copyright © [BerlinOnline Stadtportal GmbH & Co. KG](https://www.berlinonline.net/).

This extension is open and licensed under the GNU Affero General Public License (AGPL) v3.0.
Its full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
