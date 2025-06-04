#!/usr/bin/env python3
"""
Test script to verify that environment variables are properly loaded
and the PowerPoint generation platform can access all required configurations.
"""

import os
from dotenv import load_dotenv

def test_environment_configuration():
    """Test that all required environment variables are properly configured."""
    
    print("🔧 Testing PowerPoint Generation Platform Configuration")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Required environment variables
    required_vars = {
        "Database Configuration": [
            "DB_HOST",
            "DB_USER", 
            "DB_PASSWORD",
            "DB_NAME",
            "DB_PORT"
        ],
        "AI API Keys": [
            "OPENAI_API_KEY",
            "GOOGLE_API_KEY", 
            "GEMINI_API_KEY"
        ],
        "AWS S3 Configuration": [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_REGION",
            "AWS_S3_BUCKET_NAME",
            "AWS_S3_BUCKET_MEETINGS",
            "AWS_S3_BASE_URL"
        ]
    }
    
    all_configured = True
    
    for category, variables in required_vars.items():
        print(f"\n📋 {category}:")
        print("-" * 40)
        
        for var in variables:
            value = os.getenv(var)
            if value:
                # Mask sensitive values for security
                if any(sensitive in var.lower() for sensitive in ['key', 'password', 'secret']):
                    display_value = f"{value[:8]}..." if len(value) > 8 else "***"
                else:
                    display_value = value
                print(f"✅ {var}: {display_value}")
            else:
                print(f"❌ {var}: Not configured")
                all_configured = False
    
    print("\n" + "=" * 60)
    if all_configured:
        print("🎉 All environment variables are properly configured!")
        print("✅ PowerPoint generation platform is ready to use")
        return True
    else:
        print("⚠️  Some environment variables are missing")
        print("❌ Please check your .env file configuration")
        return False

def test_database_connection():
    """Test database connection using environment variables."""
    print("\n🗄️  Testing Database Connection")
    print("-" * 40)
    
    try:
        import pymysql
        
        db_config = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
            "port": int(os.getenv("DB_PORT", 3306))
        }
        
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        conn.close()
        
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_aws_s3_connection():
    """Test AWS S3 connection using environment variables."""
    print("\n☁️  Testing AWS S3 Connection")
    print("-" * 40)
    
    try:
        import boto3
        
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        
        # Test connection by listing buckets
        response = s3_client.list_buckets()
        bucket_names = [bucket['Name'] for bucket in response['Buckets']]
        
        expected_bucket = os.getenv("AWS_S3_BUCKET_NAME")
        if expected_bucket in bucket_names:
            print(f"✅ S3 connection successful")
            print(f"✅ Target bucket '{expected_bucket}' found")
        else:
            print(f"⚠️  S3 connection successful but bucket '{expected_bucket}' not found")
            print(f"Available buckets: {bucket_names}")
        
        return True
        
    except Exception as e:
        print(f"❌ AWS S3 connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 SlideCraft AI - PowerPoint Generation Platform")
    print("Environment Configuration Test")
    print("=" * 60)
    
    # Test environment configuration
    env_ok = test_environment_configuration()
    
    if env_ok:
        # Test database connection
        db_ok = test_database_connection()
        
        # Test AWS S3 connection  
        s3_ok = test_aws_s3_connection()
        
        print("\n" + "=" * 60)
        print("📊 Configuration Test Summary:")
        print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
        print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
        print(f"AWS S3 Connection: {'✅ PASS' if s3_ok else '❌ FAIL'}")
        
        if env_ok and db_ok and s3_ok:
            print("\n🚀 PowerPoint generation platform is ready to go!")
            print("You can now start the server with: python slide2.py")
        else:
            print("\n⚠️  Please fix the configuration issues before starting the server")
    
    else:
        print("\n❌ Please configure your .env file properly before proceeding")
