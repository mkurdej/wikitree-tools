
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
      if (request == "showPopup")
    	  chrome.pageAction.show(sender.tab.id);
      if (request == "hidePopup")
    	  chrome.pageAction.hide(sender.tab.id);
      sendResponse({});
  });
