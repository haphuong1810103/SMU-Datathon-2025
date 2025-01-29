from flask import Flask, render_template
import plotly.express as px
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder  # Correct import for PlotlyJSONEncoder

app = Flask(__name__)

# Sample data
def get_sample_data():
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
        title='Top Entities',
        color_discrete_sequence=['rgb(66, 66, 255)']
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
        markers=True,
        color_discrete_sequence=['rgb(66, 66, 255)']
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
        title='Entity Types Distribution',
        color_discrete_sequence=['rgb(44, 49, 79)', 'rgb(50, 205, 50)', 
                               'rgb(255, 0, 255)', 'rgb(255, 128, 0)']
    )
    entity_dist_fig.update_layout(height=400)
    
    # Convert the figures to JSON for passing to template
    graphJSON = {
        'top_entities': json.dumps(top_entities_fig, cls=PlotlyJSONEncoder),
        'mentions_time': json.dumps(mentions_time_fig, cls=PlotlyJSONEncoder),
        'entity_dist': json.dumps(entity_dist_fig, cls=PlotlyJSONEncoder)
    }
    
    return render_template('index.html', 
                         graphJSON=graphJSON, 
                         entity_list=entity_list.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)