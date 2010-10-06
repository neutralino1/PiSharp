
function findPosX(obj)
  {
    var curleft = 0;
    if(obj.offsetParent)
        while(1) 
        {
          curleft += obj.offsetLeft;
          if(!obj.offsetParent)
            break;
          obj = obj.offsetParent;
        }
    else if(obj.x)
        curleft += obj.x;
    return curleft;
  }

  function findPosY(obj)
  {
    var curtop = 0;
    if(obj.offsetParent)
        while(1)
        {
          curtop += obj.offsetTop;
          if(!obj.offsetParent)
            break;
          obj = obj.offsetParent;
        }
    else if(obj.y)
        curtop += obj.y;
    return curtop;
  }

function showToolTip(parentId, booktime)
{
var parent = document.getElementById(parentId);
var tool = document.getElementById('ToolTipDiv');
var cancel = document.getElementById('CancelDiv');
var nomore = document.getElementById('NoMoreDiv');
tool.style.top = findPosY(parent) + 32 + 2 + 'px';
tool.style.left = findPosX(parent) - 100 - 4 + 55 + 2 + 'px';
//tool.style.top = findPosY(parent) + 'px';
//tool.style.left = findPosX(parent) + 'px';
tool.style.display = 'block';
cancel.style.display = 'none';
nomore.style.display = 'none';
var time = document.getElementById('booktime');
time.value = booktime;
}

function showCancel(parentId, id)
{
var parent = document.getElementById(parentId);
var tool = document.getElementById('ToolTipDiv');
var cancel = document.getElementById('CancelDiv');
var nomore = document.getElementById('NoMoreDiv');
cancel.style.top = findPosY(parent) + 32 + 2 + 'px';
cancel.style.left = findPosX(parent) - 75 - 4 + 55 + 2 + 'px';
cancel.style.display = 'block';
tool.style.display = 'none';
nomore.style.display = 'none';
var time = document.getElementById('cancelid');
time.value = id;
//parent.style.background = '#505050';
}

function showNoMore(parentId)
{
var parent = document.getElementById(parentId);
var tool = document.getElementById('ToolTipDiv');
var cancel = document.getElementById('CancelDiv');
var nomore = document.getElementById('NoMoreDiv');
nomore.style.top = findPosY(parent) + 32 + 2 + 'px';
nomore.style.left = findPosX(parent) - 75 - 4 + 55 + 2 + 'px';
nomore.style.display = 'block';
tool.style.display = 'none';
cancel.style.display = 'none';
var t = setTimeout("closeToolTip('NoMoreDiv')", 1500);
}


function closeToolTip(divId)
{
var tool = document.getElementById(divId);
tool.style.display = 'none';
}