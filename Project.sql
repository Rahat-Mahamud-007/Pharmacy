CREATE DATABASE  IF NOT EXISTS `pharmacy` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `pharmacy`;
-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: pharmacy
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `ATTENDANCEID` int NOT NULL AUTO_INCREMENT,
  `EMPLOYEEID` int DEFAULT NULL,
  `SHIFTID` int DEFAULT NULL,
  `BRANCHID` int DEFAULT NULL,
  `ATTENDANCEDATE` date DEFAULT NULL,
  `TIMEIN` time DEFAULT NULL,
  `TIMEOUT` time DEFAULT NULL,
  PRIMARY KEY (`ATTENDANCEID`),
  KEY `EMPLOYEEID` (`EMPLOYEEID`),
  KEY `SHIFTID` (`SHIFTID`),
  KEY `BRANCHID` (`BRANCHID`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`EMPLOYEEID`) REFERENCES `employees` (`EMPLOYEEID`),
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`BRANCHID`) REFERENCES `branches` (`BRANCHID`),
  CONSTRAINT `attendance_ibfk_3` FOREIGN KEY (`SHIFTID`) REFERENCES `shifts` (`SHIFTID`),
  CONSTRAINT `attendance_ibfk_4` FOREIGN KEY (`BRANCHID`) REFERENCES `branches` (`BRANCHID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,153398,1,1,'2025-08-08','09:00:00','04:00:00'),(2,176519,2,4,'2025-08-08','04:00:00','12:00:00');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `branches`
--

DROP TABLE IF EXISTS `branches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `branches` (
  `BRANCHID` int NOT NULL AUTO_INCREMENT,
  `BRANCHNAME` varchar(100) NOT NULL,
  `LOCATION` varchar(100) NOT NULL,
  `BRANCHMANAGERNUBMBER` varchar(100) NOT NULL,
  PRIMARY KEY (`BRANCHID`),
  UNIQUE KEY `BRANCHNAME` (`BRANCHNAME`),
  UNIQUE KEY `BRANCHMANAGERNUBMBER` (`BRANCHMANAGERNUBMBER`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `branches`
--

LOCK TABLES `branches` WRITE;
/*!40000 ALTER TABLE `branches` DISABLE KEYS */;
INSERT INTO `branches` VALUES (1,'Motijheel','Motijheel, Dhaka','01711000001'),(2,'Chittagong Port','Agrabad, Chattogram','01822000002'),(3,'Rajshahi Sadar','Shaheb Bazar, Rajshahi','01933000003'),(4,'Uttor Badda','Uttor Badda','01933333333');
/*!40000 ALTER TABLE `branches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `CUSTOMERID` int NOT NULL,
  `CUSTOMERNAME` varchar(100) NOT NULL,
  `CONTACT` varchar(100) NOT NULL,
  `EMAIL` varchar(100) DEFAULT NULL,
  `PASSWORD` varchar(100) NOT NULL,
  PRIMARY KEY (`CUSTOMERID`),
  UNIQUE KEY `CUSTOMERID` (`CUSTOMERID`),
  UNIQUE KEY `CUSTOMERNAME` (`CUSTOMERNAME`),
  UNIQUE KEY `CONTACT` (`CONTACT`),
  UNIQUE KEY `PASSWORD` (`PASSWORD`),
  UNIQUE KEY `EMAIL` (`EMAIL`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (191111,'Rahat','01911111111','rahat@gmail.com','rahat'),(191131,'Customer','01911317988','customer@gmail.com','customer'),(199999,'Anis','01999999999','anis@gmail.com','anis');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `EMPLOYEEID` int NOT NULL,
  `EMPLOYEENAME` varchar(100) NOT NULL,
  `EMPLOYEEPIN` varchar(50) NOT NULL,
  `Email` varchar(50) NOT NULL,
  `DESIGNATION` varchar(100) NOT NULL,
  `CONTACT` varchar(100) NOT NULL,
  `BRANCHID` int NOT NULL,
  PRIMARY KEY (`EMPLOYEEID`),
  UNIQUE KEY `EMPLOYEEID` (`EMPLOYEEID`),
  UNIQUE KEY `EMPLOYEENAME` (`EMPLOYEENAME`),
  UNIQUE KEY `EMPLOYEEPIN` (`EMPLOYEEPIN`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `CONTACT` (`CONTACT`),
  KEY `BRANCHID` (`BRANCHID`),
  CONSTRAINT `employees_ibfk_1` FOREIGN KEY (`BRANCHID`) REFERENCES `branches` (`BRANCHID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (131111,'Sefat','0131111','sefat@gmail.com','Staff','01311111111',1),(153398,'F.M. Rahat Mahamud Refat ','0153398','admin@gmail.com','Admin','01533988366',1),(176519,'Employee','employee','176519@curepoint.com','Staff','01765195604',1);
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicinecategory`
--

DROP TABLE IF EXISTS `medicinecategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicinecategory` (
  `CATEGORYID` int NOT NULL AUTO_INCREMENT,
  `CATEGORYNAME` varchar(100) NOT NULL,
  `CATAGORYDETAILS` varchar(5000) DEFAULT NULL,
  PRIMARY KEY (`CATEGORYID`),
  UNIQUE KEY `CATEGORYNAME` (`CATEGORYNAME`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicinecategory`
--

LOCK TABLES `medicinecategory` WRITE;
/*!40000 ALTER TABLE `medicinecategory` DISABLE KEYS */;
INSERT INTO `medicinecategory` VALUES (1,'Metronidazole','Metronidazole is a member of the imidazole class of antibacterial drug and is classified therapeutically as an antiprotozoal agent. The 5-nitro group of Metronidazole is reduced by anaerobes metabolically. Studies have demonstrated that the reduced form of this drug interacts with DNA and gives bactericidal action of Metronidazole.'),(2,'Analgesics (painkillers)','Paracetamol is indicated for fever, common cold and influenza, headache, toothache, earache, bodyache, myalgia, neuralgia, dysmenorrhoea, sprains, colic pain, back pain, post-operative pain, postpartum pain, inflammatory pain and post vaccination pain in children. It is also indicated for rheumatic & osteoarthritic pain and stiffness of joints.'),(3,'Omeprazole','Seclo is indicated for the treatment of-\r\nGastric and duodenal ulcer. \r\nNSAID-associated duodenal and gastric ulcer. \r\nAs prophylaxis in patients with a history of NSAID-associated duodenal and gastric ulcer. \r\nGastro-esophageal reflux disease. \r\nLong-term management of acid reflux disease. \r\nAcid-related dyspepsia. \r\nSevere ulcerating reflux esophagitis. \r\nProphylaxis of acid aspiration during general anesthesia. \r\nZollinger-Ellison syndrome. \r\nHelicobacter pylori-induced peptic ulcer.');
/*!40000 ALTER TABLE `medicinecategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicines`
--

DROP TABLE IF EXISTS `medicines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicines` (
  `MEDICINEID` int NOT NULL AUTO_INCREMENT,
  `MEDICINENAME` varchar(100) NOT NULL,
  `CATEGORYID` int DEFAULT NULL,
  `MANUFACTURER` varchar(100) NOT NULL,
  `PRICE` decimal(10,2) NOT NULL,
  PRIMARY KEY (`MEDICINEID`),
  UNIQUE KEY `MEDICINENAME` (`MEDICINENAME`),
  KEY `CATEGORYID` (`CATEGORYID`),
  CONSTRAINT `medicines_ibfk_1` FOREIGN KEY (`CATEGORYID`) REFERENCES `medicinecategory` (`CATEGORYID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicines`
--

LOCK TABLES `medicines` WRITE;
/*!40000 ALTER TABLE `medicines` DISABLE KEYS */;
INSERT INTO `medicines` VALUES (1,'Napa (Paracetamol 500mg)',2,'Beximco Pharma ',1.20),(2,'Metryl 400 mg',1,'Opsonin Pharma Ltd. ',1.70),(3,'Seclo Capsule (Enteric Coated) 20mg',3,'Square Pharmaceuticals PLC',6.00),(4,'Seclo Capsule (Enteric Coated) 40mg',3,'Square Pharmaceuticals PLC',9.00);
/*!40000 ALTER TABLE `medicines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicinestock`
--

DROP TABLE IF EXISTS `medicinestock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicinestock` (
  `STOCKID` int NOT NULL,
  `BRANCHID` int DEFAULT NULL,
  `MEDICINEID` int DEFAULT NULL,
  `QUANTITY` int NOT NULL,
  `EXPIRYDATE` date NOT NULL,
  PRIMARY KEY (`STOCKID`),
  KEY `BRANCHID` (`BRANCHID`),
  KEY `MEDICINEID` (`MEDICINEID`),
  CONSTRAINT `medicinestock_ibfk_1` FOREIGN KEY (`BRANCHID`) REFERENCES `branches` (`BRANCHID`),
  CONSTRAINT `medicinestock_ibfk_2` FOREIGN KEY (`MEDICINEID`) REFERENCES `medicines` (`MEDICINEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicinestock`
--

LOCK TABLES `medicinestock` WRITE;
/*!40000 ALTER TABLE `medicinestock` DISABLE KEYS */;
INSERT INTO `medicinestock` VALUES (1,1,1,100,'2025-08-08');
/*!40000 ALTER TABLE `medicinestock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `onlineorders`
--

DROP TABLE IF EXISTS `onlineorders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `onlineorders` (
  `ORDERID` int NOT NULL AUTO_INCREMENT,
  `CUSTOMERID` int NOT NULL,
  `SALEDETAILID` int NOT NULL,
  `ORDERDATE` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `DELIVERYADDRESS` varchar(255) NOT NULL,
  PRIMARY KEY (`ORDERID`),
  KEY `CUSTOMERID` (`CUSTOMERID`),
  KEY `SALEDETAILID` (`SALEDETAILID`),
  CONSTRAINT `onlineorders_ibfk_1` FOREIGN KEY (`CUSTOMERID`) REFERENCES `customers` (`CUSTOMERID`),
  CONSTRAINT `onlineorders_ibfk_2` FOREIGN KEY (`SALEDETAILID`) REFERENCES `salesdetails` (`SALEDETAILID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `onlineorders`
--

LOCK TABLES `onlineorders` WRITE;
/*!40000 ALTER TABLE `onlineorders` DISABLE KEYS */;
INSERT INTO `onlineorders` VALUES (1,191131,1,'2025-08-08 18:24:36','Uttor Badda'),(2,191131,2,'2025-08-08 18:24:36','Uttor Badda'),(3,191131,3,'2025-08-09 01:13:33','Notunbazar'),(4,191131,4,'2025-08-09 01:15:36','Nadda');
/*!40000 ALTER TABLE `onlineorders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salesdetails`
--

DROP TABLE IF EXISTS `salesdetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salesdetails` (
  `SALEDETAILID` int NOT NULL AUTO_INCREMENT,
  `SALEID` int DEFAULT NULL,
  `SALEDATE` date NOT NULL,
  `BRANCHID` int DEFAULT NULL,
  `CUSTOMERID` int DEFAULT NULL,
  `EMPLOYEEID` int DEFAULT NULL,
  `PRICEPERUNIT` decimal(10,2) NOT NULL,
  `TOTALAMOUNT` decimal(10,2) NOT NULL,
  `PAYMENTMETHOD` varchar(100) DEFAULT NULL,
  `MEDICINEID` int DEFAULT NULL,
  `QUANTITY` int NOT NULL,
  PRIMARY KEY (`SALEDETAILID`),
  KEY `BRANCHID` (`BRANCHID`),
  KEY `CUSTOMERID` (`CUSTOMERID`),
  KEY `EMPLOYEEID` (`EMPLOYEEID`),
  KEY `MEDICINEID` (`MEDICINEID`),
  CONSTRAINT `salesdetails_ibfk_1` FOREIGN KEY (`BRANCHID`) REFERENCES `branches` (`BRANCHID`),
  CONSTRAINT `salesdetails_ibfk_2` FOREIGN KEY (`CUSTOMERID`) REFERENCES `customers` (`CUSTOMERID`),
  CONSTRAINT `salesdetails_ibfk_3` FOREIGN KEY (`EMPLOYEEID`) REFERENCES `employees` (`EMPLOYEEID`),
  CONSTRAINT `salesdetails_ibfk_4` FOREIGN KEY (`MEDICINEID`) REFERENCES `medicines` (`MEDICINEID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salesdetails`
--

LOCK TABLES `salesdetails` WRITE;
/*!40000 ALTER TABLE `salesdetails` DISABLE KEYS */;
INSERT INTO `salesdetails` VALUES (1,NULL,'2025-08-08',1,191131,153398,1.20,12.00,'COD',1,10),(2,NULL,'2025-08-08',1,191131,153398,1.70,17.00,'COD',2,10),(3,NULL,'2025-08-09',1,191131,153398,1.70,25.50,'COD',2,15),(4,NULL,'2025-08-09',1,191131,153398,1.20,24.00,'Bkash',1,20);
/*!40000 ALTER TABLE `salesdetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shifts`
--

DROP TABLE IF EXISTS `shifts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shifts` (
  `SHIFTID` int NOT NULL,
  `SHIFTNAME` varchar(100) DEFAULT NULL,
  `STARTTIME` time DEFAULT NULL,
  `ENDTIME` time DEFAULT NULL,
  `EMPLOYEEID` int DEFAULT NULL,
  PRIMARY KEY (`SHIFTID`),
  KEY `EMPLOYEEID` (`EMPLOYEEID`),
  CONSTRAINT `shifts_ibfk_1` FOREIGN KEY (`EMPLOYEEID`) REFERENCES `employees` (`EMPLOYEEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shifts`
--

LOCK TABLES `shifts` WRITE;
/*!40000 ALTER TABLE `shifts` DISABLE KEYS */;
INSERT INTO `shifts` VALUES (1,'Morning','09:00:00','04:00:00',153398),(2,'Evening','04:00:00','12:00:00',176519);
/*!40000 ALTER TABLE `shifts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `SUPPLIERID` int NOT NULL AUTO_INCREMENT,
  `MEDICINEID` int DEFAULT NULL,
  `SUPPLIERNAME` varchar(100) NOT NULL,
  `CONTACT` varchar(100) NOT NULL,
  PRIMARY KEY (`SUPPLIERID`),
  UNIQUE KEY `CONTACT` (`CONTACT`),
  KEY `MEDICINEID` (`MEDICINEID`),
  CONSTRAINT `suppliers_ibfk_1` FOREIGN KEY (`MEDICINEID`) REFERENCES `medicines` (`MEDICINEID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
INSERT INTO `suppliers` VALUES (1,2,'Anis','01834573928'),(2,1,'Tarikul','01912343212');
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-09 23:25:56
