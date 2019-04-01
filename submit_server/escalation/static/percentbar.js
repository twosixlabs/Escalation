//from https://github.com/DataTables/Plugins/blob/master/dataRender/percentageBars.js
jQuery.fn.dataTable.render.percentBar = function(pShape, cText, cBorder, cBar, cBack, vRound, bType) {
  pShape = pShape || 'square';
  cText = cText || '#000';
  cBorder = cBorder || '#BCBCBC';
  cBar = cBar || '#5FD868';
  cBack = cBack || '#E6E6E6';
  vRound = vRound || 2;
  bType = bType || 'ridge';
  //Bar templates
  var styleRule1 = 'max-width:100px;height:12px;margin:0 auto;';
  var styleRule2 = 'border:2px '+bType+' '+cBorder+';line-height:12px;font-size:14px;color:'+cText+';background:'+cBack+';position:relative;';
  var styleRule3 = 'height:12px;line-height:12px;text-align:center;background-color:'+cBar+';padding:auto 6px;';
  //Square is default, make template round if pShape == round
  if(pShape=='round'){
    styleRule2 += 'border-radius:5px;';
    styleRule3 += 'border-top-left-radius:4px;border-bottom-left-radius:4px;';
  }
 
  return function(d, type, row) {
    //Remove % if found in the value
    //Round to the given parameter vRound
    s = 100 * parseFloat(d.toString().replace(/\s%|%/g,'')).toFixed(vRound);
    //Not allowed to go over 100%

    if(s>100){s=100}
     
    // Order, search and type gets numbers
    if (type !== 'display') {
      return s;
    }
    if (typeof d !== 'number' && typeof d !== 'string') {
      return d;
    }
     
    //Return the code for the bar
    return '<div style="'+styleRule1+'"><div style="'+styleRule2+'"><div style="'+styleRule3+'width:'+s+ '%;"></div><div style="width:100%;text-align:center;position:absolute;left:0;top:0;">'+s+'%</div></div></div>';
  };
};
