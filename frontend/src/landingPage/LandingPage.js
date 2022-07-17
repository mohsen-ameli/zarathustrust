import LandingAni from './LandingAni'
import Carousel from './Carousel'
import PicUsp from './PicUsp'
import Socials from './Socials'
import IconUsp from './IconUsp'
import JoinUs from './JoinUs'
import Footer from './Footer'

import '../css/features.css'
import '../css/fixed_bg.css'

const LandingPage = () => {
    return (
    <div className="landing-page" style={{marginTop: "46px"}}>
        {/* Starting Page Animation */}
        <LandingAni />
        <div className="test-animation" id="ani"></div>

        {/* Carousel */}
        <Carousel />

        {/* First USP Section */}
        <IconUsp />

        {/* Second USP section with pics */}
        <PicUsp />

        {/* Join us now */}
        <JoinUs />

        {/* Socials */}
        <Socials />

        {/* Footer */}
        <Footer />
    </div>
    );
}
 
export default LandingPage;
