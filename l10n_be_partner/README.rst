.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================================
Belgium - Partner Model Customisations & Data
=============================================

This module adds the following functionality

* support for KBO/BCE number on partner records including a number of data entry controls

* partner titles for commonly used Belgian legal entities are added when installing the module

* Company settings

  - company_registry: required field for Belgian legal entities
  - rml_header1, rml_footer: multilanguage fields

* Banks

  - list of Belgian banks with BBAN and IBAN are added when installing the module
  - automatic BBAN/IBAN conversion when adding a bank to a partner

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/119/10.0

Known issues / Roadmap
======================

- The current version of the Belgian Intrastat reporting module is only based on invoices.
  Since associated stock moves are not taken into consideration, it is possible that manual
  corrections are required, e.g.

  - Product movements without invoices are not included in the current version
    of this module and must be added manually to the report lines
    before generating the ONEGATE XML declaration.
  - Credit Notes are by default assumed to be corrections to the outgoing or incoming
    invoices within the same reporting period. The product declaration values of the
    Credit Notes are as a consequence deducted from the declaration lines.
    You should encode the Credit Note with 'Intrastat Transaction Type = 2' when the goods
    returned.

- The current version of the Belgian Intrastat reporting module does not perform a
  cross-check with the VAT declaration.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-financial-reporting/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
l10n-belgium/issues/new?body=module:%20
l10n_be_partner%0Aversion:%20
8.0.0.1%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Luc De Meyer, Noviat <info@noviat.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
