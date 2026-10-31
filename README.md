# SPENDLY

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)



## General Information
Spendly is a budgeting application built using Python and Tkinter. It allows users to keep track of their expenses, set monthly spending limits and monitor their savings goals. The application includes features such as spending alerts, expense categories and visual charts to help users better understand where their money is going.

Spendly aims to make managing money easier by keeping everything organised in one place. It was created to provide a simple and accessible way for users to stay on top of their spending, build better financial habits and work towards their savings goals.


## Setup

Spendly was developed using Python 3 and Tkinter. All libraries used are included in Python's standard library, so no additional packages or dependencies need to be installed. Therefore, a `requirements.txt` file is not required.

### Requirements
- Python 3
- Tkinter
- Visual Studio Code (VS Code) or another Python-compatible editor
- 
### Installation and Setup

1. Download and install [Python 3](https://www.python.org/downloads/).
2. Download the Spendly project folder and save it to your computer.
3. Open the project folder in Visual Studio Code.
4. Make sure the Python file and supporting CSV and JSON files are stored in the same folder.
5. Open the terminal in VS Code and enter:

   ```bash
   python3 SPENDLY.py
   ```

6. The Spendly application should open in a separate window, ready to use.

### Project Files

The main files used by Spendly are:

- `SPENDLY.py` – Contains the main application code.
- `expenses.csv` – Stores recorded expenses.
- `spendly_settings.json` – Saves budget settings and savings goals.
- `savings_contributions.csv` – Records savings contributions.

All data is stored locally within the project folder, allowing users to access their saved information when reopening the application.

## How It Works

Spendly is designed to be simple and easy to navigate. Once the application is opened, users can move between four main pages: Dashboard, Expenses, Add Expense and Budget & Savings.

### Using Spendly

1. **Dashboard:** View your total monthly spending, remaining budget, savings progress and a chart showing spending by category.
2. **Add Expense:** Enter an expense amount, select a category and add a description. The expense is automatically saved.
3. **Expenses:** View previously recorded transactions and see how much has been spent in each category. Users can also reset their expense totals.
4. **Budget & Savings:** Set a monthly spending limit and savings goal, add savings contributions and track progress towards the goal.

### Example Use Cases

- **Recording an expense:** A user spends $8 on a matcha. They can enter $8, select the Food category and add "Matcha" as the description.
- **Managing a budget:** A user sets a monthly spending limit of $500. As they record expenses, Spendly calculates how much of their budget remains.
- **Tracking savings:** A user sets a savings goal of $1,000 and adds $50 to their savings. Spendly updates their total savings and progress towards the goal.

### Code Examples

**1. Saving an Expense**

The following code uses Python's CSV library to save an expense, including its date, category, amount and description.

```python
with open(FILE_NAME, "a", newline="", encoding="utf-8") as file:
    csv.writer(file).writerow(
        [date, category, amount, description]
    )
```

**2. Calculating Monthly Spending**

This function calculates the total amount spent during the current month by adding together recorded expenses.

```python
def get_monthly_spending():
    month = datetime.now().strftime("%Y-%m")

    return sum(
        expense["Amount"]
        for expense in read_expenses()
        if expense["Date"].startswith(month)
    )
```

**3. Saving Budget and Savings Settings**

Spendly uses JSON to store user settings so they can be accessed again when the application is reopened.

```python
def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)
```

These functions allow Spendly to record financial information, calculate spending totals and save user data between sessions.


## Features
- **Expense Tracking** – Add, view and organise expenses into different categories.
- **Monthly Budget** – Set a monthly spending limit and keep track of your spending.
- **Savings Goal Tracker** – Set personal savings goals and monitor your progress.
- **Savings Contributions** – Add money towards your savings goal and view your total savings.
- **Spending Breakdown** – View spending totals by category through charts and summaries.
- **Dashboard** – View your expenses, monthly budget and savings progress in one place.
- **Reset Totals** – Reset spending records with a confirmation message.
- **Confetti Animation** – A celebration animation when adding to your savings.
- **Data Storage** – Save expenses, savings and budget settings using CSV and JSON files.



## Project Status
Project is: _in progress_ / _complete_ / _no longer being worked on_. If you are no longer working on it, provide reasons why.


## Room for Improvement
Include areas you believe need improvement / could be improved. Also add TODOs for future development.

Room for improvement:
- Improvement to be done 1
- Improvement to be done 2

To do:
- Feature to be added 1
- Feature to be added 2


## Acknowledgements
Give credit here.
- This project was inspired by...
- This project was based on [this tutorial](https://www.example.com).
- Many thanks to...

