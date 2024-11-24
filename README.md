# Registration Tool API for De Anza College

Overview
The Automated Class Registration API is a Python-based Flask application designed to automate
the process of class registration on the MyPortal platform. This script uses Selenium WebDriver to
simulate user interactions, making it easier for students to register for classes by simply providing
their credentials, term, and CRNs.

### Features
- Automates the login process to the MyPortal platform.
- Handles DUO two-factor authentication dynamically.
- Selects the specified term for registration.
- Inputs and registers CRNs for specified classes.
- Sends notifications, such as DUO verification codes, via email for added convenience.
- Designed to handle multiple simultaneous requests with Gunicorn.
Installation
### Prerequisites
- Python 3.9 or higher
- Google Chrome installed on the system
- ChromeDriver compatible with your Google Chrome version
- An AWS EC2 instance (optional for deployment)
- SMTP Email credentials for email notifications (Only if the user work on campus)
### Install Dependencies
1. Clone the repository:
 ```
 git clone https://github.com/al3j4ndrolm/Registration-Tool-API-for-De-Anza-College.git
 cd Registration-Tool-API-for-De-Anza-College
 ```
2. Install required Python libraries:
 ```
 pip install -r requirements.txt
 ```
3. Export environment variables for email notifications (Only if the user work on campus):
 ```
 export SENDER_EMAIL="your-email@gmail.com"
 export SENDER_PASSWORD="your-app-password"
 ```
Usage
### Running Locally
Start the Flask server:
```bash
python3 remote_login.py
```
Use a tool like curl or Postman to make GET or POST requests to the API.
### Deployment on AWS EC2
Start the script using `nohup` or `gunicorn` for production:
```bash
gunicorn -w 3 --threads 2 -b 0.0.0.0:5000 remote_login:app
```
Access the API using your EC2 public IP and port 5000.
API Endpoints
### `GET /register_classes`
**Description**: Automates the class registration process.
**Parameters:**
- `username` (string): Your MyPortal CWID.
- `password` (string): Your MyPortal password.
- `term` (string): The term for registration (e.g., "2024 Fall De Anza").
- `crns` (list): A list of CRNs for the classes to register.
**Example:**
```bash
curl
"http://<ec2-public-ip>:5000/register_classes?username=CWID&password=YourPassword&ter
m=2024+Fall+De+Anza&crns=27505,27506"
```
**Response:**
- **Success**:
 ```json
 {"result":["* (27505) Calculus III - Class registered successfully"],"status":"Success","time_elapsed": 11.25 seconds
 ```
- **Failure**:
 ```json
 { "status": "Failure", "error": "Error message" }
 ```
### How It Works
1. **Login Simulation**: Automates user login to MyPortal with Selenium.
2. **DUO Verification Handling**: Dynamically extracts and emails the DUO verification code if
required.
3. **Registration Workflow**: Navigates through the registration tool, selects the specified term,
inputs CRNs, and submits the registration.
4. **Error Handling**: Detects issues such as invalid credentials, expired DUO verification, or failed
registration.
### Limitations
- Requires consistent updates to match MyPortal's changing web elements.
- Dependent on network stability and the MyPortal platform's availability.
- Sensitive to simultaneous requests if not deployed with proper scaling (e.g., Gunicorn with multiple
workers).
### Security and Privacy
- User credentials are not stored and are only used during the session.
- Logs can be disabled or sanitized to prevent sensitive data exposure.
- HTTPS is recommended for secure communication in production.
### Contributing
Contributions are welcome! Please submit a pull request or raise issues for bug reports and feature
requests.
### License
This project is licensed under the Apache 2.0 License. See the LICENSE file for details.
### Disclaimer
This script is intended for educational purposes. Use it responsibly and ensure compliance with
MyPortal's terms of service.
