import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")


def execute_query(query, conn):
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for easier handling of results
    cursor.execute(query)
    result = cursor.fetchall()
    df = pd.DataFrame(result)
    cursor.close()
    return df


def visualize_gas_grid_leak_status(df):
    leak_status_counts = df['LeakStatus'].value_counts()
    plt.bar(leak_status_counts.index, leak_status_counts.values, color=['red', 'green'])
    plt.xlabel('Leak Status')
    plt.ylabel('Count')
    plt.title('Gas Grid Leak Status')
    for i, count in enumerate(leak_status_counts.values):
        plt.text(i, count + 0.1, str(count), ha='center', va='bottom')
    plt.show()


def visualize_electricity_fault_status(df):
    fault_status_counts = df['FaultStatus'].value_counts()
    plt.pie(fault_status_counts, labels=fault_status_counts.index, autopct='%1.1f%%', startangle=90,
            colors=['red', 'yellow', 'green'])
    plt.title('Fault Status for Electricity Grids with No Government Regulation')
    plt.show()


def query_1(conn):
    query = """
    SELECT * FROM customer WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(customer.Address, ' ', -1), ' ', 1) = '37625';
    """
    return execute_query(query, conn)


def query_2(conn):
    query = """
    SELECT rms.SupplierID, rms.Name AS SupplierName, rms.Address AS SupplierAddress, con.ContractName, meg.GridID,
           meg.TypeOfEnergy
    FROM rmsupplier rms
    JOIN mainenergygrid meg ON rms.ContractID = meg.ContractID
    JOIN contracts con ON meg.ContractID = con.ContractID
    Limit 5;
    """
    return execute_query(query, conn)


def query_3(conn):
    query = """
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
    WHERE meg.TypeOfEnergy = 'Wind';
    """
    return execute_query(query, conn)


def query_4(conn, target_pincode='37853'):
    query = f"""
    SELECT meg.TypeOfEnergy, COUNT(*) as EnergyCount
    FROM mainenergygrid meg
    JOIN contracts con ON meg.ContractID = con.ContractID
    JOIN utilitycompanies uc ON meg.UCID = uc.UCID
    JOIN customer cu ON uc.CustomerID = cu.CustomerID
    WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(cu.Address, ' ', -1), ' ', 1) = '{target_pincode}'
    GROUP BY meg.TypeOfEnergy;
    """
    return execute_query(query, conn)


def query_5(conn, extracted_business_type='Sports'):
    query = f"""
    SELECT cu.CustomerName, b.TypeOfBusiness, b.NumberOfPeople, uc.Cost
    FROM customer cu
    JOIN business b ON cu.CustomerID = b.CustomerID
    JOIN utilitycompanies uc ON cu.CustomerID = uc.CustomerID
    WHERE b.TypeOfBusiness = "{extracted_business_type}";
    """
    return execute_query(query, conn)


# Add functions for other queries...

# Main execution
if __name__ == "__main__":
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='DBMS*fall2023',
        database='energy_grid'
    )

    # Example usage of functions
    result_query_1 = query_1(conn)
    print("\nQuery 1 Results:")
    print(result_query_1.head())

    result_query_2 = query_2(conn)
    print("\nQuery 2 Results:")
    print(result_query_2.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    """result_query_3 = query_3(conn)
    print("\nQuery 4 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())

    result_query_3 = query_3(conn)
    print("\nQuery 3 Results:")
    print(result_query_3.head())"""