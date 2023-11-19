# Ingint

Welcome to the "Ingint" backend repository. This readme file will guide you through the installation steps to set up and run the project on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python (3.9 or higher)
- pip (Python package manager)

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/oyeadii/ingintBackend.git
   ```
     
2. Change your working directory to the project folder:
   ```bash
   cd ingintBackend
   ```

3. Create a virtual environment (recommended) to isolate project dependencies:
   ```bash
   python3 -m venv venv
   ```

4. Activate the virtual environment (on Windows):
   ```bash
   venv\Scripts\activate
   ```
   - On macOS and Linux:
   ```bash
   source venv/bin/activate
   ```

5. Install project dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

6. Copy the .env.example file and rename it to .env. Edit the .env file and add the necessary environment variables specific to your project.

7. Migrate the database:
   ```bash
   python manage.py migrate
   ```

8. Create a superuser account to access the Django admin interface (follow the prompts):
   - Run below SQL command in your SQL viewer.
   ```bash
   INSERT INTO admin (email, password) VALUES ('<your email id here>', '$2b$12$vcxVVabhPRSqNLbL2M.noOMYdSXOZ3qzM0YSDTnKOFbdrDsDpNy8W');
   ```
   - Change your email in above command. Above password defaults to 'qwerty@1234'

9. Running the Project
   - Now that you have installed the project and set up your environment, you can run the Django development server:
   ```bash
   python manage.py runserver
   ```
   - The development server will start, and you can access the project at http://localhost:8000/.

## Disclaimer
   - This repo also includes code forked from https://github.com/run-llama/llama_index.git in folder named custom_llama_index.
   - This was done to have version control and also to add some custom configuration at the point of file upsert to pinecone.
