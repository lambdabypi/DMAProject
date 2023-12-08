import mysql.connector
from faker import Faker
import re

# Create a Faker instance
fake = Faker()

# Connect to the MySQL database
try:
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='DBMS*fall2023',
        database='energy_grid'
    )
    cursor = conn.cursor()

    # Generate and insert fake data into the Customer table
    for _ in range(10000):
        fake_name = fake.name()
        fake_phone_number = fake.phone_number()[:10]
        fake_email = fake.email()

        # Generate a unique AccountNo for Customer table
        fake_account_no = None
        while True:
            fake_account_no = fake.random_int(min=1, max=1000000, step=2)
            query_check = f"SELECT COUNT(*) FROM customer WHERE AccountNo = {fake_account_no}"
            cursor.execute(query_check)
            result = cursor.fetchone()[0]
            if result == 0:
                break

        # Generate an address without commas and new lines
        fake_address = f"{fake.street_address()}, {fake.city()}, {fake.state_abbr()} {fake.random_int(min=37600, max=38200)}"
        fake_address = fake_address.replace(',', ' ').replace('\n', ' ')  # Replace commas and new lines with spaces

        query_customer = f"INSERT INTO customer (AccountNo, CustomerName, PhoneNo, EmailID, Address) " \
                f"VALUES ({fake_account_no}, '{fake_name}', '{fake_phone_number}', '{fake_email}', '{fake_address}')"
        cursor.execute(query_customer)

    # Commit the changes for the customer table
    conn.commit()

    # Retrieve existing CustomerID values from the customer table
    cursor.execute("SELECT CustomerID, AccountNo FROM customer")
    customer_data = {row[0]: row[1] for row in cursor.fetchall()}

    # Generate and insert fake data into the UtilityCompanies table
    for _ in range(10000):
        fake_company_name = re.sub(r'[\n,]', ' ', fake.company())  # Replace new lines and commas with spaces
        fake_description = re.sub(r'[\n,]', ' ', fake.text())  # Replace new lines and commas with spaces
        fake_phone_no_uc = fake.phone_number()[:10]
        fake_address_uc = re.sub(r'[\n,]', ' ', fake.address())  # Replace new lines and commas with spaces
        fake_cost_uc = fake.random_int(min=1, max=10000, step=1)

        # Use an existing CustomerID value
        fake_customer_id = fake.random_element(elements=list(customer_data.keys()))

        # Use the corresponding AccountNo for UtilityCompanies table
        fake_account_no_uc = customer_data[fake_customer_id]

        try:
            query_utility = "INSERT INTO utilitycompanies (AccountNo, CustomerID, CompanyName, Description, PhoneNo, Address, Cost) " \
                            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            data = (fake_account_no_uc, fake_customer_id, fake_company_name, fake_description, fake_phone_no_uc, fake_address_uc, fake_cost_uc)
            cursor.execute(query_utility, data)
        except mysql.connector.Error as utility_error:
            if utility_error.errno == 1062:  # Duplicate entry error
                print(f"Duplicate entry detected for AccountNo {fake_account_no_uc}. Regenerating AccountNo.")
                continue
            else:
                raise

    # Commit the changes for the UtilityCompanies table
    conn.commit()

    # Generate and insert fake data into the Contracts table
    for _ in range(10000):
        fake_contract_name = fake.company()
        fake_type_of_contract = fake.random_element(elements=('Standard', 'Premium', 'Custom'))
        fake_description = fake.text()

        query_contract = f"INSERT INTO Contracts (ContractName, TypeOfContract, Description) " \
                        f"VALUES ('{fake_contract_name}', '{fake_type_of_contract}', '{fake_description}')"
        cursor.execute(query_contract)

    # Commit the changes for the Contracts table
    conn.commit()

    # Retrieve existing ContractID values from the Contracts table
    cursor.execute("SELECT ContractID FROM Contracts")
    contract_ids = [row[0] for row in cursor.fetchall()]

    # Retrieve existing UCID values from the utilitycompanies table
    cursor.execute("SELECT UCID FROM utilitycompanies")
    ucid_values = [row[0] for row in cursor.fetchall()]

    # Generate and insert fake data into the MainEnergyGrid table
    for _ in range(10000):
        fake_type_of_energy = fake.random_element(elements=('Solar', 'Wind', 'Hydro', 'Nuclear'))

        # Use existing ContractID and UCID values
        fake_contract_id = fake.random_element(elements=contract_ids)
        fake_ucid = fake.random_element(elements=ucid_values)

        query_main = f"INSERT INTO mainenergygrid (ContractID, UCID, TypeOfEnergy) " \
                    f"VALUES ({fake_contract_id}, {fake_ucid}, '{fake_type_of_energy}')"
        cursor.execute(query_main)

    # Commit the changes for the MainEnergyGrid table
    conn.commit()

    # Generate and insert fake data into the ElectricityGrid table
    for _ in range(10000):
        fake_voltage_level = fake.random_int(min=100, max=1000, step=100)
        fake_power_capacity = fake.random_int(min=1000, max=10000, step=1000)
        fake_load_quantity = fake.random_int(min=10, max=100, step=10)
        fake_fault_status = fake.random_element(elements=('Normal', 'Minor Fault', 'Major Fault'))

        query_electricity_grid = f"INSERT INTO electricitygrid (VoltageLevel, PowerCapacity, LoadQuantity, FaultStatus) " \
                                 f"VALUES ({fake_voltage_level}, {fake_power_capacity}, {fake_load_quantity}, '{fake_fault_status}')"
        cursor.execute(query_electricity_grid)

    # Commit the changes for the ElectricityGrid table
    conn.commit()

    # Generate and insert fake data into the GasGrid table
    for _ in range(10000):
        fake_pressure_level = fake.random_int(min=10, max=100, step=10)
        fake_flow_capacity = fake.random_int(min=100, max=1000, step=100)
        fake_gas_comp = fake.word()
        fake_leak_status = fake.random_element(elements=('No Leak', 'Minor Leak', 'Major Leak'))

        query_gas_grid = f"INSERT INTO gasgrid (PressureLevel, FlowCapacity, GasComp, LeakStatus) " \
                         f"VALUES ({fake_pressure_level}, {fake_flow_capacity}, '{fake_gas_comp}', '{fake_leak_status}')"
        cursor.execute(query_gas_grid)

    # Commit the changes for the GasGrid table
    conn.commit()

    cursor.execute("SELECT GridID FROM mainenergygrid")
    grid_ids = [row[0] for row in cursor.fetchall()]

    # Generate and insert fake data into the Government table
    for _ in range(10000):
        fake_contract_id_gov = fake.random_element(elements=contract_ids)
        fake_grid_id_gov = fake.random_element(elements=grid_ids)
        fake_ucid_gov = fake.random_element(elements=ucid_values)
        fake_customer_id_gov = fake.random_element(elements=list(customer_data.keys()))

        query_government = f"INSERT INTO government (ContractID, GridID, UCID, CustomerID) " \
                           f"VALUES ({fake_contract_id_gov}, {fake_grid_id_gov}, {fake_ucid_gov}, {fake_customer_id_gov})"
        cursor.execute(query_government)

    # Commit the changes for the Government table
    conn.commit()

    # Generate and insert fake data into the RMSupplier table
    for _ in range(10000):
        fake_contract_id_supplier = fake.random_element(elements=contract_ids)
        fake_name_supplier = fake.company()
        fake_address_supplier = fake.address()

        query_rmsupplier = f"INSERT INTO rmsupplier (ContractID, Name, Address) " \
                           f"VALUES ({fake_contract_id_supplier}, '{fake_name_supplier}', '{fake_address_supplier}')"
        cursor.execute(query_rmsupplier)

    # Commit the changes for the RMSupplier table
    conn.commit()

    # Generate and insert fake data into the WaterGrid table
    for _ in range(10000):
        fake_pressure_level_water = fake.random_int(min=10, max=100, step=10)
        fake_flow_capacity_water = fake.random_int(min=100, max=1000, step=100)
        fake_water_quality = fake.random_element(elements=('Potable', 'Non-Potable'))
        fake_infrastructure_status = fake.random_element(elements=('Good', 'Needs Maintenance'))

        query_water_grid = f"INSERT INTO watergrid (PressureLevel, FlowCapacity, WaterQuality, InfrastructureStatus) " \
                           f"VALUES ({fake_pressure_level_water}, {fake_flow_capacity_water}, " \
                           f"'{fake_water_quality}', '{fake_infrastructure_status}')"
        cursor.execute(query_water_grid)

    # Commit the changes for the WaterGrid table
    conn.commit()

    # Generate and insert fake data into the Business table
    for _ in range(10000):
        fake_number_of_people = fake.random_int(min=1, max=10000, step=1)

        # Define a list of industry types
        industry_types = ['Healthcare', 'Sports', 'NGOs', 'Agriculture', 'Technology', 'Finance', 'Education', 'Retail', 'Manufacturing']

        # Randomly choose an industry type
        fake_type_of_business = fake.random_element(elements=industry_types)

        # Use an existing CustomerID value
        fake_customer_id_business = fake.random_element(elements=list(customer_data.keys()))

        try:
            query_business = f"INSERT INTO business (CustomerID, TypeOfBusiness, NumberOfPeople) " \
                 f"VALUES ({fake_customer_id_business}, '{fake_type_of_business}', {fake_number_of_people})"
            cursor.execute(query_business)

        except mysql.connector.Error as business_error:
            if business_error.errno == 1062:  # Duplicate entry error
                print(f"Duplicate entry detected for CustomerID {fake_customer_id_business}. Regenerating CustomerID.")
                continue
            else:
                raise

    # Commit the changes for the Business table
    conn.commit()

    # Generate and insert fake data into the Residential table
    for _ in range(10000):
        fake_number_of_people_residential = fake.random_int(min=1, max=10, step=1)

        # Use an existing CustomerID value
        fake_customer_id_residential = fake.random_element(elements=list(customer_data.keys()))

        try:
            query_residential = f"INSERT INTO residential (CustomerID, NumberOfPeople) " \
                    f"VALUES ({fake_customer_id_residential}, {fake_number_of_people_residential})"
            cursor.execute(query_residential)

        except mysql.connector.Error as residential_error:
            if residential_error.errno == 1062:  # Duplicate entry error
                print(f"Duplicate entry detected for CustomerID {fake_customer_id_residential}. Regenerating CustomerID.")
                continue
            else:
                raise

    # Commit the changes for the Residential table
    conn.commit()
    print("Data insertion successful.")

except mysql.connector.Error as e:
    print(f"Error: {e}")

finally:
    # Close the connection
    if conn.is_connected():
        cursor.close()
        conn.close()
