.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============================================================================
Alternative for the 'l10n_be' belgian accounting module including legal reports
===============================================================================

This module activates the following functionality:

    * Support for the NBB/BNB legal Balance and P&L reportscheme including
      auto-configuration of the correct financial report entry when
      creating/changing a general account.
    * The account type will be automatically assigned
      based upon the account group when creating a new general account.
    * The setup wizard
        - allows to select mono- versus multilingual
          Chart of Accounts
        - allows to select which languages to install
    * Intervat XML VAT declarations
        - Periodical VAT Declaration
        - Periodical Intracom Declaration
        - Annual Listing of VAT-Subjected Customers

This module has been tested for use with Odoo Enterprise as well as Odoo Community.

Configuration
=============

1) Chart of Accounts
--------------------

This module has a different approach than l10n_be for the population of the
Chart of Accounts (CoA).

The l10n_be module comes with a fully populated CoA whereas this module
will only create the CoA Groups and a strict minimum set of
general accounts.

In order to have a fully populated CoA, you have to import your own CoA
after the installation of this module.
You can use the standard account import button in order to do this.
When importing your chart of accounts the reporting tags and user type will
be set automatically based upon the account group (the first digits of the account code).

2) VAT Declarations
-------------------

By default the 'invoicing' contact of the Company is used as contact for the VAT Declarations.
Ensure that this contact has a valid e-mail and phone number since these fields
will be used for the Intervat XML VAT declarations.

Roadmap
=======

- implement carry_over_condition_method
- refine coa autotyping with new account types (e.g. off_balance, expense_depreciation)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Noviat/noviat-apps/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.
