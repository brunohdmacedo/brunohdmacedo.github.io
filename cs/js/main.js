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

document.addEventListener("DOMContentLoaded", function() {
    const mobileMenuBtn = document.getElementById("mobile-menu");
    const mainMenu = document.querySelector(".main-menu");

    if (mobileMenuBtn && mainMenu) {
        mobileMenuBtn.addEventListener("click", function() {
            mainMenu.classList.toggle("active");
            
            // Alterna o ícone entre barras e "X" fechar
            const icon = mobileMenuBtn.querySelector("i");
            if (mainMenu.classList.contains("active")) {
                icon.className = "fa-solid fa-xmark";
            } else {
                icon.className = "fa-solid fa-bars";
            }
        });
    }
});
