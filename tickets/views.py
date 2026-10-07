import csv

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from .forms import TicketForm, TicketUpdateForm
from .models import Ticket


def ticket_list(request):
    tickets = Ticket.objects.all()
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')

    if query:
        tickets = tickets.filter(subject__icontains=query) | tickets.filter(description__icontains=query)
    if category:
        tickets = tickets.filter(category=category)
    if status:
        tickets = tickets.filter(status=status)

    category_names = dict(Ticket.Category.choices)
    category_stats = [
        {'label': category_names[item['category']], 'total': item['total']}
        for item in Ticket.objects.values('category').annotate(total=Count('id')).order_by('-total')
    ]
    context = {
        'tickets': tickets,
        'query': query,
        'selected_category': category,
        'selected_status': status,
        'categories': Ticket.Category.choices,
        'statuses': Ticket.Status.choices,
        'total_count': Ticket.objects.count(),
        'category_stats': category_stats,
    }
    return render(request, 'tickets/ticket_list.html', context)


def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    form = TicketUpdateForm(instance=ticket)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket, 'form': form})


def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = TicketUpdateForm(instance=ticket)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket, 'form': form})


def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_form.html', {'form': form})


def analytics(request):
    category_names = dict(Ticket.Category.choices)
    status_names = dict(Ticket.Status.choices)
    date_from_value = request.GET.get('date_from', '')
    date_to_value = request.GET.get('date_to', '')
    date_from = parse_date(date_from_value) if date_from_value else None
    date_to = parse_date(date_to_value) if date_to_value else None
    period_error = bool(date_from and date_to and date_from > date_to)
    tickets = Ticket.objects.all()
    if date_from:
        tickets = tickets.filter(created_at__date__gte=date_from)
    if date_to:
        tickets = tickets.filter(created_at__date__lte=date_to)
    category_counts = list(
        tickets.values('category').annotate(total=Count('id')).order_by('-total')
    )
    status_counts = list(
        tickets.values('status').annotate(total=Count('id')).order_by('-total')
    )
    max_category = max((item['total'] for item in category_counts), default=0)
    category_stats = [
        {
            'label': category_names[item['category']],
            'total': item['total'],
            'width': round(item['total'] / max_category * 100) if max_category else 0,
        }
        for item in category_counts
    ]
    status_stats = [
        {'label': status_names[item['status']], 'total': item['total']}
        for item in status_counts
    ]
    return render(request, 'tickets/analytics.html', {
        'total_count': tickets.count(),
        'resolved_count': tickets.filter(status=Ticket.Status.RESOLVED).count(),
        'category_stats': category_stats,
        'status_stats': status_stats,
        'top_category': category_stats[0] if category_stats else None,
        'date_from': date_from.isoformat() if date_from else '',
        'date_to': date_to.isoformat() if date_to else '',
        'period_error': period_error,
    })


def export_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="tickets.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Номер', 'Тема', 'Описание', 'Категория', 'Статус', 'Дата создания'])
    date_from_value = request.GET.get('date_from', '')
    date_to_value = request.GET.get('date_to', '')
    date_from = parse_date(date_from_value) if date_from_value else None
    date_to = parse_date(date_to_value) if date_to_value else None
    tickets = Ticket.objects.all()
    if date_from:
        tickets = tickets.filter(created_at__date__gte=date_from)
    if date_to:
        tickets = tickets.filter(created_at__date__lte=date_to)
    for ticket in tickets:
        writer.writerow([
            ticket.pk,
            ticket.subject,
            ticket.description,
            ticket.get_category_display(),
            ticket.get_status_display(),
            ticket.created_at.strftime('%d.%m.%Y %H:%M'),
        ])
    return response


def export_report(request):
    date_from_value = request.GET.get('date_from', '')
    date_to_value = request.GET.get('date_to', '')
    date_from = parse_date(date_from_value) if date_from_value else None
    date_to = parse_date(date_to_value) if date_to_value else None
    tickets = Ticket.objects.all()
    if date_from:
        tickets = tickets.filter(created_at__date__gte=date_from)
    if date_to:
        tickets = tickets.filter(created_at__date__lte=date_to)

    category_names = dict(Ticket.Category.choices)
    status_names = dict(Ticket.Status.choices)
    category_counts = tickets.values('category').annotate(total=Count('id')).order_by('-total')
    status_counts = tickets.values('status').annotate(total=Count('id')).order_by('-total')
    top_category = category_counts.first()
    period = 'все даты'
    if date_from or date_to:
        period = f"{date_from.strftime('%d.%m.%Y') if date_from else 'начало'} — {date_to.strftime('%d.%m.%Y') if date_to else 'сегодня'}"

    lines = [
        'АНАЛИТИЧЕСКИЙ ОТЧЁТ ПО ОБРАЩЕНИЯМ',
        f'Период: {period}',
        f'Всего обращений: {tickets.count()}',
        f'Решено обращений: {tickets.filter(status=Ticket.Status.RESOLVED).count()}',
        f"Самая частая категория: {category_names[top_category['category']]} ({top_category['total']})" if top_category else 'Самая частая категория: нет данных',
        '',
        'Обращения по категориям:',
    ]
    lines.extend(f"- {category_names[item['category']]}: {item['total']}" for item in category_counts)
    lines.extend(['', 'Обращения по статусам:'])
    lines.extend(f"- {status_names[item['status']]}: {item['total']}" for item in status_counts)
    lines.extend(['', 'Отчёт сформирован автоматически приложением «Служба обращений».'])

    response = HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="analytics-report.txt"'
    return response
