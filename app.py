from flask import Flask, render_template, jsonify, request
import plotly.express as px
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder
import os
import google.generativeai as genai


app = Flask(__name__)

# Configure the Gemini API
genai.configure(api_key="AIzaSyCSJyVq3QtqDoBeWVffHzZcKVh6lCei8-Q")
model = genai.GenerativeModel("gemini-1.5-flash")




@app.route('/')
def index():
    # Data Processing
    path = os.getcwd()
    pdf_csv_path = os.path.join(path, 'datasets', 'pdf.csv')
    url_csv_path = os.path.join(path, 'datasets', 'url.csv')

    pdf_df = pd.read_csv(pdf_csv_path)
    url_df = pd.read_csv(url_csv_path)
    
    # Pass the dataframes directly to the template
    return render_template('overview.html', pdf_df=pdf_df, url_df=url_df)

# Sample data
def load_data():
    curr = os.getcwd()
    df = pd.read_csv(f'{curr}/datasets/entity_df.csv')
    return df

@app.route('/analysis')
def analysis():
    df = load_data()

    # Get unique entity types for the dropdown
    entity_types = ['All Types'] + df['entityType'].unique().tolist()

    # Create Top Entities bar chart (default top 10 entities)
    top_entities = df.nlargest(10, 'frequency')
    top_entities_fig = px.bar(
        top_entities,
        x='frequency',
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

    # Create Entity Types Distribution pie chart with top 4 and Others
    type_distribution = df['entityType'].value_counts().reset_index()
    type_distribution.columns = ['type', 'count']
    
    # Separate top 4 and combine others
    top_5_types = type_distribution.head(5)
    others_sum = type_distribution.iloc[5:]['count'].sum()
    
    if len(type_distribution) > 5:
        others_df = pd.DataFrame({'type': ['Others'], 'count': [others_sum]})
        final_distribution = pd.concat([top_5_types, others_df], ignore_index=True)
    else:
        final_distribution = type_distribution
    
    entity_dist_fig = px.pie(
        final_distribution,
        values='count',
        names='type',
        title='Entity Types Distribution'
    )
    entity_dist_fig.update_layout(height=400)

    # Convert the figures to JSON for passing to template
    graphJSON = json.dumps({
        'top_entities': top_entities_fig.to_json(),
        'entity_dist': entity_dist_fig.to_json()
    })

    # Pass the entity list for the table (top 10 entities by default)
    entity_list = df.nlargest(10, 'frequency')[['entity', 'entityType', 'frequency']]

    return render_template('analysis.html',
                         graphJSON=graphJSON,
                         entity_list=entity_list.to_dict('records'),
                         entity_types=entity_types)

@app.route('/filter', methods=['POST'])
def filter_data():
    df = load_data()

    # Get filter parameters from the request
    entity_types = request.json.get('entityType', [])
    top_k = int(request.json.get('topEntities'))

    # Filter the data based on entity type
    if entity_types and "All Types" not in entity_types:
        filtered_df = df[df['entityType'].isin(entity_types)]
    else:
        filtered_df = df

    # Get the top k entities based on frequency
    top_k_entities = filtered_df.nlargest(top_k, 'frequency')

    # Create the bar chart for top k entities
    bar_chart = px.bar(
        top_k_entities,
        x='frequency',
        y='entity',
        orientation='h',
        title=f'Top {top_k} Entities for {", ".join(entity_types) if entity_types and "All Types" not in entity_types else "All Types"}'
    )
    bar_chart.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        yaxis_title='',
        xaxis_title='',
        height=400
    )

    # Create the pie chart for entity type distribution with top 4 and Others
    type_distribution = filtered_df['entityType'].value_counts().reset_index()
    type_distribution.columns = ['type', 'count']
    
    # Separate top 4 and combine others
    top_5_types = type_distribution.head(5)
    others_sum = type_distribution.iloc[5:]['count'].sum()
    
    if len(type_distribution) > 5:
        others_df = pd.DataFrame({'type': ['Others'], 'count': [others_sum]})
        final_distribution = pd.concat([top_5_types, others_df], ignore_index=True)
    else:
        final_distribution = type_distribution
    
    pie_chart = px.pie(
        final_distribution,
        values='count',
        names='type',
        title='Entity Types Distribution'
    )
    pie_chart.update_layout(height=400)

    # Return the charts as JSON
    return jsonify({
        'bar_chart': bar_chart.to_json(),
        'pie_chart': pie_chart.to_json()
    })

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
    ]
    return render_template('relationship.html', relations=relations)

@app.route('/knowledgeGraph')
def knowledgeGraph():
    return render_template('knowledgeGraph.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        response = model.generate_content(user_message)
        bot_reply = response.text if hasattr(response, 'text') else "Sorry, I couldn't process that."
    except Exception as e:
        bot_reply = f"Error: {str(e)}"
    
    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run(debug=True)