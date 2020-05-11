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