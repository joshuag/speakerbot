var vk = (function(){

    //automatically install sprintf functionality for strings. Fuck Yo' Globals, Darkness.

    String.prototype.sprintf = function(){
       output = this.toString();
       for(var i=0;i<arguments.length;i++){
            asNum = parseFloat(arguments[i]);
            if(asNum || asNum === 0){
                suffix = (asNum > 1 || asNum === 0)?"s":"";
                output = output.replace(/%s {1}(\w+)\(s\){1}/, "%s $1" + suffix);
            }
            output = output.replace("%s", arguments[i]);
        }
       return output;
    };

    function Func(){
        //Constructor for VK
        this.fartscroll = this._fartscroll(this);
        this.install_jquery_plugins();
    }

    Func.prototype.install_jquery_plugins = function(){
      (function($) {

        $.fn.autoajax_post = function(handler)
          {
            return this.each(function() {
              if(!handler){
                handler = function(){};
              }

              var $this = $(this);

              var url = $this.attr("data-url") || $this.attr("action") || $this.attr("href");

              var data = $this.attr("data-post");

              var event;

              switch(this.tagName.toLowerCase()){
                case "form":
                  event = "submit";
                  break;
                case "a":
                  event = "click";
                  break;
              }

              function post_handler(e){
                    e.stopPropagation();
                    e.preventDefault();
                    if(!data){
                      data = this.serialize();
                    }else{
                      data = decodeURIComponent(data);
                    }
                    $.ajax(
                        {
                          url: url,
                          type: "post",
                          data: data,
                          success: handler,
                          error: function(){alert("There was an error.");}
                        });
                  }
              $this[event](
                $.proxy(
                  post_handler,
                  $this
                ));
            });

          };
      }(jQuery));
    };

    Func.prototype.init_ui_hacks = function(){
        //this.fartscroll();
        var choice = this.choice(this.range(1,30));
        
        if(choice == 6){
            $("body").append('<iframe src="http://adultcatfinder.com/embed/" width="320" height="430" style="position:fixed;bottom:0px;right:10px;z-index:100" frameBorder="0"></iframe>');
        }
        
    };

    Func.prototype.choice = function(choices) {
      var index = Math.floor(Math.random() * choices.length);
      return choices[index];
    };

    Func.prototype.range = function(begin, end, step){
        if(!step) step = 1;
        out = [];
        for(var i=begin;i<=end;i=i+step){
            out.push(i);
        }
        return out;
    };

    Func.prototype._fartscroll = (function ($vk) {
     //Shamelessly adapted from the onion's fartscroll
     //Need to figure out the cost bullshit to make this work. no hacks allowed.
      return function (trigger_distance) {
        trigger_distance = trigger_distance || 400;
        var lastOffset;

        var fartHandler = function() {
          var scrollOffset = Math.floor(window.scrollY / trigger_distance);
          if (lastOffset !== scrollOffset) {
            choice = $vk.choice(['wet-fart','dry-fart','whoa','doh']);
            $.ajax('/play_sound/%s?free=true'.sprintf(choice));
            lastOffset = scrollOffset;
          }
        };

        window.addEventListener('scroll', fartHandler, false);
      };
    });
    return Func;
})();

var $vk = new vk();