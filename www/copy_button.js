function copyToClipboard() {

  // get the text from the cover letter
  var text = document.getElementById('coverLetterDisplay').innerText; 
  navigator.clipboard.writeText(text).then(function() {

    // update the button label
    document.getElementById('copyBtn').innerText = 'Copied!'; 
    
    // change back after 2 seconds
    setTimeout(function() {
      document.getElementById('copyBtn').innerText = 'Copy';
    }, 2000);

  // log error
  }, function(err) {
    console.error('Could not copy text: ', err);
  });
}
