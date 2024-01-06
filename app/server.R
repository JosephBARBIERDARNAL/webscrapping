library(shiny)
library(DT)
library(dplyr)
source('src/nlp.R')

server <- function(input, output) {
  
  # Open dataset
  dataset <- read.csv2('../data/job_df.csv', sep = ',')
  dataset <- dataset %>% select(-c('Job.ID'))

  # Extract keywords from resume
  resumeKeywords <- reactive({
    req(input$resume)
    extractKeywordsFromResume(input$resume$datapath)
  })
  
  # Render keywords
  output$keywordsDisplay <- renderUI({
    keywords <- resumeKeywords()
    if (is.null(keywords)) {
      return("No keywords extracted or resume not uploaded.")
    } else {
      keywords <- removeStopwords(keywords, language = "fr")
      return(paste(keywords, collapse = ", "))
    }
  })
  
  output$table <- renderDT({
    keywordInput <- input$keyword
    resumeKeywords <- resumeKeywords()
    allKeywords <- unique(c(unlist(strsplit(tolower(keywordInput), " ")), resumeKeywords))

    # Filter dataset to include rows containing all keywords in the Description
    filtered_data <- dataset %>%
      filter(sapply(tolower(Description), function(description) all(sapply(keywordInput, function(keyword) grepl(keyword, description)))))

    # Count and sort data based on keyword matches
    filtered_data$keywordMatchCount <- apply(filtered_data, 1, function(row) keywordCount(tolower(row), allKeywords))
    sorted_data <- filtered_data[order(-filtered_data$keywordMatchCount), ]

    # Display data if there are matches
    if (nrow(sorted_data) == 0 || max(sorted_data$keywordMatchCount) == 0) {
      table_to_display <- data.frame()
    } else {
      table_to_display <- sorted_data
    }

    # Display the DT table
    return(DT::datatable(
        table_to_display,
        options = list(pageLength = 5),
        filter="top",
        class="cell-border stripe hover",
        selection="single"))
  })
}
