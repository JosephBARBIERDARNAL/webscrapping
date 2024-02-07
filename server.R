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
    req(isTruthy(input$resume) | isTruthy(input$keyword))
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


  
  
  
  # DEFINE TABLE TO RENDER
  output$table <- renderDT({

    req(input$search_jobs)

    # filter and sort data
    dataset_filtered = filter_and_sort(dataset, combinedKeywords())
    table_to_display = dataset_filtered %>% select(-c(Job.ID, keywordMatchCount, Description, title, Url))
    
    # keep first n rows
    table_to_display = table_to_display[1:n, ]
    table_to_display$Date = as.Date(table_to_display$Date, format = "%Y/%m/%d")
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
        escape=FALSE,
        filter='top')
      )
  })
  
  
  
  
  
  
  # GENERATE COVER LETTER WITH GPT
  observeEvent(input$generate_cover_letter_modal, {

    display = TRUE

    # show spinner while operation is running
    shinyjs::runjs('$("#spinnertwo").removeClass("hidden");')

    # filter and sort data
    dataset_filtered = filter_and_sort(dataset, combinedKeywords())
    dataset_filtered = dataset_filtered %>% select(-c(Job.ID))
    jobDescription = dataset_filtered[input$table_rows_selected, ]$Description
    jobTitle = dataset_filtered[input$table_rows_selected, ]$title
      
    # extract the path to the uploaded resume
    resume_path = input$resume$datapath
    resume = pdf_text(resume_path)
      
    # call the OpenAI API to generate a cover letter and output it
    prompt = paste('Write a cover letter using the following resume and job: ',
                   'Resume info: ', resume, '        ',
                   'Job info: ', paste(jobTitle, 'at', jobDescription))
    coverLetter = GPT(prompt)
      
    # hide spinner after operation is done
    shinyjs::runjs('$("#spinnertwo").addClass("hidden");')
      
    # output cover letter
    output$coverLetterDisplay = renderText({
      paste(coverLetter, collapse = "\n")
    })

  })





  # CONTRACT FILTER
  output$contract_filter <- renderUI({
    selectInput("contract",
                "Choose Contracts:",
                choices = unique(data()$Contract),
                selected = unique(data()$Contract), # select all by default
                multiple = TRUE)
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
      title = paste(row_data$title, 'at', row_data$Company),

      # display description
      actionButton("toggle_desc", "Display Description", class = "btn-primary"),
      div(id = "job_description", style = "display: none;", description_with_br),
      br(), br(),

      # display contract type
      'Contract type:', br(), row_data$Contract,
      br(), br(),
      
      # display location
      'Location:', br(), row_data$Location,
      br(), br(),
      
      # display salary
      'Salary:', br(), display_salary(row_data$Salary),
      br(), br(),

      footer = tagList(
        # display apply button
        div(class = "apply-button-container", actionButton("apply_job", "Apply to this Job", class = "btn-primary")),
        tags$script(HTML(paste0("$('#apply_job').on('click', function() {
          window.open('", row_data$Url, "', '_blank');});"))),
        div(id = "spinnertwo", class = "spinnertwo hidden"),
        actionButton("generate_cover_letter_modal", "Generate Cover Letter for this Job", class = "btn-primary",
                onclick="document.getElementById('spinnertwo').classList.remove('hidden');"),
        verbatimTextOutput("coverLetterDisplay", placeholder = TRUE),
        div(class = "copy-container", actionButton("copyBtn", label = "Copy the text", class = "copy-btn", onclick = "copyToClipboard()"))
      ),
      easyClose = TRUE
    ))
  }) 
}





