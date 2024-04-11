import {gsap, Power2} from "gsap";
import { useEffect, useRef } from "react";
import img from "./zarathustrust_new.png";

const LandingAnimation = () => {
    const ani = useRef()
    const holdInitialTime = 2000;
    const animationTime = 7;
    const WIDTH = window.innerWidth;
    const navImgWidth = 60;

    useEffect(() => {
        const logo = document.querySelector("#zarathus-img")
        const rect = logo?.getBoundingClientRect();

        setTimeout(()=>{
            ani.current.style.backgroundColor = "transparent";
            ani.current.style.backgroundSize= `${WIDTH}px auto`;
            
            const tl = gsap.timeline()
    
            tl.fromTo(ani.current, animationTime, {
                backgroundColor: "#f8b119",
            }, {
                scale: navImgWidth / WIDTH,
                backgroundColor: "transparent",
    
                left: "-100%",
                x: rect?.left + 30,
    
                top: "-100%",
                y: rect?.top + 13,
    
                ease: Power2.easeInOut
            })
            
        }, holdInitialTime)

        // removing the element, once the animation is done
        setTimeout(() => {
            ani.current.remove()
        }, animationTime * 1000 + holdInitialTime)

        // eslint-disable-next-line
    }, [])

    return (
        <div className="landing-ani test-animation" style={{
            position: "fixed",
            top: 0,
            left: 0,
            zIndex: 10000,
            backgroundColor: "#f8b119",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
        }} ref={ani}>
            <img src={img} alt="logo" />
        </div>
    );
}
 
export default LandingAnimation;