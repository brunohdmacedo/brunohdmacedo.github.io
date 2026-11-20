const canvas =
document.getElementById("particles");

const ctx =
canvas.getContext("2d");

function resize(){

    canvas.width =
    window.innerWidth;

    canvas.height =
    window.innerHeight;

}

resize();

window.addEventListener(
"resize",
resize
);

const particles=[];

for(let i=0;i<180;i++){

    particles.push({

        x:Math.random()*canvas.width,

        y:Math.random()*canvas.height,

        size:
        Math.random()*3+1,

        speed:
        Math.random()*1.5+0.3,

        color:
        Math.random()>.5
        ?
        "#00a2ff"
        :
        "#ff8c00"

    });

}

function animate(){

    ctx.clearRect(
    0,
    0,
    canvas.width,
    canvas.height
    );

    particles.forEach(p=>{

        p.y-=p.speed;

        if(p.y<0){

            p.y=
            canvas.height+10;

            p.x=
            Math.random()*
            canvas.width;

        }

        ctx.beginPath();

        ctx.fillStyle=
        p.color;

        ctx.arc(
        p.x,
        p.y,
        p.size,
        0,
        Math.PI*2
        );

        ctx.fill();

    });

    requestAnimationFrame(
    animate
    );

}

animate();