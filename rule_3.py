def applyRule3(time, slotLength, weekSchedule, day_elective_slots, s, d):
    B = 2
    pos_in_day = day_elective_slots.index(s)
    block_start_pos = (pos_in_day // B) * B
    block_start_slot = day_elective_slots[block_start_pos]
    return weekSchedule[d][block_start_slot].startTime