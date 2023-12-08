-- Create Contracts table
CREATE TABLE Contracts (
    ContractID INT AUTO_INCREMENT PRIMARY KEY,
    ContractName VARCHAR(255) DEFAULT 0,
    TypeOfContract VARCHAR(255) DEFAULT 0,
    Description TEXT
);

-- Create Customer table
CREATE TABLE Customer (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    AccountNo INT DEFAULT 0,
    CustomerName VARCHAR(255) DEFAULT 0,
    PhoneNo VARCHAR(20) DEFAULT 0,
    EmailID VARCHAR(255) DEFAULT 0,
    Address TEXT,
    UNIQUE(AccountNo)
);

-- Create UtilityCompanies table
CREATE TABLE UtilityCompanies (
    UCID INT AUTO_INCREMENT PRIMARY KEY,
    AccountNo INT DEFAULT 0,
    CustomerID INT DEFAULT 0,
    CompanyName VARCHAR(255) DEFAULT 0,
    Description TEXT,
    PhoneNo VARCHAR(20) DEFAULT 0,
    Address TEXT,
    Cost DECIMAL(10, 2) DEFAULT 0,
    UNIQUE(AccountNo),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE
);

-- Create RMSupplier table
CREATE TABLE RMSupplier (
    SupplierID INT AUTO_INCREMENT PRIMARY KEY,
    ContractID INT DEFAULT 0,
    Name VARCHAR(255) DEFAULT 0,
    Address TEXT,
    FOREIGN KEY (ContractID) REFERENCES Contracts(ContractID) ON DELETE CASCADE
);

-- Create MainEnergyGrid table
CREATE TABLE MainEnergyGrid (
    GridID INT AUTO_INCREMENT PRIMARY KEY,
    ContractID INT DEFAULT 0,
    UCID INT DEFAULT 0,
    TypeOfEnergy VARCHAR(255) DEFAULT 0,
    FOREIGN KEY (ContractID) REFERENCES Contracts(ContractID) ON DELETE CASCADE,
    FOREIGN KEY (UCID) REFERENCES UtilityCompanies(UCID) ON DELETE CASCADE
);

-- Create ElectricityGrid table
CREATE TABLE ElectricityGrid (
    GridID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    VoltageLevel INT NULL,
    PowerCapacity INT NULL,
    LoadQuantity INT NULL,
    FaultStatus VARCHAR(255) NULL,
    FOREIGN KEY (GridID) REFERENCES MainEnergyGrid(GridID) ON DELETE CASCADE
);

-- Create WaterGrid table
CREATE TABLE WaterGrid (
    GridID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    PressureLevel INT DEFAULT 0,
    FlowCapacity INT DEFAULT 0,
    WaterQuality VARCHAR(255) DEFAULT 0,
    InfrastructureStatus VARCHAR(255) DEFAULT 0,
    FOREIGN KEY (GridID) REFERENCES MainEnergyGrid(GridID) ON DELETE CASCADE
);

-- Create GasGrid table
CREATE TABLE GasGrid (
    GridID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    PressureLevel INT DEFAULT 0,
    FlowCapacity INT DEFAULT 0,
    GasComp VARCHAR(255) DEFAULT 0,
    LeakStatus VARCHAR(255) DEFAULT 0,
    FOREIGN KEY (GridID) REFERENCES MainEnergyGrid(GridID) ON DELETE CASCADE
);

-- Create Government table
CREATE TABLE Government (
    ContractID INT,
    GridID INT,
    UCID INT,
    CustomerID INT,
    PRIMARY KEY (ContractID, UCID, GridID, CustomerID),
    FOREIGN KEY (ContractID) REFERENCES Contracts(ContractID) ON DELETE CASCADE,
    FOREIGN KEY (UCID) REFERENCES UtilityCompanies(UCID) ON DELETE CASCADE,
    FOREIGN KEY (GridID) REFERENCES MainEnergyGrid(GridID) ON DELETE CASCADE,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE
);

-- Create Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
	password_hash VARCHAR(255) NOT NULL
);

-- Create Business table
CREATE TABLE Business (
	CustomerID int default 0,
    TypeOfBusiness varchar (255),
	NumberOfPeople Int default 1,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE
);

-- Create Residential table
CREATE TABLE Residential (
	CustomerID int default 0,
    NumberOfPeople Int default 1,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE
);

-- Reference to delete data
select * from gasgrid;
SELECT LEFT(CustomerID, 10) FROM customer LIMIT 5;
DELETE FROM customer
LIMIT 10000;
DELETE FROM contracts
LIMIT 10000;
DELETE FROM utilitycompanies
ORDER BY UCID
LIMIT 10000;
DELETE FROM business
LIMIT 10000;
DELETE FROM residential
LIMIT 10000;
DELETE FROM gasgrid
LIMIT 10000;
DELETE FROM government
LIMIT 10000;
DELETE FROM mainenergygrid
LIMIT 10000;
DELETE FROM rmsupplier
LIMIT 10000;
DELETE FROM electricitygrid
LIMIT 10000;
DELETE FROM watergrid
LIMIT 10000;
DELETE FROM utilitycompanies
LIMIT 10000;

-- To retrieve all available data
select * from customer;
select * from contracts;
select * from utilitycompanies;
select * from electricitygrid;
select * from gasgrid;
select * from government;
select * from mainenergygrid;
select * from rmsupplier;
select * from watergrid;
select * from users;
select * from residential;
select * from business;

-- To retrieve all data related to customers within the pincode '37625' (Simple Query)
SELECT * from customer
WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(customer.Address, ' ', -1), ' ', 1) = '37625';

-- To retrieve details on the supplier, their address, the contract between the supplier and the main energy grid, while mentioning the type of energy in the grid.
SELECT rms.SupplierID, rms.Name AS SupplierName, rms.Address AS SupplierAddress, con.ContractName, meg.GridID, meg.TypeOfEnergy
FROM rmsupplier rms
JOIN mainenergygrid meg ON rms.ContractID = meg.ContractID
JOIN contracts con ON meg.ContractID = con.ContractID;

-- To retrieve a list of grids along with their details, that are utilising the energy type 'wind' to source their energy (Using Inner Join)
SELECT meg.GridID, meg.TypeOfEnergy, eg.VoltageLevel AS ElectricityVoltageLevel, eg.PowerCapacity AS ElectricityPowerCapacity, eg.LoadQuantity AS ElectricityLoadQuantity, eg.FaultStatus AS ElectricityFaultStatus, gg.PressureLevel AS GasPressureLevel, gg.FlowCapacity AS GasFlowCapacity, gg.GasComp AS GasComposition, gg.LeakStatus AS GasLeakStatus, gg.InfrastructureStatus AS GasInfrastructureStatus, wg.PressureLevel AS WaterPressureLevel, wg.FlowCapacity AS WaterFlowCapacity, wg.WaterQuality AS WaterQuality, wg.InfrastructureStatus AS WaterInfrastructureStatus
FROM mainenergygrid meg
INNER JOIN contracts con ON meg.ContractID = con.ContractID
INNER JOIN electricitygrid eg ON meg.GridID = eg.GridID
INNER JOIN gasgrid gg ON meg.GridID = gg.GridID
INNER JOIN watergrid wg ON meg.GridID = wg.GridID
WHERE meg.TypeOfEnergy = 'Wind';

-- Retrieve each type of contract, count for each type.
SELECT c.TypeOfContract, COUNT(*) AS TotalCount
FROM contracts c
LEFT JOIN mainenergygrid meg ON c.ContractID = meg.ContractID
LEFT JOIN rmsupplier rs ON c.ContractID = rs.ContractID
GROUP BY c.TypeOfContract
ORDER BY c.TypeOfContract;

-- Retrieve top 5 utility company names, and their total billing cost
SELECT CompanyName, SUM(Cost) AS TotalCost
FROM utilitycompanies
GROUP BY CompanyName
ORDER BY TotalCost DESC;

-- To check for the number of households that utilize specific type of energies in the area with pincode '37853' (Aggregate)
SELECT meg.TypeOfEnergy, COUNT(*) as EnergyCount
FROM mainenergygrid meg
JOIN contracts con ON meg.ContractID = con.ContractID
JOIN utilitycompanies uc ON meg.UCID = uc.UCID
JOIN customer cu ON uc.CustomerID = cu.CustomerID
WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(cu.Address, ' ', -1), ' ', 1) = '37853'
GROUP BY meg.TypeOfEnergy;

-- Retrieve the extracted Business Type, the count of people, and the sum of cost for the extracted business type for each customer (In this case sports)
SELECT cu.CustomerName, b.TypeOfBusiness, b.NumberOfPeople, uc.Cost
FROM customer cu
JOIN business b ON cu.CustomerID = b.CustomerID
JOIN utilitycompanies uc ON cu.CustomerID = uc.CustomerID
WHERE b.TypeOfBusiness = "Sports";

-- Retrieve each type of business, total number of people for each type of business, and the total cost for each type of business
SELECT b.TypeOfBusiness, SUM(b.NumberOfPeople) AS TotalPeople, SUM(uc.Cost) AS TotalCost
FROM business b
JOIN customer c ON b.CustomerID = c.CustomerID
LEFT JOIN utilitycompanies uc ON c.CustomerID = uc.CustomerID
GROUP BY b.TypeOfBusiness;

-- To retrieve all contracts where the VolageLevel in the Electricity Grid is greater than 50 (Nested Query)
SELECT ContractName
FROM contracts
WHERE ContractID IN ( SELECT ContractID FROM mainenergygrid WHERE GridID IN (SELECT GridID FROM electricitygrid WHERE VoltageLevel > 50));

-- To retrieve all customers who utilise energy as a business (SubQuery)
SELECT CustomerName
FROM customer
WHERE CustomerID IN (SELECT CustomerID FROM business);

-- To find all contracts and the corresponding utility companies where the contract cost is greater than the average cost of all contracts (Subquery in the FROM clause)
SELECT c.GridID, c.TypeOfEnergy, uc.CompanyName, uc.Cost
FROM mainenergygrid c
JOIN utilitycompanies uc ON c.UCID = uc.UCID
JOIN (SELECT AVG(Cost) AS AvgCost FROM utilitycompanies) AS avg_costs ON uc.Cost > avg_costs.AvgCost;

-- To retrieve the companies and their total costs (Correlated Query)
SELECT CompanyName, (SELECT SUM(Cost) FROM utilitycompanies uc WHERE uc.UCID = u.UCID) AS "Total Cost (in thousands)"
FROM utilitycompanies u;

-- To retrieve the customers who are residential, where the number of people is atleast 8 (Using >= ALL)
SELECT r.CustomerID, cu.CustomerName, r.NumberOfPeople
FROM residential r
JOIN customer cu on r.CustomerID = cu.CustomerID 
WHERE NumberOfPeople >= ALL (SELECT NumberOfPeople FROM residential where NumberOfPeople = 8);

-- Find the gas grids with a flow capacity greater than any of the flow capacities of water grids (Using >ANY)
SELECT *
FROM gasgrid g
WHERE FlowCapacity > ANY (SELECT FlowCapacity FROM watergrid w);

-- To retrieve the utility companies where they are connected with the main energy grid (Using Exists)
SELECT *
FROM utilitycompanies uc
WHERE EXISTS (SELECT 1 FROM mainenergygrid me WHERE me.UCID = uc.UCID);

-- Find all electricity grids where no government regulations are associated. (Using Not Exists)
SELECT *
FROM electricitygrid eg
WHERE NOT EXISTS (SELECT 1 FROM government gov WHERE gov.GridID = eg.GridID);

-- Get all distinct customers who are both residential and business (Set Operation (Union))
SELECT CustomerID, CustomerName
FROM customer
WHERE CustomerID IN (SELECT CustomerID FROM residential)
UNION
SELECT CustomerID, CustomerName
FROM customer
WHERE CustomerID IN (SELECT CustomerID FROM business);

select * from users;
-- A trigger to set the LeakStatus as a a specific value under the ' InfrastuctureStatus' column whenever the column LeakStatus is updated with either 'Minor Leak' or 'Major Leak' in the gasgrid table.
DELIMITER //
CREATE TRIGGER update_gas_grid_status
AFTER UPDATE ON gasgrid
FOR EACH ROW
BEGIN
    IF LeakStatus = 'Minor Leak' OR LeakStatus = 'Major Leak' THEN
        UPDATE gasgrid
        SET InfrastructureStatus = 'Needs Repair'
        WHERE GridID = GridID;
    END IF;
END;
//
DELIMITER ;

-- To drop the trigger (Demo only)
DROP TRIGGER IF EXISTS update_gas_grid_status;

-- To check for available triggers
SHOW TRIGGERS;