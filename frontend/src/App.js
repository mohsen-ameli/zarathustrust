import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

import AccountPage from "./pages/AccountPage";
import UsersPage from "./pages/UsersPage";
import HomePage from "./pages/HomePage";
import NotFoundPage from "./pages/NotFoundPage";
import NavbarPage from "./pages/NavbarPage";
import DefaultPage from "./pages/DefaultPage";
import AboutPage from "./pages/AboutPage";

function App() {
    return (
        <Router>
            <NavbarPage />
            <div className="app container" style={{marginTop: "5rem"}} id="main-content">
                <Switch>
                    {/* <Route exact path="/" component={DefaultPage} /> */}
                    <Route exact path="/home/:id" component={HomePage} />
                    <Route path="/account" component={AccountPage} />
                    <Route path="/about" component={AboutPage} />
                    <Route path="/users" component={UsersPage} />
                    <Route component={NotFoundPage} />
                </Switch>
                <div>Still Under Development</div>
            </div>
        </Router>
    );
}

export default App;
