services=("flick-access-service" "flick-streaming-service" "flick-gateway" "flick-recommendation-service" "flick-notification-service" "flick-auth-service" "flick-catalog-service")
for s in "${services[@]}"; do
  echo "Checking $s..."
  curl -m 10 -s "https://$s.onrender.com/health/" || echo "Timeout or error"
  echo ""
done
