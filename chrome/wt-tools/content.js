
tablify = function(value){
    var ret = $("<table>");
    for(var i in value){
        for(var j = 0; j < value[i].length; j++){
            var row = $("<tr>");
            var data = $("<td>");
            data.html(i);
            row.append(data);
            data = $("<td>");
            if(typeof value[i][j] == "string"){
                data.html(value[i][j]);
            } else {
                data.append(tablify(value[i][j]));
            }
            row.append(data);
            ret.append(row);
        }
    }
    return ret;
};


parseItem = function(element){
    var ret = {};
    var items = element.find("[itemscope]");
    var subitems = items.find("[itemprop]");
    
    element.find("[itemprop]").not(subitems).each(function(index){
        var $this = $(this);
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
};


scan = function(){
    var $person = $("html[itemscope][itemtype='http://schema.org/Person']");
    if($person.length){
        var data = parseItem($person);
        return {person:data};
    }
};

lint = function(data){
	var ret = [];
    var age = undefined;
    var status = 'error';
    var birth = undefined;
    var death = undefined;
    if(data.person.birthDate != undefined){
        birth = new Date(data.person.birthDate[0]);
        death = new Date();
        if(data.person.deathDate != undefined){
            death = new Date(data.person.deathDate[0]);
        }
        age = death - birth;
        age /= 3600000;
        age /= 24;
        age = Math.floor(age/365.25);
        if(age >= 0){
            if(age < 100){
                status = 'ok';
            } else if (age < 115) {
                status = 'warning';
            }
        }
    }
    ret.push({status:status,message:"age: "+age});

    if(data.person.marriage != undefined){
        for(var i = 0; i < data.person.marriage.length; i++){
            status = "warning";
            var marriageAge = undefined;
            var marriageDate = undefined;
            if(data.person.marriage[i].startDate != undefined){
                marriageDate = new Date(data.person.marriage[i].startDate[0]);
                if(birth != undefined){
                    marriageAge = marriageDate - birth;
                    marriageAge /= 3600000;
                    marriageAge /= 24;
                    marriageAge = Math.floor(marriageAge/365.25);
                    if(marriageAge < 0)
                        status = "error";
                    if(marriageAge >= 14)
                        status = "ok";
                }
                if(death != undefined && marriageDate > death)
                    status = "error";
            }
            var md = marriageDate;
            if(md != undefined){
                md = new Date(md.getTimezoneOffset()*60000+md.getTime());
                md = md.toDateString();
            }
            ret.push({status:status,message:"marriage date: " + md + " age: " + marriageAge});
        }
    }

    if(data.person.gender=="unknown"){
    	ret.push({status:"warning", message:"gender unknown"});
    }
    return ret;
};


main = function(){
	var data = scan();
	if(data != undefined){
		var ret = lint(data);
		var ok = true;
		var $status = $("<div>");
		$status.addClass("wt-tools");
		$status.append("WikiTree Tools:");
		for(var i = 0; i<ret.length; ++i){
			if(ret[i].status != "ok")
				ok = false;
			var span = $("<span>");
			span.addClass("wt-tools-"+ret[i].status);
			span.html(ret[i].message);
			$status.append(span);
		}
		
		var $button = $('<button type="button" style="float: right;">Hide</button>');
		$button.click(function(){
			$status.hide(500);
			chrome.runtime.sendMessage("showPopup", function(response) {
			});
		});
	
		$status.append($button);
		$("body").prepend($status);
		
		if(!ok){
			$status.show(500);
		} else {
			chrome.runtime.sendMessage("showPopup", function(response) {
			});
		}
		
		chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
		    if (request == "showStatus"){
			      $status.show(500);
			      chrome.runtime.sendMessage("hidePopup", function(response) {
					});
		    }
		    sendResponse();
		});
	}
};

main();
