# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
import datetime

class member_application(models.Model):
	_name = 'sacco.member.application'
	_order = 'no asc'

	no = fields.Char(string = 'No.')
	name = fields.Char(string = 'Name of Artist/Composer')
	alias = fields.Char(string = 'Alias or A.K.A')
	title = fields.Char()
	address = fields.Char(string = 'Postal Address')
	phone_no = fields.Char(string = 'Phone No.')
	mobile_no = fields.Char()
	email = fields.Char(string = 'Email')
	customer_type = fields.Selection([('member',"Member"),('fosa',"FOSA"),('bosa',"BOSA")],string = 'Customer Type')
	registration_date = fields.Date(default = fields.Date.today)
	status = fields.Selection([('open',"Open"),('pending',"Pending"),('approved',"Approved"),('rejected',"Rejected")],default = 'open')
	employer_code = fields.Many2one('sacco.employer' , string = "Employer Code")
	date_of_birth = fields.Date(string = 'Date of Birth')
	birth_county = fields.Char(string= 'County of Birth')
	nationality = fields.Char(string='Nationality')
	
	home_address = fields.Char(string='Residential Address')
	location = fields.Char()
	sublocation = fields.Char()
	district = fields.Char(string = 'County')
	#salary details############################################################
	payrollno = fields.Char()
	basic_pay = fields.Float()
	house_allowance = fields.Float()
	other_benefits = fields.Float()
	transport_allowance = fields.Float()
	total_deductions = fields.Float()
	net_income = fields.Float()

	###########################################################################

	idno = fields.Char(string = 'ID Number')
	passportno = fields.Char(string = 'Passport Number')

	marital_status = fields.Selection([('single','Single'),('married','Married')])
	gender = fields.Selection([('male','Male'),('female','Female')])
	monthly_contribution = fields.Float()
	dividend_amount = fields.Float()
	occupation = fields.Char()
	designation = fields.Selection([('mr',"MR"),('mrs',"Mrs"),('miss',"Miss")])
	contact_person = fields.Char()
	contact_person_phone_no = fields.Char()
	contact_person_relation = fields.Selection([('kin','Kin'),('relative','Relative'),('friend','Friend')])
	recruited_by = fields.Char()
	approved_by = fields.Char()

	bank_name = fields.Char()
	bank_account_no = fields.Char()
	account_holder = fields.Char(string = 'Account Holder Full Name/Surname')
	account_type = fields.Selection([('saving',"Savings"),('current',"Current"),('business',"Business")])
	branch_name = fields.Char()
	bank_address = fields.Char()
	flagged = fields.Boolean()

	member_pin = fields.Char(string ='KRA PIN')
	image = fields.Binary("Image",help = "Member Image")
	next_of_kin_id_member_app = fields.One2many('next.of.kin','member_application_id')
	composed_music = fields.One2many('sacco.composed.music', 'composed_music_id')
	produced_music = fields.One2many('sacco.produced.music', 'produced_music_id')
	created = fields.Boolean(string='Sacco Member?')

	#papment Details
	paid_amount = fields.Float()
	payment_phone = fields.Char()
	transaction_id = fields.Char()
	original_Trans_ref = fields.Char()
	transaction_date = fields.Date()
	paymment_channel = fields.Char()
	customer_name = fields.Char()
	message_id = fields.Char()
	currency_code = fields.Char()
	biller_Code = fields.Char()

	#other music Details
	music_society = fields.Char(string='Music Society')
	music_society_no = fields.Char(string='Music Society No') 
	performers_right = fields.Char(string='Perfomer Rights')
	registered_as = fields.Char(string='Registered As')
	membership_no = fields.Char(string='Membership No')
	
	other_membership_no =fields.Char(string = 'Other Membership NO')


	@api.one
	@api.onchange('no')
	def get_sequence(self):

		setup = self.env['sacco.setup'].search([('id','=',1)])
		sequence = self.env['ir.sequence'].search([('id','=',setup.member_application_nos.id)])
		self.no = sequence.next_by_id(sequence.id, context = None)


	#@api.one
	#def confirm_payment(self):
		#get API Details and compare with Input Data.


		#Send a notification mail

	@api.one
	def create_member(self):
		if self.status != 'approved':

			setup = self.env['sacco.setup'].search([('id','=',1)])
			sequence = self.env['ir.sequence'].search([('id','=',setup.member_nos.id)])
			member_no = sequence.next_by_id(sequence.id, context = None)

			new_member = self.env['sacco.member'].create({'no':member_no,'name':self.name,'address':self.address,'phone_no':self.phone_no,'mobile_no':self.mobile_no,
				'email':self.email,'customer_type':self.customer_type,'registration_date':self.registration_date,
				'employer_code':self.employer_code.id,'date_of_birth':self.date_of_birth,'home_address':self.home_address,
				'location':self.location,'sublocation':self.sublocation,'district':self.district,'payrollno':self.payrollno,
				'idno':self.idno,'passportno':self.passportno,'marital_status':self.marital_status,
				'gender':self.gender,'monthly_contribution':self.monthly_contribution,'member_pin':self.member_pin,
				'recruited_by':self.recruited_by,'approved_by':self.approved_by,
				'bank_account_no':self.bank_account_no,'bank_name':self.bank_name,'image':self.image})

			#write ids to next of kin table to transfer view to member table
			kin = self.env['next.of.kin'].search([('member_application_id','=',self.id)])
			for item in kin:
				item.member_no = new_member.id
			self.created = True
			#write ids to composed music table to transfer view to member table
			kin = self.env['sacco.composed.music'].search([('composed_music_id','=',self.id)])
			for item in kin:
				item.member_no = new_member.id
			self.created = True
			#write ids to next of kin table to transfer view to member table
			kin = self.env['sacco.produced.music'].search([('produced_music','=',self.id)])
			for item in kin:
				item.member_no = new_member.id
			self.created = True
		else:
			raise ValidationError("Status must be approved before creating member")

	############################################################################################################################
	'''
	All approvals management code in here. Until we find a centralized solution, all models will carry their
	own approvals code. This approach is however open to new ideas in the future once we find a way to centralize
	code that can call and manipulate models and be called remotely from any model or py file through importation.
	This first approach will be used as a template for all other approvals. In case of overal change of approach, change
	this approval so that other programmers can copy and paste and modify where necessary
	Ensure you have the following functions:
	::>>SendApprovalRequest
	::>>checkAdditionalApprovers-->should not change much for subsequent models
	::>>CancelApprovalRequest
	::>>ApproveApprovalRequest
	::>>rejectApprovalRequest
	'''
	'''
	@api.one
	def checkAdditionalApprovers(self,document_type,template_name,document_no):
		#init
		approval_template = self.env['approval.template'].search([('document_type','=',document_type)])
		additional_approvers = self.env['additional.approvers']
		approval_entry = self.env['approval.entry']
		#continue
		approvers = {}
		#approval_template.search([])#('document_type','=',document_type)

		if len(approval_template)<=0:
			raise ValidationError("No approval template found for Document Type: "+ document_type)

		else:
			approvers = additional_approvers.search([('template_id','=',approval_template.id)])

			if len(approvers)<=0:
				raise ValidationError("No additional approvers for document type:"+document_type)

			else:
				sequence = 0
				for approver in approvers:
					sequence +=1
					status = ''
					if sequence == 1:
						status = 'open'
					else:
						status = 'created'
					self.env['approval.entry'].create({'document_type':document_type,'document_no':document_no,'document_id':self.id,'sequence':sequence,'approver_id':approver.approver_id.id,'sender_id':self.env.user.id,'status':status,'sender':self.env.user.id,'approver':approver.approver_id.id})
		self.approveApprovalRequest()



	@api.one
	def sendApprovalRequest(self):
		if self.status != 'open':
			raise ValidationError("Status must be open to send request")

		document_type = 'member_app'
		template_name = 'member_app'


		self.checkAdditionalApprovers(document_type,template_name,self.no)


	@api.one
	def cancelApprovalRequest(self):#this is standard. Dont modify for subsequent models
		if self.status != 'pending':
			raise ValidationError("Status must be pending to cancel request")
		#init
		#approval_templates = self.env['approval.template']
		#additional_approvers = self.env['additional.approvers']
		approval_entry = self.env['approval.entry'].search([('document_no','=',self.no),('status','!=','rejected')])
		if len(approval_entry)>0:
			#raise ValidationError("Found approval entries to cancel")
			approval_entry.write({'status':'cancelled'})
			self.status = 'open'

	@api.one
	def approveApprovalRequest(self):
		#init
		approval_entry = self.env['approval.entry'].search([('document_no','=',self.no),('status','=','open'),('approver_id','=',self.env.user.id)])
		#if len(approval_entry)<=0:
		#	raise ValidationError('Current user is not authorized to approve this document')
		approval_entry.write({'status':'approved'})
		next_approval_entry = self.env['approval.entry'].search([('document_no','=',self.no),('status','in',['created','open'])])
		#next_approval_entry.sorted(key=lambda r: r.sequence)
		if len(next_approval_entry)>0:
			next_approval_entry = min(next_approval_entry)
			next_approval_entry.status = 'open'
			self.status = 'pending'
			return False
		else:
			self.status = 'approved'
			return True



	@api.one
	def rejectApprovalRequest(self):
		if self.status != 'pending':
			raise ValidationError("Status must be pending to reject request")
		#init

		approval_entry = self.env['approval.entry'].search([('document_no','=',self.no),('status','!=','cancelled')])


		if len(approval_entry)>0:
			#raise ValidationError('Found approval entries to cancel')
			approval_entry.write({'status':'rejected'})
			self.status = 'rejected'
############################################################################################################################
	'''
class member(models.Model):
	_name = 'sacco.member'
	_order = 'no asc'

	no = fields.Char(string = 'No.')#, readonly = True
	name = fields.Char(string = 'Name of Artist/Composer')
	alias = fields.Char(string = 'Alias or A.K.A')
	title = fields.Char()
	address = fields.Char(string = 'Postal Address')
	phone_no = fields.Char(string = 'Phone No.')
	mobile_no = fields.Char()
	email = fields.Char(string = 'Email')
	customer_type = fields.Selection([('member',"Member"),('fosa',"FOSA"),('bosa',"BOSA")],string = 'Customer Type')
	registration_date = fields.Date()

	employer_code = fields.Many2one('sacco.employer',string = "Employer Code")
	date_of_birth = fields.Date(string = 'Date of Birth')
	birth_county = fields.Char(string= 'County of Birth')
	nationality = fields.Char(string='Nationality')	
	home_address = fields.Char(string='Residential Address')
	location = fields.Char()
	sublocation = fields.Char()
	district = fields.Char()
	#salary details############################################################
	payrollno = fields.Char()
	basic_pay = fields.Float()
	house_allowance = fields.Float()
	other_benefits = fields.Float()
	transport_allowance = fields.Float()
	total_deductions = fields.Float()
	net_income = fields.Float()

	###########################################################################
	idno = fields.Char()
	passportno = fields.Char()
	marital_status = fields.Selection([('single','Single'),('married','Married')])
	gender = fields.Selection([('male','Male'),('female','Female')])
	monthly_contribution = fields.Float()
	dividend_amount = fields.Float()
	occupation = fields.Char()
	designation = fields.Char()
	contact_person = fields.Char()
	contact_person_phone_no = fields.Char()
	contact_person_relation = fields.Selection([('kin','Kin'),('relative','Relative'),('friend','Friend')])
	recruited_by = fields.Char()
	approved_by = fields.Char()
	bank_name = fields.Char()
	bank_account_no = fields.Char()
	member_pin = fields.Char(string ='KRA PIN')
	#This marks the beginning of unique fields for member not in member appliaction
	current_loan = fields.Float(compute = '_compute_member_statistics')#
	current_shares = fields.Float(compute = '_compute_member_statistics')#
	#total_repayment = fields.Float(compute = '_compute_member_statistics')
	#principal_balance = fields.Float(compute = '_compute_member_statistics')
	#principal_repayment = fields.Float(compute = '_compute_member_statistics')
	current_unallocated = fields.Float(compute = '_compute_member_statistics')
	image = fields.Binary("Image",help = "Member Image")
	registration_fee_paid = fields.Float()
	current_savings = fields.Float(compute = '_compute_member_statistics')#
	current_deposits = fields.Float(compute = '_compute_member_statistics')#
	next_of_kin_id_member = fields.One2many('next.of.kin','member_no')
	member_account_status = fields.Selection([('active',"Active"),('suspended',"Suspended"),('closed',"Closed")], default = 'active')
	#next_of_kin_id_member_app = fields.One2many('next.of.kin','member_application_id')
	composed_music = fields.One2many('sacco.composed.music', 'member_no')
	produced_music = fields.One2many('sacco.produced.music', 'member_no')
	created = fields.Boolean(string='Sacco Member?')
	ledger_ids = fields.One2many('sacco.member.ledger.entry','member_no')
	#loan_ids = fields.One2many('res.partner','name')


	bank_name = fields.Char()
	bank_account_no = fields.Char()
	account_holder = fields.Char(string = 'Account Holder Full Name/Surname')
	account_type = fields.Selection([('saving',"Savings"),('current',"Current"),('business',"Business")])
	branch_name = fields.Char()
	bank_address = fields.Char()
	flagged = fields.Boolean()


	#papment Details
	paid_amount = fields.Float()
	payment_phone = fields.Char()
	transaction_id = fields.Char()
	original_Trans_ref = fields.Char()
	transaction_date = fields.Date()
	paymment_channel = fields.Char()
	customer_name = fields.Char()
	message_id = fields.Char()
	currency_code = fields.Char()
	biller_Code = fields.Char()

	#other music Details
	music_society = fields.Char(string='Music Society')
	music_society_no = fields.Char(string='Music Society No') 
	performers_right = fields.Char(string='Perfomer Rights')
	registered_as = fields.Char(string='Registered As')
	membership_no = fields.Char(string='Membership No')
	
	other_membership_no =fields.Char(string = 'Other Membership NO')

	@api.one
	@api.onchange('no')
	def get_sequence(self):
		setup = self.env['sacco.setup'].search([('id','=',1)])
		sequence = self.env['ir.sequence'].search([('id','=',setup.member_nos.id)])
		self.no = sequence.next_by_id(sequence.id, context = None)

	@api.multi
	def print_list(self):
		printed = True
		return self.env['report'].get_action(self,'sacco_member.member_card')

	@api.one
	@api.depends('ledger_ids')
	def _compute_member_statistics(self):


		loans = 0.0
		deposits = 0.0
		savings = 0.0
		shares = 0.0
		unallocated = 0.0

		for ledger_entry in self.ledger_ids:
			if ledger_entry['transaction_type'] == 'loan':#should rethink about how we do for loans
				loans+= ledger_entry['amount']
			if ledger_entry['transaction_type'] == 'deposits':
				deposits += ledger_entry['amount']
			if ledger_entry['transaction_type']== 'withdrawal':
				deposits -= ledger_entry['amount']
			if ledger_entry['transaction_type'] == 'shares':
				shares += ledger_entry['amount']
			if ledger_entry['transaction_type'] == 'savings':
				savings += ledger_entry['amount']
			if ledger_entry.transaction_type == 'unallocated':
				unallocated += ledger_entry.amount
		self.current_loan = loans
		self.current_shares = shares
		self.current_savings = savings
		self.current_deposits = deposits
		self.current_unallocated = unallocated

class member_ledger(models.Model):
	_name = 'sacco.member.ledger.entry'
	_order = 'entry_no asc'

	transaction_no = fields.Char()
	transaction_type = fields.Selection([('deposits',"Member Deposits"),('withdrawal',"Deposit Withdrawal"),('shares',"Shares Contribution"),('loan',"Loan"),('savings',"Savings"),('interest',"Interest Payment"),('unallocated',"Unallocated Funds")])
	transaction_name = fields.Char()
	member_no = fields.Many2one('sacco.member')#'sacco.member', member_no
	member_name = fields.Char()#member_name
	date = fields.Date()
	amount = fields.Float()
	debit = fields.Float()
	credit = fields.Float()
	entry_no = fields.Integer()

class member_closure(models.Model):
	_name = 'sacco.member.closure'

	no = fields.Char()
	member_no = fields.Many2one('sacco.member' ,store = True , domain = [('member_account_status','=','active')])
	image = fields.Binary(help = 'Member Image')
	closing_date = fields.Date()
	status = fields.Selection([('open',"Open"),('pending',"Pending Approval"),('approved',"Approved"),('rejected',"Rejected")],default='open')
	closed = fields.Boolean(default = False)
	total_loan = fields.Float()
	total_interest = fields.Float()
	member_savings = fields.Float()
	closure_type = fields.Selection([('dismissal',"Summary Dismissal")])
	deposit_refundable = fields.Float()
	remarks = fields.Text()
	approval_entries = fields.One2many('approval.entry','document_id')

	approvers = fields.Integer(compute = 'check_current_approver')#



	@api.one
	@api.onchange('no')
	def get_sequence(self):
		setup = self.env['sacco.setup'].search([('id','=',1)])
		sequence = self.env['ir.sequence'].search([('id','=',setup.member_closure_nos.id)])
		self.no = sequence.next_by_id(sequence.id, context = None)

	@api.one
	def deactivate_member(self):
		self.closed = True
		member = self.env['sacco.member'].search([('id','=',self.member_no.id)])
		member.member_account_status = 'suspended'

	############################################################################################################################
	'''
	All approvals management code in here. Until we find a centralized solution, all models will carry their
	own approvals code. This approach is however open to new ideas in the future once we find a way to centralize
	code that can call and manipulate models and be called remotely from any model or py file through importation.
	This first approach will be used as a template for all other approvals. In case of overal change of approach, change
	this approval so that other programmers can copy and paste and modify where necessary
	Ensure you have the following functions:
	::>>SendApprovalRequest
	::>>checkAdditionalApprovers-->should not change much for subsequent models
	::>>CancelApprovalRequest
	::>>ApproveApprovalRequest
	'''
	@api.one
	def checkAdditionalApprovers(self,document_type,template_name,document_no):
		#init
		approval_template = self.env['approval.template'].search([('document_type','=',document_type)])
		additional_approvers = self.env['additional.approvers']
		approval_entry = self.env['approval.entry']
		#continue
		approvers = {}


		if len(approval_template)<=0:
			raise ValidationError("No approval template found for Document Type: "+ document_type)

		else:
			approvers = additional_approvers.search([('template_id','=',approval_template.id)])

			if len(approvers)<=0:
				raise ValidationError("No additional approvers for document type:"+document_type)

			else:
				sequence = 0
				for approver in approvers:
					sequence +=1
					status = ''
					if sequence == 1:
						status = 'open'
					else:
						status = 'created'
					self.env['approval.entry'].create({'document_type':document_type,'document_no':document_no,'document_id':self.id,'sequence':sequence,'approver_id':approver.approver_id.id,'sender_id':self.env.user.id,'status':status,'sender':self.env.user.id,'approver':approver.approver_id.id})
		self.approveApprovalRequest()



	@api.one
	def sendApprovalRequest(self):
		if self.status != 'open':
			raise ValidationError("Status must be open to send request")

		document_type = 'closure'
		template_name = 'closure'#not yet in use


		self.checkAdditionalApprovers(document_type,template_name,self.no)
			#self.status = 'pending'

	@api.one
	def cancelApprovalRequest(self):#this is standard. Dont modify for subsequent models
		if self.status != 'pending':
			raise ValidationError("Status must be pending to cancel request")
		#init
		#approval_templates = self.env['approval.template']
		#additional_approvers = self.env['additional.approvers']
		approval_entry = self.env['approval.entry'].search([('document_no','=',self.no),('status','!=','rejected')])
		if len(approval_entry)>0:
			#raise ValidationError("Found approval entries to cancel")
			approval_entry.write({'status':'cancelled'})
			self.status = 'open'

	@api.one
	def approveApprovalRequest(self):
		#init
		approval_entry = self.env['approval.entry'].search([('document_no','=',self.no),('status','=','open'),('approver_id','=',self.env.user.id)])
		#if len(approval_entry)<=0:
		#	raise ValidationError('Current user is not authorized to approve this document')
		approval_entry.write({'status':'approved'})
		next_approval_entry = self.env['approval.entry'].search([('document_no','=',self.no),('status','=','created')])
		#next_approval_entry.sorted(key=lambda r: r.sequence)
		if len(next_approval_entry)>0:
			next_approval_entry.status = 'open'
			self.status = 'pending'
			return False
		else:
			self.status = 'approved'
			return True



	@api.one
	def rejectApprovalRequest(self):
		if self.status != 'pending':
			raise ValidationError("Status must be pending to reject request")
		#init

		approval_entry = self.env['approval.entry'].search([('document_no','=',self.no),('status','!=','cancelled')])


		if len(approval_entry)>0:
			#raise ValidationError('Found approval entries to cancel')
			approval_entry.write({'status':'rejected'})
			self.status = 'rejected'

	@api.one
	@api.depends('approval_entries')
	def check_current_approver(self):
		self.approvers = len(self.approval_entries)

class account_activation(models.Model):
	_name = 'sacco.member.activation'

	no = fields.Char()
	member_no = fields.Many2one('sacco.member', store = True ,domain = [('member_account_status','!=','active')])
	activation_date = fields.Date()
	status = fields.Selection([('open',"Open"),('pending',"Pending Approval"),('approved',"Approved"),('rejected',"Rejected")],default='open')
	activated = fields.Boolean(default = False)
	total_loan = fields.Float()
	total_interest = fields.Float()
	total_deposits = fields.Float()
	closure_type = fields.Selection([('dismissal',"Summary Dismissal")])

	@api.one
	@api.onchange('no')
	def get_sequence(self):
		setup = self.env['sacco.setup'].search([('id','=',1)])
		sequence = self.env['ir.sequence'].search([('id','=',setup.member_activation_nos.id)])
		self.no = sequence.next_by_id(sequence.id, context = None)

	@api.one
	def activate_member(self):
		self.activated = True
		member = self.env['sacco.member'].search([('id','=',self.member_no.id)])
		member.member_account_status = 'active'

class employer(models.Model):
	_name = 'sacco.employer'

	name = fields.Char()
	description = fields.Char()
	no_of_members = fields.Integer(compute = 'employer_statistics')
	male = fields.Integer(compute = 'employer_statistics')
	female = fields.Integer(compute = 'employer_statistics')
	employee_ids = fields.One2many('sacco.member','employer_code') #used to compute employer statistics

	@api.one
	@api.depends('employee_ids')
	def employer_statistics(self):
		self.no_of_members = self.env['sacco.member'].search_count([('employer_code.id','=',self.id)])
		self.male = self.env['sacco.member'].search_count([('employer_code.id','=',self.id),('gender','=','male')])
		self.female = self.env['sacco.member'].search_count([('employer_code.id','=',self.id),('gender','=','female')])

class share_transfer(models.Model):
	_name = 'sacco.share.transfer'

	name = fields.Char()
	date = fields.Date(default = fields.Date.today)
	transfer_from = fields.Many2one('sacco.member', domain = [('member_account_status','=','active')], store = True)
	transfer_from_shares = fields.Float(compute = 'populate_transfer_stats')
	transfer_from_picture = fields.Binary(compute = 'populate_transfer_stats')
	transfer_to = fields.Many2one('sacco.member', domain = [('member_account_status','=','active')], store = True)
	transfer_to_shares = fields.Float(compute = 'populate_transfer_stats')
	transfer_to_picture = fields.Binary(compute = 'populate_transfer_stats')
	share_worth = fields.Float()
	status = fields.Selection([('open',"Open"),('pending','Pending Approval'),('approved',"Approved")])
	transferred = fields.Boolean()

	@api.one
	@api.onchange('name')
	def get_sequence(self):
		setup = self.env['sacco.setup'].search([('id','=',1)])
		sequence = self.env['ir.sequence'].search([('id','=',setup.share_transfer_nos.id)])
		self.name = sequence.next_by_id(sequence.id, context = None)


	@api.one
	@api.constrains('share_worth')
	def share_transfer_limit(self):
		if self.transfer_from_shares < self.share_worth:
			raise ValidationError("You cannot tranfer more shares than the Member owns:::["+ str(self.transfer_from_shares)+'] < ['+str(self.share_worth)+']')

	@api.one
	@api.depends('transfer_from','transfer_to')
	def populate_transfer_stats(self):
		#from
		transfer_from = self.env['sacco.member'].search([('id','=',self.transfer_from.id)])
		self.transfer_from_shares = transfer_from.current_shares
		self.transfer_from_picture = transfer_from.image
		#to
		transfer_to = self.env['sacco.member'].search([('id','=',self.transfer_to.id)])
		self.transfer_to_shares = transfer_to.current_shares
		self.transfer_to_picture = transfer_to.image

	@api.one
	def transfer(self):
		if self.status == 'approved':
			if self.transferred == True:
				raise ValidationError("This document has already been posted")
			#find last ledger entry
			ledgers = self.env['sacco.member.ledger.entry'].search([])
			entries = [ledger.entry_no for ledger in ledgers]
			try:
				entry_no = max(entries)
			except:
				entry_no = 0

			member_ledger = self.env['sacco.member.ledger.entry']
			#transfer from
			transfer_from = self.env['sacco.member'].search([('id','=',self.transfer_from.id)])
			entry_no +=1
			member_ledger.create({'entry_no':entry_no,'member_no':transfer_from.id,'member_name':transfer_from.name,'date':self.date,
				'transaction_no':self.name,'transaction_type':'shares','transaction_name':'Share Transfer::' + self.name,
				'amount':-(self.share_worth)})
			#transfer to
			transfer_to = self.env['sacco.member'].search([('id','=',self.transfer_to.id)])
			entry_no += 1
			member_ledger.create({'entry_no':entry_no,'member_no':transfer_to.id,'member_name':transfer_to.name,'date':self.date,
				'transaction_no':self.name,'transaction_type':'shares','transaction_name':'Share Transfer::' + self.name,
				'amount':self.share_worth})
			self.transferred = True
		else:
			raise ValidationError("Status must be approved before transferring shares")

class member_ledger_mirror(models.Model):
	_name = 'sacco.member.ledger.entry.mirror'
	_order = 'entry_no asc'

	entry_no = fields.Integer()
	member_no = fields.Many2one('sacco.member')
	member_name = fields.Char()
	date = fields.Date()
	mpesa_date = fields.Date()
	transaction_no = fields.Char()
	transaction_type = fields.Selection([('deposits',"Member Deposits"),('withdrawal',"Deposit Withdrawal"),('shares',"Shares Contribution"),('loan',"Loan"),('savings',"Savings"),('interest',"Interest Payment"),('unallocated',"Unallocated Funds")])
	transaction_name = fields.Char()
	amount = fields.Float()


class licensed_customers(models.Model):
	_name='sacco.licensed.customers'

	name = fields.Char(string='Business Name')
	full_name = fields.Char()
	id_no = fields.Char()
	kra_pin = fields.Char(string= 'KRA PIN')

	address = fields.Char(string = 'Postal Address')
	phone_no = fields.Char(string = 'Phone No.')
	mobile_no = fields.Char()
	email = fields.Char(string = 'Email')
	registration_date = fields.Date(default = fields.Date.today)
	status = fields.Selection([('open',"Open"),('pending',"Pending"),('approved',"Approved"),('rejected',"Rejected")],default = 'open')
	business_id = fields.One2many('sacco.license.lines', 'line_id')
	county = fields.Char()

class licenses_lines(models.Model):
	_name = 'sacco.license.lines'

	line_id = fields.Many2one('sacco.licensed.customers')
	#licenses = fields.Selection([('vehicle',"Vehicle $ Transport"),('concert',"Concert, Exhibitions"),('cafe',"Restaurants, Cafe, Coffeshop"),
	#							('office',"Office Building & Factories"),('dance',"Dance"),('tv',"TV Broadcasts"),
	#							('shop',"Shops(Including Charity Shops)"),('college',"University & Colleges"),('roadshow',"RoadShows"),
	#							('hair',"Hair Dressers(Beauty Shops)"),('ringtone',"Rindtone & Rindback"),
	#							('club',"Amatuer & Clubs"),('radio',"Radio, Outside Broadcasts"),
	#							('cinemas',"Cinemas & Theatres"),('rave',"Rave & Dance Parties")])
	licenses = fields.Many2one('sacco.license.type')
	description = fields.Char()
	amount = fields.Float()
	comment = fields.Char()


class license_type(models.Model):
	_name = 'sacco.license.type'

	name = fields.Char()
	description = fields.Char()
	amount = fields.Float()
	

class sacco_composed_music(models.Model):
	_name = 'sacco.composed.music'

	name = fields.Char()
	comment = fields.Char()
	composed_music_id = fields.Many2one('sacco.member.application')
	member_no = fields.Char()



class sacco_produced_music(models.Model):
	_name = 'sacco.produced.music'

	name = fields.Char()
	comment = fields.Char()
	produced_music_id = fields.Many2one('sacco.member.application')
	member_no = fields.Char()


