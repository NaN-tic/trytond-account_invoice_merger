# This file is part of the account_invoice_merger module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Sale']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'
    invoice_merger = fields.Boolean('Invoice Merged')

    def create_invoice(self, invoice_type):
        if self.invoice_merger:
            return
        super(Sale, self).create_invoice(invoice_type)
