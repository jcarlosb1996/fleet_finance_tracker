Fleet Finance Tracker

A Django-based web application to manage vehicle-based income and expenses.
Designed for entrepreneurs and fleet owners who track multiple income sources (Turo, Uber, Amazon, etc.) and shared ownership with partners.

 Features

 Add Deposits: Record income from various sources (Turo, Uber, Amazon, or others).
  <img width="751" height="654" alt="Screenshot 2025-11-13 at 2 09 55 PM" src="https://github.com/user-attachments/assets/0dbfb1c1-ff13-45b2-80c8-a258609667c3" />

 Vehicle Management: Add and organize vehicles under your fleet.
  <img width="812" height="777" alt="Screenshot 2025-11-13 at 2 11 06 PM" src="https://github.com/user-attachments/assets/38e89ea0-ac65-4e33-ad12-612362d03daf" />
  <img width="1336" height="617" alt="Screenshot 2025-11-13 at 2 12 52 PM" src="https://github.com/user-attachments/assets/348bdd2a-7afd-40cd-a138-f9ac08fa0dbd" />

 Partner Tracking: Assign partners and automatically split profits based on percentage.
   <img width="1407" height="280" alt="Screenshot 2025-11-13 at 2 15 34 PM" src="https://github.com/user-attachments/assets/d96e4ce5-4d38-4e03-ad28-c7a937ea3894" />
  <img width="889" height="389" alt="Screenshot 2025-11-13 at 2 15 16 PM" src="https://github.com/user-attachments/assets/4b384fd4-bae4-495e-b7be-6df302d964ca" />

 Recurring Expenses: Track ongoing monthly or weekly costs.
 <img width="869" height="704" alt="Screenshot 2025-11-13 at 2 17 09 PM" src="https://github.com/user-attachments/assets/8107ff57-09f0-448d-a31e-286524288b34" />
 <img width="1325" height="449" alt="Screenshot 2025-11-13 at 2 16 46 PM" src="https://github.com/user-attachments/assets/2fb31184-2092-4fea-aa2e-426caa61d045" />

 Weekly Summary Dashboard: Displays owner vs. partner weekly earnings after expenses.
  <img width="1359" height="375" alt="Screenshot 2025-11-13 at 2 18 09 PM" src="https://github.com/user-attachments/assets/878bb865-25db-488a-81ea-06d4f92847b5" />

 Month-to-Month Earnings: View total net income across months for each source.
  <img width="1440" height="451" alt="Screenshot 2025-11-13 at 2 21 36 PM" src="https://github.com/user-attachments/assets/bf6ac028-3a37-4edf-845f-37c2f17a1303" />

 Automatic Calculations: Net income is computed dynamically after partner shares and expenses.
 
 Tech Stack

Backend: Django (Python)

Database: SQLite (for local use)

Frontend: Bootstrap 5 + Django Templates

Other: Pillow (for images), Python Decimal for precision math



Setup Instructions
# Clone the repository
git clone https://github.com/jcarlosb1996/fleet_finance_tracker.git
cd fleet_finance_tracker

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python3 manage.py migrate

# Start the local server
python3 manage.py runserver
