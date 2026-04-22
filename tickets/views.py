import os
import io
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.utils import timezone
from django.contrib.staticfiles import finders
from django.contrib import messages
from django.contrib.auth.models import User

# Email Imports
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage

# PDF Generation Imports
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# Your Models and Forms
from .models import Ticket, Announcement
from .forms import TicketForm

# -------------------------------------------------------------------------
# 1. MAIN DASHBOARD / HOME VIEW
# -------------------------------------------------------------------------
@login_required(login_url='/login/')
def home(request):
    announcements = Announcement.objects.all().order_by('-created_at')[:5]
    
    open_count = Ticket.objects.filter(created_by=request.user).exclude(status='Resolved').count()
    resolved_count = Ticket.objects.filter(created_by=request.user, status='Resolved').count()
    
    total_pending = Ticket.objects.filter(status='Pending').count()
    total_in_progress = Ticket.objects.filter(status='In Progress').count()
    
    today = timezone.now().date()
    resolved_today = Ticket.objects.filter(status='Resolved', updated_at__date=today).count()
    total_resolved = Ticket.objects.filter(status='Resolved').count()
    
    context = {
        'announcements': announcements,
        'open_count': open_count,
        'resolved_count': resolved_count,
        'total_pending': total_pending,
        'total_in_progress': total_in_progress,
        'resolved_today_count': resolved_today,
        'total_resolved_count': total_resolved,
    }
    return render(request, 'home.html', context)

# -------------------------------------------------------------------------
# 2. TICKET MANAGEMENT (CRUD)
# -------------------------------------------------------------------------
@login_required(login_url='/login/')
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            
            if hasattr(request.user, 'profile'):
                ticket.department = request.user.profile.department
            else:
                ticket.department = "General"
                
            ticket.save()

            # --- UPDATED INSTANT EMAIL NOTIFICATION ---
            try:
                subject = f"New ICT Ticket Alert: #{ticket.id} - {ticket.title}"
                
                # 1. Get all Superuser emails
                superusers = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
                
                # 2. Define the mandatory emails
                manual_emails = ['nwwdaict@gmail.com', 'mosesmutuma709@gmail.com']
                
                # 3. Combine and remove duplicates
                recipient_list = list(set(superusers + manual_emails))
                # Remove any empty strings if a superuser doesn't have an email set
                recipient_list = [email for email in recipient_list if email]

                email_context = {
                    'ticket': ticket,
                    'user': request.user,
                    'site_url': 'https://nwwda-helpdesk.onrender.com',
                }
                
                html_content = render_to_string('emails/new_ticket_notification.html', email_context)
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject, 
                    text_content, 
                    settings.DEFAULT_FROM_EMAIL, 
                    recipient_list
                )
                email.attach_alternative(html_content, "text/html")
                email.content_subtype = 'related' 

                for cid_name, relative_path in [('logo', 'images/logo.jpg'), ('coa', 'images/coa.png')]:
                    img_path = finders.find(relative_path)
                    if img_path and os.path.exists(img_path):
                        with open(img_path, 'rb') as f:
                            img = MIMEImage(f.read())
                            img.add_header('Content-ID', f'<{cid_name}>')
                            img.add_header('Content-Disposition', 'inline', filename=cid_name)
                            email.attach(img)

                email.send()
            except Exception as e:
                # This ensures the user still sees their ticket was created even if Gmail fails
                print(f"CRITICAL: Email failed to send: {e}")

            return redirect('my_tickets')
    else:
        form = TicketForm()
    return render(request, 'create_ticket.html', {'form': form})

@login_required(login_url='/login/')
def my_tickets(request):
    tickets = Ticket.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'my_tickets.html', {'tickets': tickets})

@login_required(login_url='/login/')
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, created_by=request.user)
    if ticket.status != 'Pending':
        messages.warning(request, "This ticket is now being processed by ICT and is locked for edits.")
        return redirect('my_tickets')
    return render(request, 'ticket_detail.html', {'ticket': ticket})

@login_required(login_url='/login/')
def update_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, created_by=request.user)
    if ticket.status != 'Pending':
        messages.error(request, "Cannot update a ticket that is already in progress or resolved.")
        return redirect('my_tickets')

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('my_tickets')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'update_ticket.html', {'form': form, 'ticket': ticket})

@login_required(login_url='/login/')
def delete_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, created_by=request.user)
    if ticket.status != 'Pending':
        messages.error(request, "You cannot delete a ticket that is currently being handled by ICT.")
        return redirect('my_tickets')

    if request.method == 'POST':
        ticket.delete()
        return redirect('my_tickets')
    return render(request, 'confirm_delete.html', {'ticket': ticket})

# -------------------------------------------------------------------------
# 3. OFFICIAL PDF REPORT GENERATION
# -------------------------------------------------------------------------
@login_required(login_url='/login/')
def export_tickets_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=20, bottomMargin=50)
    elements = []
    styles = getSampleStyleSheet()

    logo_path = finders.find('images/logo.jpg')
    coa_path = finders.find('images/logo.jpg')
    
    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=60, height=60) 
        logo.hAlign = 'CENTER'
        elements.append(logo)
    
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], alignment=1, fontSize=16, textColor=colors.HexColor("#1a1a2e"))
    sub_header_style = ParagraphStyle('SubHeader', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold')
    section_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], alignment=0, fontSize=12, textColor=colors.HexColor("#1a1a2e"), spaceAfter=10)
    
    elements.append(Paragraph("NORTHERN WATER WORKS DEVELOPMENT AGENCY", header_style))
    elements.append(Paragraph("DEPARTMENT OF INFORMATION COMMUNICATION TECHNOLOGY", sub_header_style))
    elements.append(Paragraph("FULL TICKET (ISSUES) REPORT", sub_header_style))
    elements.append(Spacer(1, 20))

    # Shared Table Style (Left aligned content)
    ts = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    # 1. Pending Section
    elements.append(Paragraph("PENDING TICKETS", section_style))
    pending_data = [['ID', 'REPORTED BY', 'TICKET TITLE', 'STATUS', 'DATE REPORTED']]
    pending_tickets = Ticket.objects.exclude(status='Resolved').order_by('id')
    
    for t in pending_tickets:
        full_name = t.created_by.get_full_name() or t.created_by.username
        title = (t.title[:35] + '..') if len(t.title) > 35 else t.title
        rep_date = t.created_at.strftime('%Y-%m-%d')
        pending_data.append([t.id, full_name.upper(), title, t.status.upper(), rep_date])

    if len(pending_data) > 1:
        t1 = Table(pending_data, colWidths=[35, 120, 170, 80, 100])
        t1.setStyle(ts)
        elements.append(t1)
    else:
        elements.append(Paragraph("No pending tickets recorded.", styles['Normal']))
    
    elements.append(Spacer(1, 20))

    # 2. Resolved Section
    elements.append(Paragraph("RESOLVED TICKETS", section_style))
    resolved_data = [['ID', 'REPORTED BY', 'TICKET TITLE', 'STATUS', 'DATE RESOLVED']]
    resolved_tickets = Ticket.objects.filter(status='Resolved').order_by('id')

    for t in resolved_tickets:
        full_name = t.created_by.get_full_name() or t.created_by.username
        title = (t.title[:35] + '..') if len(t.title) > 35 else t.title
        res_date = t.updated_at.strftime('%Y-%m-%d')
        resolved_data.append([t.id, full_name.upper(), title, t.status.upper(), res_date])

    if len(resolved_data) > 1:
        t2 = Table(resolved_data, colWidths=[35, 120, 170, 80, 100])
        t2.setStyle(ts)
        elements.append(t2)
    else:
        elements.append(Paragraph("No resolved tickets recorded.", styles['Normal']))

    elements.append(Spacer(1, 40))

    sig_data = [
        ["__________________________", "", "__________________________"],
        ["ICT Officer", "", "ICT Manager"],
        [f"Date: {timezone.now().date()}", "", "Official Agency Stamp"]
    ]
    sig_table = Table(sig_data, colWidths=[200, 100, 200])
    sig_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTSIZE', (0, 0), (-1, -1), 9)]))
    elements.append(sig_table)

    def add_watermark_and_footer(canvas, doc):
        canvas.saveState()
        if coa_path and os.path.exists(coa_path):
            canvas.setFillAlpha(0.08) 
            canvas.drawImage(coa_path, 4*cm, 8*cm, width=13*cm, height=13*cm, mask='auto')
        
        canvas.setFont('Helvetica', 8)
        canvas.setFillAlpha(1.0)
        canvas.drawString(30, 20, "Official ICT Document - NWWDA")
        canvas.drawRightString(550, 20, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_watermark_and_footer, onLaterPages=add_watermark_and_footer)
    buffer.seek(0)
    
    return FileResponse(buffer, content_type='application/pdf')

# -------------------------------------------------------------------------
# 4. AUTHENTICATION
# -------------------------------------------------------------------------
def staff_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out of the NWWDA Secure Gateway.")
    return redirect('login')