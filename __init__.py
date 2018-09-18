# This file is part of the account_invoice_merger module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import invoice


def register():
    Pool.register(
        invoice.InvoiceMergeStart,
        module='account_invoice_merger', type_='model')
    Pool.register(
        invoice.InvoiceMerge,
        module='account_invoice_merger', type_='wizard')
