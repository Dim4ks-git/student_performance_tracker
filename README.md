# Student Performance Tracker

The Student Performance Tracker is a JavaFX desktop application designed to help students understand their academic performance and identify practical ways to improve. It collects student-reported data, analyses performance trends, and provides personalised suggestions to support academic growth.

## Project Stack
- Bitbucket for source control and repository hosting
- JavaFX for the desktop graphical user interface
- CI/CD pipeline for automated build, testing, and deployment workflows

## Installation Specifications

### Prerequisites
- Java JDK 17 or newer
- Maven build tool
- JavaFX SDK compatible with the installed JDK
- An IDE such as IntelliJ IDEA or Eclipse
- Git installed and configured on your machine

### Clone the Repository
```bash
git clone https://bitbucket.org/<your-username>/student_performance_tracker.git
cd student_performance_tracker
```

### Configure JavaFX
Ensure the JavaFX libraries are added to your Maven project configuration in the `pom.xml` file so the application can compile and run correctly.

### Build the Project
```bash
mvn clean install
```

### Run the Application
```bash
mvn javafx:run
```

## CI/CD
This project is intended to be integrated with a Bitbucket-based CI/CD workflow to automate:
- dependency installation
- project builds
- automated testing
- code quality checks
- deployment or packaging for release builds

## Features
- Track academic performance indicators
- Analyse trends over time
- Receive personalised improvement recommendations
- Use a desktop interface built with JavaFX
