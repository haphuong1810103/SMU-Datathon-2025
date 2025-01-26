library(shiny)
library(shinydashboard)
library(ggplot2)
library(readxl)
library(tidyverse)
library(spacyr)
library(tidytext)
library(igraph)
library(ggraph)
library(tidygraph)

# Load and process the data
file_path <- "Dataset/news_excerpts_parsed.xlsx"
data <- read_excel(file_path, col_names = TRUE)
data <- data[1:100, ]
text_corpus <- paste(data$Text, collapse = " ")

# Extract entities and relationships
spacy_initialize(python_executable = "python")
parsed_text <- spacy_parse(text_corpus, entity = TRUE)
entities <- entity_extract(parsed_text)
entities <- entities %>% mutate(entity = tolower(entity))
entity_counts <- entities %>%
  group_by(entity) %>%
  summarize(count = n(), entity_type = first(entity_type)) %>%
  arrange(desc(count))
entity_summary <- entities %>%
  count(entity_type, sort = TRUE) %>%
  mutate(full_name = case_when(
    entity_type == "PERSON" ~ "PERSON",
    entity_type == "ORG" ~ "ORGANIZATION",
    entity_type == "LOC" ~ "LOCATION",
    entity_type == "GPE" ~ "GEOPOLITICAL ENTITY",
    entity_type == "NORP" ~ "NATIONALITIES/\nRELIGIOUS/\nPOLITICAL GROUPS",
    entity_type == "DATE" ~ "DATE",
    TRUE ~ toupper(entity_type)
  ))

# Define UI
ui <- dashboardPage(
  dashboardHeader(title = "Entity Visualization App"),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Entity Counts", tabName = "counts", icon = icon("bar-chart")),
      menuItem("Network Graph", tabName = "graph", icon = icon("project-diagram")),
      menuItem("Linked Entities", tabName = "linked", icon = icon("link"))
    )
  ),
  dashboardBody(
    tabItems(
      # Tab 1: Entity Counts
      tabItem(
        tabName = "counts",
        fluidRow(
          box(
            title = "Entity Types", status = "primary", solidHeader = TRUE, width = 12,
            sliderInput("top_entity_types", "Number of Top Entity Types:",
                        min = 1, max = nrow(entity_summary), value = 10, step = 1),
            plotOutput("entityTypePlot")
          ),
          box(
            title = "Entities", status = "primary", solidHeader = TRUE, width = 12,
            selectInput("filter_type", "Filter by Entity Type:",
                        choices = c("All", unique(entity_summary$full_name)), selected = "All"),
            sliderInput("top_entities", "Number of Top Entities:",
                        min = 1, max = 100, value = 10, step = 1),
            plotOutput("entityPlot")
          )
        )
      ),
      # Tab 2: Network Graph
      tabItem(
        tabName = "graph",
        fluidRow(
          box(
            title = "Network Graph", status = "primary", solidHeader = TRUE, width = 12,
            selectInput("top_k_graph", "Number of Top Entities:",
                        choices = seq(10, 100, 10), selected = 50),
            plotOutput("networkGraph", height = "600px")
          )
        )
      ),
      # Tab 3: Linked Entities
      tabItem(
        tabName = "linked",
        fluidRow(
          box(
            title = "Linked Entities", status = "primary", solidHeader = TRUE, width = 12,
            selectInput("selected_entity", "Select an Entity:", 
                        choices = unique(entity_counts$entity), selected = entity_counts$entity[1]),
            sliderInput("top_linked", "Number of Linked Entities to Show:",
                        min = 1, max = 50, value = 10, step = 1),
            plotOutput("linkedEntityPlot")
          )
        )
      )
    )
  )
)

# Define Server
server <- function(input, output, session) {
  output$entityTypePlot <- renderPlot({
    top_entity_summary <- entity_summary %>%
      slice_max(order_by = n, n = input$top_entity_types)
    ggplot(top_entity_summary, aes(x = reorder(full_name, n), y = n)) +
      geom_bar(stat = "identity", fill = "steelblue") +
      coord_flip() +
      labs(title = "Top Entity Types", x = "Entity Type", y = "Frequency") +
      theme_bw()
  })
  
  output$entityPlot <- renderPlot({
    filtered_entities <- if (input$filter_type == "All") {
      entity_counts
    } else {
      entity_counts %>% filter(entity_type == entity_summary$entity_type[entity_summary$full_name == input$filter_type])
    }
    top_entities <- filtered_entities %>%
      slice_max(order_by = count, n = input$top_entities)
    ggplot(top_entities, aes(x = reorder(entity, count), y = count, fill = entity_type)) +
      geom_bar(stat = "identity") +
      coord_flip() +
      labs(title = "Top Entities", x = "Entity", y = "Frequency", fill = "Entity Type") +
      scale_fill_viridis_d() +
      theme_bw()
  })
  
  output$networkGraph <- renderPlot({
    K <- as.numeric(input$top_k_graph)
    top_entities <- entity_counts %>% slice_max(order_by = count, n = K)
    filtered_entities <- entities %>% filter(entity %in% top_entities$entity)
    
    # Build Relationships
    sentences <- unnest_tokens(data.frame(text = text_corpus), word, text, token = "sentences")
    sentence_entities <- sentences %>%
      mutate(sentence_id = row_number()) %>%
      left_join(filtered_entities, by = c("sentence_id" = "sentence_id")) %>%
      group_by(sentence_id) %>%
      filter(!is.na(entity)) %>%
      mutate(entity = str_c(entity, "_*_", entity_type)) %>%
      summarize(entities_in_sentence = list(entity))
    
    edges <- sentence_entities %>%
      filter(lengths(entities_in_sentence) >= 2) %>%
      rowwise() %>%
      mutate(entity_pairs = list(combn(entities_in_sentence, 2, simplify = FALSE))) %>%
      unnest(entity_pairs)
    
    edges$from <- sapply(edges$entity_pairs, "[[", 1)
    edges$to <- sapply(edges$entity_pairs, "[[", 2)
    edges <- edges %>% distinct(from, to) %>% filter(from != to)
    
    graph <- as_tbl_graph(edges, directed = FALSE)
    node_data <- graph %>% activate(nodes) %>% as_tibble()
    node_data <- node_data %>% separate(name, into = c("name", "type"), sep = "_\\*_")
    graph <- graph %>% activate(nodes) %>% mutate(name = node_data$name, type = node_data$type)
    
    ggraph(graph, layout = "circle") +
      geom_edge_link(aes(edge_alpha = 0.8), show.legend = FALSE) +
      geom_node_point(aes(color = type), size = 5) +
      geom_node_text(aes(label = name,
                         angle = ifelse(x >= 0, asin(y) * 360 / 2 / pi, 360 - asin(y) * 360 / 2 / pi),
                         hjust = ifelse(x >= 0, 0, 1)), size = 3) +
      theme_void()
  })
  
  output$linkedEntityPlot <- renderPlot({
    selected_entity <- input$selected_entity
    
    sentences <- unnest_tokens(data.frame(text = text_corpus), word, text, token = "sentences")
    sentence_entities <- sentences %>%
      mutate(sentence_id = row_number()) %>%
      left_join(entities, by = c("sentence_id" = "sentence_id")) %>%
      group_by(sentence_id) %>%
      filter(!is.na(entity)) %>%
      summarize(entities_in_sentence = list(entity))
    
    edges <- sentence_entities %>%
      filter(lengths(entities_in_sentence) >= 2) %>%
      rowwise() %>%
      mutate(entity_pairs = list(combn(entities_in_sentence, 2, simplify = FALSE))) %>%
      unnest(entity_pairs)
    
    edges$from <- sapply(edges$entity_pairs, "[[", 1)
    edges$to <- sapply(edges$entity_pairs, "[[", 2)
    edges = edges %>% select(from, to) %>%
      filter(from == selected_entity | to == selected_entity)
    linked_entities = tibble(entity_linked = c(edges$from, edges$to)) %>%
      count(entity_linked) %>% filter(entity_linked != selected_entity) %>%
      slice_max(order_by = n, n = input$top_linked, with_ties = FALSE)
    
    ggplot(linked_entities, aes(x = reorder(entity_linked, n), y = n)) +
      geom_bar(stat = "identity", fill = "darkorange") +
      coord_flip() +
      labs(title = paste("Entities Linked to", selected_entity),
           x = "Linked Entity", y = "Frequency") +
      theme_bw()
  })
  
  # Cleanup Spacy when session ends
  session$onSessionEnded(function() {
    spacy_finalize()
  })
}

# Run the app
shinyApp(ui, server)