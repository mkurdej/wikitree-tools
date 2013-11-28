

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
}

lint = function(data){
    var age = undefined;
    var bg = 'red'
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
                bg = 'lightgreen';
            } else if (age < 115) {
                bg = 'yellow';
            }
        }
    }
    var p = $("<p>");
    p.html("age: "+age);
    p.css("background-color",bg);
    $("body").append(p);

    if(data.person.marriage != undefined){
        for(var i = 0; i < data.person.marriage.length; i++){
            bg = "yellow";
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
                        bg = "red";
                    if(marriageAge >= 14)
                        bg = "lightgreen";
                }
                if(death != undefined && marriageDate > death)
                    bg = "red";
            }
            p = $("<p>");
            var md = marriageDate;
            if(md != undefined){
                md = new Date(md.getTimezoneOffset()*60000+md.getTime());
                md = md.toDateString();
            }
            p.html("marriage date: " + md + " age: " + marriageAge);
            p.css("background-color",bg);
            $("body").append(p);
        }
    }

    if(data.person.gender=="unknown"){
        p = $("<p>");
        p.html("gender unknown");
        p.css("background-color","yellow");
        $("body").append(p);
    }
}

$(document).ready( function(){
    chrome.runtime.getBackgroundPage( function(bg){
        $("body").append($("<h1>"+bg.wt_data.person.name[0]+"</h1>"));
        lint(bg.wt_data);
        //$("body").append(tablify(bg.wt_data.person));
    });
});
