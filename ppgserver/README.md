# PPG Server Setup

This repository provides the necessary configurations and scripts to run the PPGServer service alongside other services like InfluxDB, Grafana, and Telegraf using Docker Compose. You can start all the services at once or just the ppgserver depending on your environment configuration.


## Prerequisites

Ensure you have the following installed before proceeding:

1. **Docker**: [Download Docker](https://www.docker.com/products/docker-desktop).
2. **Docker Compose**:
   - On Windows and Mac, Docker Compose is included with Docker Desktop.
   - On Linux, you can install it separately using:
   ```bash
   sudo apt-get update
   sudo apt-get install docker-compose
   ```
3. **Python dependencies**: Ensure you have Python 3.x installed. Then, create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```
4. Clone the Repository:
   ```bash
   git clone https://github.com/Apptimia/rt-sensor-mqtt-grafana.git
   cd rt-sensor-mqtt-grafana
   ```
5. Configure the .env file:
   - In the repository folder, open the .env file and set:
   ```bash
   Set INCLUDE_PPGSERVER=true #Set true to include the PPGServer in the setup.
   ```
## Running the Services
1. Stop running containers(if needed):
   ```bash
   docker-compose down
   ```
2. Make the start.sh script executable:
   ```bash
   chmod +x start.sh
   ```
3. Start the services:
   ```bash
   ./start.sh
   ```
   - This will start the services based on the configurations, including the PPGServer.
4. Stop the services: If you want to stop all running services:
   ```bash
   docker-compose down
   ```