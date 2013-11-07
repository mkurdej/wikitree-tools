// Copyright Roland Arsenault

;(function(wt, $, undefined) {

  wt.Person = function(user_id){
    this.user_id = user_id;
    this.loaded = false;
  }

  wt.Person.prototype.load = function(callback){
    if(!this.loaded && !this.loading){
      this.loading = true;
      var self = this;
      $.post('/api.php', 
        { 'action': 'getPerson', 'key': this.user_id, 'fields': 'Name,FirstName,LastNameCurrent,Gender,Father,Mother', 'format': 'json' }
      ).done(function(data) { 
        if (data[0].status) { 
          console.log("There was an error getting the person:",data);
          self.loading = false;
          if(callback != undefined)
            callback(self);
        } else {
          for(var attrib in data[0].person)
            self[attrib] = data[0].person[attrib];
          if (self.Father != undefined){
            self.Father = wt.getPerson(self.Father);
          }
          if (self.Mother != undefined){
            self.Mother = wt.getPerson(self.Mother);
          }

          $.post('/api.php', {
            'action': 'getPerson', 'key': self.user_id, 'fields': 'Id,Siblings,Spouses,Children', 'format': 'json' 
            }).done(function(data) { 
              for(var attrib in data[0].person)
                self[attrib] = data[0].person[attrib];
              self.loading = false;
              self.loaded = true;
              if(callback != undefined)
                callback(self);
            });

        }
      });
    } else if(callback != undefined)
      callback(self);
  }
  
})(window.wt = window.wt || {}, jQuery);
