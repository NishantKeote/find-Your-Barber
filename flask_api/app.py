from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
import json
from datetime import datetime, timedelta
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask-secret-key-for-barber-management'
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:8000", "http://127.0.0.1:8000"])

# Database connection to Django's SQLite database
DJANGO_DB_PATH = '../django_backend/db.sqlite3'

def get_db_connection():
    """Get connection to Django database"""
    conn = sqlite3.connect(DJANGO_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/location/geocode', methods=['POST'])
def geocode_address():
    """Convert address to coordinates"""
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({'error': 'Address is required'}), 400
        
        geolocator = Nominatim(user_agent="barber_management_system")
        location = geolocator.geocode(address)
        
        if location:
            return jsonify({
                'latitude': location.latitude,
                'longitude': location.longitude,
                'address': location.address
            })
        else:
            return jsonify({'error': 'Address not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/shops/nearby', methods=['POST'])
def find_nearby_shops():
    """Find shops near given coordinates"""
    try:
        data = request.get_json()
        user_lat = float(data.get('latitude'))
        user_lng = float(data.get('longitude'))
        radius_km = float(data.get('radius', 10))  # Default 10km radius
        
        conn = get_db_connection()
        shops = conn.execute('''
            SELECT s.*, u.username as owner_name 
            FROM shops_shop s
            JOIN users_user u ON s.owner_id = u.id
            WHERE s.is_active = 1
        ''').fetchall()
        
        nearby_shops = []
        for shop in shops:
            shop_location = (shop['latitude'], shop['longitude'])
            user_location = (user_lat, user_lng)
            
            distance = geodesic(user_location, shop_location).kilometers
            
            if distance <= radius_km:
                nearby_shops.append({
                    'id': shop['id'],
                    'name': shop['name'],
                    'description': shop['description'],
                    'address': shop['address'],
                    'phone_number': shop['phone_number'],
                    'opening_time': shop['opening_time'],
                    'closing_time': shop['closing_time'],
                    'current_waiting_count': shop['current_waiting_count'],
                    'max_waiting_list_size': shop['max_waiting_list_size'],
                    'distance_km': round(distance, 2),
                    'owner_name': shop['owner_name']
                })
        
        # Sort by distance
        nearby_shops.sort(key=lambda x: x['distance_km'])
        
        conn.close()
        return jsonify({'shops': nearby_shops})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/waiting-list/realtime/<int:shop_id>')
def get_realtime_waiting_list(shop_id):
    """Get real-time waiting list for a shop"""
    try:
        conn = get_db_connection()
        
        # Get waiting list entries
        waiting_list = conn.execute('''
            SELECT w.*, u.username, u.first_name, u.last_name
            FROM waiting_lists_waitinglistentry w
            JOIN users_user u ON w.customer_id = u.id
            WHERE w.shop_id = ? AND w.status = 'waiting'
            ORDER BY w.position_number
        ''', (shop_id,)).fetchall()
        
        # Get shop info
        shop = conn.execute('''
            SELECT current_waiting_count, max_waiting_list_size, name
            FROM shops_shop WHERE id = ?
        ''', (shop_id,)).fetchone()
        
        if not shop:
            conn.close()
            return jsonify({'error': 'Shop not found'}), 404
        
        waiting_entries = []
        for entry in waiting_list:
            waiting_entries.append({
                'id': entry['id'],
                'customer_name': f"{entry['first_name'] or ''} {entry['last_name'] or ''}".strip() or entry['username'],
                'position_number': entry['position_number'],
                'joined_at': entry['joined_at'],
                'estimated_wait_time': entry['estimated_wait_time']
            })
        
        conn.close()
        return jsonify({
            'shop_name': shop['name'],
            'current_count': shop['current_waiting_count'],
            'max_count': shop['max_waiting_list_size'],
            'waiting_list': waiting_entries
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket events for real-time updates
@socketio.on('connect')
def on_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def on_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_shop')
def on_join_shop(data):
    """Join a shop room for real-time updates"""
    shop_id = data.get('shop_id')
    if shop_id:
        join_room(f'shop_{shop_id}')
        emit('status', {'msg': f'Joined shop {shop_id} room'})

@socketio.on('leave_shop')
def on_leave_shop(data):
    """Leave a shop room"""
    shop_id = data.get('shop_id')
    if shop_id:
        leave_room(f'shop_{shop_id}')
        emit('status', {'msg': f'Left shop {shop_id} room'})

@socketio.on('waiting_list_update')
def on_waiting_list_update(data):
    """Broadcast waiting list updates to all clients in shop room"""
    shop_id = data.get('shop_id')
    if shop_id:
        socketio.emit('waiting_list_changed', data, room=f'shop_{shop_id}')

@app.route('/api/search/shops', methods=['POST'])
def search_shops():
    """Search shops by name, description, or location"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        user_lat = data.get('latitude')
        user_lng = data.get('longitude')
        
        if not query:
            return jsonify({'shops': []})
        
        conn = get_db_connection()
        
        # Search in name, description, and address
        shops = conn.execute('''
            SELECT s.*, u.username as owner_name 
            FROM shops_shop s
            JOIN users_user u ON s.owner_id = u.id
            WHERE s.is_active = 1 
            AND (s.name LIKE ? OR s.description LIKE ? OR s.address LIKE ?)
        ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
        
        search_results = []
        for shop in shops:
            result = {
                'id': shop['id'],
                'name': shop['name'],
                'description': shop['description'],
                'address': shop['address'],
                'phone_number': shop['phone_number'],
                'opening_time': shop['opening_time'],
                'closing_time': shop['closing_time'],
                'current_waiting_count': shop['current_waiting_count'],
                'max_waiting_list_size': shop['max_waiting_list_size'],
                'owner_name': shop['owner_name']
            }
            
            # Calculate distance if user location is provided
            if user_lat and user_lng:
                shop_location = (shop['latitude'], shop['longitude'])
                user_location = (user_lat, user_lng)
                distance = geodesic(user_location, shop_location).kilometers
                result['distance_km'] = round(distance, 2)
            
            search_results.append(result)
        
        # Sort by distance if available, otherwise by name
        if user_lat and user_lng:
            search_results.sort(key=lambda x: x.get('distance_km', float('inf')))
        else:
            search_results.sort(key=lambda x: x['name'])
        
        conn.close()
        return jsonify({'shops': search_results})
        
    except Exception as e:
        return jsonResponse({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Flask API for Barber Management System'
    })

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("Available endpoints:")
    print("- POST /api/location/geocode - Convert address to coordinates")
    print("- POST /api/shops/nearby - Find nearby shops")
    print("- GET /api/waiting-list/realtime/<shop_id> - Real-time waiting list")
    print("- POST /api/search/shops - Search shops")
    print("- WebSocket events: connect, join_shop, leave_shop, waiting_list_update")
    
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)