import json
import boto3
import os
import csv
import requests
import itertools
from collections import Counter

# Initialize the AWS S3 client to read/write files in the cloud
s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'your-drawpredict-data-bucket')

def lambda_handler(event, context):
    """
    Main entry point for AWS Lambda. Handles both:
    1. Automated Data Syncing (via EventBridge cron job)
    2. Real-Time Play Generation requests (via React API call)
    """
    path = event.get('path', '')
    http_method = event.get('httpMethod', '')
    
    # ---------------------------------------------------------
    # ROUTE 1: AUTOMATED DATA SYNC ENGINE
    # ---------------------------------------------------------
    if "sync" in path or event.get('source') == 'aws.events':
        return handle_server_sync()

    # ---------------------------------------------------------
    # ROUTE 2: REAL-TIME TACTICAL PLAY GENERATOR
    # ---------------------------------------------------------
    elif "matrix" in path or http_method == 'GET':
        # Default query parameters
        query_params = event.get('queryStringParameters') or {}
        game = query_params.get('game', 'daily4') # daily4 or pick3
        strategy = query_params.get('strategy', 'positional') # positional or box
        target_structure = query_params.get('structure', 'Single (24-Way)')
        
        return generate_tactical_plays(game, strategy, target_structure)
        
    return {
        'statusCode': 400,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Invalid routing path'})
    }

def handle_server_sync():
    """Bypasses state firewalls and caches fresh data directly into AWS S3"""
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    endpoints = {
        'live_pick3_suite.csv': "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3day.csv",
        'live_daily_4_suite.csv': "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4day.csv"
    }
    
    sync_results = {}
    for filename, url in endpoints.items():
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                # Stream directly to your private AWS S3 data bucket
                s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=res.text)
                sync_results[filename] = "Synchronized Successfully"
            else:
                sync_results[filename] = f"Failed with status code {res.status_code}"
        except Exception as e:
            sync_results[filename] = f"Error: {str(e)}"
            
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'message': 'Sync process finalized', 'results': sync_results})
    }

def generate_tactical_plays(game, strategy, target_structure):
    """Processes matrix statistics in the cloud and outputs target suggestions"""
    filename = 'live_daily_4_suite.csv' if game == 'daily4' else 'live_pick3_suite.csv'
    digit_count = 4 if game == 'daily4' else 3
    
    try:
        # Pull latest file out of AWS S3 memory
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
        lines = obj['Body'].read().decode('utf-8').splitlines()
        
        valid_rows = []
        for row in csv.reader(lines):
            if len(row) >= 7:
                valid_rows.append(row)
                
        if not valid_rows:
            return {'statusCode': 404, 'body': json.dumps({'error': 'No valid data available'})}
            
        # Parse drawing matrix digits
        matrix = []
        digit_distribution = {i: [0] * digit_count for i in range(10)}
        matching_straights = []
        
        for row in valid_rows:
            # Dropdown parsing columns based on standard Texas file layouts
            digits = [int(x) for x in row[4:4+digit_count] if x.isdigit()]
            if len(digits) == digit_count:
                matrix.append(digits)
                
                # Build positional distributions
                for pos_idx, digit in enumerate(digits):
                    digit_distribution[digit][pos_idx] += 1
                
                # Track structure categorization
                counts = Counter(digits)
                unique_counts = sorted(list(counts.values()), reverse=True)
                
                current_struct = "Single"
                if digit_count == 4:
                    if unique_counts == [1, 1, 1, 1]: current_struct = "Single (24-Way)"
                    elif unique_counts == [2, 1, 1]: current_struct = "Single Pair (12-Way)"
                    elif unique_counts == [2, 2]: current_struct = "Double-Double (6-Way)"
                    elif unique_counts == [3, 1]: current_struct = "Triple (4-Way)"
                    elif unique_counts == [4]: current_struct = "Quad (1-Way)"
                else:
                    if unique_counts == [1, 1, 1]: current_struct = "3-Way Box"
                    elif unique_counts == [2, 1]: current_struct = "6-Way Box"
                    
                if current_struct == target_structure:
                    matching_straights.append("".join(map(str, digits)))

        # Run filter algorithms
        generated_numbers = []
        if strategy == 'positional':
            top_digits_per_pos = []
            for pos in range(digit_count):
                sorted_digits = sorted(range(10), key=lambda d: digit_distribution[d][pos], reverse=True)
                top_digits_per_pos.append(sorted_digits[:3])
            
            all_combos = list(itertools.product(*top_digits_per_pos))
            generated_numbers = ["".join(map(str, combo)) for combo in all_combos[:16]]
        else:
            generated_numbers = list(set(matching_straights))[:16]

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # Crucial for React frontend communication
            },
            'body': json.dumps({
                'game': game,
                'total_drawings_analyzed': len(matrix),
                'strategy_applied': strategy,
                'plays': generated_numbers
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
