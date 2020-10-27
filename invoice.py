# This file is part of the account_invoice_merger module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Button, StateAction, StateView, Wizard
from trytond.i18n import gettext
from trytond.exceptions import UserError

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

        parties = set()
        types = set()
        invoice_address = set()
        journals = set()
        payment_terms = set()
        bank_accounts = set()
        descriptions = []
        references = []
        for invoice in invoices:
            if invoice.state != 'draft':
                raise UserError(gettext('account_invoice_merger.msg_state_not_draft',
                    invoice=invoice.rec_name))
            if invoice.number:
                raise UserError(gettext('account_invoice_merger.msg_has_number',
                    invoice=invoice.rec_name))

            types.add(invoice.type)
            parties.add(invoice.party)
            invoice_address.add(invoice.invoice_address)
            journals.add(invoice.journal)
            payment_terms.add(invoice.payment_term)
            bank_account = getattr(invoice, 'bank_account', None)
            if bank_account:
                bank_accounts.add(bank_account)
            descriptions.append(invoice.description)
            references.append(invoice.reference)

        if len(types) > 1:
            raise UserError(gettext('account_invoice_merger.msg_different_types',
                invoices=', '.join([str(invoice.id) for invoice in invoices])))
        elif len(parties) > 1:
            raise UserError(gettext('account_invoice_merger.msg_different_parties',
                invoices=', '.join([str(invoice.id) for invoice in invoices])))
        elif len(invoice_address) > 1:
            raise UserError(gettext('account_invoice_merger.msg_different_parties_address',
                invoices=', '.join([str(invoice.id) for invoice in invoices])))
        elif len(journals) > 1:
            raise UserError(gettext('account_invoice_merger.msg_different_journals',
                invoices=', '.join([str(invoice.id) for invoice in invoices])))
        elif len(payment_terms) > 1:
            raise UserError(gettext('account_invoice_merger.msg_different_payment_term',
                invoices=', '.join([str(invoice.id) for invoice in invoices])))
        elif len(bank_accounts) > 1:
            raise UserError(gettext('account_invoice_merger.msg_different_bank_account',
                invoices=', '.join([str(invoice.id) for invoice in invoices])))

        main_invoice, = invoices[:1]
        other_invoices = invoices[1:]

        invoice.description = ', '.join(descriptions)
        invoice.reference = ', '.join(descriptions)
        InvoiceLine.write([line for i in other_invoices for line in i.lines],
                {'invoice': main_invoice})

        with Transaction().set_user(0, set_context=True):
            Invoice.update_taxes([main_invoice])
            Invoice.cancel(other_invoices)
            # TODO sao can not reload records
            # Invoice.delete(other_invoices)

        data = {'res_id': [main_invoice.id]}
        action['views'].reverse()
        return action, data
