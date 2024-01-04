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
      return(paste("Keywords: ", paste(keywords, collapse = ", ")))
    }
  })
  
  output$table <- renderDT({
    keywordInput <- input$keyword
    resumeKeywords <- resumeKeywords()
    keywords <- unique(c(unlist(strsplit(tolower(keywordInput), " ")), resumeKeywords))
    
    # Filtering data based on keyword occurrence
    filtered_data <- dataset[apply(dataset, 1, function(row) keywordCount(row, keywords) >= 2), ]
    
    # Check if the filtered data is empty or not
    if (nrow(filtered_data) == 0) {
      return(DT::datatable(data.frame(), options = list(pageLength = 5), filter="top"))
    } else {
      return(DT::datatable(filtered_data, options = list(pageLength = 5), filter="top"))
    }
  })
}
