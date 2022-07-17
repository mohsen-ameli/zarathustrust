import { t } from 'i18next';
import zarathus_5 from '../images/zarathus-5.jpg'

const Carousel = () => {
    return (
        <div id="carouselExampleIndicators" className="carousel slide h-25" data-bs-ride="carousel">
            <div className="carousel-inner">
                <div className="carousel-item active" data-bs-interval="7000">
                    <img src={zarathus_5} className="d-block w-100" alt="..." />
                    <div className="carousel-caption active" style={{color: "black"}}>
                        <h1 style={{color: "black"}}>{t("carousel_title")}</h1>
                        <p>{t("carousel_body")}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
 
export default Carousel;