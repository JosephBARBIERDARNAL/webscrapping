library(shiny)
library(shinyjs)
library(DT)
library(dplyr)
library(pdftools)
source('src/nlp.R')
source('src/cover_letter.R')

server = function(input, output) {
  
  # open dataset
  dataset = read.csv2('www/all_jobs.csv', sep = ',')
  dataset$Title <- sprintf('<a href="%s" target="_blank">%s</a>', dataset$Url, dataset$Title)
  dataset = dataset %>% select(-c(Keyword, Site, Url))
  sampled_rows = sample(nrow(dataset), 100)
  dataset = dataset[sampled_rows, ]
  dataset$Description = substr(dataset$Description, 1, 300)

  # extract keywords from resume
  resumeKeywords = reactive({
    req(input$resume)
    extractKeywordsFromResume(input$resume$datapath)
  })

  
  # render keywords (dev)
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

    # filter dataset to include rows containing all keywords in the Description
    filtered_data <- dataset %>%
      filter(sapply(tolower(Description), function(description) all(sapply(keywordInput, function(keyword) grepl(keyword, description)))))

    # count and sort data based on keyword matches
    filtered_data$keywordMatchCount <- apply(filtered_data, 1, function(row) keywordCount(tolower(row), allKeywords))
    sorted_data <- filtered_data[order(-filtered_data$keywordMatchCount), ]

    # display data if there are matches
    if (nrow(sorted_data) == 0 || max(sorted_data$keywordMatchCount) == 0) {
      table_to_display <- data.frame()
    } else {
      table_to_display <- sorted_data %>% select(-c(Job.ID, keywordMatchCount))
    }

    # display the DT table
    return(DT::datatable(
        table_to_display,
        options = list(pageLength = 5,
                       scrollX = TRUE,
                       columnDefs = list(list(
                         targets = "_all",
                         className = "dt-center"),
                         
                         # width for the columns
                         list(width = '1px', targets = 0), # index
                         list(width = '120px', targets = 1), # title
                         list(width = '100px', targets = 2), # company
                         list(width = '40px', targets = 3), # location
                         list(width = '250px', targets = 4)), # company
                       autoWidth = TRUE),
        filter="top",
        class="cell-border stripe hover",
        selection="single",
        escape=FALSE) %>% formatStyle(columns = c('Title'), `cursor` = 'pointer')
      )
  })
  
  # observe event for the 'Generate Cover Letter' button click
  observeEvent(input$generate_cover_letter, {
    
    # ensure there's a selected job and a resume uploaded
    if (!is.null(input$resume) && !is.null(input$table_rows_selected)) {
      
      # start spinner
      shinyjs::runjs('$("#spinner").removeClass("hidden");')
      
      # extract the path to the uploaded resume
      resume_path = input$resume$datapath
      resume = pdf_text(resume_path)
      
      # find the row selected by the user
      selectedRowIndex = input$table_rows_selected
      jobDescription = dataset[selectedRowIndex, ]$Description
      
      # call the OpenAI API to generate a cover letter and output it
      prompt = paste('Write a cover letter for the following resume and job: ',
                     resume,
                     jobDescription)
      coverLetter = GPT(prompt)
      
      # hide spinner after operation is done
      shinyjs::runjs('$("#spinner").addClass("hidden");')
      
      output$coverLetterDisplay = renderText({
        paste(coverLetter, collapse = "\n")
      })
      
    # message for the user when no job selected
    } else {
      output$coverLetterDisplay = renderText(
        'Upload a resume and select a job before trying to generate a cover letter.'
      )
    }
  })
}
