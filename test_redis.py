import redis
import os
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

def test_redis_connection():
    """Test Redis connection and basic operations"""
    try:
        # Initialize Redis client
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=6380,
            password=os.getenv('REDIS_PASSWORD'),
            ssl=os.getenv('REDIS_SSL', 'True').lower() == 'true',
            decode_responses=True
        )
        
        # Test 1: Basic Connection
        print("Test 1: Testing basic connection...")
        redis_client.ping()
        print("✅ Successfully connected to Redis")
        
        # Test 2: Write and Read
        print("\nTest 2: Testing write and read operations...")
        test_data = {
            "test_id": f"test-{int(time.time())}",
            "phone": "+911234567890",
            "timestamp": time.time()
        }
        
        # Write data
        redis_client.setex(
            test_data["test_id"],
            300,  # 5 minutes expiration
            json.dumps(test_data)
        )
        print("✅ Successfully wrote test data")
        
        # Read data
        stored_data = redis_client.get(test_data["test_id"])
        if stored_data:
            retrieved_data = json.loads(stored_data)
            if retrieved_data == test_data:
                print("✅ Successfully read and verified test data")
            else:
                print("❌ Data verification failed")
        else:
            print("❌ Failed to read test data")
        
        # Test 3: Cleanup
        print("\nTest 3: Testing cleanup...")
        redis_client.delete(test_data["test_id"])
        if not redis_client.get(test_data["test_id"]):
            print("✅ Successfully cleaned up test data")
        else:
            print("❌ Failed to clean up test data")
            
    except redis.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
    except redis.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    print("Starting Redis connection tests...\n")
    test_redis_connection()
    print("\nTests completed!") 