/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AGENDA` (
  `erabIzena` varchar(45) NOT NULL,
  `kontaktu` varchar(45) NOT NULL,
  `gakoPub` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`erabIzena`,`kontaktu`),
  UNIQUE KEY `erabIzena_UNIQUE` (`erabIzena`),
  UNIQUE KEY `kontaktu_UNIQUE` (`kontaktu`),
  CONSTRAINT `fk_AGENDA_ERABILTZAILE` FOREIGN KEY (`erabIzena`) REFERENCES `ERABILTZAILE` (`izena`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BIDALI` (
  `nork` varchar(45) NOT NULL,
  `nori` varchar(45) NOT NULL,
  `mezu` longtext NOT NULL,
  `noiz` datetime NOT NULL,
  `gaia` varchar(45) DEFAULT NULL,
  `norkEzabatu` tinyint DEFAULT '0',
  `noriEzabatu` tinyint DEFAULT '0',
  PRIMARY KEY (`nork`,`nori`,`noiz`),
  KEY `fk_BIDALI_ERABILTZAILEnori_idx` (`nori`),
  CONSTRAINT `fk_BIDALI_ERABILTZAILEnori` FOREIGN KEY (`nori`) REFERENCES `ERABILTZAILE` (`izena`),
  CONSTRAINT `fk_BIDALI_ERABILTZAILEnork` FOREIGN KEY (`nork`) REFERENCES `ERABILTZAILE` (`izena`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CUENTAACTUAL` (
  `userID` varchar(20) NOT NULL,
  `izena` varchar(45) NOT NULL,
  PRIMARY KEY (`userID`),
  KEY `fk_CUENTAACTUAL_ERABILTZAILE_idx` (`izena`),
  CONSTRAINT `fk_CUENTAACTUAL_ERABILTZAILE` FOREIGN KEY (`izena`) REFERENCES `ERABILTZAILE` (`izena`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ERABILTZAILE` (
  `izena` varchar(45) NOT NULL,
  `pasahitzaSHA1` varchar(40) NOT NULL,
  `sortzeData` date DEFAULT NULL,
  `ezabatuta` tinyint DEFAULT '0',
  PRIMARY KEY (`izena`),
  UNIQUE KEY `izena_UNIQUE` (`izena`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SESION` (
  `userID` varchar(20) NOT NULL,
  `izena` varchar(45) NOT NULL,
  PRIMARY KEY (`userID`,`izena`),
  KEY `fk_SESION_ERABILTZAILE_idx` (`izena`),
  CONSTRAINT `fk_SESION_ERABILTZAILE` FOREIGN KEY (`izena`) REFERENCES `ERABILTZAILE` (`izena`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
