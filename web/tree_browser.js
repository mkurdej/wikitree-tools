# Copyright Roland Arsenault

var anchorProfile;

function ProfileManager(){
  this.profiles = {};
}

ProfileManager.prototype = {
  getProfile: function(user_id){
    if(this.profiles[user_id] == undefined){
      this.profiles[user_id] = new Profile(user_id);
    }
    return this.profiles[user_id];
  },
}

var profileManager = new ProfileManager();

function Profile(user_id){
  this.user_id = user_id;
}

Profile.prototype = {
  load: function(callback){
    if(this.data == undefined && !this.loading){
      this.loading = true;
      var self = this;
      $.post('/api.php', 
        { 'action': 'getPerson', 'key': this.user_id, 'fields': 'Name,FirstName,LastNameCurrent,Gender,Father,Mother', 'format': 'json' }
      ).done(function(data) { 
        self.loading = false;
        if (data[0].status) { 
          console.log("There was an error getting the person:",data);
        } else {
          self.data = data[0].person;
        }
        if(callback != undefined)
          callback();
      });
    } else if(callback != undefined)
      callback();
  },
};

function ProfileDisplayNode(profile){
  this.profile = profile;
  this.div = $(document.createElement( "div" ));
  this.div.prop("class","profile");
 
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
    self.nameDiv.html(profile.data.FirstName+" "+profile.data.LastNameCurrent);
    self.nameDiv.prop("class",profile.data.Gender);
    self.nameDiv.click(function(){
      self.load();
      url = "/wiki/"+profile.data.Name
      $("#wt-frame-view").prop("src",url);
    });
  });
}

ProfileDisplayNode.prototype = {
  load: function(){
    if(this.profile.father == undefined && this.profile.data.Father != undefined){
      this.profile.father = profileManager.getProfile(this.profile.data.Father)
      var pdiv = new ProfileDisplayNode(this.profile.father);
      this.fatherDiv.append(pdiv.div);
    }
    if(this.profile.mother == undefined && this.profile.data.Mother != undefined){
      this.profile.mother = profileManager.getProfile(this.profile.data.Mother)
      var pdiv = new ProfileDisplayNode(this.profile.mother);
      this.motherDiv.append(pdiv.div);
    }
  },
}

function verifyLogin(){
  // Do we alredy have an active session?
	var user_id   = $.cookie('wikitree_wtb_UserID');
	var user_name = $.cookie('wikitree_wtb_UserName');
	if (user_id && user_name) { 
		$.post('/api.php',
			{ 'action': 'login', 'user_id': user_id }
		).done(function(data) {
			if (data.login.result == user_id) {
        anchorProfile = profileManager.getProfile(user_id);
        anchorProfileDisplay = new ProfileDisplayNode(anchorProfile);
        $("#tree").append(anchorProfileDisplay.div);
        anchorProfileDisplay.div.draggable();
			}
		});
	}

}

function init(){
  $("#wikitree").resizable();
  $("#wikitree").draggable();
  $("#tree").resizable();
  $("#tree").draggable();
  verifyLogin();
}
      
$( document ).ready(init);
