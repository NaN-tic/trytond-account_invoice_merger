# This file is part of the account_invoice_merger module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta

__all__ = ['PurchaseLine']
__metaclass__ = PoolMeta


class PurchaseLine:
    __name__ = 'purchase.line'

    def get_invoice_line(self, invoice_type):
        invoice_lines = super(PurchaseLine, self).get_invoice_line(invoice_type)

        # Avoid to reinvoice the credit note lines previously invoiced
        # in normal invoices with negative quantities
        if (invoice_lines and invoice_type == 'in_credit_note'):
            qty = sum((l.quantity for l in self.invoice_lines
                    if l.invoice.type == 'in_invoice'), 0)
            # By default is obtained one invoice line for each purchase line
            invoice_lines[0].quantity += 2 * qty
            if invoice_lines[0].quantity <= 0:
                return []
        return invoice_lines
