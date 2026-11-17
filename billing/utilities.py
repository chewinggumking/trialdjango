from members.models import RentalStatus


def create_flat_bills(flat, bill_type):
    rented_flat = RentalStatus.objects.filter(flat_number=flat).first()
    if not rented_flat or not rented_flat.is_rented:
        rental_noc = 0
    else:
        amount = bill_type.maintenance_total()
        rental_noc = float(amount) * 0.1

    flat.flatbill_set.create(
        municipal_tax=bill_type.municipal_tax,
        maintenance=bill_type.maintenance,
        water_charges=bill_type.water_charges,
        parking_charges=bill_type.parking_charges,
        sinking_fund=bill_type.sinking_fund,
        building_repair=bill_type.building_repair,
        elec_ins_chgs=bill_type.elec_ins_chgs,
        noc_charges=rental_noc,
    )


# --- Config: parking and interest rates ---
PARKING_RATES = {
    ("car", "covered"): 2000,
    ("car", "open"): 1200,
    ("bike", "covered"): 800,
    ("bike", "open"): 500,
}

EXTRA_VEHICLE_RATES = {
    "car": 1000,
    "bike": 400,
}

INTEREST_RATE = 0.21  # 21%


def calculate_parking_charges(flat):
    if not hasattr(flat, 'vehicles') or not flat.vehicles:
        return 0

    total_parking_charge = 0
    primary = flat.vehicles[0]
    vehicle_type = primary["type"]
    parking_type = primary["parking_type"]
    total_parking_charge += PARKING_RATES.get((vehicle_type, parking_type), 0)

    for extra_vehicle in flat.vehicles[1:]:
        total_parking_charge += EXTRA_VEHICLE_RATES.get(extra_vehicle["type"], 0)

    return total_parking_charge


def calculate_bill_with_interest(flat, current_bill_amount):
    if not hasattr(flat, 'bills') or not flat.bills:
        return current_bill_amount

    unpaid_bills = [b for b in flat.bills if not b.get("is_paid")]
    if not unpaid_bills:
        return current_bill_amount

    if len(unpaid_bills) == 1:
        last_bill_principal = unpaid_bills[0]["amount"]
        principal = current_bill_amount + last_bill_principal
        interest = last_bill_principal * INTEREST_RATE
        return principal + interest

    last_bill_principal_no_interest = unpaid_bills[-1]["amount"]
    combined_principal = last_bill_principal_no_interest + current_bill_amount
    interest = combined_principal * INTEREST_RATE
    return combined_principal + interest
