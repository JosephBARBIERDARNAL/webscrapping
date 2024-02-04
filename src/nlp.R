
library(pdftools)
extractKeywordsFromResume <- function(resumePath) {
  if (is.null(resumePath)) {
    return(NULL)
  }

  pdf_text <- pdf_text(resumePath)
  words <- unlist(strsplit(pdf_text, "\\W"))
  words <- tolower(words[words != ""])
  freq <- sort(table(words), decreasing = TRUE)
  keywords <- names(freq[freq >= 2])

  return(keywords)
}

library(stopwords)
removeStopwords <- function(words, language = "en") {
  return(words[!words %in% stopwords(language)])
}

keywordCount = function(row, keywords) {
  return(sum(sapply(keywords, function(k) sum(grepl(k, tolower(row))))))
}

