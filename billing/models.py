from django.db import models

from members.models import Flat


class BillDetails(models.Model):
    flat_type       = models.CharField(max_length =1, help_text ="Your Choices are 1, 2, 3.", default="3")
    municipal_tax   = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Taxes Levied by BMC")
    maintenance     = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Maintenance Charges")
    water_charges   = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Water Costs")
    parking_charges = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Car/Scooter/Stilt")
    sinking_fund    = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Sinking Fund")
    building_repair = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Fund for Building Repairs")
    elec_ins_chgs   = models.DecimalField("Electricity Insurance Charges", max_digits=10,
                                            decimal_places=2,
                                            help_text = "Electricity Insurance"
                                        )
    
    class Meta:
        verbose_name_plural = "Billing Details"

    def __str__(self):
        return ("The Initial Costs for Flat type: {}").format(self.flat_type)
    
    def maintenance_total(self):
        return(self.maintenance + 
                self.water_charges +
                self.parking_charges + 
                self.sinking_fund + 
                self.building_repair + 
                self.elec_ins_chgs
                )




class FlatBill(models.Model):
    flat_name       = models.ForeignKey(Flat, on_delete=models.CASCADE)
    bill_date       = models.DateField("Bill Date", auto_now_add=True)
    municipal_tax   = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Taxes Levied by BMC")
    maintenance     = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Maintenance Charges")
    water_charges   = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Water Costs")
    parking_charges = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Car/Scooter/Stilt")
    sinking_fund    = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Sinking Fund")
    building_repair = models.DecimalField(max_digits=10, decimal_places=2, help_text = "Fund for Building Repairs")
    is_paid         = models.BooleanField(default=False)
    elec_ins_chgs   = models.DecimalField("Electricity Insurance Charges", max_digits=10,
                                            decimal_places=2,
                                            help_text = "Electricity Insurance"
                                        )
    noc_charges     = models.DecimalField("N.O.C. Charges", max_digits=10, decimal_places=2, 
                                         help_text = "Non Occupancy Charges",
                                         default = 0,
                                         )
    add_item_name_1 = models.CharField("Additional Items e.g. Building Maintenance",
                                        max_length=100, blank=True )
    add_item_name_2 = models.CharField("Additional Items e.g. Emergency_fund",
                                        max_length=100, blank=True )
    add_item_amt_1  = models.DecimalField(default = 0, max_digits=10, decimal_places=2, help_text = "Amount for Additional Item 1")
    add_item_amt_2  = models.DecimalField(default = 0, max_digits=10, decimal_places=2, help_text = "Amount for Additional Item 2")                                        
    
    
    def __str__(self):
        return ("Bill for Flat: {} Dated : {}".format(self.flat_name, self.bill_date))

    def total(self):
        return(self.municipal_tax + 
                self.maintenance + 
                self.water_charges +
                self.parking_charges + 
                self.sinking_fund + 
                self.building_repair + 
                self.elec_ins_chgs + 
                self.noc_charges + 
                self.add_item_amt_1 + 
                self.add_item_amt_2
                )
    
# def get_total(instance):
#     return instance.total()

class Receipt(models.Model):
    related_bill = models.OneToOneField(FlatBill, on_delete=models.CASCADE)
    paid_on = models.DateField()
    payment_mode = models.CharField(max_length=200, help_text = "Cheque, Bank Transfer etc.")
    drawn_on = models.CharField(max_length=250, help_text="Financial institution received from.")
    transaction_no = models.CharField(max_length=250, help_text="Cheque Number or Bank Transfer Number.")
    received_amount = models.DecimalField(max_digits=25, decimal_places=2, help_text="Amount Received from Member.")

    def __str__(self):
        return ("Receipt for {} paid on {} for the amount Rs. {}.".format(self.related_bill.flat_name, 
                                                                          self.paid_on,
                                                                          self.received_amount)
                )
