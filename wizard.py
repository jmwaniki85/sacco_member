from openerp import models, fields, api
class member_register_wizard(models.TransientModel):
	_name = 'member_register_wizard'

	member_no = fields.Many2one('sacco.member')
	member_status = fields.Selection([('active',"Active"),('closed',"Closed"),('all',"All")], default = 'active')

	@api.multi
	def print_register(self):
		if self.member_status == 'active':
			register = self.env['sacco.member'].search([('member_account_status','=','active')])
		elif self.member_status == 'closed':
			register = self.env['sacco.member'].search([('member_account_status','=','closed')])
		else:
			register = self.env['sacco.member'].search([])
		
		return self.env['report'].get_action(register,'sacco_member.member_register')  

class member_application_wizard(models.TransientModel):
	_name = 'sacco.member.application.wizard'

	@api.multi
	def receipts_post(self):
		payments = self.env['sacco.member.application.payments'].browse(self._context.get('active_ids'))
		for payment in payments:
		    payment.action_post()