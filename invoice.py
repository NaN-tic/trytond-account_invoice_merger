# This file is part of the account_invoice_merger module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Button, StateAction, StateView, Wizard

__all__ = ['InvoiceMerge', 'InvoiceMergeStart']


class InvoiceMergeStart(ModelView):
    'Invoice Merge Start'
    __name__ = 'account.invoice.merge.start'
    invoices = fields.Char('Invoices', readonly=True)


class InvoiceMerge(Wizard):
    'Invoice Merge'
    __name__ = 'account.invoice.merge'
    start = StateView('account.invoice.merge.start',
        'account_invoice_merger.account_invoice_merge_start_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Merge', 'merge', 'tryton-ok', default=True),
            ])
    merge = StateAction('account_invoice.act_invoice_form')

    @classmethod
    def __setup__(cls):
        super(InvoiceMerge, cls).__setup__()
        cls._error_messages.update({
                'state_not_draft': ('You can not merge the invoice %s because '
                    'its state is different of draft.'),
                'different_parties': ('You can not merge these invoices '
                    'because its customers/suppliers are different.'),
                'different_parties_address': ('You can not merge these '
                    'invoices because its invoice addresses are different.'),
                'different_journals': ('You can not merge these invoices '
                    'because its journals are different.'),
                'different_payment_term': ('You can not merge these invoices '
                    'because its payment term are different.'),
                'sale_shipment_state': ('Sale "%(sale)s" shipment state is waiting. '
                    'You need to delivery shipment before merge invoices.'),
                })

    def default_start(self, fields):
        Invoice = Pool().get('account.invoice')
        default = {}
        for invoice in Invoice.browse(Transaction().context['active_ids']):
            if 'invoices' not in default:
                default['invoices'] = '%s' % invoice.id
            else:
                default['invoices'] = '%s, %s' % (
                    default['invoices'], invoice.id)
        return default

    def do_merge(self, action):
        pool = Pool()
        Invoice = pool.get('account.invoice')
        InvoiceLine = pool.get('account.invoice.line')
        InvoiceTax = pool.get('account.invoice.tax')
        Sale = pool.get('sale.sale')
        SaleInvoice = pool.get('sale.sale-account.invoice')
        PurchaseInvoice = pool.get('purchase.purchase-account.invoice')
        invoices = Invoice.browse(Transaction().context['active_ids'])
        new_invoice = False
        vals = {}
        description = ''
        sales = []

        for invoice in invoices:
            if invoice.state != 'draft':
                self.raise_user_error('state_not_draft',
                    (invoice.rec_name,))

            if not 'party' in vals:
                vals['party'] = invoice.party
            elif vals['party'] != invoice.party:
                self.raise_user_error('different_parties',
                    (invoice.rec_name,))

            if 'invoice_address' not in vals:
                vals['invoice_address'] = invoice.invoice_address
            elif vals['invoice_address'] != invoice.invoice_address:
                self.raise_user_error('different_parties_address',
                    (invoice.rec_name,))

            if 'journal' not in vals:
                vals['journal'] = invoice.journal
            elif vals['journal'] != invoice.journal:
                self.raise_user_error('different_journals',
                    (invoice.rec_name,))

            if 'payment_term' not in vals:
                vals['payment_term'] = invoice.payment_term
            elif vals['payment_term'] != invoice.payment_term:
                self.raise_user_error('different_payment_term',
                    (invoice.rec_name,))

            for line in invoice.lines:
                origin = line.origin
                if origin.__name__ == 'sale.line':
                    sale = origin.sale
                    if sale.shipment_state == 'waiting':
                        self.raise_user_error('sale_shipment_state', {
                                'sale': sale.rec_name,
                                })
                    sales.append(sale)

            description += '%s ' % invoice.description

            if invoice.type in ('out_credit_note', 'in_credit_note'):
                for line in invoice.lines:
                    InvoiceLine.write([line], {'quantity': -1 * line.quantity})
                if invoice.type == 'out_credit_note':
                    invoice.type = 'out_invoice'
                else:
                    invoice.type = 'in_invoice'

            if not new_invoice:
                default = {
                    'lines': None,
                    'taxes': None,
                    'type': invoice.type,
                    }
                new_invoice = Invoice.copy([invoice],
                    default=default)[0]

            if invoice.lines:
                InvoiceLine.write([line for line in invoice.lines],
                        {'invoice': new_invoice})
            if invoice.taxes:
                InvoiceTax.write([tax for tax in invoice.taxes], 
                        {'invoice': new_invoice})
            if invoice.type == 'out_invoice':
                sale_invoices = SaleInvoice.search([
                        ('invoice', '=', invoice.id)])
                SaleInvoice.write(sale_invoices, {'invoice': new_invoice})
            else:
                puchase_invoices = PurchaseInvoice.search([
                        ('invoice', '=', invoice.id)])
                PurchaseInvoice.write(puchase_invoices,
                        {'invoice': new_invoice})

        if sales:
            Sale.write(sales, {'invoice_merger': True})

        Invoice.write(invoices, {'state': 'cancel'})
        Invoice.delete(invoices)

        data = {'res_id': [new_invoice.id]}
        action['views'].reverse()
        return action, data
