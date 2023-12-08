from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key

# Configure MySQL
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'DBMS*fall2023',
    'database': 'energy_grid',
    'raise_on_warnings': True
}

# Create MySQL connection
try:
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()
    print("Connected to MySQL Database!")
except Error as e:
    print(f"Error: {e}")

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Define User model
class Users(UserMixin):
    def __init__(self, user_id, username, password_hash):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Query the database to get the User by user_id
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            user_id, username, password_hash = user_data
            user = Users(user_id, username, password_hash)
            return user
        else:
            return None
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

# Define RegistrationForm
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# Define LoginForm
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    register = BooleanField('Register', default=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            # Create a new connection and cursor
            connection = mysql.connector.connect(**mysql_config)
            cursor = connection.cursor()

            # Query the database to get the user by username
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()

            if user_data and Users(*user_data).check_password(password):
                user = Users(*user_data)
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('index'))  # Redirect to the index page

            else:
                flash('Invalid username or password', 'error')

        except Exception as e:
            flash(f"Error: {e}", 'error')

        finally:
            # Close the cursor and connection
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection and connection.is_connected():
                connection.close()

    return render_template('login.html', form=form, error=flash('error'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            # Create a new connection and cursor
            connection = mysql.connector.connect(**mysql_config)
            cursor = connection.cursor()

            # Check if the username is already taken
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Username already taken, please choose another one.', 'error')
            else:
                # Create a new user and save to the database
                new_user = Users(None, username, None)
                new_user.set_password(password)

                # Insert the new user into the database
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                               (new_user.username, new_user.password_hash))
                connection.commit()

                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))

        except Exception as e:
            flash(f"Error: {e}", 'error')

        finally:
            # Close the cursor and connection
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection and connection.is_connected():
                connection.close()

    return render_template('register.html', form=form)

# Routes and other functions...
@app.route('/')
def login1():
    return redirect(url_for('login'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/query1_results')
@login_required
def query1_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query1 = """SELECT * 
                FROM customer 
                WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(customer.Address, ' ', -1), ' ', 1) = '37625'
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query1)

        # Fetch all results and column names
        results1 = cursor.fetchall()
        columns1 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query1_result.html', results=results1, columns=columns1)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query2_results')
@login_required
def query2_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query2 = """SELECT rms.SupplierID, rms.Name AS SupplierName, rms.Address AS SupplierAddress, con.ContractName, meg.GridID,
                    meg.TypeOfEnergy
                    FROM rmsupplier rms
                    JOIN mainenergygrid meg ON rms.ContractID = meg.ContractID
                    JOIN contracts con ON meg.ContractID = con.ContractID
                    Limit 5
                """
        
        # Execute the custom query
        cursor.execute(query2)

        # Fetch all results and column names
        results2 = cursor.fetchall()
        columns2 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query2_result.html', results=results2, columns=columns2)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query3_results')
@login_required
def query3_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query3 = """
                SELECT meg.GridID, meg.TypeOfEnergy, eg.VoltageLevel AS ElectricityVoltageLevel,
                    eg.PowerCapacity AS ElectricityPowerCapacity, eg.LoadQuantity AS ElectricityLoadQuantity,
                    eg.FaultStatus AS ElectricityFaultStatus, gg.PressureLevel AS GasPressureLevel,
                    gg.FlowCapacity AS GasFlowCapacity, gg.GasComp AS GasComposition, gg.LeakStatus AS GasLeakStatus,
                    gg.InfrastructureStatus AS GasInfrastructureStatus, wg.PressureLevel AS WaterPressureLevel,
                    wg.FlowCapacity AS WaterFlowCapacity, wg.WaterQuality AS WaterQuality,
                    wg.InfrastructureStatus AS WaterInfrastructureStatus
                FROM mainenergygrid meg
                INNER JOIN contracts con ON meg.ContractID = con.ContractID
                INNER JOIN electricitygrid eg ON meg.GridID = eg.GridID
                INNER JOIN gasgrid gg ON meg.GridID = gg.GridID
                INNER JOIN watergrid wg ON meg.GridID = wg.GridID
                WHERE meg.TypeOfEnergy = 'Wind'
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query3)

        # Fetch all results and column names
        results3 = cursor.fetchall()
        columns3 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query3_result.html', results=results3, columns=columns3)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query4_results')
@login_required
def query4_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query4 = """
                SELECT c.TypeOfContract, COUNT(*) AS TotalCount
                FROM contracts c
                LEFT JOIN mainenergygrid meg ON c.ContractID = meg.ContractID
                LEFT JOIN rmsupplier rs ON c.ContractID = rs.ContractID
                GROUP BY c.TypeOfContract
                ORDER BY c.TypeOfContract
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query4)

        # Fetch all results and column names
        results4 = cursor.fetchall()
        df4 = pd.read_sql_query(query4, connection)
        columns4 = [column[0] for column in cursor.description]

        ax = df4.plot(kind='bar', x='TypeOfContract', y='TotalCount', legend=False, figsize=(12,8))
        plt.title('Total Count of Contracts by Type')
        plt.xlabel('Type of Contract')
        plt.ylabel('Total Count')

        for p in ax.patches:
            ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 10), textcoords='offset points')

        # Save the plot to a file (in non-interactive mode)
        plot_filepath = r'D:\Documents\Prof_Docs\DMA\ProjectFiles\static\plot4.png'
        plt.savefig(plot_filepath)

        plt.show()

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query4_result.html', results=results4, columns=columns4, query=query4, df=df4, plot_filepath=plot_filepath)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query5_results')
@login_required
def query5_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query5 = """
                SELECT CompanyName, SUM(Cost) AS TotalCost
                FROM utilitycompanies
                GROUP BY CompanyName
                ORDER BY TotalCost DESC
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query5)

        # Fetch all results and column names
        results5 = cursor.fetchall()
        columns5 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query5_result.html', results=results5, columns=columns5)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query6_results')
@login_required
def query6_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query6 = """SELECT meg.TypeOfEnergy, COUNT(*) as EnergyCount
                FROM mainenergygrid meg
                JOIN contracts con ON meg.ContractID = con.ContractID
                JOIN utilitycompanies uc ON meg.UCID = uc.UCID
                JOIN customer cu ON uc.CustomerID = cu.CustomerID
                WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(cu.Address, ' ', -1), ' ', 1) = '37853'
                GROUP BY meg.TypeOfEnergy
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query6)

        # Fetch all results and column names
        results6 = cursor.fetchall()
        df6 = pd.read_sql_query(query6, connection)
        columns6 = [column[0] for column in cursor.description]
        target_pincode = '37853'
        energy_types = []
        energy_counts = []

        for row in results6:
            energy_type, count = row
            energy_types.append(energy_type)
            energy_counts.append(count)

        # Visualize the data using a bar chart for the specified pincode
        print("\nVisualization:")
        plt.figure(figsize=(10, 6))
        plt.bar(energy_types, energy_counts, color=['blue', 'green', 'red', 'purple'])
        plt.title(f'Distribution of Energy Producer Types for Pincode {target_pincode}')
        plt.xlabel('Energy Type')
        plt.ylabel('Count')

        # Save the plot to a file (in non-interactive mode)
        plot_filepath = r'D:\Documents\Prof_Docs\DMA\ProjectFiles\static\plot6.png'
        plt.savefig(plot_filepath)

        plt.show()
        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query6_result.html', results=results6, columns=columns6, query=query6, df=df6, plot_filepath=plot_filepath)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query7_results')
@login_required
def query7_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query7 = """SELECT cu.CustomerName, b.TypeOfBusiness, b.NumberOfPeople, uc.Cost
                FROM customer cu
                JOIN business b ON cu.CustomerID = b.CustomerID
                JOIN utilitycompanies uc ON cu.CustomerID = uc.CustomerID
                WHERE b.TypeOfBusiness = "Sports"
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query7)

        # Fetch all results and column names
        results7 = cursor.fetchall()
        columns7 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query7_result.html', results=results7, columns=columns7)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query8_results')
@login_required
def query8_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query8 = """SELECT b.TypeOfBusiness, SUM(b.NumberOfPeople) AS TotalPeople, SUM(uc.Cost) AS TotalCost
                FROM business b
                JOIN customer c ON b.CustomerID = c.CustomerID
                LEFT JOIN utilitycompanies uc ON c.CustomerID = uc.CustomerID
                GROUP BY b.TypeOfBusiness
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query8)

        # Fetch all results and column names
        results8 = cursor.fetchall()
        df8 = pd.read_sql_query(query8, connection)
        columns8 = [column[0] for column in cursor.description]

        fig, ax1 = plt.subplots(figsize=(12, 6))

        color = 'tab:red'
        ax1.set_xlabel('Type of Business')
        ax1.set_ylabel('Total People', color=color)
        ax1.bar(df8['TypeOfBusiness'], df8['TotalPeople'], color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel('Total Cost', color=color)
        ax2.plot(df8['TypeOfBusiness'], df8['TotalCost'], color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        for i, v in enumerate(df8['TotalPeople']):
            ax1.text(i, v + 0.1, str(v), ha='center', va='bottom')

        plt.title('Total People and Cost by Type of Business')
        plt.tight_layout()

        # Save the plot to a file (in non-interactive mode)
        plot_filepath = r'D:\Documents\Prof_Docs\DMA\ProjectFiles\static\plot8.png'
        plt.savefig(plot_filepath)

        plt.show()

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query8_result.html', results=results8, columns=columns8, query=query8, df=df8, plot_filepath=plot_filepath)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query9_results')
@login_required
def query9_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query9 = """SELECT ContractName
                FROM contracts
                WHERE ContractID IN ( SELECT ContractID FROM mainenergygrid WHERE GridID IN (SELECT GridID FROM electricitygrid WHERE VoltageLevel > 50))
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query9)

        # Fetch all results and column names
        results9 = cursor.fetchall()
        columns9 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query9_result.html', results=results9, columns=columns9)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query10_results')
@login_required
def query10_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query10 = """SELECT CustomerName
                FROM customer
                WHERE CustomerID IN (SELECT CustomerID FROM business)
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query10)

        # Fetch all results and column names
        results10 = cursor.fetchall()
        columns10 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query10_result.html', results=results10, columns=columns10)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query11_results')
@login_required
def query11_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query11 = """SELECT c.GridID, c.TypeOfEnergy, uc.CompanyName, uc.Cost
                FROM mainenergygrid c
                JOIN utilitycompanies uc ON c.UCID = uc.UCID
                JOIN (SELECT AVG(Cost) AS AvgCost FROM utilitycompanies) AS avg_costs ON uc.Cost > avg_costs.AvgCost
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query11)

        # Fetch all results and column names
        results11 = cursor.fetchall()
        columns11 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query11_result.html', results=results11, columns=columns11)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query12_results')
@login_required
def query12_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query12 = """SELECT CompanyName, (SELECT SUM(Cost) FROM utilitycompanies uc WHERE uc.UCID = u.UCID) AS "Total Cost (in thousands)"
                FROM utilitycompanies u
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query12)

        # Fetch all results and column names
        results12 = cursor.fetchall()
        columns12 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query12_result.html', results=results12, columns=columns12)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query13_results')
@login_required
def query13_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query13 = """SELECT r.CustomerID, cu.CustomerName, r.NumberOfPeople
                FROM residential r
                JOIN customer cu on r.CustomerID = cu.CustomerID 
                WHERE NumberOfPeople >= ALL (SELECT NumberOfPeople FROM residential where NumberOfPeople = 8)
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query13)

        # Fetch all results and column names
        results13 = cursor.fetchall()
        columns13 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query13_result.html', results=results13, columns=columns13)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query14_results')
@login_required
def query14_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query14 = """SELECT *
                FROM gasgrid g
                WHERE FlowCapacity > ANY (SELECT FlowCapacity FROM watergrid w)
                LIMIT 20;
                """
        
        # Execute the custom query
        cursor.execute(query14)

        # Fetch all results and column names
        results14 = cursor.fetchall()
        columns14 = [column[0] for column in cursor.description]
        
        df14 = pd.read_sql_query(query14, connection)
        leak_status_counts = df14['LeakStatus'].value_counts()

        plt.bar(leak_status_counts.index, leak_status_counts.values, color=['red', 'green','blue'])
        plt.xlabel('Leak Status')
        plt.ylabel('Count')
        plt.title('Gas Grid Leak Status')

        # Adding annotations
        for i, count in enumerate(leak_status_counts.values):
            plt.text(i, count + 0.1, str(count), ha='center', va='bottom')

        plot_filepath = r'D:\Documents\Prof_Docs\DMA\ProjectFiles\static\plot14.png'
        plt.savefig(plot_filepath)

        plt.show()

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query14_result.html', results=results14, columns=columns14, query=query14, df=df14, plot_filepath=plot_filepath)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query15_results')
@login_required
def query15_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query15 = """SELECT *
                FROM utilitycompanies uc
                WHERE EXISTS (SELECT 1 FROM mainenergygrid me WHERE me.UCID = uc.UCID)
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query15)

        # Fetch all results and column names
        results15 = cursor.fetchall()
        columns15 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query15_result.html', results=results15, columns=columns15)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query16_results')
@login_required
def query16_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query16 = """SELECT *
                FROM electricitygrid eg
                WHERE NOT EXISTS (SELECT 1 FROM government gov WHERE gov.GridID = eg.GridID)
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query16)

        # Fetch all results and column names
        results16 = cursor.fetchall()
        df16 = pd.read_sql_query(query16, connection)
        columns16 = [column[0] for column in cursor.description]

        fault_status_counts = df16['FaultStatus'].value_counts()

        plt.pie(fault_status_counts, labels=fault_status_counts.index, autopct='%1.1f%%', startangle=90, colors=['red', 'yellow', 'green'])
        plt.title('Fault Status for Electricity Grids with No Government Regulation')

        plot_filepath = r'D:\Documents\Prof_Docs\DMA\ProjectFiles\static\plot16.png'
        plt.savefig(plot_filepath)

        plt.show()

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query16_result.html', results=results16, columns=columns16, query=query16, df=df16, plot_filepath=plot_filepath)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/query17_results')
@login_required
def query17_results():
    try:
        # Create a new connection and cursor
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        # Replace the following query with your custom query
        query17 = """SELECT CustomerID, CustomerName
                FROM customer
                WHERE CustomerID IN (SELECT CustomerID FROM residential)
                UNION
                SELECT CustomerID, CustomerName
                FROM customer
                WHERE CustomerID IN (SELECT CustomerID FROM business)
                LIMIT 5;
                """
        
        # Execute the custom query
        cursor.execute(query17)

        # Fetch all results and column names
        results17 = cursor.fetchall()
        columns17 = [column[0] for column in cursor.description]

        # Assuming you have a template named 'custom_query_result.html'
        return render_template('query17_result.html', results=results17, columns=columns17)

    except Error as e:
        flash(f"Error executing custom query: {e}", 'error')
        return redirect(url_for('index'))

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

# Close MySQL connection on application shutdown
@app.teardown_appcontext
def close_connection(exception=None):
    global connection, cursor

    if 'connection' in globals() and connection:
        try:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection closed.")
        except AttributeError:
            pass

    cursor = None
    connection = None

if __name__ == '__main__':
    app.run(debug=True)
