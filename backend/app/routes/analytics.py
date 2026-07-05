from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import func, desc, and_
from app.extensions import db
from app.models import Member, MembershipPlan, Payment, Attendance
from datetime import datetime, date, timedelta

analytics_bp = Blueprint('analytics', __name__)

def get_current_gym_id():
    """Extract gym_id from JWT token for multi-tenant isolation"""
    claims = get_jwt()
    return claims.get('gym_id')

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get comprehensive dashboard analytics for the current gym"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    try:
        # Date calculations
        today = date.today()
        current_month_start = date(today.year, today.month, 1)
        last_month = current_month_start - timedelta(days=1)
        last_month_start = date(last_month.year, last_month.month, 1)
        
        # Members Analytics
        total_members = Member.query.filter_by(gym_id=gym_id).count()
        active_members = Member.query.filter_by(gym_id=gym_id, status='Active').count()
        
        # Get recent members (last 30 days)
        recent_members_cutoff = today - timedelta(days=30)
        recent_members_count = Member.query.filter(
            and_(
                Member.gym_id == gym_id,
                Member.created_at >= recent_members_cutoff
            )
        ).count()
        
        # Latest members for recent activity
        latest_members = Member.query.filter_by(gym_id=gym_id)\
            .order_by(desc(Member.created_at))\
            .limit(5).all()
        
        # Membership Plans Analytics
        total_plans = MembershipPlan.query.filter_by(gym_id=gym_id).count()
        active_plans = MembershipPlan.query.filter_by(gym_id=gym_id, status='Active').count()
        
        # Attendance Analytics
        todays_checkins = Attendance.query.filter_by(
            gym_id=gym_id,
            attendance_date=today
        ).count()
        
        currently_inside = Attendance.query.filter_by(
            gym_id=gym_id,
            attendance_date=today,
            status='Checked In'
        ).count()
        
        # Weekly attendance trend (last 7 days)
        weekly_attendance = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = Attendance.query.filter_by(
                gym_id=gym_id,
                attendance_date=day
            ).count()
            weekly_attendance.append({
                'date': day.isoformat(),
                'count': count
            })
        
        # Recent attendance
        recent_attendance = Attendance.query.filter_by(gym_id=gym_id)\
            .join(Member)\
            .order_by(desc(Attendance.check_in_time))\
            .limit(5).all()
        
        # Payments Analytics
        # Current month revenue
        current_month_revenue = db.session.query(func.sum(Payment.payment_amount))\
            .filter(
                and_(
                    Payment.gym_id == gym_id,
                    Payment.payment_date >= current_month_start,
                    Payment.payment_status == 'Paid'
                )
            ).scalar() or 0
        
        # Last month revenue for comparison
        last_month_revenue = db.session.query(func.sum(Payment.payment_amount))\
            .filter(
                and_(
                    Payment.gym_id == gym_id,
                    Payment.payment_date >= last_month_start,
                    Payment.payment_date < current_month_start,
                    Payment.payment_status == 'Paid'
                )
            ).scalar() or 0
        
        # Pending payments
        pending_payments_count = Payment.query.filter_by(
            gym_id=gym_id,
            payment_status='Pending'
        ).count()
        
        pending_payments_amount = db.session.query(func.sum(Payment.payment_amount))\
            .filter(
                and_(
                    Payment.gym_id == gym_id,
                    Payment.payment_status == 'Pending'
                )
            ).scalar() or 0
        
        # Recent payments
        recent_payments = Payment.query.filter_by(gym_id=gym_id)\
            .join(Member)\
            .order_by(desc(Payment.created_at))\
            .limit(5).all()
        
        # Monthly revenue trend (last 6 months)
        monthly_revenue = []
        for i in range(5, -1, -1):
            if current_month_start.month - i <= 0:
                year = current_month_start.year - 1
                month = 12 + (current_month_start.month - i)
            else:
                year = current_month_start.year
                month = current_month_start.month - i
                
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(year, month + 1, 1) - timedelta(days=1)
            
            revenue = db.session.query(func.sum(Payment.payment_amount))\
                .filter(
                    and_(
                        Payment.gym_id == gym_id,
                        Payment.payment_date >= month_start,
                        Payment.payment_date <= month_end,
                        Payment.payment_status == 'Paid'
                    )
                ).scalar() or 0
            
            monthly_revenue.append({
                'month': month_start.strftime('%b %Y'),
                'revenue': float(revenue)
            })
        
        # Calculate growth percentages
        revenue_growth = 0
        if last_month_revenue > 0:
            revenue_growth = ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100
        
        members_growth = 0
        if total_members > 0:
            members_growth = (recent_members_count / total_members) * 100
        
        return jsonify({
            'members': {
                'total': total_members,
                'active': active_members,
                'recent_count': recent_members_count,
                'growth_percentage': round(members_growth, 1),
                'recent_members': [member.to_dict() for member in latest_members]
            },
            'membership_plans': {
                'total': total_plans,
                'active': active_plans
            },
            'attendance': {
                'todays_checkins': todays_checkins,
                'currently_inside': currently_inside,
                'weekly_trend': weekly_attendance,
                'recent_attendance': [record.to_dict() for record in recent_attendance]
            },
            'payments': {
                'current_month_revenue': float(current_month_revenue),
                'last_month_revenue': float(last_month_revenue),
                'revenue_growth': round(revenue_growth, 1),
                'pending_count': pending_payments_count,
                'pending_amount': float(pending_payments_amount),
                'monthly_trend': monthly_revenue,
                'recent_payments': [payment.to_dict() for payment in recent_payments]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch analytics: {str(e)}'}), 500

@analytics_bp.route('/quick-stats', methods=['GET'])
@jwt_required()
def get_quick_stats():
    """Get quick stats for dashboard cards"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    try:
        today = date.today()
        
        # Quick counts
        total_members = Member.query.filter_by(gym_id=gym_id).count()
        todays_attendance = Attendance.query.filter_by(
            gym_id=gym_id,
            attendance_date=today
        ).count()
        total_plans = MembershipPlan.query.filter_by(gym_id=gym_id, status='Active').count()
        
        # Current month revenue
        current_month_start = date(today.year, today.month, 1)
        monthly_revenue = db.session.query(func.sum(Payment.payment_amount))\
            .filter(
                and_(
                    Payment.gym_id == gym_id,
                    Payment.payment_date >= current_month_start,
                    Payment.payment_status == 'Paid'
                )
            ).scalar() or 0
        
        return jsonify({
            'total_members': total_members,
            'todays_attendance': todays_attendance,
            'total_plans': total_plans,
            'monthly_revenue': float(monthly_revenue)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch quick stats: {str(e)}'}), 500