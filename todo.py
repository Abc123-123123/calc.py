# todo.py

import os

# 🟢 SET YOUR FILE PATH HERE
# Example: "C:/Users/YourName/Documents/tasks.txt"
filename = "D:\daily task\calc.py"

def load_tasks(file_path):
    tasks = []
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                tasks.append(line.strip())
    return tasks

def save_tasks(tasks, file_path):
    with open(file_path, "w") as file:
        for task in tasks:
            file.write(task + "\n")

def show_tasks(tasks):
    if not tasks:
        print("No tasks yet.")
    else:
        print("Your tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")

def main():
    tasks = load_tasks(filename)

    while True:
        print("\nTo-Do List Menu:")
        print("1. View tasks")
        print("2. Add task")
        print("3. Remove task")
        print("4. Exit")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            show_tasks(tasks)

        elif choice == "2":
            new_task = input("Enter new task: ")
            tasks.append(new_task)
            save_tasks(tasks, filename)
            print("Task added.")

        elif choice == "3":
            show_tasks(tasks)
            try:
                index = int(input("Enter task number to remove: ")) - 1
                if 0 <= index < len(tasks):
                    removed = tasks.pop(index)
                    save_tasks(tasks, filename)
                    print(f"Removed: {removed}")
                else:
                    print("Invalid task number.")
            except ValueError:
                print("Please enter a valid number.")

        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()