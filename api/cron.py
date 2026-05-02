from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Item

def check_ended_auctions() -> None:
    """Send winner emails for auctions that have ended and were not notified."""
    print("Checking ended auctions")
    now = timezone.now()
    ended_items = Item.objects.filter(end_time__lte=now, email_sent=False)
    print(f"Found {ended_items.count()} ended items")
    for item in ended_items:
        highest = item.bids.order_by("-amount", "created_at").first() if hasattr(item, "bids") else None
        
        if highest and highest.bidder.email:
            print(f"Sending email to {highest.bidder.email}")
            send_mail(
                subject=f"You won the auction for {item.title}",
                message=(
                    f"Congratulations! Your bid of ${highest.amount} won the auction for '{item.title}'. "
                    "Please proceed to complete your purchase."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[highest.bidder.email],
                fail_silently=False,
            )
            print(f"Email sent to {highest.bidder.email}")
            item.email_sent = True
            item.save(update_fields=["email_sent"])
            print(f"Item {item.id} marked as email sent")
        else:
            # Mark as processed even with no bids to avoid re-checking
            item.email_sent = True
            item.save(update_fields=["email_sent"])
