// Copyright Roland Arsenault

var anchorProfile;

function ProfileDisplayNode(profile){
  this.profile = profile;
  this.div = $(document.createElement( "div" ));
  this.div.prop("class","profile");
  this.fatherDisplayNode = null;
  this.motherDisplayNode = null;
 
  table = $(document.createElement("table"));
  this.div.append(table);
  
  row = $(document.createElement("tr"));
  row.append('<td></td>');
  data = $(document.createElement("td"));
  this.fatherDiv = $(document.createElement("div"));
  data.append(this.fatherDiv);
  row.append(data);
  table.append(row);
  
  row = $(document.createElement("tr"));
  data = $(document.createElement("td"));
  this.nameDiv = $(document.createElement( "div" ));
  this.nameDiv.prop("class","unknown");
  data.append(this.nameDiv);
  row.append(data);
  
  var self = this;
  data = $(document.createElement("td"));
  this.showParents = $(document.createElement("button"));
  this.showParents.html("-");

  this.showParents.click(function(){
    self.load();
    if(self.showParents.html() == "-"){
      self.showParents.html("+");
      self.fatherDiv.hide(400);
      self.motherDiv.hide(400);
    } else  {
      self.showParents.html("-");
      self.fatherDiv.show(400);
      self.motherDiv.show(400);
    }
  });
  data.append(this.showParents);
  row.append(data);
  table.append(row);

  row = $(document.createElement("tr"));
  row.append('<td></td>');
  data = $(document.createElement("td"));
  this.motherDiv = $(document.createElement("div"));
  data.append(this.motherDiv);
  row.append(data);
  table.append(row);
  

  profile.load(function(){
    self.nameDiv.html(profile.FirstName+" "+profile.LastNameCurrent);
    self.nameDiv.prop("class",profile.Gender);
    self.nameDiv.click(function(){
      url = "/wiki/"+profile.Name
      $("#wt-frame-view").prop("src",url);
    });
  });
}

ProfileDisplayNode.prototype.load = function(){
  if(this.fatherDisplayNode == null && this.profile.Father != undefined){
    this.fatherDisplayNode = new ProfileDisplayNode(this.profile.Father);
    this.fatherDiv.append(this.fatherDisplayNode.div);
  }
  if(this.motherDisplayNode == null && this.profile.Mother != undefined){
    this.motherDisplayNode = new ProfileDisplayNode(this.profile.Mother);
    this.motherDiv.append(this.motherDisplayNode.div);
  }
}


function init(){
  $("#wikitree").resizable();
  $("#wikitree").draggable();
  $("#tree").resizable();
  $("#tree").draggable();
  
  wt.init($('#status'));
  wt.onLogin(function(){
    wt.getRootPerson().load(function(rootPerson){
      anchorProfile = rootPerson;
      var anchorProfileDisplay = new ProfileDisplayNode(anchorProfile);
      $("#tree").append(anchorProfileDisplay.div);
      anchorProfileDisplay.div.draggable();
    });
  });
}
      
$( document ).ready(init);
