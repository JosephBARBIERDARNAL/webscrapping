library(shiny)
library(shinyjs)
library(DT)
library(dplyr)
library(pdftools)
source('src/nlp.R')
source('src/cover_letter.R')
source('src/dynamic_sort.R')



server = function(input, output, session) {

  options(shinyjs.debug = TRUE)
  
  # OPEN AND CLEAN DATASET
  dataset = read.csv2('www/all_jobs.csv', sep = ',')
  dataset$title = dataset$Title
  dataset$Title = sprintf('<a href="%s" target="_blank">%s</a>', dataset$Url, dataset$title)
  dataset = dataset %>% select(-c(Keyword, Site))
  n = 100
  dataset = dataset[sample(nrow(dataset), n), ]

  


  resumeKeywords <- reactiveVal()
  inputKeywords <- reactiveVal()


  # LANGUAGE SELECTION (RADIO BUTTON)
  observe({
    if (input$language == "fr") {
      updateSelectInput(session, "keywordSelect", 
                        choices = removeStopwords(resumeKeywords(), "fr"), 
                        selected = removeStopwords(resumeKeywords(), "fr"))
    } else {
      updateSelectInput(session, "keywordSelect", 
                        choices = removeStopwords(resumeKeywords(), "en"), 
                        selected = removeStopwords(resumeKeywords(), "en"))
    }    
  })



   


  
  # FIND KEYWORDS IN RESUME
  resumeKeywords <- reactive({
    req(input$resume)
    resume <- pdf_text(input$resume$datapath)
    keywords <- extractKeywords(resume)
    keywords <- removeStopwords(keywords, input$language)
    return(keywords)
  })  
  # FIND KEYWORDS FROM USER INPUT
  inputKeywords  <- reactive({
  if(is.null(input$keyword) || input$keyword == ""){
    return(character(0))
  } else {
    return(unlist(strsplit(tolower(input$keyword), " ", fixed = TRUE)))
  }
  })
  # UPDATE SELECT INPUT
  observe({
    keywords_resume <- resumeKeywords()
    keywords_input <- inputKeywords()
    keywords <- unique(c(keywords_resume, keywords_input))
    keywords <- removeStopwords(keywords, input$language)
    updateSelectInput(session, "keywordSelect", 
                      choices = keywords, 
                      selected = keywords)
  })
  
  combinedKeywords <- reactive({
    c(resumeKeywords(), inputKeywords()) %>%
      unique() %>%
      removeStopwords(input$language)
  })

  observeEvent(input$search_jobs, {
    shinyjs::runjs('$("#spinner").removeClass("hidden");')
    updateSelectInput(session, "keywordSelect", choices = combinedKeywords(), selected = combinedKeywords())
  })

  dataset_filtered <- reactive({
    req(combinedKeywords())
    filter_and_sort(dataset, combinedKeywords())
  })
  
  
  
  
  
  # TOGGLE DESCRIPTION HIDE/DISPLAY
  observeEvent(input$toggle_desc, {
    shinyjs::runjs('
    if ($("#toggle_desc").text() === "Display Description") {
      $("#toggle_desc").text("Hide Description");
      $("#job_description").show();
    } else {
      $("#toggle_desc").text("Display Description");
      $("#job_description").hide();
    }
  ')
  })




  output$keywordsUI <- renderUI({
    if (!is.null(input$resume)) {
      fluidRow(
        div(class = "main",
        includeCSS("www/style.css"),
        h2("Keywords From Your Resume:"),
        selectInput("keywordSelect", "", choices = NULL, multiple = TRUE)
      ))
    }
  })
  output$matchesUI <- renderUI({
    req(input$search_jobs)
    if (!is.null(input$resume)) {
      fluidRow(
        div(class = "main",
        includeCSS("www/style.css"),
        h2("Best Job Matches:"),
        div(class = "job-table", dataTableOutput("table"))
      ))
    }
  })


  
  
  
  # DEFINE TABLE TO RENDER
  output$table <- renderDT({

    req(input$search_jobs)
    # filter and sort data
    dataset_filtered = filter_and_sort(dataset, combinedKeywords())
    table_to_display = dataset_filtered %>% select(-c(Job.ID, keywordMatchCount, Description, title, Url))
    
    # keep first n rows
    table_to_display = table_to_display[1:n, ]
    shinyjs::runjs('$("#spinner").addClass("hidden");')

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
        class="cell-border stripe hover",
        selection="single",
        escape=FALSE)
      )
  })
  
  
  
  
  
  
  # GENERATE COVER LETTER WITH GPT
  observeEvent(input$generate_cover_letter_modal, {

    # ensure there's a selected job and a resume uploaded
    if (!is.null(input$resume) && !is.null(input$table_rows_selected)) {

      # show spinner while operation is running
      shinyjs::runjs('$("#spinner").removeClass("hidden");')

      # filter and sort data
      dataset_filtered = filter_and_sort(dataset, combinedKeywords())
      dataset_filtered = dataset_filtered %>% select(-c(Job.ID))
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








  # POP UP WINDOW
  observeEvent(input$table_rows_selected, {
    
    # select row
    dataset_filtered = filter_and_sort(dataset, combinedKeywords())
    row_data = dataset_filtered[input$table_rows_selected, ]
    
    # empty cover letter at first
    output$coverLetterDisplay = renderText(NULL)

    # display description with line breaks
    description_with_br = gsub("\n", "<br>", HTML(row_data$Description))
     
    showModal(modalDialog(
      title = paste0(row_data$title, ' at ', row_data$Company),

      # display description
      actionButton("toggle_desc", "Display Description", class = "btn-primary"),
      div(id = "job_description", style = "display: none;", description_with_br),
      br(), br(),
      
      # display location
      'Location:', br(), row_data$Location,
      br(), br(),
      
      # display salary
      'Salary:', br(), display_salary(row_data$Salary),
      br(), br(),

      # display apply button
      div(class = "apply-button-container", actionButton("apply_job", "Apply for this Job", class = "btn-primary")),
        tags$script(HTML(paste0("$('#apply_job').on('click', function() {
          window.open('", row_data$Url, "', '_blank');});"))),

      footer = tagList(
        div(id = "spinner",
            class = "spinner hidden",
            actionButton("generate_cover_letter_modal",
                        "Generate Cover Letter for this Job",
                        class = "btn-primary")),
        verbatimTextOutput("coverLetterDisplay", placeholder = TRUE),
        div(class = "copy-container", actionButton("copyBtn", label = "Copy the text", class = "copy-btn", onclick = "copyToClipboard()")),
      ),
      easyClose = TRUE
    ))
  })
  
}





