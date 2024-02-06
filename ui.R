

library(shiny)
library(shinyjs)
source('src/improve_ui.R')

ui = fluidPage(
  
    navbarPage("Job Recommendation System",
    
    # include CSS and JS 
    tags$head(tags$link(rel = "stylesheet", type = "text/css", href = "style.css"),
              tags$script(src = "copy_button.js")),
    
    # enable shiny JS
    shinyjs::useShinyjs(),
  
    # home page with project description
    tabPanel("Home", tabName = "tabs",
      div(class = "home",
        div(class = "home-title", h1("Welcome to the Job Recommendation System")),
        hr(),
        add_space(1),
        div(class = "home-description",
          h2("About"),
          p("This system helps you find job opportunities based on your resume and keywords. 
            Upload your resume and enter relevant keywords to discover job matches."),
          p("The system will extract keywords from your resume and search for jobs that match those keywords."),
          p("This project was realized by Lacoste Victor, Judic Erwan, Joseph Barbier and Komla Djodji Adayeke. You can
          find the source code on this ", a("GitHub repo", href="https://github.com/JosephBARBIERDARNAL/webscrapping",
          target="_blank") ,"."),
          add_space(3),
          h2("How it works?"),
          p("By uploading a CV, the system returns the job offers that match you best. The algorithm in the background
            locates the most important words in your CV and sorts the offers whose description has the highest number of words in common."),
          p("What's more, it's also possible to automatically generate a cover letter for the job offer of your choice,
            totally individualized. This is powered by the OpenAI API and their GPT-3.5-turbo. As there are no dedicated tools with R for this type of use, we make the HTTP request ourselves to access the API and retrieve the model response. ")
          )
        ) 
      ),
    
    # Job Search Tool Page
    tabPanel("Job Search Tool", tabName = "tabs",
      sidebarLayout(
        div(class = "sidebar", 
          sidebarPanel(width=3,
            div(class = "sidebar-content",  
              div(class = "resume-upload", fileInput("resume", "Upload your resume (PDF only)", accept = ".pdf")),
              div(class = "keyword-input", textInput("keyword", "Enter keyword(s) (separated by space):", value = "")),
              div(class = "keywords-search-output", uiOutput("keywordsSearch"))
            )
          )
        ),
          
        div(class = "main",
          mainPanel(width=8,
            h2("Extracted Keywords:"),
            add_space(1),
            div(class = "keywords-display-output", uiOutput("keywordsDisplay")),
            add_space(3), 
            h2("Best job matches:"),
            add_space(1),
            div(class = "job-table", dataTableOutput("table")),
            add_space(10)
          )
        )
      )
    ),
    tags$footer(
      add_space(10),
      div(class = "footer-content",
          p("Job Recommendation System - Web Scraping and Shiny web application")
      )
    )
  )
)