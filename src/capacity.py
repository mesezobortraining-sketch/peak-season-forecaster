"""Capacity planning: turn parcel volumes into the headcount needed."""
import numpy as np


def headcount_needed(parcels, target_uph, hours_per_associate, absence_rate):
    """Parcels -> labour hours -> people, allowing for absence.

    parcels              parcels to process (a number or a pandas Series)
    target_uph           units (parcels) one associate handles per hour
    hours_per_associate  productive hours each person works per day
    absence_rate         share of booked staff who don't show up (0.10 = 10%)
    """
    labour_hours = parcels / target_uph
    people = labour_hours / hours_per_associate / (1 - absence_rate)
    return np.ceil(people)
