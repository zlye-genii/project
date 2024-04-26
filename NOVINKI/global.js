document.querySelector('button').onclick = function(){
    console.log(this)  // теперь this это кнопка
    this.style.background = "red";
  }