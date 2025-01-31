from flask import Flask, render_template
import plotly.express as px
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder 
import os

app = Flask(__name__)

# Sample data
def get_sample_data():
    curr = os.getcwd()
    df = pd.read_csv(f'{curr}/datasets/entity_df.csv')
    print(df.head())
    # Top entities data
    top_entities = pd.DataFrame({
        'entity': ['Apple', 'Amazon', 'Facebook', 'Energy', 'Airlines', 'Car Brands', 'Technology'],
        'mentions': [2500, 2300, 2000, 1200, 1000, 800, 500]
    })
    
    # Time series data
    time_data = pd.DataFrame({
        'year': [2016, 2017, 2018, 2019, 2020, 2021],
        'mentions': [5000, 22000, 15000, 35000, 20000, 28000]
    })
    
    # Entity types data
    type_data = pd.DataFrame({
        'type': ['Organization', 'Person', 'Location', 'Event'],
        'percentage': [30, 35, 20, 15]
    })
    
    # Entity list data
    entity_list = pd.DataFrame({
        'Entity': ['Spotify Subscription', 'Freepik Sales', 'Mobile Service'],
        'Type': ['Organization', 'Location', 'Organization'],
        'Mentions': [3000, 2000, 3000]
    })
    
    return top_entities, time_data, type_data, entity_list
@app.route('/')
def index():
    top_entities, time_data, type_data, entity_list = get_sample_data()
    
    # Create Top Entities bar chart
    top_entities_fig = px.bar(
        top_entities,
        x='mentions',
        y='entity',
        orientation='h',
        title='Top Entities'
    )
    top_entities_fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        yaxis_title='',
        xaxis_title='',
        height=400
    )
    
    # Create Mentions Over Time line chart
    mentions_time_fig = px.line(
        time_data,
        x='year',
        y='mentions',
        title='Entity Mentions Over Time',
        markers=True
    )
    mentions_time_fig.update_layout(
        plot_bgcolor='white',
        yaxis_title='',
        xaxis_title='',
        height=400
    )
    
    # Create Entity Types Distribution pie chart
    entity_dist_fig = px.pie(
        type_data,
        values='percentage',
        names='type',
        title='Entity Types Distribution'
    )
    entity_dist_fig.update_layout(height=400)
    
    # Convert the figures to JSON for passing to template
    graphJSON = json.dumps({
        'top_entities': top_entities_fig.to_json(),
        'mentions_time': mentions_time_fig.to_json(),
        'entity_dist': entity_dist_fig.to_json()
    })
    
    return render_template('analysis.html', 
                         graphJSON=graphJSON, 
                         entity_list=entity_list.to_dict('records'))


@app.route('/relationship')
def relationship():
    # Sample relationship data
    relations = [
        {
            'entity1': 'Spotify Subscription',
            'relationship': 'Acquires',
            'entity2': 'Shopping',
            'frequency': 1000,
            'sentiment': 'Negative'
        },
        {
            'entity1': 'Freepik Sales',
            'relationship': 'Partnered',
            'entity2': 'Transfer',
            'frequency': 2212,
            'sentiment': 'Positive'
        },
        # Add more sample data as needed
    ]
    return render_template('relationship.html', relations=relations)

@app.route('/knowledgeGraph')
def knowledgeGraph():
    return render_template('knowledgeGraph.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')