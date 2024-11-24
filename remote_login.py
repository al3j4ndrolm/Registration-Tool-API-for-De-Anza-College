from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import smtplib
from email.mime.text import MIMEText
import time
import os

# Set up Flask app
app = Flask(__name__)
#debug test

# Function to automate registration
def automate_registration(username, password, crns, term):
	# Chrome Options
	options = Options()
	options.add_argument("--headless")  # Headless mode
	options.add_argument("--no-sandbox")  # Avoid permission issues
	options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues
	options.add_argument("--disable-gpu")  # Disable GPU acceleration
	options.add_argument("--disable-extensions")  # Disable extensions
	options.add_argument("--remote-debugging-port=9222")  # Debugging support

	# Set ChromeDriver service
	service = Service("/usr/local/bin/chromedriver")  # Update path if necessary
	driver = webdriver.Chrome(service=service, options=options)

	try:
		# Open login page
		driver.get("https://experience.elluciancloud.com/fdaccdso/page/001G000000iHnVbIAK/FHDA-student/FHDAExtStudent/StudentRegistrationExt/")

		# Login
		input_myportal_credentials(driver, username, password)

		if check_valid_credentials(driver):

			if check_access_to_myportal(driver):
				automatic_registration(driver, term, crns)

			elif check_duos_verification_required(driver):
				pass_worker_identification(driver)
				automatic_registration(driver,term, crns)

		else:
			raise Exception("The credentials are invalid (CWID or password are incorrect)")
		return return_result_message(driver)

	except Exception as e:
		raise Exception(f"Automation failed: {str(e)}")

	finally:
		driver.quit()

# Flask route for registration
@app.route('/register_classes', methods=['GET', 'POST'])
def register_classes():

	if request.method == 'GET':

		start_time = time.perf_counter()

		# Extract parameters from request
		username = request.args.get("username")
		password = request.args.get("password")
		crns = request.args.getlist("crns")  # Multiple CRNs
		term = request.args.get("term")

		# Validate inputs
		if not username or not password or not crns or not term:
			return jsonify({"error": "Missing required fields"}), 400

		# Run Selenium automation
		try:
			result = automate_registration(username, password, crns, term)
			return jsonify({"time_elapsed": time.perf_counter() - start_time, "status": "Success", "result": result}), 200
		except Exception as e:
			return jsonify({"time_elapsed": round(time.perf_counter() - start_time, 2), "status": "Failure", "error": str(e)}), 500

def automatic_registration(driver, term, crns):
	access_registration_tool(driver)
	select_term_to_register(driver, term)
	input_crns_to_register(driver, crns)
	submit_and_register_classes(driver)

# Selenium helper functions
def input_myportal_credentials(driver, username, password):
	username_field = driver.find_element(By.ID, "username")
	password_field = driver.find_element(By.ID, "password")
	username_field.send_keys(username)
	password_field.send_keys(password)
	password_field.send_keys(Keys.RETURN)

@app.route('/api/login', methods=['POST'])
def register():
    data = request.json  # Parses JSON body
    username = data['username']
    password = data['password']
    return f"Received username: {username} and password: {password}"

def check_valid_credentials(driver):
	try:

		WebDriverWait(driver, 1).until(
			EC.visibility_of_element_located((By.CLASS_NAME, 'alert-danger'))  # Ensure visibility
		)
		return False  # Credentials are invalid
	except TimeoutException:
		return True  # Credentials are valid


def check_duos_verification_required(driver):
	try:
		WebDriverWait(driver, 2).until(
			EC.presence_of_element_located((By.CLASS_NAME, 'logo--white-label'))
		)
		return True
	except TimeoutException:
		return False

def check_extreme_duos_verification_required(driver):

	try:
		instruction = WebDriverWait(driver, 2).until(
			EC.visibility_of_element_located((By.CLASS_NAME, 'row.display-flex.instruction-text'))  # Ensure visibility
		)

		if instruction == "Verify it's you by entering this verification code in the Duo Mobile app...":
			return True
		else:
			False
	except TimeoutException:
		return False

def pass_worker_identification(driver):

	if check_extreme_duos_verification_required(driver):
		send_email("lopezalejandro5b@gmail.com", "MyProfessor - DUO verification code", f"Your DUO verification code for MyProfessor is: {get_duos_verification_code(driver)}")
	try:
		duos_verification_button = WebDriverWait(driver, 30).until(
			EC.element_to_be_clickable((By.ID, "trust-browser-button"))
		)
		duos_verification_button.click()
	except TimeoutException:
		raise Exception("Your Duo's verification expired. Please try again.")


def access_registration_tool(driver):
	try:
		# student_registration_card = WebDriverWait(driver, 30).until(
		# 	EC.element_to_be_clickable((By.ID, "StudentRegistrationCard"))
		# )
		# student_registration_card.click()

		add_or_drop_classes_link = WebDriverWait(driver, 10).until(
			EC.element_to_be_clickable((By.LINK_TEXT, "Add or Drop Classes"))
		)
		add_or_drop_classes_link.click()
		driver.switch_to.window(driver.window_handles[1])  # Switch to new tab
	except Exception as e:
		raise Exception("There's a problem accessing the registration tool!")

def select_term_to_register(driver, term):
	try:
		dropdown = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, "term_id"))
		)
		select = Select(dropdown)
		select.select_by_visible_text(term)
		submit_button = driver.find_element(By.XPATH, "//input[@value='Submit']")
		submit_button.click()
	except Exception as e:
		raise Exception(f"There's a problem selecting the term {term}: {str(e)}")

def input_crns_to_register(driver, crn_list):
	for i, crn in enumerate(crn_list, start=1):
		try:
			crn_input = driver.find_element(By.ID, f"crn_id{i}")
			crn_input.clear()
			crn_input.send_keys(crn)
		except Exception as e:
			raise Exception("There's a problem inputing your CRNS!")

def get_duos_verification_code(driver):
    try:
        duos_verification_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'row.display-flex.align-flex-justify-content-center.verification-code'))
        )
        duos_verification_code = duos_verification_element.text

        if not duos_verification_code:
            raise Exception("Verification code element found, but it contains no text.")
        return duos_verification_code

    except TimeoutException:
        raise Exception("Unable to get the verification code from DUO within the timeout period.")
    except Exception as e:
        raise Exception(f"An error occurred while retrieving the verification code: {str(e)}")

def send_email(to_email, subject, message):
    try:
        # SMTP server configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("SENDER_EMAIL")  # Ensure environment variable is set
        sender_password = os.getenv("SENDER_PASSWORD")  # Use App Password for Gmail

        if not sender_email or not sender_password:
            print("Missing sender email or password.")
            return

        # Create the email
        msg = MIMEText(message, "plain")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        # Debug the message
        print("Message being sent:")
        print(msg.as_string())

        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def submit_and_register_classes(driver):
	try:
		submit_button = driver.find_element(By.XPATH, "//input[@value='Submit Changes']")
		submit_button.click()
	except Exception as e:
		raise Exception("There's a problem submiting your CRNS!")

def get_page_source(driver):
	page_source = driver.page_source
	with open("page_source.html", "w", encoding="utf-8") as file:
		file.write(page_source)
	print("Page source saved as 'page_source.html'")

def return_result_message(driver):

	selector = f"table[summary='This layout table is used to present Registration Errors.']"
	table = driver.find_element(By.CSS_SELECTOR, selector)
    
    # Extracting all rows in the table (Individual classes)
	rows = table.find_elements(By.TAG_NAME, "tr")

	result = []
	for row in rows:
		cells = row.find_elements(By.TAG_NAME, "td")
		row_data = [cell.text.strip() for cell in cells]  # Get text from each cell
		if row_data:  # Ignore empty rows
			result.append(f"* ({row_data[1]}) {row_data[-1]} - {row_data[0]}")

	return result

def check_access_to_myportal(driver):

	try:
		myportal_header = WebDriverWait(driver, 3).until(
	            EC.presence_of_element_located((By.ID, 'experience-header'))
	        )
		return True
	except:
		return False


# Run the app
if __name__ == "__main__":
	os.environ["DISPLAY"] = ":99"  # For Xvfb if needed
	app.run(host="0.0.0.0", port=5000, debug=False)
