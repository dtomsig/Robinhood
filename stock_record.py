class Stock_Record:
	
    def __init__(self):
        self.stock_map = {}
    
    def add_stock(self, stock_name, date, quantity, price):
        if(stock_name in self.stock_map):
            self.stock_map[stock_name].append(tuple([date, quantity, price]))                   
        else:
            self.stock_map[stock_name] = [(date, quantity, price)] 
        

    def sell_stock(self, stock_name, sell_date, quantity, price):
        if(stock_name not in self.stock_map):
            return
        
        num_short_term = num_long_term = 0
        long_term_gain = short_term_gain = 0
        
        while(quantity > 0 and self.stock_map != False):
            buy_date             = self.stock_map[stock_name][0][0]
            buy_quantity         = self.stock_map[stock_name][0][1]
            buy_price            = self.stock_map[stock_name][0][2]
            stock_change         = 0

            if(quantity >= buy_quantity):
                quantity -= buy_quantity
                stock_change = buy_quantity
                self.stock_map[stock_name] = self.stock_map[stock_name][1:]
            else:
                self.stock_map[stock_name][0][1] -= quantity
                stock_change = quantity
                quantity = 0
            
            sell_year = sell_month = sell_day = {sell_date.split("-")[0], 
                                                 sell_date.split("-")[1],
                                                 sell_date.split("-")[2]}
                                                 
            buy_year = buy_month = buy_day = {buy_date.split("-")[0], 
                                              buy_date.split("-")[1],
                                              buy_date.split("-")[2]}
           
            if(sell_year > buy_year and (sell_month > buy_month or 
                                         (sell_month == buy_month and 
                                          sell_date > buy_date))):
                num_long_term += stock_change
                long_term_gain += stock_change * (price - buy_price)
            else:
                num_short_term += stock_change
                short_term_gain += stock_change * (price - buy_price)

        return(dict({"num_short_term"  : num_short_term, 
                     "num_long_term"   : num_long_term,
                     "long_term_gain"  : long_term_gain,
                     "short_term_gain" : short_term_gain}))
