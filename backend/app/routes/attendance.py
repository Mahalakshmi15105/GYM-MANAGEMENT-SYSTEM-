from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_, desc, func, and_
from app.extensions import db
from app.models import Attendance, Member
from app.activity_logging import ActivityLogger
from datetime import datetime, date, timedelta
import uuid

attendance_bp = Blueprint('attendance', __name__)

def get_current_gym_id():
    """Extract gym_id from JWT token for multi-tenant isolation"""
    claims = get_jwt()
    return claims.get('gym_id')

@attendance_bp.route('', methods=['GET'])
@jwt_required()
def list_attendance():
    """List all attendance records for the current gym (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    # Get query parameters for filtering and search
    status_filter = request.args.get('status')
    search_query = request.args.get('q', '').strip()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    member_id = request.args.get('member_id')
    
    # Base query with multi-tenant isolation and joins
    query = Attendance.query.filter_by(gym_id=gym_id).join(Member)
    
    # Apply status filter
    if status_filter and status_filter != 'All':
        query = query.filter(Attendance.status == status_filter)
    
    # Apply member filter
    if member_id:
        query = query.filter(Attendance.member_id == member_id)
    
    # Apply date range filter
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance_date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance_date <= end_dt)
        except ValueError:
            pass
    
    # Apply search filter
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Member.first_name.ilike(search_pattern),
                Member.last_name.ilike(search_pattern),
                Member.phone.ilike(search_pattern)
            )
        )
    
    # Order by check-in time (newest first) and limit for safety
    attendance_records = query.order_by(desc(Attendance.check_in_time)).limit(100).all()
    
    # Log the view operation
    ActivityLogger.log_view('attendance', view_type='list', gym_id=gym_id)
    
    return jsonify({
        'attendance': [record.to_dict() for record in attendance_records]
    }), 200

@attendance_bp.route('', methods=['POST'])
@jwt_required()
def create_attendance():
    """Create a new attendance record (check-in) for the current gym"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    data = request.get_json() or {}
    
    # Required fields validation
    if not data.get('member_id'):
        return jsonify({'error': 'Member ID is required'}), 400
    
    # Validate member exists and belongs to this gym
    member = Member.query.filter_by(id=data['member_id'], gym_id=gym_id).first()
    if not member:
        return jsonify({'error': 'Member not found in your gym'}), 400
    
    # Check if member is already checked in today
    today = date.today()
    existing_checkin = Attendance.query.filter_by(
        gym_id=gym_id,
        member_id=data['member_id'],
        attendance_date=today,
        status='Checked In'
    ).first()
    
    if existing_checkin:
        return jsonify({'error': 'Member is already checked in today'}), 400
    
    try:
        # Parse check-in time or use current time
        check_in_time = datetime.utcnow()
        if data.get('check_in_time'):
            try:
                check_in_time = datetime.fromisoformat(data['check_in_time'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Calculate expected finish time based on member's workout duration
        workout_duration_minutes = member.workout_duration_minutes or 120  # Default 2 hours
        expected_finish_time = check_in_time + timedelta(minutes=workout_duration_minutes)
        
        # Create new attendance record
        new_attendance = Attendance(
            gym_id=gym_id,
            member_id=data['member_id'],
            check_in_time=check_in_time,
            expected_finish_time=expected_finish_time,
            attendance_date=check_in_time.date(),
            status='Checked In',
            notes=data.get('notes', '')
        )
        
        db.session.add(new_attendance)
        db.session.commit()
        
        # Log the check-in operation
        member_name = f"{member.first_name} {member.last_name}".strip()
        ActivityLogger.log_create(
            'attendance',
            new_attendance.id,
            entity_name=f"Check-in: {member_name}",
            gym_id=gym_id,
            extra_data={
                'action': 'check_in',
                'member_name': member_name,
                'check_in_time': check_in_time.isoformat()
            }
        )
        
        return jsonify({
            'message': 'Check-in recorded successfully',
            'attendance': new_attendance.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to record check-in: {str(e)}'}), 500

@attendance_bp.route('/<int:attendance_id>/checkout', methods=['PUT'])
@jwt_required()
def checkout_attendance(attendance_id):
    """Check out a member (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    attendance = Attendance.query.filter_by(id=attendance_id, gym_id=gym_id).first()
    if not attendance:
        return jsonify({'error': 'Attendance record not found'}), 404
    
    if attendance.status == 'Checked Out':
        return jsonify({'error': 'Member is already checked out'}), 400
    
    data = request.get_json() or {}
    
    try:
        # Parse check-out time or use current time
        check_out_time = datetime.utcnow()
        if data.get('check_out_time'):
            try:
                check_out_time = datetime.fromisoformat(data['check_out_time'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Validate check-out time is after check-in time
        if check_out_time <= attendance.check_in_time:
            return jsonify({'error': 'Check-out time must be after check-in time'}), 400
        
        attendance.check_out_time = check_out_time
        attendance.status = 'Checked Out'
        attendance.updated_at = datetime.utcnow()
        
        if data.get('notes'):
            attendance.notes = data['notes']
        
        db.session.commit()
        
        # Log the check-out operation
        member_name = f"{attendance.member.first_name} {attendance.member.last_name}".strip() if attendance.member else "Unknown Member"
        ActivityLogger.log_update(
            'attendance',
            attendance_id,
            changes={'status': {'old': 'Checked In', 'new': 'Checked Out'}},
            entity_name=f"Check-out: {member_name}",
            gym_id=gym_id
        )
        
        return jsonify({
            'message': 'Check-out recorded successfully',
            'attendance': attendance.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to record check-out: {str(e)}'}), 500

@attendance_bp.route('/<int:attendance_id>', methods=['GET'])
@jwt_required()
def get_attendance(attendance_id):
    """Get attendance record details by ID (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    attendance = Attendance.query.filter_by(id=attendance_id, gym_id=gym_id).first()
    if not attendance:
        return jsonify({'error': 'Attendance record not found'}), 404
    
    return jsonify(attendance.to_dict()), 200

@attendance_bp.route('/<int:attendance_id>', methods=['PUT'])
@jwt_required()
def update_attendance(attendance_id):
    """Update attendance record (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    attendance = Attendance.query.filter_by(id=attendance_id, gym_id=gym_id).first()
    if not attendance:
        return jsonify({'error': 'Attendance record not found'}), 404
    
    data = request.get_json() or {}
    
    try:
        # Update notes
        if 'notes' in data:
            attendance.notes = data['notes']
        
        # Update check-in time
        if 'check_in_time' in data and data['check_in_time']:
            try:
                check_in_time = datetime.fromisoformat(data['check_in_time'].replace('Z', '+00:00'))
                attendance.check_in_time = check_in_time
                attendance.attendance_date = check_in_time.date()
            except ValueError:
                return jsonify({'error': 'Invalid check-in time format'}), 400
        
        # Update check-out time
        if 'check_out_time' in data:
            if data['check_out_time']:
                try:
                    check_out_time = datetime.fromisoformat(data['check_out_time'].replace('Z', '+00:00'))
                    if check_out_time <= attendance.check_in_time:
                        return jsonify({'error': 'Check-out time must be after check-in time'}), 400
                    attendance.check_out_time = check_out_time
                    attendance.status = 'Checked Out'
                except ValueError:
                    return jsonify({'error': 'Invalid check-out time format'}), 400
            else:
                # Remove check-out time
                attendance.check_out_time = None
                attendance.status = 'Checked In'
        
        attendance.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Attendance record updated successfully',
            'attendance': attendance.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update attendance record: {str(e)}'}), 500

@attendance_bp.route('/<int:attendance_id>', methods=['DELETE'])
@jwt_required()
def delete_attendance(attendance_id):
    """Delete attendance record (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    attendance = Attendance.query.filter_by(id=attendance_id, gym_id=gym_id).first()
    if not attendance:
        return jsonify({'error': 'Attendance record not found'}), 404
    
    try:
        db.session.delete(attendance)
        db.session.commit()
        return jsonify({'message': 'Attendance record deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete attendance record: {str(e)}'}), 500

@attendance_bp.route('/search', methods=['GET'])
@jwt_required()
def search_attendance():
    """Search attendance records by member criteria (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    query_param = request.args.get('q', '').strip()
    if not query_param:
        return jsonify({'attendance': []}), 200
    
    search_pattern = f"%{query_param}%"
    attendance_records = Attendance.query.filter_by(gym_id=gym_id).join(Member).filter(
        or_(
            Member.first_name.ilike(search_pattern),
            Member.last_name.ilike(search_pattern),
            Member.phone.ilike(search_pattern)
        )
    ).order_by(desc(Attendance.check_in_time)).limit(20).all()
    
    return jsonify({
        'attendance': [record.to_dict() for record in attendance_records]
    }), 200

@attendance_bp.route('/members', methods=['GET'])
@jwt_required()
def get_members_for_attendance():
    """Get all active members for attendance dropdown (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    members = Member.query.filter_by(gym_id=gym_id, status='Active').order_by(Member.first_name.asc()).all()
    
    return jsonify({
        'members': [{
            'id': member.id,
            'name': f"{member.first_name} {member.last_name}",
            'phone': member.phone,
            'membership_plan_name': member.membership_plan_name
        } for member in members]
    }), 200

@attendance_bp.route('/reports/daily', methods=['GET'])
@jwt_required()
def daily_report():
    """Get daily attendance report (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    report_date = request.args.get('date')
    if report_date:
        try:
            report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    else:
        report_date = date.today()
    
    # Get attendance records for the date
    attendance_records = Attendance.query.filter_by(
        gym_id=gym_id,
        attendance_date=report_date
    ).join(Member).order_by(Attendance.check_in_time.asc()).all()
    
    # Calculate statistics
    total_checkins = len(attendance_records)
    checked_out = len([r for r in attendance_records if r.status == 'Checked Out'])
    still_inside = total_checkins - checked_out
    
    # Calculate average workout duration for checked out members
    durations = [r.get_duration_minutes() for r in attendance_records if r.get_duration_minutes()]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    return jsonify({
        'date': report_date.isoformat(),
        'statistics': {
            'total_checkins': total_checkins,
            'checked_out': checked_out,
            'still_inside': still_inside,
            'average_duration_minutes': round(avg_duration, 1)
        },
        'attendance': [record.to_dict() for record in attendance_records]
    }), 200

@attendance_bp.route('/reports/weekly', methods=['GET'])
@jwt_required()
def weekly_report():
    """Get weekly attendance report (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    week_start = request.args.get('week_start')
    if week_start:
        try:
            week_start = datetime.strptime(week_start, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    else:
        # Get current week (Monday to Sunday)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
    
    week_end = week_start + timedelta(days=6)
    
    # Get attendance records for the week
    attendance_records = Attendance.query.filter(
        and_(
            Attendance.gym_id == gym_id,
            Attendance.attendance_date >= week_start,
            Attendance.attendance_date <= week_end
        )
    ).join(Member).all()
    
    # Group by day
    daily_stats = {}
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_records = [r for r in attendance_records if r.attendance_date == day]
        daily_stats[day.isoformat()] = {
            'date': day.isoformat(),
            'day_name': day.strftime('%A'),
            'total_checkins': len(day_records),
            'checked_out': len([r for r in day_records if r.status == 'Checked Out'])
        }
    
    total_checkins = len(attendance_records)
    unique_members = len(set(r.member_id for r in attendance_records))
    
    return jsonify({
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'statistics': {
            'total_checkins': total_checkins,
            'unique_members': unique_members,
            'daily_average': round(total_checkins / 7, 1)
        },
        'daily_breakdown': list(daily_stats.values())
    }), 200

@attendance_bp.route('/reports/monthly', methods=['GET'])
@jwt_required()
def monthly_report():
    """Get monthly attendance report (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    month_str = request.args.get('month')  # Format: YYYY-MM
    if month_str:
        try:
            year, month = map(int, month_str.split('-'))
            month_start = date(year, month, 1)
        except ValueError:
            return jsonify({'error': 'Invalid month format. Use YYYY-MM'}), 400
    else:
        today = date.today()
        month_start = date(today.year, today.month, 1)
    
    # Calculate month end
    if month_start.month == 12:
        month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)
    
    # Get attendance records for the month
    attendance_records = Attendance.query.filter(
        and_(
            Attendance.gym_id == gym_id,
            Attendance.attendance_date >= month_start,
            Attendance.attendance_date <= month_end
        )
    ).join(Member).all()
    
    # Calculate statistics
    total_checkins = len(attendance_records)
    unique_members = len(set(r.member_id for r in attendance_records))
    
    # Group by week
    weekly_stats = {}
    current_date = month_start
    week_num = 1
    
    while current_date <= month_end:
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Adjust week boundaries to month
        week_start = max(week_start, month_start)
        week_end = min(week_end, month_end)
        
        week_records = [r for r in attendance_records 
                       if week_start <= r.attendance_date <= week_end]
        
        weekly_stats[f'week_{week_num}'] = {
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'total_checkins': len(week_records),
            'unique_members': len(set(r.member_id for r in week_records))
        }
        
        current_date = week_end + timedelta(days=1)
        week_num += 1
    
    return jsonify({
        'month': month_start.strftime('%B %Y'),
        'month_start': month_start.isoformat(),
        'month_end': month_end.isoformat(),
        'statistics': {
            'total_checkins': total_checkins,
            'unique_members': unique_members,
            'daily_average': round(total_checkins / (month_end - month_start + timedelta(days=1)).days, 1)
        },
        'weekly_breakdown': list(weekly_stats.values())
    }), 200


@attendance_bp.route('/qr-checkin', methods=['POST'])
@jwt_required()
def qr_checkin():
    """QR-based attendance check-in for members"""
    from app.models import Gym
    from urllib.parse import urlparse, parse_qs
    
    claims = get_jwt()
    member_id = claims.get('member_id')
    gym_id = claims.get('gym_id')
    
    # Only members can use QR check-in
    if not member_id or claims.get('role') != 'member':
        return jsonify({'error': 'Access denied. Only members can use QR check-in.'}), 403
    
    data = request.get_json() or {}
    qr_code = data.get('qr_code')
    
    if not qr_code:
        return jsonify({'error': 'QR code is required'}), 400
    
    try:
        # Extract gym QR code from URL if QR code contains a URL
        gym_qr_value = qr_code
        if qr_code.startswith('http'):
            # Parse URL and extract gym parameter
            parsed = urlparse(qr_code)
            query_params = parse_qs(parsed.query)
            if 'gym' in query_params:
                gym_qr_value = query_params['gym'][0]
        
        # Verify the QR code belongs to the member's gym
        gym = Gym.query.filter_by(id=gym_id).first()
        if not gym:
            return jsonify({'error': 'Gym not found'}), 404
        
        if gym.attendance_qr != gym_qr_value:
            return jsonify({'error': 'Invalid QR code. This QR does not belong to your gym.'}), 400
        
        # Check if member exists and belongs to this gym
        member = Member.query.filter_by(id=member_id, gym_id=gym_id).first()
        if not member:
            return jsonify({'error': 'Member not found in this gym'}), 404
        
        # Check if member has already checked in today
        today = date.today()
        existing_attendance = Attendance.query.filter_by(
            member_id=member_id,
            gym_id=gym_id,
            attendance_date=today
        ).first()
        
        if existing_attendance:
            return jsonify({
                'error': 'Already checked in today',
                'attendance': existing_attendance.to_dict()
            }), 400
        
        # Create attendance record
        now = datetime.utcnow()
        new_attendance = Attendance(
            gym_id=gym_id,
            member_id=member_id,
            check_in_time=now,
            attendance_date=today,
            status='Checked In'
        )
        
        db.session.add(new_attendance)
        db.session.commit()
        
        # Log the activity
        ActivityLogger.log_activity(
            'qr_checkin',
            f"Member {member.first_name} {member.last_name} checked in via QR",
            entity_type='attendance',
            entity_id=new_attendance.id,
            gym_id=gym_id,
            extra_data={'member_id': member_id, 'qr_code': qr_code}
        )
        
        return jsonify({
            'message': 'Check-in successful',
            'attendance': new_attendance.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to check in: {str(e)}'}), 500