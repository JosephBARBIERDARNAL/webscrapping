source('src/nlp.R')

filter_and_sort = function(dataset, allKeywords) {
  
  # function to count keyword matches in a row
  keywordCount = function(row, keywords) {
    sum(sapply(keywords, function(keyword) grepl(keyword, tolower(paste(row[["Description"]], row[["Title"]])))))
  }

  # apply keyword match counting and sort
  dataset$keywordMatchCount = apply(dataset, 1, function(row) keywordCount(row, allKeywords))
  sorted_data = dataset[order(-dataset$keywordMatchCount), ]
  return(sorted_data)
}
