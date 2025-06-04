# Setup & Deployment Guide - SlideCraft AI

This guide provides detailed instructions for setting up and deploying the SlideCraft AI platform.

## 🔧 Local Development Setup

### Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **MySQL 5.7+** or **MySQL 8.0+**
- **AWS Account** with S3 access
- **Google Cloud Account** with Gemini AI API access
- **Git** for version control

### Step 1: Environment Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd AIPlannerExecutor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv slidecraft-env
   source slidecraft-env/bin/activate  # On Windows: slidecraft-env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Database Configuration

1. **Create MySQL Database**
   ```sql
   CREATE DATABASE getaligned;
   USE getaligned;
   
   CREATE TABLE slide_requests (
       id VARCHAR(255) PRIMARY KEY,
       user_id VARCHAR(255),
       mindmap_json LONGTEXT,
       slide_json LONGTEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   );
   ```

2. **Update Database Configuration**
   
   Edit `configs.ini`:
   ```ini
   [MySQLConfig]
   DB_HOST=localhost
   DB_USERNAME=your_username
   DB_PASSWORD=your_password
   DB_NAME=getaligned
   ```

### Step 3: API Keys Configuration

1. **Google Gemini AI API**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Update in `configs.ini`:
   ```ini
   [AIConfig]
   OPENAI_API_KEY=your_gemini_api_key
   ```

2. **AWS S3 Configuration**
   
   Update the AWS credentials in `slide2.py` and `slide_service.py`:
   ```python
   # Replace with your AWS credentials
   ACCESS_KEY = "your_aws_access_key"
   SECRET_KEY = "your_aws_secret_key"
   BUCKET_NAME = "your_s3_bucket_name"
   REGION = "your_aws_region"  # e.g., "us-east-1"
   ```

   Create an S3 bucket:
   ```bash
   aws s3 mb s3://your-bucket-name --region your-region
   ```

### Step 4: Environment Variables

Create a `.env` file in the project root:
```env
# Database Configuration
DB_HOST=localhost
DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password
DB_NAME=getaligned

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=your_aws_region
S3_BUCKET_NAME=your_bucket_name

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Step 5: Run the Application

1. **Start the main application**
   ```bash
   python slide2.py
   ```
   Server will run on `http://localhost:8086`

2. **Start the image service** (optional, if running separately)
   ```bash
   python slide_service.py
   ```

3. **Test the setup**
   ```bash
   curl http://localhost:8086/
   ```

## 🐳 Docker Deployment

### Dockerfile
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8086

# Set environment variables
ENV FLASK_APP=slide2.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "slide2.py"]
```

### Docker Compose
Create a `docker-compose.yml`:
```yaml
version: '3.8'

services:
  slidecraft-app:
    build: .
    ports:
      - "8086:8086"
    environment:
      - DB_HOST=mysql
      - DB_USERNAME=slidecraft
      - DB_PASSWORD=secure_password
      - DB_NAME=slidecraft_db
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      - mysql
    volumes:
      - ./configs.ini:/app/configs.ini

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=slidecraft_db
      - MYSQL_USER=slidecraft
      - MYSQL_PASSWORD=secure_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  mysql_data:
```

### Build and Run
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f slidecraft-app

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### AWS Deployment

1. **EC2 Instance Setup**
   ```bash
   # Launch EC2 instance (Ubuntu 20.04 LTS)
   # Connect via SSH
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3 python3-pip python3-venv nginx -y
   
   # Clone repository
   git clone <your-repo-url>
   cd AIPlannerExecutor
   
   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Nginx Configuration**
   Create `/etc/nginx/sites-available/slidecraft`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       location / {
           proxy_pass http://127.0.0.1:8086;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   # Enable site
   sudo ln -s /etc/nginx/sites-available/slidecraft /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. **Systemd Service**
   Create `/etc/systemd/system/slidecraft.service`:
   ```ini
   [Unit]
   Description=SlideCraft AI Application
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/AIPlannerExecutor
   Environment=PATH=/home/ubuntu/AIPlannerExecutor/venv/bin
   ExecStart=/home/ubuntu/AIPlannerExecutor/venv/bin/python slide2.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Enable and start service
   sudo systemctl daemon-reload
   sudo systemctl enable slidecraft
   sudo systemctl start slidecraft
   sudo systemctl status slidecraft
   ```

### Google Cloud Platform

1. **App Engine Deployment**
   
   Create `app.yaml`:
   ```yaml
   runtime: python39
   
   env_variables:
     DB_HOST: "your-cloud-sql-ip"
     DB_USERNAME: "your-db-user"
     DB_PASSWORD: "your-db-password"
     DB_NAME: "slidecraft_db"
     GEMINI_API_KEY: "your-gemini-key"
   
   automatic_scaling:
     min_instances: 1
     max_instances: 10
   ```

   ```bash
   # Deploy to App Engine
   gcloud app deploy
   ```

2. **Cloud SQL Setup**
   ```bash
   # Create Cloud SQL instance
   gcloud sql instances create slidecraft-db \
     --database-version=MYSQL_8_0 \
     --tier=db-f1-micro \
     --region=us-central1
   
   # Create database
   gcloud sql databases create slidecraft_db --instance=slidecraft-db
   ```

## 🔒 Security Configuration

### Production Security Checklist

1. **Environment Variables**
   - Never commit API keys to version control
   - Use environment-specific configuration files
   - Implement secret management (AWS Secrets Manager, etc.)

2. **Database Security**
   - Use strong passwords
   - Enable SSL connections
   - Restrict database access by IP
   - Regular backups

3. **API Security**
   - Implement authentication (JWT, OAuth)
   - Add rate limiting
   - Input validation and sanitization
   - CORS configuration for specific domains

4. **AWS S3 Security**
   - Use IAM roles instead of access keys
   - Enable bucket encryption
   - Implement bucket policies
   - Regular access audits

### Example Security Enhancements

```python
# Add to slide2.py for basic authentication
from flask_httpauth import HTTPTokenAuth
from werkzeug.security import check_password_hash

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    # Implement your token verification logic
    return validate_api_token(token)

@app.route('/api/v1/slides/generate')
@auth.login_required
def generate_slides():
    # Protected endpoint
    pass
```

## 📊 Monitoring & Logging

### Application Logging
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
if not app.debug:
    file_handler = RotatingFileHandler('logs/slidecraft.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
```

## 🚀 Performance Optimization

### Caching Strategy
1. **Redis Integration** for slide caching
2. **Database Connection Pooling**
3. **CDN** for static assets
4. **Image Optimization** before S3 upload

### Scaling Considerations
1. **Load Balancing** with multiple instances
2. **Database Read Replicas**
3. **Asynchronous Processing** with Celery/RQ
4. **Microservices Architecture** for different components

## 🔄 Maintenance

### Regular Tasks
1. **Database Backups**
   ```bash
   # Daily backup script
   mysqldump -u username -p slidecraft_db > backup_$(date +%Y%m%d).sql
   ```

2. **Log Rotation**
3. **Security Updates**
4. **Performance Monitoring**
5. **API Usage Analytics**

### Troubleshooting Common Issues

1. **Database Connection Issues**
   - Check credentials and network connectivity
   - Verify MySQL service status
   - Review firewall settings

2. **AI API Errors**
   - Verify API key validity
   - Check rate limits
   - Monitor API quotas

3. **Image Generation Failures**
   - Check S3 permissions
   - Verify AWS credentials
   - Monitor storage quotas

This completes the setup and deployment guide for SlideCraft AI. Follow these instructions carefully for a successful deployment.
