$(document).ready(function() {
    // Creates a new canvas element and appends it as a child
    // to the parent element, and returns the reference to
    // the newly created canvas element


    var CAMPAIGN_ID = 1;

    function scratchCall(id,result){
        $.ajax({
            url: '/scratch',
            type: "POST",
            data: {"id" :id ,"result": result},
            dataType: "json",

        });
    }


    function createCanvas(parent, width, height) {
        var canvas = {};
        canvas.node = document.createElement('canvas');
        canvas.context = canvas.node.getContext('2d');
        canvas.node.width = width || 100;
        canvas.node.height = height || 100;
        parent.appendChild(canvas.node);
        return canvas;
    }

    function clippedBackgroundImage( ctx, img, w, h ){
      ctx.save(); // Save the context before clipping
      // ctx.clip(); // Clip to whatever path is on the context

      var imgHeight = w / w * h;
      if (imgHeight < h){
        ctx.fillStyle = '#000';
        ctx.fill();
      }
      ctx.drawImage(img,0,0,w,imgHeight);

      ctx.restore(); // Get rid of the clipping region
    }

    function getPercentageErased(ctx,w,h) {

        // get the pixel data from the canvas
        var imgData = ctx.getImageData(0,0,w,h);
        var totalPixels = w*h;
        // loop through each pixel and count non-transparent pixels
        var count=0;
        for (var i=0;i<imgData.data.length;i+=4)
          {
              // nontransparent = imgData.data[i+3]==0
              if(imgData.data[i+3]==0){ count++; }
          }
        return (count*100)/totalPixels;
    }


    function init(container, width, height, fillColor) {
        var canvas = createCanvas(container, width, height);
        var ctx = canvas.context;
        var result = false;
        // define a custom fillCircle method
        ctx.fillCircle = function(x, y, radius, fillColor) {
            this.fillStyle = fillColor;
            this.beginPath();
            this.moveTo(x, y);
            this.arc(x, y, radius, 0, Math.PI * 2, false);
            this.fill();
        };
        ctx.clearTo = function(fillColor) {
            ctx.fillStyle = fillColor;
            ctx.fillRect(0, 0, width, height);
        };
        // ctx.clearTo(fillColor || "#ddd");
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 4;
        var img = new Image;
        img.onload = function (){
            clippedBackgroundImage(ctx,img,width,height);
        };
        img.src = '/static/wrapper.png'

        // bind mouse events
        canvas.node.onmousemove = function(e) {
            if (!canvas.isDrawing ) {
               return;
            }
            if (result) {
                return;
            };
            var x = e.pageX - this.offsetLeft;
            var y = e.pageY - this.offsetTop;
            var radius = 25; // or whatever
            var fillColor = '#ff0000';
            ctx.globalCompositeOperation = 'destination-out';
            ctx.fillCircle(x, y, radius, fillColor);
            var erased = getPercentageErased(ctx,width,height);
            if (erased >= 40) {
                console.log('done');
                ctx.clearRect(0,0,width,height);
                scratchCall(CAMPAIGN_ID,'win');
                result = true;
            };

        };
        canvas.node.onvmousemove = function(e) {
        	e.preventDefault();
            if (!canvas.isDrawing) {
               return;
            }
            var x = e.pageX - this.offsetLeft;1
            var y = e.pageY - this.offsetTop;
            var radius = 25; // or whatever
            var fillColor = '#ff0000';
            ctx.globalCompositeOperation = 'destination-out';
            ctx.fillCircle(x, y, radius, fillColor);
        };

        canvas.node.onmousedown = function(e) {
            canvas.isDrawing = true;
        };
       	
        canvas.node.onvmousedown = function(e) {
            canvas.isDrawing = true;

        };

        canvas.node.onvmouseup = function(e) {
            canvas.isDrawing = false;
        };

        canvas.node.onmouseup = function(e) {
            canvas.isDrawing = false;
        };

        canvas.node.onmouseleave = function(e) {
            canvas.isDrawing = false;
        };
    }

    var container = document.getElementById('canvas');
    init(container, 531, 438, '#ddd');

});