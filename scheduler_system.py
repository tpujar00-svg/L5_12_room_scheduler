
"""Manage room reservations and equipment scheduling."""

import json
from datetime import datetime

# Global state
reservations = {}
equipment_pool = {"projector": 2, "microphone": 4, "webcam": 1}
conflicts = []
next_reservation_id = 1


def schedule_room(room_id, time_slot, equipment_list=None):
    """Schedule a room and record any reservation conflicts."""
    global next_reservation_id

    if equipment_list is None:
        equipment_list = []

    for reservation in reservations.values():
        if (
            reservation["room"] == room_id
            and reservation["slot"] == time_slot
        ):
            conflicts.append(
                f"{room_id} double-booked at {time_slot}"
            )

    for equipment in equipment_list:
        if equipment not in equipment_pool:
            raise ValueError(f"Unknown equipment: {equipment}")
        if equipment_pool[equipment] <= 0:
            raise ValueError(f"No {equipment} available")

    for equipment in equipment_list:
        equipment_pool[equipment] -= 1

    reservations[next_reservation_id] = {
        "room": room_id,
        "slot": time_slot,
        "equipment": equipment_list.copy(),
    }
    reservation_id = next_reservation_id
    next_reservation_id += 1

    return reservation_id


def cancel_reservation(reservation_id):
    """Cancel a reservation and return its equipment."""
    reservation = reservations.get(reservation_id)

    if reservation is None:
        return False

    for equipment in reservation["equipment"]:
        equipment_pool[equipment] += 1

    del reservations[reservation_id]
    return True


def slot_hours(time_slot):
    """Calculate the duration of a slot formatted as start-end."""
    try:
        start, end = time_slot.split("-")
        return int(end) - int(start)
    except (ValueError, AttributeError):
        return 0


def export_schedule(file="schedule.json"):
    """Export reservations to a JSON file."""
    with open(file, "w", encoding="utf-8") as schedule_file:
        json.dump(reservations, schedule_file, indent=2)


def log_conflicts(file="conflicts.log"):
    """Append conflicts to a log and print its contents."""
    with open(file, "a", encoding="utf-8") as log_file:
        for conflict in conflicts:
            log_file.write(f"{datetime.now()} {conflict}\n")

    with open(file, "r", encoding="utf-8") as log_file:
        print(log_file.read())


def main():
    """Run the room scheduler demonstration."""
    schedule_room("Board-1", "09-11")
    schedule_room("Board-1", "09-11")

    schedule_room("Huddle-3", "14-12")
    schedule_room("Huddle-3", "1530")

    print("Slot length for b:", slot_hours(reservations[1]["slot"]))

    cancel_reservation(7)

    slot = input(
        "Slot for Board-2, like 10-12 (Enter for 10-12): "
    ).strip()
    if not slot:
        slot = "10-12"

    schedule_room("Board-2", slot, ["projector", "webcam"])
    export_schedule()
    log_conflicts()

    print("Equipment left:", equipment_pool)
    print("Reservations:", reservations)


if __name__ == "__main__":
    main()
