# function to filter and sort dataframe since it's not dynamic by default
filter_and_sort = function(dataset, keywordInput, resumeKeywords) {
  
  # filter dataset to include rows containing all keywords in the Description
  allKeywords = unique(c(unlist(strsplit(tolower(keywordInput), " ")), resumeKeywords))
  filtered_data = dataset %>%
    filter(sapply(tolower(Description), function(description) all(sapply(keywordInput, function(keyword) grepl(keyword, description)))))
  
  # count and sort data based on keyword matches
  filtered_data$keywordMatchCount = apply(filtered_data, 1, function(row) keywordCount(tolower(row), allKeywords))
  sorted_data = filtered_data[order(-filtered_data$keywordMatchCount), ]
  return(sorted_data)
}