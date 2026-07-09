from datetime import datetime, date, time, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from sqlalchemy import asc, desc, func, or_

from app.extensions import db
from app.models import Attendance, Member, MembershipPlan, Payment
from app.currency_utils import get_gym_currency


reports_bp = Blueprint('reports', __name__)


def get_current_gym_id():
    claims = get_jwt()
    return claims.get('gym_id')


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def compute_duration_minutes(check_in_time, check_out_time):
    if not check_in_time or not check_out_time:
        return None
    return max(int((check_out_time - check_in_time).total_seconds() // 60), 0)


def parse_sort(value, allowed_fields, default_field):
    if not value:
        return default_field, 'desc'

    parts = [part.strip() for part in value.split(',') if part.strip()]
    field = parts[0] if parts and parts[0] in allowed_fields else default_field
    direction = parts[1].lower() if len(parts) > 1 and parts[1].lower() in {'asc', 'desc'} else 'desc'
    return field, direction


def paginate_query(query, page, per_page):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination


def serialize_member(member):
    latest_payment = Payment.query.filter_by(gym_id=member.gym_id, member_id=member.id, payment_status='Paid').order_by(desc(Payment.payment_date), desc(Payment.created_at)).first()
    attendance_count = Attendance.query.filter_by(gym_id=member.gym_id, member_id=member.id).count()
    total_paid = db.session.query(func.sum(Payment.payment_amount)).filter(
        Payment.gym_id == member.gym_id,
        Payment.member_id == member.id,
        Payment.payment_status == 'Paid'
    ).scalar() or 0

    if member.membership_end_date:
        remaining_days = (member.membership_end_date - date.today()).days
    else:
        remaining_days = None

    return {
        'id': member.id,
        'member_id': member.member_id,
        'first_name': member.first_name,
        'last_name': member.last_name,
        'full_name': f"{member.first_name} {member.last_name}".strip(),
        'email': member.email,
        'phone': member.phone,
        'membership_plan_name': member.membership_plan_name,
        'membership_start_date': member.membership_start_date.isoformat() if member.membership_start_date else None,
        'membership_end_date': member.membership_end_date.isoformat() if member.membership_end_date else None,
        'status': member.status,
        'attendance_count': attendance_count,
        'total_paid': float(total_paid),
        'last_payment_date': latest_payment.payment_date.isoformat() if latest_payment else None,
        'last_payment_amount': float(latest_payment.payment_amount) if latest_payment else 0,
        'remaining_membership_days': remaining_days,
        'created_at': member.created_at.isoformat() if member.created_at else None,
        'updated_at': member.updated_at.isoformat() if member.updated_at else None,
    }


def serialize_attendance(attendance, member):
    return {
        'id': attendance.id,
        'member_id': attendance.member_id,
        'member_name': f"{member.first_name} {member.last_name}".strip() if member else 'Unknown Member',
        'member_phone': member.phone if member else None,
        'attendance_date': attendance.attendance_date.isoformat() if attendance.attendance_date else None,
        'check_in_time': attendance.check_in_time.isoformat() if attendance.check_in_time else None,
        'check_out_time': attendance.check_out_time.isoformat() if attendance.check_out_time else None,
        'duration_minutes': compute_duration_minutes(attendance.check_in_time, attendance.check_out_time),
        'status': attendance.status,
        'notes': attendance.notes,
        'created_at': attendance.created_at.isoformat() if attendance.created_at else None,
    }


def serialize_payment(payment, member, membership_plan):
    member_name = f"{member.first_name} {member.last_name}".strip() if member else 'Unknown Member'
    return {
        'id': payment.id,
        'member_id': payment.member_id,
        'member_name': member_name,
        'member_phone': member.phone if member else None,
        'membership_plan_id': payment.membership_plan_id,
        'membership_plan_name': membership_plan.plan_name if membership_plan else None,
        'payment_amount': float(payment.payment_amount),
        'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
        'payment_method': payment.payment_method,
        'payment_status': payment.payment_status,
        'transaction_id': payment.transaction_id,
        'notes': payment.notes,
        'created_at': payment.created_at.isoformat() if payment.created_at else None,
    }


def build_member_query(gym_id, search_query):
    query = Member.query.filter(Member.gym_id == gym_id)
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Member.first_name.ilike(search_pattern),
                Member.last_name.ilike(search_pattern),
                Member.email.ilike(search_pattern),
                Member.phone.ilike(search_pattern),
                Member.member_id.ilike(search_pattern),
                Member.membership_plan_name.ilike(search_pattern),
                Member.status.ilike(search_pattern),
            )
        )
    return query


def build_attendance_query(gym_id, search_query, member_id, start_date, end_date):
    query = db.session.query(Attendance, Member).join(Member, Attendance.member_id == Member.id).filter(Attendance.gym_id == gym_id)
    if member_id:
        query = query.filter(Attendance.member_id == member_id)
    if start_date:
        query = query.filter(Attendance.attendance_date >= start_date)
    if end_date:
        query = query.filter(Attendance.attendance_date <= end_date)
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Member.first_name.ilike(search_pattern),
                Member.last_name.ilike(search_pattern),
                Member.phone.ilike(search_pattern),
                Member.member_id.ilike(search_pattern),
                Attendance.status.ilike(search_pattern),
            )
        )
    return query


def build_payment_query(gym_id, search_query, member_id, status_filter, method_filter, start_date, end_date):
    query = db.session.query(Payment, Member, MembershipPlan).join(Member, Payment.member_id == Member.id).outerjoin(MembershipPlan, Payment.membership_plan_id == MembershipPlan.id).filter(Payment.gym_id == gym_id)
    if member_id:
        query = query.filter(Payment.member_id == member_id)
    if status_filter and status_filter != 'All':
        query = query.filter(Payment.payment_status == status_filter)
    if method_filter and method_filter != 'All':
        query = query.filter(Payment.payment_method == method_filter)
    if start_date:
        query = query.filter(Payment.payment_date >= start_date)
    if end_date:
        query = query.filter(Payment.payment_date <= end_date)
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Member.first_name.ilike(search_pattern),
                Member.last_name.ilike(search_pattern),
                Member.phone.ilike(search_pattern),
                Payment.transaction_id.ilike(search_pattern),
                Payment.payment_method.ilike(search_pattern),
                Payment.payment_status.ilike(search_pattern),
                MembershipPlan.plan_name.ilike(search_pattern),
            )
        )
    return query


def build_revenue_summary(gym_id, start_date=None, end_date=None):
    query = db.session.query(func.sum(Payment.payment_amount)).filter(
        Payment.gym_id == gym_id,
        Payment.payment_status == 'Paid'
    )
    if start_date:
        query = query.filter(Payment.payment_date >= start_date)
    if end_date:
        query = query.filter(Payment.payment_date <= end_date)
    return float(query.scalar() or 0)


def monthly_attendance_summary(gym_id, month_date=None):
    base_date = month_date or date.today()
    month_start = date(base_date.year, base_date.month, 1)
    if month_start.month == 12:
        next_month = date(month_start.year + 1, 1, 1)
    else:
        next_month = date(month_start.year, month_start.month + 1, 1)

    records = Attendance.query.filter(
        Attendance.gym_id == gym_id,
        Attendance.attendance_date >= month_start,
        Attendance.attendance_date < next_month,
    ).all()

    by_day = []
    current = month_start
    while current < next_month:
        day_records = [record for record in records if record.attendance_date == current]
        by_day.append({
            'date': current.isoformat(),
            'checkins': len(day_records),
            'checked_out': len([record for record in day_records if record.status == 'Checked Out']),
        })
        current += timedelta(days=1)

    return {
        'month': month_start.strftime('%Y-%m'),
        'daily_breakdown': by_day,
        'total_checkins': len(records),
        'unique_members': len({record.member_id for record in records}),
    }


def revenue_trends(gym_id):
    today = date.today()
    daily = []
    for offset in range(13):
        day = today - timedelta(days=12 - offset)
        amount = db.session.query(func.sum(Payment.payment_amount)).filter(
            Payment.gym_id == gym_id,
            Payment.payment_status == 'Paid',
            Payment.payment_date == day,
        ).scalar() or 0
        daily.append({'date': day.isoformat(), 'revenue': float(amount)})

    monthly = []
    for offset in range(5, -1, -1):
        year = today.year
        month = today.month - offset
        while month <= 0:
            month += 12
            year -= 1
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        amount = db.session.query(func.sum(Payment.payment_amount)).filter(
            Payment.gym_id == gym_id,
            Payment.payment_status == 'Paid',
            Payment.payment_date >= month_start,
            Payment.payment_date <= month_end,
        ).scalar() or 0
        monthly.append({'month': month_start.strftime('%b %Y'), 'revenue': float(amount)})

    yearly = []
    for offset in range(2, -1, -1):
        year = today.year - offset
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        amount = db.session.query(func.sum(Payment.payment_amount)).filter(
            Payment.gym_id == gym_id,
            Payment.payment_status == 'Paid',
            Payment.payment_date >= year_start,
            Payment.payment_date <= year_end,
        ).scalar() or 0
        yearly.append({'year': str(year), 'revenue': float(amount)})

    plan_rows = db.session.query(
        MembershipPlan.plan_name.label('plan_name'),
        func.sum(Payment.payment_amount).label('revenue')
    ).join(
        Payment, Payment.membership_plan_id == MembershipPlan.id
    ).filter(
        Payment.gym_id == gym_id,
        Payment.payment_status == 'Paid'
    ).group_by(MembershipPlan.plan_name).all()

    by_status_rows = db.session.query(
        Payment.payment_status.label('status'),
        func.count(Payment.id).label('count')
    ).filter(Payment.gym_id == gym_id).group_by(Payment.payment_status).all()

    return {
        'daily': daily,
        'monthly': monthly,
        'yearly': yearly,
        'by_plan': [{'plan_name': row.plan_name or 'Unassigned', 'revenue': float(row.revenue or 0)} for row in plan_rows],
        'by_status': [{'status': row.status, 'count': row.count} for row in by_status_rows],
    }


@reports_bp.route('', methods=['GET'])
@jwt_required()
def get_reports():
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400

    search_query = request.args.get('q', '').strip()
    member_id = request.args.get('member_id', type=int)
    report_type = request.args.get('report_type', 'all')
    status_filter = request.args.get('status', 'All')
    method_filter = request.args.get('method', 'All')
    start_date = parse_date(request.args.get('start_date'))
    end_date = parse_date(request.args.get('end_date'))
    page = max(request.args.get('page', default=1, type=int), 1)
    per_page = min(max(request.args.get('per_page', default=10, type=int), 1), 100)
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'desc')
    export_mode = request.args.get('export') == '1'

    if request.args.get('start_date') and not start_date:
        return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    if request.args.get('end_date') and not end_date:
        return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    if start_date and end_date and start_date > end_date:
        return jsonify({'error': 'start_date cannot be after end_date'}), 400

    member_query = build_member_query(gym_id, search_query)
    attendance_query = build_attendance_query(gym_id, search_query, member_id, start_date, end_date)
    payment_query = build_payment_query(gym_id, search_query, member_id, status_filter, method_filter, start_date, end_date)

    member_sort_field, member_sort_direction = parse_sort(sort_by, {'member_id', 'full_name', 'email', 'phone', 'membership_plan_name', 'status', 'created_at'}, 'created_at')
    attendance_sort_field, attendance_sort_direction = parse_sort(sort_by, {'attendance_date', 'member_name', 'status', 'check_in_time', 'created_at'}, 'attendance_date')
    payment_sort_field, payment_sort_direction = parse_sort(sort_by, {'payment_date', 'member_name', 'payment_amount', 'payment_status', 'payment_method', 'transaction_id', 'created_at'}, 'payment_date')

    member_order_column = {
        'member_id': Member.member_id,
        'full_name': Member.first_name,
        'email': Member.email,
        'phone': Member.phone,
        'membership_plan_name': Member.membership_plan_name,
        'status': Member.status,
        'created_at': Member.created_at,
    }.get(member_sort_field, Member.created_at)
    member_query = member_query.order_by(asc(member_order_column) if member_sort_direction == 'asc' else desc(member_order_column), desc(Member.id))

    attendance_order_column = {
        'attendance_date': Attendance.attendance_date,
        'member_name': Member.first_name,
        'status': Attendance.status,
        'check_in_time': Attendance.check_in_time,
        'created_at': Attendance.created_at,
    }.get(attendance_sort_field, Attendance.attendance_date)
    attendance_query = attendance_query.order_by(asc(attendance_order_column) if attendance_sort_direction == 'asc' else desc(attendance_order_column), desc(Attendance.id))

    payment_order_column = {
        'payment_date': Payment.payment_date,
        'member_name': Member.first_name,
        'payment_amount': Payment.payment_amount,
        'payment_status': Payment.payment_status,
        'payment_method': Payment.payment_method,
        'transaction_id': Payment.transaction_id,
        'created_at': Payment.created_at,
    }.get(payment_sort_field, Payment.payment_date)
    payment_query = payment_query.order_by(asc(payment_order_column) if payment_sort_direction == 'asc' else desc(payment_order_column), desc(Payment.id))

    if export_mode:
        member_items = member_query.all()
        attendance_items = attendance_query.all()
        payment_items = payment_query.all()
        member_pagination = attendance_pagination = payment_pagination = type('Pagination', (), {
            'total': len(member_items),
            'pages': 1,
            'has_next': False,
            'has_prev': False,
        })()
    else:
        member_items, member_pagination = paginate_query(member_query, page, per_page)
        attendance_items, attendance_pagination = paginate_query(attendance_query, page, per_page)
        payment_items, payment_pagination = paginate_query(payment_query, page, per_page)

    member_ids = [member.id for member in Member.query.filter(Member.gym_id == gym_id).all()]

    total_revenue = build_revenue_summary(gym_id, start_date=start_date, end_date=end_date)
    revenue = revenue_trends(gym_id)

    active_members = Member.query.filter(Member.gym_id == gym_id, Member.status == 'Active').count()
    inactive_members = Member.query.filter(Member.gym_id == gym_id, Member.status != 'Active').count()

    summary = {
        'total_members': Member.query.filter_by(gym_id=gym_id).count(),
        'total_attendance': Attendance.query.filter_by(gym_id=gym_id).count(),
        'total_payments': Payment.query.filter_by(gym_id=gym_id).count(),
        'total_revenue': total_revenue,
        'active_members': active_members,
        'inactive_members': inactive_members,
    }

    return jsonify({
        'currency': get_gym_currency(gym_id),
        'summary': summary,
        'filters': {
            'q': search_query,
            'member_id': member_id,
            'status': status_filter,
            'method': method_filter,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'page': page,
            'per_page': per_page,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'report_type': report_type,
        },
        'charts': {
            'monthly_revenue': revenue['monthly'],
            'attendance_trend': monthly_attendance_summary(gym_id),
            'payment_status': revenue['by_status'],
            'active_vs_inactive_members': [
                {'label': 'Active', 'value': active_members},
                {'label': 'Inactive', 'value': inactive_members},
            ],
        },
        'member_report': {
            'total': member_pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': member_pagination.pages,
            'has_next': member_pagination.has_next,
            'has_prev': member_pagination.has_prev,
            'members': [serialize_member(member) for member in member_items],
        },
        'attendance_report': {
            'total': attendance_pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': attendance_pagination.pages,
            'has_next': attendance_pagination.has_next,
            'has_prev': attendance_pagination.has_prev,
            'attendance': [serialize_attendance(attendance, member) for attendance, member in attendance_items],
            'monthly_summary': monthly_attendance_summary(gym_id),
        },
        'payment_report': {
            'total': payment_pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': payment_pagination.pages,
            'has_next': payment_pagination.has_next,
            'has_prev': payment_pagination.has_prev,
            'payments': [serialize_payment(payment, member, membership_plan) for payment, member, membership_plan in payment_items],
            'total_amount': float(db.session.query(func.sum(Payment.payment_amount)).filter(Payment.gym_id == gym_id).scalar() or 0),
        },
        'revenue_report': {
            'daily': revenue['daily'],
            'monthly': revenue['monthly'],
            'yearly': revenue['yearly'],
            'by_plan': revenue['by_plan'],
            'summary_cards': {
                'daily_revenue': revenue['daily'][-1]['revenue'] if revenue['daily'] else 0,
                'monthly_revenue': revenue['monthly'][-1]['revenue'] if revenue['monthly'] else 0,
                'yearly_revenue': revenue['yearly'][-1]['revenue'] if revenue['yearly'] else 0,
                'total_revenue': total_revenue,
            },
        },
    }), 200


@reports_bp.route('/members/<int:member_id>', methods=['GET'])
@jwt_required()
def get_member_report(member_id):
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400

    member = Member.query.filter_by(id=member_id, gym_id=gym_id).first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404

    attendance_rows = Attendance.query.filter_by(gym_id=gym_id, member_id=member_id).order_by(desc(Attendance.attendance_date), desc(Attendance.check_in_time)).all()
    payment_rows = Payment.query.filter_by(gym_id=gym_id, member_id=member_id).order_by(desc(Payment.payment_date), desc(Payment.created_at)).all()
    last_paid_payment = Payment.query.filter_by(gym_id=gym_id, member_id=member_id, payment_status='Paid').order_by(desc(Payment.payment_date), desc(Payment.created_at)).first()
    total_paid = db.session.query(func.sum(Payment.payment_amount)).filter(Payment.gym_id == gym_id, Payment.member_id == member_id, Payment.payment_status == 'Paid').scalar() or 0

    attendance_history = [serialize_attendance(attendance, member) for attendance in attendance_rows]
    payment_history = []
    for payment in payment_rows:
        membership_plan = None
        if payment.membership_plan_id:
            membership_plan = MembershipPlan.query.filter_by(id=payment.membership_plan_id, gym_id=gym_id).first()
        payment_history.append(serialize_payment(payment, member, membership_plan))

    return jsonify({
        'currency': get_gym_currency(gym_id),
        'member': serialize_member(member),
        'membership_plan': member.membership_plan_name,
        'join_date': member.membership_start_date.isoformat() if member.membership_start_date else None,
        'expiry_date': member.membership_end_date.isoformat() if member.membership_end_date else None,
        'remaining_membership_days': (member.membership_end_date - date.today()).days if member.membership_end_date else None,
        'attendance_history': attendance_history,
        'payment_history': payment_history,
        'total_attendance': len(attendance_history),
        'total_amount_paid': float(total_paid),
        'last_payment': serialize_payment(
            last_paid_payment,
            member,
            MembershipPlan.query.filter_by(id=last_paid_payment.membership_plan_id, gym_id=gym_id).first() if last_paid_payment and last_paid_payment.membership_plan_id else None
        ) if last_paid_payment else None,
        'status': member.status,
    }), 200