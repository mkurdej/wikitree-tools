
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
      console.log(request);
      wt_data = request;
      chrome.pageAction.show(sender.tab.id);
      sendResponse({});
  });
