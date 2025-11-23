from flask import Flask, request, Response
from flask_restful import Resource, Api
from pymongo import MongoClient
import json
import csv
import io
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# MongoDB connection
try:
    client = MongoClient('mongodb://db:27017/', serverSelectionTimeoutMS=5000)
    db = client.brevets_db
    collection = db.controls
    # Test connection
    client.server_info()
    print("Successfully connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    collection = None


def get_data_from_db(time_type='all'):
    """
    Get data from MongoDB
    time_type: 'all', 'open', or 'close'
    """
    if collection is None:
        return []
    
    try:
        controls = list(collection.find({}, {
            '_id': 0,
            'km': 1,
            'miles': 1,
            'location': 1,
            'open': 1,
            'close': 1,
        }))
        
        if not controls:
            return []
        
        controls.sort(key=lambda x: x.get('open', ''))
        
        if time_type == 'open':
            result = []
            for control in controls:
                result.append({
                    'km': control.get('km', 0),
                    'miles': control.get('miles', 0),
                    'location': control.get('location', ''),
                    'open': control.get('open', '')
                })
            return result
            
        elif time_type == 'close':
            result = []
            for control in controls:
                result.append({
                    'km': control.get('km', 0),
                    'miles': control.get('miles', 0),
                    'location': control.get('location', ''),
                    'close': control.get('close', '')
                })
            return result
            
        else:
            open_times = []
            close_times = []
            for control in controls:
                open_times.append({
                    'km': control.get('km', 0),
                    'miles': control.get('miles', 0),
                    'location': control.get('location', ''),
                    'open': control.get('open', '')
                })
                close_times.append({
                    'km': control.get('km', 0),
                    'miles': control.get('miles', 0),
                    'location': control.get('location', ''),
                    'close': control.get('close', '')
                })
            return {'open_times': open_times, 'close_times': close_times}
            
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []


def apply_top_k(data, top_k):
    """Apply top K filter to data (already sorted in ascending order)"""
    if isinstance(data, dict):
        # For 'all' endpoint
        return {
            'open_times': data['open_times'][:top_k],
            'close_times': data['close_times'][:top_k]
        }
    else:
        # For 'open' and 'close' endpoints
        return data[:top_k]


def format_as_json(data):
    """Format data as JSON"""
    return Response(
        json.dumps(data, indent=2),
        mimetype='application/json'
    )


def format_as_csv(data):
    """Format data as CSV"""
    output = io.StringIO()
    
    if isinstance(data, dict):
        # For 'all' endpoint - combine open and close times
        writer = csv.writer(output)
        writer.writerow(['km', 'miles', 'location', 'open_time', 'close_time'])
        
        for i in range(len(data['open_times'])):
            open_item = data['open_times'][i]
            close_item = data['close_times'][i]
            writer.writerow([
                open_item.get('km', ''),
                open_item.get('miles', ''),
                open_item.get('location', ''),
                open_item.get('open', ''),
                close_item.get('close', '')
            ])
    else:
        # For 'open' and 'close' endpoints
        writer = csv.writer(output)
        
        if data and 'open' in data[0]:
            # Open times
            writer.writerow(['km', 'miles', 'location', 'open_time'])
            for item in data:
                writer.writerow([
                    item.get('km', ''),
                    item.get('miles', ''),
                    item.get('location', ''),
                    item.get('open', '')
                ])
        elif data and 'close' in data[0]:
            # Close times
            writer.writerow(['km', 'miles', 'location', 'close_time'])
            for item in data:
                writer.writerow([
                    item.get('km', ''),
                    item.get('miles', ''),
                    item.get('location', ''),
                    item.get('close', '')
                ])
    
    return Response(
        output.getvalue(),
        mimetype='text/csv'
    )


class ListAll(Resource):
    """List all open and close times"""
    
    def get(self, format='json'):
        # Get top parameter from query string
        top_k = request.args.get('top', type=int)
        
        # Get data from database
        data = get_data_from_db('all')
        
        if not data:
            if format.lower() == 'csv':
                return Response('No data available\n', mimetype='text/csv')
            return {'message': 'No data available'}, 200
        
        # Apply top K filter if specified
        if top_k:
            data = apply_top_k(data, top_k)
        
        # Format response
        if format.lower() == 'csv':
            return format_as_csv(data)
        else:
            return format_as_json(data)


class ListOpenOnly(Resource):
    """List only open times"""
    
    def get(self, format='json'):
        # Get top parameter from query string
        top_k = request.args.get('top', type=int)
        
        # Get data from database
        data = get_data_from_db('open')
        
        if not data:
            if format.lower() == 'csv':
                return Response('No data available\n', mimetype='text/csv')
            return {'message': 'No data available'}, 200
        
        # Apply top K filter if specified
        if top_k:
            data = apply_top_k(data, top_k)
        
        # Format response
        if format.lower() == 'csv':
            return format_as_csv(data)
        else:
            return format_as_json(data)


class ListCloseOnly(Resource):
    """List only close times"""
    
    def get(self, format='json'):
        # Get top parameter from query string
        top_k = request.args.get('top', type=int)
        
        # Get data from database
        data = get_data_from_db('close')
        
        if not data:
            if format.lower() == 'csv':
                return Response('No data available\n', mimetype='text/csv')
            return {'message': 'No data available'}, 200
        
        # Apply top K filter if specified
        if top_k:
            data = apply_top_k(data, top_k)
        
        # Format response
        if format.lower() == 'csv':
            return format_as_csv(data)
        else:
            return format_as_json(data)


class HealthCheck(Resource):
    """Health check endpoint"""
    
    def get(self):
        try:
            if collection is not None:
                count = collection.count_documents({})
                return {
                    'status': 'healthy',
                    'database': 'connected',
                    'controls_count': count
                }, 200
            else:
                return {
                    'status': 'unhealthy',
                    'database': 'disconnected'
                }, 503
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }, 503


# Register API endpoints
api.add_resource(ListAll, 
                '/listAll',
                '/listAll/<string:format>')
api.add_resource(ListOpenOnly,
                '/listOpenOnly', 
                '/listOpenOnly/<string:format>')
api.add_resource(ListCloseOnly,
                '/listCloseOnly',
                '/listCloseOnly/<string:format>')
api.add_resource(HealthCheck, '/health')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)