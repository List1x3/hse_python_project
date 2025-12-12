var now = 1;
var sp = [];
var spelems = [];
var nowx = -1;
var nowy = -1;
var nowzn = "X";
var now_color = "#FF5722";
var left_zones = 0;
var rows = 3;
var n = 3;
var buttons = document.querySelector('.submit');
var gameon = 1;
var spznak = [];
var winscreen = document.querySelector(".winscreen");
var wintext = document.querySelector(".wintext");

function createGrid(n) {
    const board = document.querySelector('.board');
    
    board.innerHTML = '';
    
    board.style.gridTemplateColumns = `repeat(${n}, 1fr)`;
    
    for (let i = 0; i < n; i++) {
        spelems[i] = [];
        for(let j = 0; j < n; j++){
            var square = document.createElement('div');
            square.className = 'square';
            square.textContent = i + " " + j;
            square.x = i;
            square.y = j;
        
            square.addEventListener('click', function() {
                if (sp[this.x][this.y] == 0 && gameon){
                    if(nowx != -1 && nowy != -1){
                        if(sp[nowx][nowy] == 0){
                            spelems[nowx][nowy].style.backgroundColor = '#4CAF50';
                            spelems[nowx][nowy].textContent = this.x + " " + this.y;
                        }
                        
                    }
                    if(this.textContent != "X" && this.textContent != "O"){
                        buttons.style.display = 'block';
                        this.style.backgroundColor = now_color;
                        this.textContent = nowzn;
                        nowx = this.x;
                        nowy = this.y;
                    
                    }
                }
                
                
            });
        
            board.appendChild(square);
            spelems[i][j] = square
        }
        
    }
    
}

function check_if_win(x, y, now){
    // Вертикально
    spznak = [];
    var counter = 0;
    var ny = y;
    while(0 <= x && x <= n - 1 && 0 <= ny && ny <= n - 1 && sp[x][ny] == now){
        spznak.push([x, ny]);
        ny += 1;
        counter += 1;
        
        
    }
    ny = y - 1
    while(0 <= x && x <= n - 1 && 0 <= ny && ny <= n - 1 && sp[x][ny] == now){
        spznak.push([x, ny]);
        ny -= 1;
        counter += 1;
        
        
    }
    if (counter>= rows){
        return true;
    }
    // Горизонтально
    spznak = [];
    counter = 0;
    ny = y;
    var nx = x;
    while(0 <= nx && nx <= n - 1 && 0 <= y && y <= n - 1 && sp[nx][y] == now){
        spznak.push([nx, ny]);
        nx += 1;
        counter += 1;
        
    }
    nx = x - 1;
    while(0 <= nx && nx <= n - 1 && 0 <= y && y <= n - 1 && sp[nx][y] == now){
        spznak.push([nx, ny]);
        nx -= 1;
        counter += 1;
        
    }
    if (counter >= rows){
        return true;
    }
    // наискосок вправо
    spznak = [];
    counter = 0;
    ny = y;
    nx = x;
    while(0 <= nx && nx <= n - 1 && 0 <= ny && ny <= n - 1 && sp[nx][ny] == now){
        spznak.push([nx, ny]);
        nx += 1;
        ny += 1;
        counter += 1; 
        
    }
    ny = y - 1;
    nx = x - 1;
    while(0 <= nx && nx <= n - 1 && 0 <= ny && ny <= n - 1 && sp[nx][ny] == now){
        spznak.push([nx, ny]);
        nx -= 1;
        ny -= 1;
        counter += 1; 
    }
    if (counter >= rows){
        return true;
    }
    // наискосок влево
    spznak = [];
    counter = 0;
    ny = y;
    nx = x;
    while(0 <= nx && nx <= n - 1 && 0 <= ny && ny <= n - 1 && sp[nx][ny] == now){
        spznak.push([nx, ny]);
        nx -= 1;
        ny += 1;
        counter += 1; 
        
    }
    ny = y - 1;
    nx = x + 1;
    while(0 <= nx && nx <= n - 1 && 0 <= ny && ny <= n - 1 && sp[nx][ny] == now){
        spznak.push([nx, ny]);
        nx += 1;
        ny -= 1;
        counter += 1; 
        
    }
    if (counter >= rows){
        return true;
    }
    return false;

}

function color_all_squares(){
    for(let i = 0; i < spznak.length; i++){
        setTimeout(function() {spelems[spznak[i][0]][spznak[i][1]].style.backgroundColor = '#ceff1d';}, 300 + 300 * i);

    }
}

function final_showdown(){
    winscreen.style.display = 'flex';
    winscreen.style.opacity = 1;
    // let current_opacity = 0;
    // while(winscreen.style.opacity < 1){
    //     setTimeout(function(){
    //         winscreen.style.opacity = current_opacity;
    //         current_opacity += 0.1;
    // }, 1)
    // }

}

function finish_hod(){
    if (nowx != -1 && nowy != -1){
        left_zones --;
        sp[nowx][nowy] = now;
        buttons.style.display = 'none';
        if(check_if_win(nowx, nowy, now) == true){
            wintext.textContent = "ПОБЕДА<br>" + nowzn;
            color_all_squares();
            final_showdown();
            // setTimeout(final_showdown(), 300 + 300 * sp.length);
        }
        else if(left_zones == 0){
            wintext .textContent = "НИЧЬЯ";
            final_showdown();
            // setTimeout(final_showdown(), 300 + 300 * sp.length);
        }
        else{
            nowx = -1;
            nowy = -1;
            if(now == 1){
                now = 2;
                nowzn = "O";
                now_color = "#42aaff";
            }
            else{
                now = 1;
                now_color = "#FF5722";
                nowzn = "X";
            }
        }

        
        
    }
    else{
        console.log("nowdob");
    }

}

function return_to_menu(){
    window.location = 'main.html'
}

function init() {
    
    winscreen.style.display = 'none';
    n = 3;
    left_zones = n * n;
    rows = 3; 
    now = 1;
    nowx = -1;
    nowy = -1;
    
    sp = [];
    for(let i = 0; i < n; i++){
        sp.push([]);
        for(let j = 0; j < n; j++){
            sp[i].push(0);
        }
    }
    createGrid(n);
    
    if (buttons) {
        buttons.addEventListener('click', finish_hod);
    } else {
        console.error('Кнопка не найдена');
    }
}



document.addEventListener('DOMContentLoaded', init);
