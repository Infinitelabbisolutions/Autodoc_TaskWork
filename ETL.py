import pandas as pd
import numpy as np
from datetime import datetime

def load_data(file_path):
    df = pd.read_csv(file_path)
    df['event_date'] = pd.to_datetime(df['event_date'])
    return df

def analyze_funnel(df):
    session_journeys = df.groupby('session').agg({
        'event_date': 'min',
        'user': 'first',
        'page_type': lambda x: list(x),
        'event_type': lambda x: list(x),
        'product': lambda x: list(x)
    }).reset_index()
    
    session_journeys['first_page_type'] = session_journeys['page_type'].apply(lambda x: x[0])
    session_journeys['reached_product'] = session_journeys['page_type'].apply(lambda x: 'product_page' in x)
    session_journeys['reached_cart'] = session_journeys['event_type'].apply(lambda x: 'add_to_cart' in x)
    session_journeys['reached_purchase'] = session_journeys['event_type'].apply(lambda x: 'order' in x)
    
    return session_journeys

def analyze_by_first_page(session_journeys):
    first_page_analysis = session_journeys.groupby('first_page_type').agg({
        'session': 'count',
        'reached_product': 'mean',
        'reached_cart': 'mean',
        'reached_purchase': 'mean'
    }).reset_index()
    
    first_page_analysis = first_page_analysis.rename(columns={
        'session': 'total_sessions',
        'reached_product': 'product_view_rate',
        'reached_cart': 'cart_rate',
        'reached_purchase': 'purchase_rate'
    })
    
    for col in ['product_view_rate', 'cart_rate', 'purchase_rate']:
        first_page_analysis[col] = first_page_analysis[col] * 100
        
    return first_page_analysis

def analyze_product_only_viewers(df):
    first_sessions = df.groupby('user')['event_date'].min().reset_index()
    first_sessions['date'] = first_sessions['event_date'].dt.date
    
    df['date'] = df['event_date'].dt.date
    product_viewers = df.merge(first_sessions, on=['user', 'date'], suffixes=('', '_first'))
    
    product_only = product_viewers.groupby('user').agg({
        'date': 'first',
        'event_type': lambda x: all(e == 'page_view' for e in x),
        'page_type': lambda x: any(p == 'product_page' for p in x)
    }).reset_index()
    
    product_only_viewers = product_only[
        (product_only['event_type']) & 
        (product_only['page_type'])
    ]
    
    return product_only_viewers.groupby('date').size().reset_index(name='viewers_count')

def detect_abnormal_behavior(df):
    user_metrics = df.groupby('user').agg({
        'session': 'nunique',
        'event_type': 'count',
        'page_type': 'nunique',
    }).reset_index()
    
    user_metrics = user_metrics.rename(columns={
        'session': 'session_count',
        'event_type': 'total_events',
        'page_type': 'unique_page_types'
    })
    
    user_metrics['events_per_session'] = user_metrics['total_events'] / user_metrics['session_count']
    
    abnormal_users = user_metrics[
        (user_metrics['events_per_session'] > 5) |
        (user_metrics['total_events'] > 10) |
        ((user_metrics['unique_page_types'] == 1) & (user_metrics['total_events'] > 5))
    ]
    
    return abnormal_users

def main():
    df = load_data('data.csv')
    session_journeys = analyze_funnel(df)
    first_page_analysis = analyze_by_first_page(session_journeys)
    product_viewers = analyze_product_only_viewers(df)
    abnormal_behavior = detect_abnormal_behavior(df)
    session_journeys.to_csv('funnel_data.csv', index=False)
    first_page_analysis.to_csv('first_page_analysis.csv', index=False)
    product_viewers.to_csv('product_viewers.csv', index=False)
    abnormal_behavior.to_csv('abnormal_behavior.csv', index=False)

if __name__ == "__main__":
    main()