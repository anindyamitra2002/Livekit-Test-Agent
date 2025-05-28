# Deployment Guide for StackVoice Telephonic Agent

## Prerequisites
1. Azure Cache for Redis instance
2. Render.com account (for frontend)
3. Azure Container Apps (for backend)
4. Pinecone account and API key

## Frontend Deployment (Render.com)

1. Create a new Web Service in Render.com
2. Connect your GitHub repository
3. Configure the service:
   - Name: `stackvoice-frontend`
   - Environment: `Docker`
   - Branch: `main` (or your preferred branch)
   - Root Directory: `.` (root of the repository)

4. Set Environment Variables in Render.com:
   ```
   REDIS_HOST=your-redis-host.redis.cache.windows.net
   REDIS_PORT=6380
   REDIS_PASSWORD=your-redis-access-key
   REDIS_SSL=True
   PINECONE_API_KEY=your-pinecone-api-key
   ```

5. Deploy the service

## Backend Deployment (Azure Container Apps)

1. Create a new Container App in Azure Portal
2. Configure the container:
   - Name: `stackvoice-backend`
   - Image Source: Your container registry
   - Image: `your-registry/stackvoice-backend:latest`
   - Port: `8080` (or your backend port)

3. Set Environment Variables:
   ```
   REDIS_HOST=your-redis-host.redis.cache.windows.net
   REDIS_PORT=6380
   REDIS_PASSWORD=your-redis-access-key
   REDIS_SSL=True
   ```

4. Configure Networking:
   - Enable ingress
   - Set appropriate security rules

## Azure Cache for Redis Configuration

1. In Azure Portal, go to your Redis Cache instance
2. Under "Settings" > "Access keys", copy:
   - Host name (for REDIS_HOST)
   - Primary access key (for REDIS_PASSWORD)

3. Under "Settings" > "Advanced settings":
   - Enable SSL (required)
   - Note the port (usually 6380)

## Testing the Deployment

1. Test Redis Connection:
   ```python
   import redis
   import os
   
   # Test Redis connection
   redis_client = redis.Redis(
       host=os.getenv('REDIS_HOST'),
       port=int(os.getenv('REDIS_PORT', 6380)),
       password=os.getenv('REDIS_PASSWORD'),
       ssl=True,
       decode_responses=True
   )
   
   # Test connection
   try:
       redis_client.ping()
       print("Successfully connected to Redis")
   except Exception as e:
       print(f"Failed to connect to Redis: {e}")
   ```

2. Test Frontend to Backend Communication:
   - Make a test call from the frontend
   - Verify metadata is stored in Redis
   - Check if backend can retrieve the metadata

## Monitoring

1. Azure Cache for Redis:
   - Monitor in Azure Portal
   - Set up alerts for:
     - Memory usage
     - Connected clients
     - Cache hits/misses

2. Render.com:
   - Monitor logs in dashboard
   - Set up alerts for:
     - Failed deployments
     - High resource usage

3. Azure Container Apps:
   - Monitor in Azure Portal
   - Set up alerts for:
     - Container health
     - Resource usage
     - Failed deployments

## Troubleshooting

1. Redis Connection Issues:
   - Verify SSL settings
   - Check firewall rules
   - Validate credentials
   - Check network connectivity

2. Frontend Issues:
   - Check Render.com logs
   - Verify environment variables
   - Test Redis connection
   - Check Pinecone connection

3. Backend Issues:
   - Check Azure Container Apps logs
   - Verify environment variables
   - Test Redis connection
   - Check LiveKit connection

## Security Considerations

1. Redis Security:
   - Use SSL (enabled by default in Azure Cache)
   - Use strong passwords
   - Restrict access to Redis instance
   - Enable firewall rules

2. Environment Variables:
   - Never commit .env files
   - Use secure storage for secrets
   - Rotate credentials regularly

3. Network Security:
   - Use HTTPS for all connections
   - Implement proper CORS policies
   - Use Azure Private Link if needed 