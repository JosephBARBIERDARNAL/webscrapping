library(shiny)
library(DT)
library(dplyr)
source('src/nlp.R')

server <- function(input, output) {
  
  # Sample dataset, replace with your own
  dataset <- read.csv2('../data/job_df.csv', sep = ',')
  dataset= dataset %>%
    select(-c('Job.ID'))
  
  
  output$table <- renderDT({
    keyword <- input$keyword
    # Ensure that keyword input is not NULL or empty
    if (is.null(keyword) || keyword == "") {
      return(datatable(dataset, options = list(pageLength = 5), filter="top"))
    }
    
    # Splitting the keywords for multiple keyword functionality
    keywords <- unlist(strsplit(tolower(keyword), " "))
    if (length(keywords) == 0) {
      return(datatable(dataset, options = list(pageLength = 5)))
    }
    
    # Filtering data based on keyword occurrence
    filtered_data <- dataset[apply(dataset, 1, function(row) keywordCount(row, keywords) >= 2), ]
    print('yes')
    
    # Check if the filtered data is empty or not
    if (nrow(filtered_data) == 0) {
      return(DT::datatable(data.frame(), options = list(pageLength = 5), filter="top"))
    } else {
      return(DT::datatable(filtered_data, options = list(pageLength = 5), filter="top"))
    }
  })
}
