library(shiny)
source('src/improve-ui.R')

ui <- navbarPage("Job Recommendation System",
  
  # Include CSS Style
  tags$head(tags$link(rel = "stylesheet", type = "text/css", href = "style.css")),

  # Home Page
  tabPanel("Home", tabName = "tabs",
    div(class = "home",
      div(class = "home-title", h1("Welcome to the Job Recommendation System")),
      hr(),
      add_space(3),
      div(class = "home-description",
        p("This system helps you find job opportunities based on your resume and keywords. 
          Upload your resume and enter relevant keywords to discover job matches."),
        p("The system will extract keywords from your resume and search for jobs that match those keywords."),
        add_space(3),
        p("This project was realized by Joseph Barbier, Judic Erwan, Lacoste Victor and Komla Djodji Adayeke. You can
        find the source code on this ", a("GitHub repo", href="https://github.com/JosephBARBIERDARNAL/webscrapping",
        target="_blank") ,".")
        )
      ) 
    ),
  
  # Job Search Tool Page
  tabPanel("Job Search Tool", tabName = "tabs",
    sidebarLayout(
      div(class = "sidebar", 
        sidebarPanel(
          div(class = "sidebar-content",  
            div(class = "resume-upload", fileInput("resume", "Upload your resume (PDF only)", accept = ".pdf")),
            div(class = "keyword-input", textInput("keyword", "Enter keyword(s) (separated by space):", value = "")),
            div(class = "keywords-search-output", uiOutput("keywordsSearch"))
          )
        )
      ),
        
      div(class = "main",
        mainPanel(
          h2("Extracted Keywords:"),
          add_space(1),
          div(class = "keywords-display-output", uiOutput("keywordsDisplay")),
          add_space(3), 
          h2("Best job matches:"),
          add_space(1),
          div(class = "job-table", dataTableOutput("table"))
        )
      )
    )
  )
)
