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
                    'its state is different from draft.'),
                'different_parties': ('You can not merge these invoices '
                    'because their customers/suppliers are different.'),
                'different_parties_address': ('You can not merge these '
                    'invoices because their invoice addresses are different.'),
                'different_journals': ('You can not merge these invoices '
                    'because their journals are different.'),
                'different_payment_term': ('You can not merge these invoices '
                    'because their payment terms are different.'),
                'different_bank_account': ('You can not merge these invoices '
                    'because their bank accounts are different.'),
                })

    def default_start(self, fields):
        return {
            'invoices': ', '.join([str(id)
                 for id in Transaction().context['active_ids']])
            }

    def do_merge(self, action):
        pool = Pool()
        Invoice = pool.get('account.invoice')
        InvoiceLine = pool.get('account.invoice.line')

        invoices = Invoice.browse(Transaction().context['active_ids'])
        new_invoice = False
        vals = {}
        description = ''

        for invoice in invoices:
            if invoice.state != 'draft':
                self.raise_user_error('state_not_draft',
                    (invoice.rec_name,))

            if 'party' not in vals:
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
            
            bank_account = getattr(invoice, 'bank_account', None)
            if 'bank_account' not in vals:
                vals['bank_account'] = bank_account
            elif vals['bank_account'] != bank_account:
                self.raise_user_error('different_bank_account',
                                      (invoice.rec_name,))

            description += '%s ' % invoice.description

            if not new_invoice:
                default = {
                    'lines': None,
                    'taxes': None,
                    'bank_account': None,
                    'type': invoice.type,
                    }
                new_invoice = Invoice.copy([invoice],
                    default=default)[0]

            if invoice.lines:
                InvoiceLine.write([line for line in invoice.lines],
                        {'invoice': new_invoice})

        to_write = {'state': 'cancel'}
        if vals['bank_account']:
            to_write['bank_account'] = None
            new_invoice.bank_account = vals['bank_account']
            new_invoice.save()

        with Transaction().set_user(0, set_context=True):
            Invoice.update_taxes([new_invoice])
            Invoice.write(invoices, to_write)
            Invoice.delete(invoices)

        data = {'res_id': [new_invoice.id]}
        action['views'].reverse()
        return action, data
