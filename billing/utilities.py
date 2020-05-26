from members.models import RentalStatus

def create_flat_bills(flat, bill_type):
    rented_flat=RentalStatus.objects.get(flat_number =flat)
    if not rented_flat.is_rented:
        rental_noc = 0
    else:
        amount = bill_type.maintenance_total()
        rental_noc=float(amount)*0.1
    flat.flatbill_set.create(
        municipal_tax = bill_type.municipal_tax,
        maintenance = bill_type.maintenance,
        water_charges = bill_type.water_charges,
        parking_charges = bill_type.parking_charges,
        sinking_fund = bill_type.sinking_fund,
        building_repair = bill_type.building_repair,
        elec_ins_chgs = bill_type.elec_ins_chgs,
        noc_charges = rental_noc,
    )

    """ 
    PARKING CHARGES
    If flat has vehicle, check the type of vehicle
        then check the type of parking, 
        assign it to a variable, 
         If flat has more vehicles and what kind of vehicle code
        add additional cost to parking charges.
    
    Interest on non payment
    If flat has past bills that are unpaid(is_paid = False)
        in the next bill add last bill + 21%
    in the next bill if the flat still has unpaid bills
        take the amount of last bill without interest
        add it the present bill amount and add interest on both the 
        amounts for a new total
    """