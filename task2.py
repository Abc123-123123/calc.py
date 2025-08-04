import os

filename = r"D:\daily task\tasks.txt"  # <-- Correct path

def load_tasks():
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return [line.strip() for line in file.readlines()]
    return []

def save_tasks(tasks):
    with open(filename, "w") as file:
        for task in tasks:
            file.write(task + "\n")

def show_tasks(tasks):
    if not tasks:
        print("No tasks yet.")
    else:
        print("Your tasks:")
        for i, task in enumerate(tasks, start=1):
            print(f"{i}. {task}")

def main():
    tasks = load_tasks()

    while True:
        print("\nTo-Do List Menu:")
        print("1. View tasks")
        print("2. Add task")
        print("3. Remove task")
        print("4. Exit")

        choice = input("Choose 1-4: ").strip()

        if choice == "1":
            show_tasks(tasks)

        elif choice == "2":
            task = input("Enter new task: ")
            tasks.append(task)
            save_tasks(tasks)
            print("✅ Task added.")

        elif choice == "3":
            show_tasks(tasks)
            try:
                number = int(input("Task number to remove: ")) - 1
                if 0 <= number < len(tasks):
                    removed = tasks.pop(number)
                    save_tasks(tasks)
                    print(f"🗑️ Removed: {removed}")
                else:
                    print("Invalid task number.")
            except ValueError:
                print("❌ Enter a valid number.")

        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
