import {gsap, Power2} from "gsap";
import { useEffect, useRef } from "react";

const LandingAni = () => {
    let ani = useRef()
    const holdInitialTime = 3000;
    const animationTime = 7;
    const WIDTH = window.innerWidth;
    const navImgWidth = 60;

    useEffect(() => {
        let elem = document.querySelector("#zarathus-img")
        let rect = elem?.getBoundingClientRect();

        ani.current.style.backgroundColor = "#f8b119";
        ani.current.style.zIndex = "10000";

        setTimeout(()=>{
            ani.current.style.backgroundColor = "transparent";
            ani.current.style.backgroundSize= `${WIDTH}px auto`;
            
            const tl = gsap.timeline()
    
            tl.fromTo(ani.current, animationTime, {
                zIndex: 10000,
                backgroundColor: "#f8b119",
            }, {
                scale: navImgWidth / WIDTH,
                backgroundColor: "transparent",
                backgroundImage: 'url("../../static/accounts/images/zarathustrust_new.png")',
                backgroundRepeat: "no-repeat",
                backgroundPosition: "center",
    
                left: "-100%",
                x: rect?.left + 30,
    
                top: "-100%",
                y: rect?.top + 13,
    
                zIndex: 10000,
                ease: Power2.easeInOut
            })
            
        }, holdInitialTime)

        // removing the element, once the animation is done
        setTimeout(() => {
            ani.current.style.display = "none"
        }, animationTime * 1000 + holdInitialTime + 1000)

        // eslint-disable-next-line
    }, [])

    return (
        <div className="landing-ani test-animation" ref={ani}>.</div>
    );
}
 
export default LandingAni;