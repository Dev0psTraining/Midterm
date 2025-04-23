# DevOps Pipeline Project (Local Environment)

## Project Overview

This repository contains a complete implementation of a DevOps pipeline in a local environment. The project demonstrates essential DevOps practices including version control, automated testing, continuous integration, continuous deployment, infrastructure as code, and monitoring.

The core of the application is a simple task management system built with Python Flask that allows users to create and view tasks. This application serves as the foundation for implementing a comprehensive DevOps workflow.

## Tools and Technologies

- **Web Application**: Python 3.11, Flask 2.3.3
- **Version Control**: Git, GitHub
- **CI/CD**: GitHub Actions
- **Infrastructure as Code**: Ansible
- **Deployment Strategy**: Blue-Green Deployment
- **Testing**: Pytest, Coverage
- **Monitoring**: Custom health check scripts, web dashboard
- **Environment**: Local machine/VM

## Project Structure

```
taskmanager/
├── app/                        # Flask application
│   ├── __init__.py
│   ├── routes.py
│   ├── templates/
│       ├── base.html
│       ├── index.html
│       └── tasks.html
├── tests/                      # Unit tests
│   ├── __init__.py
│   └── test_routes.py
├── infrastructure/             # IaC components
│   ├── ansible/
│   │   ├── ansible.cfg
│   │   ├── inventory.ini
│   │   ├── deploy.yml
│   │   ├── rollback.yml
│   │   └── roles/...
├── monitoring/                 # Health checks and monitoring
│   ├── health_check.py
│   └── auto_rollback.py
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions workflow
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies
└── run.py                     # Application entry point
```

## Setup and Installation

### Prerequisites

- Python 3.11 or higher
- Git
- Ansible
- GitHub account

### Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/taskmanager.git
   cd taskmanager
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application Locally

1. Start the Flask application:
   ```bash
   python run.py
   ```

2. Access the application at http://localhost:5000

## Running Tests

Execute the unit tests with:

```bash
pytest
```

For a coverage report:

```bash
pytest --cov=app tests/
```

## CI/CD and IaC Explanation

### Continuous Integration

Our CI pipeline is implemented using GitHub Actions and performs the following:

1. Runs on every push to `main` and `dev` branches, as well as on pull requests
2. Sets up Python environment and installs dependencies
3. Runs code linting with flake8
4. Executes unit tests with pytest
5. Prepares a deployment package for successful builds

The CI pipeline ensures code quality and prevents integration issues by verifying that all changes pass tests before they can be merged.

### Infrastructure as Code

Ansible is used for infrastructure configuration and application deployment:

1. **Environment Setup**: Installs necessary dependencies and configures the system
2. **Application Deployment**: Deploys the application using a blue-green strategy
3. **Service Management**: Sets up and manages the application service
4. **Rollback Support**: Provides automated rollback capabilities

All infrastructure configuration is version-controlled, ensuring consistent environments and allowing infrastructure changes to follow the same workflow as application code.

### Continuous Deployment

The deployment process follows a blue-green strategy:

1. Two environments (blue and green) are maintained on the server
2. New deployments go to the inactive environment
3. Once deployment is complete, traffic is switched to the new environment
4. If issues occur, traffic can be instantly rolled back to the previous environment

This approach minimizes downtime and provides a quick rollback mechanism if issues are detected.

## Deployment Workflow

![Deployment Workflow](deployment_workflow.png)

1. Developers push changes to the `dev` branch or feature branches
2. GitHub Actions runs the CI pipeline to test the code
3. After successful tests and code review, changes are merged to `main`
4. The deployment package is created
5. Ansible deploys to the inactive environment (blue or green)
6. Traffic is switched to the new environment via a symlink
7. Health checks verify the deployment
8. If issues are detected, automatic rollback can be triggered

## Deployment to Production

Production deployment is handled via the Ansible playbook:

```bash
cd infrastructure/ansible
sudo ansible-playbook deploy.yml
```

This creates the following structure:
- Production path: `/opt/taskmanager/`
- Blue environment: `/opt/taskmanager/blue/`
- Green environment: `/opt/taskmanager/green/`
- Active symlink: `/opt/taskmanager/current/` (points to either blue or green)

The blue-green deployment strategy allows for zero-downtime deployments and instant rollbacks.

## Monitoring and Health Checks

Two monitoring solutions are provided:

### Basic Health Check

```bash
cd monitoring
python health_check.py
```

This script periodically checks the application's API endpoint and logs the results.

### Advanced Monitoring with Dashboard

```bash
cd monitoring
python auto_rollback.py
```

This provides:
1. A web-based status dashboard at http://localhost:8080
2. Continuous health monitoring
3. Automatic rollback if repeated failures are detected
4. Visual status indication and logs display

## Manual Rollback

If needed, you can manually rollback to the previous deployment:

```bash
cd infrastructure/ansible
sudo ansible-playbook rollback.yml
```

## Optional Bonus Features

This implementation includes all optional bonus features:

1. **Visual Dashboard**: A web-based dashboard for monitoring application status
2. **Automated Rollback**: Automatic rollback when health checks fail repeatedly
3. **Complete Blue-Green Deployment**: Fully automated switching between environments

## Troubleshooting

### Common Issues

1. **Permission problems with Ansible deployment**:
   - Ensure you have sudo permissions
   - Run the playbook with sudo: `sudo ansible-playbook deploy.yml`

2. **Port conflicts**:
   - If port 5000 is already in use, modify the port in `run.py`
   - If port 8080 is used by another application, change it in `auto_rollback.py`

3. **GitHub Actions workflow errors**:
   - Check repository permissions
   - Verify that GitHub Actions is enabled for your repository

4. **Application not starting after deployment**:
   - Check systemd service status: `sudo systemctl status taskmanager`
   - Review logs: `sudo journalctl -u taskmanager`

## Documentation

For the final submission, ensure you have:

1. A working GitHub repository with all required code
2. Successful CI pipeline runs
3. Production deployment 
4. Health check monitoring system
5. A PDF file with relevant screenshots and workflow diagram

---

Project created for DevOps Pipeline Midterm Project, April 2025.