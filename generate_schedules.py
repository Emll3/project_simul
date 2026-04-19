"""
Schedule generator for the outpatient radiology department simulation.
Generates input .txt files for all strategy/urgent-slot combinations.

Format: 32 lines (slots), 6 columns (Mon-Sat), values: 1=elective, 2=urgent
"""

# Day structure:
# Slots 1-16: morning (08:00-11:45), Thu & Sat are half-days (only 16 slots)
# Slots 17-32: afternoon (13:00-16:45), Mon/Tue/Wed/Fri only
HALF_DAYS = {3, 5}  # Thursday (idx 3) and Saturday (idx 5)
FULL_SLOTS = 32
HALF_SLOTS = 16
NUM_DAYS = 6  # Mon-Sat

def get_available_slots(day: int) -> int:
    return HALF_SLOTS if day in HALF_DAYS else FULL_SLOTS

def total_slots_per_week() -> int:
    return sum(get_available_slots(d) for d in range(NUM_DAYS))
    # 4 full days * 32 + 2 half days * 16 = 128 + 32 = 160

# ── Strategy 1 ──────────────────────────────────────────────────────────────
# Urgent slots placed at the END of each morning/afternoon block, evenly spread.

def strategy1(num_urgent: int) -> list[list[int]]:
    """
    Urgent slots at end of morning and afternoon blocks, distributed evenly.
    Returns a 32x6 grid (rows=slots, cols=days).
    """
    schedule = [[1] * NUM_DAYS for _ in range(FULL_SLOTS)]

    # Count usable block-ends per day
    # Morning block: slots 0-15 (all days)
    # Afternoon block: slots 16-31 (full days only)
    # For half-days: only morning block
    morning_blocks = NUM_DAYS  # 6
    afternoon_blocks = NUM_DAYS - len(HALF_DAYS)  # 4
    total_blocks = morning_blocks + afternoon_blocks  # 10

    # Distribute urgent slots as evenly as possible across blocks
    # Build list of (day, block_end_slot) ordered by priority
    block_ends = []
    # Morning ends (slot index 15) for all days
    for d in range(NUM_DAYS):
        block_ends.append((d, 15))
    # Afternoon ends (slot index 31) for full days
    for d in range(NUM_DAYS):
        if d not in HALF_DAYS:
            block_ends.append((d, 31))

    # Place urgent slots starting from end of each block, cycling through blocks
    urgent_placed = 0
    block_idx = 0
    urgent_per_block = [0] * len(block_ends)

    while urgent_placed < num_urgent:
        urgent_per_block[block_idx % len(block_ends)] += 1
        urgent_placed += 1
        block_idx += 1

    for b_idx, (d, block_end) in enumerate(block_ends):
        count = urgent_per_block[b_idx]
        for i in range(count):
            slot = block_end - i
            if slot >= 0:
                schedule[slot][d] = 2

    return schedule


# ── Strategy 2 ──────────────────────────────────────────────────────────────
# Urgent slots evenly distributed over the day (as illustrated in Appendix Fig 5).
def strategy2(num_urgent: int) -> list[list[int]]:
    """
    Urgent slots evenly distributed over the available slots per day.
    Uses Bresenham-style even spacing to avoid duplicates.
    Returns a 32x6 grid.
    """
    schedule = [[1] * NUM_DAYS for _ in range(FULL_SLOTS)]

    total = total_slots_per_week()  # 160

    # Distribute num_urgent proportionally per day
    urgent_per_day = {}
    for d in range(NUM_DAYS):
        urgent_per_day[d] = num_urgent * get_available_slots(d) / total

    # Convert to integers while preserving total exactly (largest-remainder method)
    floored = {d: int(urgent_per_day[d]) for d in range(NUM_DAYS)}
    remainders = sorted(range(NUM_DAYS), key=lambda d: -(urgent_per_day[d] - floored[d]))
    diff = num_urgent - sum(floored.values())
    for d in remainders[:diff]:
        floored[d] += 1
    urgent_per_day = floored

    for d in range(NUM_DAYS):
        n = urgent_per_day[d]
        available = get_available_slots(d)
        if n == 0:
            continue

        # Bresenham-style even spacing: guarantees no duplicates
        chosen = set()
        for i in range(n):
            # Maps i to an evenly spaced index across 'available' slots
            idx = int((i + 0.5) * available / n)
            chosen.add(idx)

        for s in chosen:
            schedule[s][d] = 2

    return schedule


# ── Strategy 3 ──────────────────────────────────────────────────────────────
# After every 6 elective slots, one urgent slot (from beginning of session).
def strategy3(num_urgent: int) -> list[list[int]]:
    """
    Starting from the beginning of a session, one urgent slot is placed
    after every block of 6 elective slots. num_urgent is ignored — the
    total follows naturally from the block size (every 7th slot is urgent).
    Returns a 32x6 grid.
    """
    schedule = [[1] * NUM_DAYS for _ in range(FULL_SLOTS)]

    for d in range(NUM_DAYS):
        elective_count = 0
        for slot_idx in range(get_available_slots(d)):
            if elective_count == 6:
                schedule[slot_idx][d] = 2  # urgent slot after 6 elective
                elective_count = 0
            else:
                elective_count += 1  # remains elective (already 1)

    return schedule


# ── File writer ──────────────────────────────────────────────────────────────

def write_schedule(schedule: list[list[int]], filepath: str):
    """Write a 32x6 schedule grid to a text file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for slot_idx in range(FULL_SLOTS):
            row = ''.join(str(schedule[slot_idx][d]) for d in range(NUM_DAYS))
            f.write(row + '\n')
    print(f"Written: {filepath}")


def generate_all_schedules(output_dir: str = '.'):
    """Generate all required schedule files."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    strategies = {
        'S1': strategy1,
        'S2': strategy2,
        # Strategy 3 doesn't take num_urgent as a free parameter in the same way,
        # but we still generate for context
        'S3': strategy3,
    }

    urgent_counts = list(range(10, 21))  # 10 to 20

    for strat_name, strat_fn in strategies.items():
        for n_urgent in urgent_counts:
            schedule = strat_fn(n_urgent)
            filename = f"input-{strat_name}-{n_urgent}.txt"
            filepath = os.path.join(output_dir, filename)
            write_schedule(schedule, filepath)

    print(f"\nAll schedules written to '{output_dir}'")


if __name__ == '__main__':
    generate_all_schedules('schedules')
