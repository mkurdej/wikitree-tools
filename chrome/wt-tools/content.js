

parseItem = function(element){
    var ret = {};
    var items = element.find("[itemscope]")
    var subitems = items.find("[itemprop]")
    
    element.find("[itemprop]").not(subitems).each(function(index){
        var $this = $(this)
        var name = $this.attr("itemprop");
        if(ret[name] == undefined)
            ret[name] = [];
        if($this.attr("itemscope") != undefined){
            ret[name].push(parseItem($this));
        } else {
            if(this.nodeName == "META"){
                ret[name].push($this.attr("content"));
            } else if (this.nodeName == "TIME"){
                ret[name].push($this.attr("datetime"));
            } else if (this.nodeName == "A" || this.nodeName == "LINK"){
                ret[name].push($this.attr("href"));
            } else{
                ret[name].push($this.html());
            }
        }
    });
    return ret;
}


scan = function(){

    
    var $person = $("html[itemscope][itemtype='http://schema.org/Person']");

    if($person.length){
        var data = parseItem($person);
        
        chrome.runtime.sendMessage({person:data});
    }
}

scan();