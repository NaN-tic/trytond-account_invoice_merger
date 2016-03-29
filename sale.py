# This file is part of the account_invoice_merger module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta

__all__ = ['SaleLine']


class SaleLine:
    __metaclass__ = PoolMeta
    __name__ = 'sale.line'

    def get_invoice_line(self, invoice_type):
        invoice_lines = super(SaleLine, self).get_invoice_line(invoice_type)

        # Avoid to reinvoice the credit note lines previously invoiced
        # in normal invoices with negative quantities
        if (invoice_lines and invoice_type == 'out_credit_note'):
            qty = sum((l.quantity for l in self.invoice_lines
                    if l.invoice.type == 'out_invoice'), 0)
            # By default is obtained one invoice line for each sale line
            invoice_lines[0].quantity += 2 * qty
            if invoice_lines[0].quantity <= 0:
                return []
        return invoice_lines
