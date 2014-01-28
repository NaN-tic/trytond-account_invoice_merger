# This file is part of the account_invoice_merger module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .invoice import *
from .sale import *


def register():
    Pool.register(
        InvoiceMergeStart,
        Sale,
        module='account_invoice_merger', type_='model')
    Pool.register(
        InvoiceMerge,
        module='account_invoice_merger', type_='wizard')
