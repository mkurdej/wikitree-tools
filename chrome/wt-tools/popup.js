



$(document).ready( function(){
	$("#showToolsButton").click(function(){
		chrome.tabs.query({active: true, currentWindow: true},function(tabs){
			chrome.tabs.sendMessage(tabs[0].id,"showStatus");
			window.close();
		});
	});
	
	chrome.tabs.query({active: true, currentWindow: true},function(tabs){
		chrome.tabs.sendMessage(tabs[0].id,"showStatus");
		window.close();
	});

});
