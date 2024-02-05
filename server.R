library(shiny)
library(shinyjs)
library(DT)
library(dplyr)
library(pdftools)
source('src/nlp.R')
source('src/improve_ui.R')
source('src/cover_letter.R')

server = function(input, output) {
  
  
  
  
  # OPEN AND CLEAN DATASET
  dataset = read.csv2('www/all_jobs.csv', sep = ',')
  dataset$title = dataset$Title
  dataset$Title = sprintf('<a href="%s" target="_blank">%s</a>', dataset$Url, dataset$title)
  dataset = dataset %>% select(-c(Keyword, Site, Url))
  sampled_rows = sample(nrow(dataset), 10)
  dataset = dataset[sampled_rows, ]

  
  
  
  # FIND KEYWORDS IN RESUME
  resumeKeywords = reactive({
    req(input$resume)
    resume = pdf_text(input$resume$datapath)
    extractKeywords(resume)
  })
  # DISPLAY KEYWORDS FOUND IN RESUME
  output$keywordsDisplay <- renderUI({
    keywords <- resumeKeywords()
    if (is.null(keywords)) {
      return("No keywords extracted or resume not uploaded.")
    } else {
      keywords <- removeStopwords(keywords, language = "fr")
      return(paste(keywords, collapse = ", "))
    }
  })
  
  
  
  
  # POP UP WINDOW
  observeEvent(input$table_rows_selected, {
    
    ##############################################################################################################
    # re-filter dataset 
    keywordInput <- input$keyword
    resumeKeywords <- resumeKeywords()
    allKeywords <- unique(c(unlist(strsplit(tolower(keywordInput), " ")), resumeKeywords))
    filtered_data = dataset %>%
      filter(sapply(tolower(Description), function(description) all(sapply(keywordInput, function(keyword) grepl(keyword, description)))))
    filtered_data$keywordMatchCount = apply(filtered_data, 1, function(row) keywordCount(tolower(row), allKeywords))
    sorted_data = filtered_data[order(-filtered_data$keywordMatchCount), ]
    ##############################################################################################################
    
    # select row
    dataset_filtered = sorted_data %>% select(-c(Job.ID))
    row_data = dataset_filtered[input$table_rows_selected, ]
    
    # empty cover letter at first
    output$coverLetterDisplay = renderText(NULL)
     
    showModal(modalDialog(
      title = paste0(row_data$title, ' at ', row_data$Company),
      
      # display location
      'Location:', br(), row_data$Location,
      br(), br(),
      
      # display description
      'Description:', br(), row_data$Description,
      br(), br(),
      
      # display salary
      'Salary:', br(), display_salary(row_data$Salary),
      br(), br(),

      footer = tagList(
        div(id = "spinner", class = "spinner hidden"),
        actionButton("generate_cover_letter_modal", "Generate Cover Letter For This Job", class = "btn-primary"),
        verbatimTextOutput("coverLetterDisplay", placeholder = TRUE),
        div(class = "copy-container", actionButton("copyBtn", label = "Copy the text", class = "copy-btn", onclick = "copyToClipboard()")),
      ),
      easyClose = TRUE
    ))
  })
  
  
  
  
  # DEFINE TABLE TO RENDER
  output$table <- renderDT({
    keywordInput <- input$keyword
    resumeKeywords <- resumeKeywords()
    allKeywords <- unique(c(unlist(strsplit(tolower(keywordInput), " ")), resumeKeywords))

    # filter dataset to include rows containing all keywords in the Description
    filtered_data = dataset %>%
      filter(sapply(tolower(Description), function(description) all(sapply(keywordInput, function(keyword) grepl(keyword, description)))))

    # count and sort data based on keyword matches
    filtered_data$keywordMatchCount = apply(filtered_data, 1, function(row) keywordCount(tolower(row), allKeywords))
    sorted_data = filtered_data[order(-filtered_data$keywordMatchCount), ]

    # display data 
    table_to_display = sorted_data %>% select(-c(Job.ID, keywordMatchCount, Description, title))

    # display the DT table
    return(DT::datatable(
        table_to_display,
        options = list(pageLength = 10,
                       scrollX = TRUE,
                       columnDefs = list(list(
                         targets = "_all",
                         className = "dt-center"),
                         
                         # width for the columns
                         list(width = '1px', targets = 0), 
                         list(width = '120px', targets = 1), 
                         list(width = '100px', targets = 2), 
                         list(width = '120px', targets = 3), 
                         list(width = '100px', targets = 4)), 
                       autoWidth = TRUE),
        filter="top",
        class="cell-border stripe hover",
        selection="single",
        escape=FALSE) #%>% formatStyle(columns = c('Title'), `cursor` = 'pointer')
      )
  })
  
  
  
  
  
  
  # GENERATE COVER LETTER WITH GPT
  observeEvent(input$generate_cover_letter_modal, {
    
    # ensure there's a selected job and a resume uploaded
    if (!is.null(input$resume) && !is.null(input$table_rows_selected)) {
      
      # start spinner
      shinyjs::runjs('$("#spinner").removeClass("hidden");')
      
      
      ##############################################################################################################
      keywordInput <- input$keyword
      resumeKeywords <- resumeKeywords()
      allKeywords <- unique(c(unlist(strsplit(tolower(keywordInput), " ")), resumeKeywords))
      filtered_data = dataset %>%
        filter(sapply(tolower(Description), function(description) all(sapply(keywordInput, function(keyword) grepl(keyword, description)))))
      filtered_data$keywordMatchCount = apply(filtered_data, 1, function(row) keywordCount(tolower(row), allKeywords))
      sorted_data = filtered_data[order(-filtered_data$keywordMatchCount), ]
      ##############################################################################################################
      
      # select row
      dataset_filtered = sorted_data %>% select(-c(Job.ID))
      jobDescription = dataset_filtered[input$table_rows_selected, ]$Description
      
      # extract the path to the uploaded resume
      resume_path = input$resume$datapath
      resume = pdf_text(resume_path)
      
      # call the OpenAI API to generate a cover letter and output it
      prompt = paste('Write a cover letter using the following resume and job: ',
                     'Resume info: ', resume, '        ',
                     'Job info: ', jobDescription)
      coverLetter = GPT(prompt)
      
      # hide spinner after operation is done
      shinyjs::runjs('$("#spinner").addClass("hidden");')
      
      # output cover letter
      output$coverLetterDisplay = renderText({
        paste(coverLetter, collapse = "\n")
      })
      
    # message for the user when no job selected
    } else {
      output$coverLetterDisplay = renderText(
        'Something went wrong. Please try again later.'
      )
    }
  })
}
