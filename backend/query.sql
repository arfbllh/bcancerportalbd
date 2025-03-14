CREATE TABLE `dataset` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `name` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
)
CREATE TABLE `cna_gene` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `gene` varchar(255) DEFAULT NULL,
  `cytoband` varchar(255) DEFAULT NULL,
  `CNA` varchar(20) DEFAULT NULL,
  `num` int DEFAULT NULL,
  `freq` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci