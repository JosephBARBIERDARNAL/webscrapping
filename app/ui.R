library(shiny)

ui <- fluidPage(
  
  # call CSS style
  tags$head(tags$link(rel = "stylesheet", type = "text/css", href = "style.css")),
  
  titlePanel("Keyword Search in Dataset"),
  sidebarLayout(
    sidebarPanel(
      textInput("keyword", "Enter keyword(s):", value = "")
    ),
    mainPanel(
      dataTableOutput("table")
    )
  )
)

