keywordCount = function(row, keywords) {
  return(sum(sapply(keywords, function(k) sum(grepl(k, tolower(row))))))
}

