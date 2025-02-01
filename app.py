from flask import Flask, render_template, jsonify, request
import plotly.express as px
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder
import os
import google.generativeai as genai
import networkx as nx
from collections import Counter
from itertools import combinations
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ast
import PyPDF2
from werkzeug.utils import secure_filename
from wordcloud import WordCloud
import io
import base64


app = Flask(__name__)

# Configure the Gemini API
genai.configure(api_key="AIzaSyCSJyVq3QtqDoBeWVffHzZcKVh6lCei8-Q")
model = genai.GenerativeModel("gemini-1.5-flash")

# Set upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''  # Handle pages with no extractable text
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"





@app.route('/')
def index():
    # Data Processing
    path = os.getcwd()
    pdf_csv_path = os.path.join(path, 'datasets', 'pdf.csv')
    url_csv_path = os.path.join(path, 'datasets', 'url.csv')

    pdf_df = pd.read_csv(pdf_csv_path)
    url_df = pd.read_csv(url_csv_path)

    def process_entities(entities_column):
        entities_list = ast.literal_eval(entities_column)
        formatted_entities = [f"{entity['span']} ({entity['label']})" for entity in entities_list]
        return ', '.join(formatted_entities)

    # Apply the function to the 'entities' column for both DataFrames
    pdf_df['entities'] = pdf_df['entities'].apply(process_entities)
    url_df['entities'] = url_df['entities'].apply(process_entities)

    
    # Pass the dataframes directly to the template
    pdf_df = pdf_df.fillna('')  # Replace NaN with an empty string
    url_df = url_df.fillna('')
    return render_template('overview.html', pdf_df=pdf_df, url_df=url_df)

def load_data():
    curr = os.getcwd()
    df = pd.read_csv(f'{curr}/datasets/entity_df.csv')
    return df

def generate_wordcloud(text, title):
    # Generate the WordCloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Plot the WordCloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=20)

    # Save the WordCloud to a BytesIO object
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png', bbox_inches='tight', pad_inches=0)
    img_bytes.seek(0)

    # Convert the image to a base64 string
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    plt.close()

    return img_base64

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

    # Generate WordCloud for PDF text
    pdf_path = os.path.join(os.getcwd(), 'datasets', 'pdf.csv')
    pdf_df = pd.read_csv(pdf_path)
    pdf_text = ' '.join(pdf_df['Text'].dropna())
    pdf_wordcloud = generate_wordcloud(pdf_text, 'PDF WordCloud')

    # Generate WordCloud for URL text
    url_path = os.path.join(os.getcwd(), 'datasets', 'url.csv')
    url_df = pd.read_csv(url_path)
    url_text = ' '.join(url_df['Text'].dropna())
    url_wordcloud = generate_wordcloud(url_text, 'URL WordCloud')


    # Create Topic Frequency Heatmap
    topic_path = os.path.join(os.getcwd(), 'datasets', 'topic_counts.csv')
    topic_df = pd.read_csv(topic_path)

    topic_heatmap_fig = px.scatter(
        topic_df, 
        x='Topic', 
        y='Count', 
        size='Count', 
        title='Topic Frequency Bubble Chart'
    )
    
    topic_heatmap_fig.update_layout(height=400)

    # Convert the figures to JSON for passing to template
    graphJSON = json.dumps({
        'top_entities': top_entities_fig.to_json(),
        'entity_dist': entity_dist_fig.to_json(),
        'topic_heatmap': topic_heatmap_fig.to_json()
    })


    return render_template('analysis.html',
                         graphJSON=graphJSON,
                         entity_types=entity_types,
                         pdf_wordcloud=pdf_wordcloud,
                         url_wordcloud=url_wordcloud)

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
def relationship(top_k=100):
    # Extract query parameters
    min_frequency = int(request.args.get('min_frequency', 1))
    entity_type_1 = request.args.get('entity_type_1', 'All Types')
    entity_type_2 = request.args.get('entity_type_2', 'All Types')
    
    # Get unique entity types dynamically from your data
    unique_entity_types = entity_df['entityType'].unique().tolist()
    unique_entity_types.insert(0, 'All Types')  # Add 'All Types' as the first option

    # Filter entities
    top_entities = set(entity_counts.nlargest(top_k, 'count')['entity'])
    entity_type_map = dict(zip(entity_df['entity'], entity_df['entityType']))
    edges = []
    
    for sentence in text_corpus:
        words = set(sentence.split())
        sentence_entities = words.intersection(top_entities)
        edges.extend(combinations(sentence_entities, 2))
    
    edge_counts = Counter(edges)
    
    # Calculate total relationships and total entities
    total_relationships = len(edge_counts)  # Total unique relationships (edges)
    total_entities = len(set([e[0] for e in edge_counts]) | set([e[1] for e in edge_counts]))  # Unique entities involved in relationships
    
    relations = []
    
    for (entity1, entity2), frequency in edge_counts.items():
        # Filter by minimum frequency
        if frequency < min_frequency:
            continue
        
        # Filter by entity types
        entity1_type = entity_type_map.get(entity1, 'Unknown')
        entity2_type = entity_type_map.get(entity2, 'Unknown')
        
        if (entity_type_1 != 'All Types' and entity1_type != entity_type_1) or \
           (entity_type_2 != 'All Types' and entity2_type != entity_type_2):
            continue
        
        relations.append({
            'entity1': entity1,
            'entity1_type': entity1_type,
            'relationship': 'Related To',
            'entity2': entity2,
            'entity2_type': entity2_type,
            'frequency': frequency
        })

    return render_template('relationship.html', 
                           relations=relations, 
                           min_frequency=min_frequency,
                           entity_type_1=entity_type_1,
                           entity_type_2=entity_type_2,
                           unique_entity_types=unique_entity_types,
                           total_relationships=total_relationships,
                           total_entities=total_entities)


curr = os.getcwd()
entity_df = pd.read_csv(f'{curr}/datasets/entity_df.csv')
entity_counts = entity_df.groupby(['entity', 'entityType'])['frequency'].sum().reset_index(name='count')
news_data = pd.read_excel(f'{curr}/datasets/input/news_excerpts_parsed.xlsx')['Text'].dropna().tolist()
wikileaks_data = pd.read_excel(f'{curr}/datasets/input/wikileaks_parsed.xlsx')['Text'].dropna().tolist()
text_corpus = news_data + wikileaks_data  
text_corpus = text_corpus[:2000]  # Limit to 1000 sentences for performance
def plot_network(top_k=10):
    top_entities = set(entity_counts.nlargest(top_k, 'count')['entity'])
    entity_type_map = dict(zip(entity_df['entity'], entity_df['entityType']))
    edges = []
    for sentence in text_corpus:
        words = set(sentence.split())
        sentence_entities = words.intersection(top_entities)
        edges.extend(combinations(sentence_entities, 2))
    edge_counts = Counter(edges)
    G = nx.Graph()
    for edge, weight in edge_counts.items():
        G.add_edge(edge[0], edge[1], weight=weight)
    entity_types = list(set(entity_type_map.values()))  # Unique entity types
    color_map = {etype: plt.cm.tab10(i % 10) for i, etype in enumerate(entity_types)}  # Color mapping
    node_colors = [color_map.get(entity_type_map.get(node, ''), 'gray') for node in G.nodes()]
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color=node_colors)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=10)

    # Add legend
    for etype, color in color_map.items():
        plt.scatter([], [], c=[color], label=etype)
    plt.legend(title="Entity Types")

    plt.title("Entity Relationship Network")
    graph_path = os.path.join("static", "images", "entity_network.png")
    plt.savefig(graph_path)
    plt.close()

    return graph_path

@app.route('/knowledgeGraph')
def knowledgeGraph():
    graph_path = plot_network(10)
    return render_template('knowledgeGraph.html', graph_path='/static/images/entity_network.png')

@app.route('/updateGraph', methods=['POST'])
def update_graph():
    top_k = request.json.get('top_k', 10)
    graph_path = plot_network(top_k)
    return {"graph_path": "/static/images/entity_network.png"}


@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')



def query_ai_model(user_message, extracted_text):
    """Send user query + extracted text to AI model."""
    try:
        if not extracted_text:
            prompt = f"{user_message}"
        else:
            prompt = f"""
            User Message: {user_message}

            Attached PDF Content (if none, will be empty, then safely ignore):
            {extracted_text[:1000]}  # Limit text to avoid overloading the model

            Answer concisely based on both inputs.
            """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"
    
@app.route('/ask', methods=['POST'])
def ask():
    """Handle user question + extracted PDF text."""
    data = request.json
    user_message = data.get("message", "")
    extracted_text = data.get("extracted_text", "")

    if not user_message and not extracted_text:
        return jsonify({"error": "No message or extracted text provided"}), 400

    ai_response = query_ai_model(user_message, extracted_text)
    
    return jsonify({"reply": ai_response})

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload & text extraction."""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_path)

        return jsonify({"status": "success", "extracted_text": extracted_text})
    
    return jsonify({"status": "error", "message": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(debug=True)