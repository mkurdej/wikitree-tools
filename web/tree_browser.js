// Copyright Roland Arsenault

var treeDisplay;

function TreeDisplay(anchorProfile,treeDiv){
	this.treeDiv = treeDiv;
	this.addProfileDisplayNode(anchorProfile);
	this.center = 1;
}

TreeDisplay.prototype.layout = function(){
	var baseOffset = this.treeDiv.offset();
	var baseWidth = this.treeDiv.innerWidth();
	var baseHeight = this.treeDiv.innerHeight();
	
	var centerGen =  Math.floor(Math.log(this.center)/Math.LN2);
	var centerGenSize = Math.pow(2,centerGen);
	var centerGenPos = this.center-centerGenSize;
	
	var center = {
		left: baseOffset.left+baseWidth/2,
		top: baseOffset.top+baseHeight/2
	};
	
	$(".profile",this.treeDiv).each(function(index){
		console.log(index,this);
		var $this = $(this);
		var anum = $this.data("ahnentafel");
		gen = Math.floor(Math.log(anum)/Math.LN2);
		genSize = Math.pow(2,gen);
		genPos = anum-genSize;
		console.log("Generation: "+gen,'size',genSize,'pos',genPos);
		var xOffset = $this.outerWidth() * (-.5+1.1*(gen-centerGen));
		var yOffset = $this.outerHeight() * ((genPos-genSize/2)-(centerGenPos-centerGenSize/2))*1.1;
		$this.offset({
			left:center.left+xOffset,
			top:center.top+yOffset
		});
	});
};

TreeDisplay.prototype.addProfileDisplayNode = function (profile,aNum){
	var retDiv = $(document.createElement( "div" ));
	retDiv.data("profile",profile);
	if(aNum == undefined){
		aNum = 1;
	}
	retDiv.data("ahnentafel", aNum);
	  
	retDiv.prop("class","profile");
	  
	var header = $(document.createElement( "div" ));
	header.prop("class","unknown");
	retDiv.append(header);
	
	var nameDisplay = $(document.createElement( "span" ));
	nameDisplay.css("width","90%");
	header.append(nameDisplay);
	  
	var plus = $(document.createElement( "button" ));
	plus.html("+");
	plus.attr("type","button");
	header.append(plus);
	  
	var self = this;
	
	plus.click(function(){
		self.center = aNum;
		self.addProfileDisplayNode(profile.Father, aNum*2);
		self.addProfileDisplayNode(profile.Mother, aNum*2+1);
		plus.remove(); 
  	});
	
	
	profile.load(function(){
		nameDisplay.html(profile.FirstName+" "+profile.LastNameCurrent);
		header.prop("class",profile.Gender);
		retDiv.append('<a href="/wiki/'+profile.Name+'" target="wt-frame-view"+>View Profile</a>');
	});
	this.treeDiv.append(retDiv);
	this.layout();
};


function init(){
  wt.init($('#status'));
  wt.onLogin(function(){
    wt.getRootPerson().load(function(rootPerson){
    	treeDisplay = new TreeDisplay(rootPerson,$("#tree-content"));
    });
  });
}
      
$( document ).ready(init);
