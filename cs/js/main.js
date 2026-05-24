window.addEventListener("load",()=>{

    setTimeout(()=>{

        document
        .getElementById("loading-screen")
        .style.display="none";

    },1000);

});

const heroImage =
document.querySelector(".ct");

window.addEventListener("scroll",()=>{

    const scroll =
    window.scrollY;

    heroImage.style.transform =
    `scale(1.05)
     translateY(${scroll*0.05}px)`;

});