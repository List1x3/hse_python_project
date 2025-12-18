var n = 5;
var ups = document.querySelector(".but-up");
var downs = document.querySelector(".but-down");
var f1 = document.querySelector(".chose-one-1");
var f2 = document.querySelector(".chose-one-2");


function go_to_game(){
    const d = AppConfig.urls.game.replace('N', n);
    window.location.href=d;
}

function go_to_game_bot(){
    const d = AppConfig.urls.game_bot.replace('N', n);
    window.location.href=d;
}


function addone(){
    n ++;
    f1.textContent = n;
    f2.textContent = n;

    if (n == 10){
        ups.style.display = 'none';
        downs.style.display = 'block';
    }
    else if(n == 3){
        ups.style.display = 'block';
        downs.style.display = 'none';
    }
    else{
        ups.style.display = 'block';
        downs.style.display = 'block';
    }
}


function remone(){
    n --;
    f1.textContent = n;
    f2.textContent = n;
    if (n == 10){
        ups.style.display = 'none';
        downs.style.display = 'block';
    }
    else if(n == 3){
        ups.style.display = 'block';
        downs.style.display = 'none';
    }
    else{
        ups.style.display = 'block';
        downs.style.display = 'block';
    }
}