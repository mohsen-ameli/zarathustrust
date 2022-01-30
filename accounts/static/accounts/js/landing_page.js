const ani = document.getElementById("ani");
const holdInitialTime = 3000;
const animationTime = 7;
const width = window.innerWidth;
const height = window.innerHeight;
const navImgWidth = 60;

let elem = document.querySelector("body > nav > div > a > img")
let rect = elem.getBoundingClientRect();


ani.style.backgroundColor = "#f8b119";
ani.style.zIndex = "10000";

setTimeout(()=>{
    ani.style.backgroundColor = "transparent";
    ani.style.backgroundSize= `${width}px auto`;
    
    const tl = new TimelineMax();

    tl.fromTo(ani, animationTime, {
        zIndex: 10000,
        backgroundColor: "#f8b119",
    }, {
        scale: navImgWidth / width,
        backgroundColor: "transparent",
        backgroundImage: 'url("../../static/accounts/images/zarathustrust_new.png")',
        backgroundRepeat: "no-repeat",
        backgroundPosition: "center",

        left: "-100%",
        x: rect.left + 30,

        top: "-100%",
        y: rect.top + 13,

        zIndex: 10000,
        ease: Power2.easeInOut
    })
    
}, holdInitialTime)

// removing the element, once the animation is done
setTimeout(()=> {
    ani.style.display = "none"
}, animationTime * 1000 + holdInitialTime + 1000)