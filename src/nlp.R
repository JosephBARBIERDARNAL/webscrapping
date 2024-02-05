
library(pdftools)
extractKeywords = function(resume) {
  words = unlist(strsplit(resume, "\\W"))
  words = tolower(words[words != ""])
  words = words[!grepl("[0-9]", words)]
  freq = sort(table(words), decreasing = TRUE)
  keywords = names(freq[freq >= 2])
  return(keywords)
}


library(stopwords)
removeStopwords <- function(words, language = "en") {
  return(words[!words %in% stopwords(language)])
}


keywordCount = function(row, keywords) {
  return(sum(sapply(keywords, function(k) sum(grepl(k, tolower(row))))))
}


display_salary = function(string) {
  if (grepl("\\d", string)){
    return(string)
  } else {
    return('Not found.')
  }
}

