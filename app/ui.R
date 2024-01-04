library(shiny)
source('src/improve-ui.R')

ui <- fluidPage(
  
  # call CSS style
  tags$head(tags$link(rel = "stylesheet", type = "text/css", href = "style.css")),
  
  titlePanel("Job Recommendation System"),
  sidebarLayout(
    
    div(class = "sidebar", 
      sidebarPanel(
        div(class = "sidebar-content",  
          fileInput("resume", "Upload your resume (PDF only)", accept = ".pdf"),
          textInput("keyword", "Enter keyword(s):", value = "")
        )
      )
    ),
    
    div(class = "main",
      mainPanel(
        h3("Extracted Keywords:"),
        uiOutput("keywordsDisplay"),
        add_space(3), 
        dataTableOutput("table")
      )
    )
  )
)

