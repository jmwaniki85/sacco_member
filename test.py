def compute_mtd_sale(self):
        cursor = self._cr
        user = self._uid
        
        today = datetime.datetime.today()
        start_date = str(today.replace(day=1).strftime('%m/%d/%Y'))
        next_month = today.replace(day=28) + datetime.timedelta(days=4)
        end_date = str(next_month - datetime.timedelta(days=next_month.day-1))
        print end_date 
        # Lookup the sales orders
        sale_obj = self.pool.get('sale.order')
        order_ids = sale_obj.search(cursor, user, [('date_order','>=',start_date),('date_order','<=',end_date),('partner_id','=',self.id),('state','!=','draft')])
        total = 0.0
        for sale in sale_obj.browse(cursor, user, order_ids):
            total += sale.amount_total
        self.mtd_sales = total