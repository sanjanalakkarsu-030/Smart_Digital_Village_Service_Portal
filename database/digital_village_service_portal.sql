-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 03, 2026 at 07:30 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `digital_village_service_portal`
--

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

CREATE TABLE `admins` (
  `admin_id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `role` enum('Admin','Sarpanch') DEFAULT 'Admin',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `agriculture_information`
--

CREATE TABLE `agriculture_information` (
  `agri_info_id` int(11) NOT NULL,
  `title` varchar(150) NOT NULL,
  `crop_name` varchar(100) DEFAULT NULL,
  `fertilizer` varchar(100) DEFAULT NULL,
  `weather_update` varchar(200) DEFAULT NULL,
  `description` text NOT NULL,
  `created_by` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('Active','Inactive') DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `agriculture_queries`
--

CREATE TABLE `agriculture_queries` (
  `query_id` int(11) NOT NULL,
  `citizen_id` int(11) NOT NULL,
  `crop_name` varchar(100) NOT NULL,
  `soil_type` varchar(50) DEFAULT NULL,
  `farmer_query` text NOT NULL,
  `admin_reply` text DEFAULT NULL,
  `status` enum('Pending','Answered') DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `announcements`
--

CREATE TABLE `announcements` (
  `announcement_id` int(11) NOT NULL,
  `title` varchar(150) NOT NULL,
  `description` text NOT NULL,
  `event_date` date DEFAULT NULL,
  `posted_by` int(11) NOT NULL,
  `published_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('Published','Draft','Expired') DEFAULT 'Published'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `citizens`
--

CREATE TABLE `citizens` (
  `citizen_id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `mobile_number` varchar(15) NOT NULL,
  `house_number` varchar(20) NOT NULL,
  `ward_number` int(11) NOT NULL,
  `gender` enum('Male','Female','Other') NOT NULL,
  `address` text NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `registration_date` date NOT NULL,
  `account_status` enum('Active','Inactive') DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `complaints`
--

CREATE TABLE `complaints` (
  `complaint_id` int(11) NOT NULL,
  `citizen_id` int(11) NOT NULL,
  `ward_number` int(11) NOT NULL,
  `category` varchar(50) NOT NULL,
  `subject` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `location` varchar(100) NOT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `complaint_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('Pending','In Progress','Resolved') DEFAULT 'Pending',
  `admin_remarks` text DEFAULT NULL,
  `resolved_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `government_schemes`
--

CREATE TABLE `government_schemes` (
  `scheme_id` int(11) NOT NULL,
  `scheme_name` varchar(150) NOT NULL,
  `category` varchar(50) NOT NULL,
  `description` text NOT NULL,
  `eligibility` text NOT NULL,
  `required_documents` text NOT NULL,
  `last_date` date DEFAULT NULL,
  `apply_link` varchar(255) DEFAULT NULL,
  `status` enum('Active','Inactive') DEFAULT 'Active',
  `created_by` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `health_information`
--

CREATE TABLE `health_information` (
  `health_id` int(11) NOT NULL,
  `title` varchar(150) NOT NULL,
  `hospital_name` varchar(150) DEFAULT NULL,
  `doctor_name` varchar(100) DEFAULT NULL,
  `contact_number` varchar(15) DEFAULT NULL,
  `village` varchar(100) DEFAULT NULL,
  `description` text NOT NULL,
  `created_by` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('Active','Inactive') DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`admin_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `agriculture_information`
--
ALTER TABLE `agriculture_information`
  ADD PRIMARY KEY (`agri_info_id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `agriculture_queries`
--
ALTER TABLE `agriculture_queries`
  ADD PRIMARY KEY (`query_id`),
  ADD KEY `citizen_id` (`citizen_id`);

--
-- Indexes for table `announcements`
--
ALTER TABLE `announcements`
  ADD PRIMARY KEY (`announcement_id`),
  ADD KEY `posted_by` (`posted_by`);

--
-- Indexes for table `citizens`
--
ALTER TABLE `citizens`
  ADD PRIMARY KEY (`citizen_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `complaints`
--
ALTER TABLE `complaints`
  ADD PRIMARY KEY (`complaint_id`),
  ADD KEY `citizen_id` (`citizen_id`);

--
-- Indexes for table `government_schemes`
--
ALTER TABLE `government_schemes`
  ADD PRIMARY KEY (`scheme_id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `health_information`
--
ALTER TABLE `health_information`
  ADD PRIMARY KEY (`health_id`),
  ADD KEY `created_by` (`created_by`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admins`
--
ALTER TABLE `admins`
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `agriculture_information`
--
ALTER TABLE `agriculture_information`
  MODIFY `agri_info_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `agriculture_queries`
--
ALTER TABLE `agriculture_queries`
  MODIFY `query_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `announcements`
--
ALTER TABLE `announcements`
  MODIFY `announcement_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `citizens`
--
ALTER TABLE `citizens`
  MODIFY `citizen_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `complaints`
--
ALTER TABLE `complaints`
  MODIFY `complaint_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `government_schemes`
--
ALTER TABLE `government_schemes`
  MODIFY `scheme_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `health_information`
--
ALTER TABLE `health_information`
  MODIFY `health_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `agriculture_information`
--
ALTER TABLE `agriculture_information`
  ADD CONSTRAINT `agriculture_information_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `admins` (`admin_id`);

--
-- Constraints for table `agriculture_queries`
--
ALTER TABLE `agriculture_queries`
  ADD CONSTRAINT `agriculture_queries_ibfk_1` FOREIGN KEY (`citizen_id`) REFERENCES `citizens` (`citizen_id`);

--
-- Constraints for table `announcements`
--
ALTER TABLE `announcements`
  ADD CONSTRAINT `announcements_ibfk_1` FOREIGN KEY (`posted_by`) REFERENCES `admins` (`admin_id`);

--
-- Constraints for table `complaints`
--
ALTER TABLE `complaints`
  ADD CONSTRAINT `complaints_ibfk_1` FOREIGN KEY (`citizen_id`) REFERENCES `citizens` (`citizen_id`);

--
-- Constraints for table `government_schemes`
--
ALTER TABLE `government_schemes`
  ADD CONSTRAINT `government_schemes_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `admins` (`admin_id`);

--
-- Constraints for table `health_information`
--
ALTER TABLE `health_information`
  ADD CONSTRAINT `health_information_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `admins` (`admin_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
