# core/tasks.py
from celery import shared_task
from django.contrib.auth import get_user_model
import time

User = get_user_model()




@shared_task(bind=True) # bind=True gives us access to self.request (the task metadata)
def process_heavy_calculation(self, number1, number2):
    print(f"🧮 Worker received calculations for Task ID: {self.request.id}")
    
    # Simulate a heavy machine-learning or data calculation delay
    time.sleep(30) 
    
    result = int(number1) * int(number2)
    print(f"✅ Calculation complete. Output: {result}")
    
    # Whatever you return here is saved in Redis as the "Result"
    return result


# core/tasks.py
# from celery import shared_task

@shared_task
def send_future_alert_task(user_id, custom_message):
    print("🔔 FUTURE DYNAMIC ALARM TRIGGERED!")
    print(f"👤 Target User ID: {user_id}")
    print(f"💬 Alert Content: {custom_message}")
    return f"Alert delivered to user {user_id} successfully."

@shared_task
def cleanup_expired_data():
    print("⏰ ENTERPRISE CRON JOB EXECUTING VIA CELERY ENGINE...")
    user_count = User.objects.count()
    print(f"📊 SYSTEM STATUS: Total registered users in DB: {user_count}")
    return f"Processed status check for {user_count} users successfully."