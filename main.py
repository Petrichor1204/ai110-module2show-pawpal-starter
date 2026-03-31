from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    owner = Owner(name="Jordan", available_start="07:00", available_end="19:00")

    pet1 = Pet(name="Mochi", species="dog", age=3, breed="Shiba")
    pet2 = Pet(name="Nori", species="cat", age=5, breed="Domestic Short Hair")

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # tasks for Mochi
    task1 = Task(title="Morning walk", duration_minutes=30, priority="high", frequency="daily", preferred_time="morning")
    task2 = Task(title="Feed", duration_minutes=15, priority="medium", frequency="daily", preferred_time="morning")

    # task for Nori
    task3 = Task(title="Litter box clean", duration_minutes=20, priority="high", frequency="daily", preferred_time="afternoon")
    task4 = Task(title="Play session", duration_minutes=25, priority="low", frequency="daily", preferred_time="evening")

    scheduler = Scheduler(owner)
    scheduler.add_task(task1, pet_name="Mochi")
    scheduler.add_task(task2, pet_name="Mochi")
    scheduler.add_task(task3, pet_name="Nori")
    scheduler.add_task(task4, pet_name="Nori")

    today_plan = scheduler.generate_schedule()

    print("Today's Schedule")
    print("-----------------")
    for entry in today_plan:
        print(
            f"{entry['start']} - {entry['end']}: {entry['pet']} -> {entry['task'].title} "
            f"[{entry['priority']}]"
        )

    print("\nPlan explanation:\n")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()