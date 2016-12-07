Overdue Payments customisation
==============================

This module replaces the standard Overdue Payments report.

Features
--------

* The print wizard allows to print a single payment notice as well as
  notices for all customers.
* The print wizard allows to select receivables or both
  receivables and payables and hence covers the case of Partners
  which are Customer and Supplier at the same time.
* Outstanding amounts are displayed in invoice currency.
* The litigation column has been replaced by an indication that
  clearly shows the payments that are overdue.
* The Invoice number is printed for outgoing transactions.
* The payment notice text can be customized with html tags.

Overdue message template customization
--------------------------------------
* %{partner_name}s: insert partner name
* %{date}s: insert date
* %{company_name}: insert company.name
* %{user_signature}: insert user signature
