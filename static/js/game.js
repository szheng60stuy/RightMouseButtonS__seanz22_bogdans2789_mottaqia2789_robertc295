let players = [];
let pIndex = 0;
let terr = ["America", "China", "England"];
let out = NULL;

async function Setup()
{
  players = document.getElementById('plyrs').children;
  out = document.getElementById('outlog');
}

function Atck(target, source)
{
  out.innerText = source + "is attacking" + target;
  
}
