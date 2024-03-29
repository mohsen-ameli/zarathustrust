import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import React, { useState, createContext } from "react";
import { AuthProvider } from './context/AuthContext';

import LandingPage from "./landingPage/LandingPage";
import Home from "./pages/Home";
import NewDunc from "./pages/NewDunc";
import About from "./pages/About";
import Navbar from "./components/Navbar";
import PrivateRoute from './components/PrivateRoute';
import Deposit from "./deposit/Deposit";
import DepositInfo from './deposit/DepositInfo';
import WalletSearch from './wallet/WalletSearch';
import WalletConfirm from './wallet/WalletConfirm';
import TransferSearch from './transfer/TransferSearch';
import TransferConfirm from './transfer/TransferConfirm'
import Withdraw from './withdraw/Withdraw';
import CurrencyEx from './currencyEx/CurrencyEx';
import CurrencyExConfirm from './currencyEx/CurrencyExConfirm';
import Transactions from './transaction/Transactions';
import TransactionsDetail from './transaction/TransactionsDetail'

import Login from './auth/Login';
import Logout from './auth/Logout';
import SignUp from './auth/signup/SignUp';
import CountryPicker from './auth/signup/CountryPicker';
import VerifyEmail from './auth/signup/VerifyEmail';
import VerifyPhone from './auth/signup/VerifyPhone';
import VerifyReferral from './auth/signup/VerifyReferral';
import Settings from './settings/Settings';
import InviteFriend from './settings/InviteFriend';

import PassReset from './auth/forgotpass/PassReset';
import PassResetConfirm from './auth/forgotpass/PassResetConfirm';
import RequireBanking from './components/RequireBanking';
import CookiePolicy from './pages/CookiePolicy';

export const ThemeContext = createContext(null)

function App() {
    let [theme, setTheme] = useState(() => localStorage?.getItem("theme") ? localStorage?.getItem("theme") : "dark")

    let toggleTheme = () => {
        theme === "light" ? setTheme("dark") && localStorage.setItem("theme", "dark") : setTheme("light") && localStorage.setItem("theme", "light")
    }

    return (
        <Router>
            <AuthProvider>
            <ThemeContext.Provider value={{ theme, toggleTheme }}>
                <div className="app" id={theme}>
                    <Navbar />
                    <Switch>
                        <Route exact path="/" component={LandingPage} />
                        <Route>
                            <div className="container" id="main-content">
                                <PrivateRoute path="/home" comp={Home} />
                                <PrivateRoute path="/deposit" comp={Deposit} />
                                <PrivateRoute path="/deposit-info" comp={DepositInfo} />
                                <PrivateRoute path="/withdraw" comp={Withdraw} />
                                <PrivateRoute path="/wallet-search/:curr" exact comp={WalletConfirm} />
                                <PrivateRoute path="/wallet-search" exact comp={WalletSearch} />
                                <PrivateRoute path="/transfer-confirm/:user" exact comp={TransferConfirm} />
                                <PrivateRoute path="/transfer-search" exact comp={TransferSearch} />
                                <PrivateRoute path="/currency-exchange/:fromCurr/:fromIso/:amount/:toCurr/:toIso" exact comp={CurrencyExConfirm} />
                                <PrivateRoute path="/currency-exchange" exact comp={CurrencyEx} />
                                <PrivateRoute path="/transactions/:tId" exact comp={TransactionsDetail} />
                                <PrivateRoute path="/transactions" exact comp={Transactions} />
                                <PrivateRoute path="/settings" comp={Settings} />
                                <PrivateRoute path="/invite-friend" comp={InviteFriend} />
                                <PrivateRoute path="/require-banking" comp={RequireBanking} />
                                <Route path="/about" component={About} />
                                <Route path="/cookie-policy" component={CookiePolicy} />
                                <Route path="/country-picker" component={CountryPicker} />
                                <Route path="/signup" component={SignUp} />
                                <Route path="/verify-email" component={VerifyEmail} />
                                <Route path="/verify-phone" component={VerifyPhone} />
                                <Route path="/verify-referral" component={VerifyReferral} />
                                <Route path="/login" component={Login} />
                                <Route path="/logout" component={Logout} />
                                <Route path="/password-reset" component={PassReset} />
                                <Route path="/password-reset-confirm/:uidb64/:token" component={PassResetConfirm} />

                                <Route path="/new_dunc" component={NewDunc} />
                                {/* <Route path="*" component={NotFound} /> */}
                            </div>
                        </Route>
                    </Switch>
                </div>
            </ThemeContext.Provider>
            </AuthProvider>
        </Router>
    );
}

export default App;
