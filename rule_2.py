def applyRule2(time, slotLength, weekSchedule, day_elective_slots, s, d):
    K = 2
    pos_in_day = day_elective_slots.index(s) if s in day_elective_slots else 0
    first_slot_time = weekSchedule[d][day_elective_slots[0]].startTime if day_elective_slots else time
    if pos_in_day < K:
        return first_slot_time
    return time - slotLength