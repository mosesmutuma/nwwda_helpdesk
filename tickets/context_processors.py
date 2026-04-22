from .models import Ticket
from django.utils import timezone

def ticket_stats(request):
    today = timezone.now().date()

    # Active Work (Status based)
    pending_count = Ticket.objects.filter(status__icontains='pending').count()
    in_progress_count = Ticket.objects.filter(status__icontains='progress').count()

    # Metric 1: Resolved Today (Resets at midnight)
    resolved_today = Ticket.objects.filter(
        status__icontains='resolved', 
        updated_at__date=today
    ).count()

    # Metric 2: Total Resolved (All-time history)
    total_resolved = Ticket.objects.filter(status__icontains='resolved').count()

    return {
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'resolved_today_count': resolved_today,
        'total_resolved_count': total_resolved,
        # fallback for existing templates
        'resolved_count': resolved_today, 
    }