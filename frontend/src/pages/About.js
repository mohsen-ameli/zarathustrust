import { Link } from 'react-router-dom';
import RotateLoader from 'react-spinners/RotateLoader';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

const About = () => {
    const { t } = useTranslation()
    const [isLoading, setIsLoading] = useState(true)


    useEffect(() => {
        setIsLoading(false)
    }, [])


    return (
    <div className="about-page">
        { isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
        }

        <div className="card text-white zarathus-card mx-auto">
            <div className="card-body">
                <h3 className="fw-normal text-center">{t("about_page")}</h3>
                <hr className="zarathus-hr"></hr>
                <h5 className="fw-normal">
                    {t("about_msg")}
                </h5>
                <hr className="zarathus-hr"></hr>
                    <Link className="neon-button" to="/home">{t("home")}</Link>
                <small style={{float: "right"}}>{t("version")}</small>
            </div>
        </div>
    </div>
    );
}
 
export default About;