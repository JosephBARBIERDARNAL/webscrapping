library(httr)
library(jsonlite)

GPT = function(
    prompt,
    modelName = "gpt-3.5-turbo",
    temperature = 0.2,
    apiKey = readLines("../apikey.txt")) {
  
  response = POST(
    url = "https://api.openai.com/v1/chat/completions", 
    add_headers(Authorization = paste("Bearer", apiKey)),
    content_type_json(),
    encode = "json",
    body = list(
      model = modelName,
      temperature = temperature,
      messages = list(list(
        role = "user", 
        content = prompt
      ))
    )
  )
  
  # verify that we got a valid answer within our request
  if(status_code(response)>200) {
    stop(content(response))
  }
  return(trimws(content(response)$choices[[1]]$message$content))
}
