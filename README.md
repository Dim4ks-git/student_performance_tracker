# Student Performance Tracker

The Student Performance Tracker is a JavaFX desktop application designed to help students understand their academic performance and identify practical ways to improve. It collects student-reported data, analyses performance trends, and provides personalised suggestions to support academic growth.

## Project Stack
- Bitbucket for source control and repository hosting
- JavaFX for the desktop graphical user interface
- CI/CD pipeline for automated build, testing, and deployment workflows

## Project Structure
To view the project structure from the project root, run:

```bash
tree -L 10
```

Example structure:

```text
student_performance_tracker/
├── LICENSE
├── README.md
├── pom.xml
├── src/
│   └── main/
│       ├── java/
│       │   └── ie/
│       │       └── mtu/
│       │           └── studenttracker/
│       │               ├── App.java
│       │               ├── PrimaryController.java
│       │               └── SecondaryController.java
│       └── resources/
├── target/
└── .git/
```

## Prerequisites
- Java JDK 11 or newer
- Maven installed and added to your system PATH
- JavaFX dependencies configured in the Maven project
- Git installed
- IntelliJ IDEA, Eclipse, or another Java IDE recommended

## Installation

### 1. Clone the repository
```bash
git clone https://bitbucket.org/<your-username>/student_performance_tracker.git
cd student_performance_tracker
```

### 2. Build dependencies
```bash
mvn clean install
```

## Usage
Run all commands from the project root directory.

### Fedora Linux
```bash
cd /path/to/student_performance_tracker
mvn test
mvn clean verify
mvn clean package
```

### macOS
```bash
cd /path/to/student_performance_tracker
mvn test
mvn clean verify
mvn clean package
```

### Windows 11
PowerShell:
```powershell
cd C:\path\to\student_performance_tracker
.\mvnw.cmd test
.\mvnw.cmd clean verify
.\mvnw.cmd clean package
.\mvnw.cmd clean javafx:run
```

Command Prompt:
```cmd
cd C:\path\to\student_performance_tracker
mvn test
mvn clean verify
mvn clean package
```

## Run the Application
```bash
mvn javafx:run
```

## CI/CD
This project is intended to be integrated with a Bitbucket-based CI/CD workflow to automate:
- dependency installation
- Maven builds
- automated testing
- verification checks
- packaging and release workflow

## Features
- Track academic performance indicators
- Analyse trends over time
- Receive personalised improvement recommendations
- Use a desktop interface built with JavaFX
