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
        objects = pool.object_name_list()
        SaleInvoice = (pool.get('sale.sale-account.invoice')
            if 'sale.sale-account.invoice' in objects else None)
        PurchaseInvoice = (pool.get('purchase.purchase-account.invoice')
            if 'purchase.purchase-account.invoice' in objects else None)
        
        invoices = Invoice.browse(Transaction().context['active_ids'])
        new_invoice = False
        vals = {}
        description = ''

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

            if invoice.type == 'out_invoice' and SaleInvoice:
                sale_invoices = SaleInvoice.search([
                        ('invoice', '=', invoice.id)])
                SaleInvoice.write(sale_invoices, {'invoice': new_invoice})
            if invoice.type == 'in_invoice' and PurchaseInvoice:
                puchase_invoices = PurchaseInvoice.search([
                        ('invoice', '=', invoice.id)])
                PurchaseInvoice.write(puchase_invoices,
                        {'invoice': new_invoice})

        with Transaction().set_user(0, set_context=True):
            Invoice.update_taxes([new_invoice])
            Invoice.write(invoices, {'state': 'cancel'})
            Invoice.delete(invoices)

        data = {'res_id': [new_invoice.id]}
        action['views'].reverse()
        return action, data
