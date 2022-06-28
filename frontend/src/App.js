import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import React from "react";

import Home from "./pages/Home";
import NotFound from "./pages/NotFound";
import Navbar from "./components/Navbar";
import LandingPage from "./landingPage/LandingPage";
import About from "./pages/About";
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

import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import SignUp from './auth/SignUp';
import CountryPicker from './auth/CountryPicker';

function App() {
    return (
        <Router>
            <AuthProvider>
                <Navbar />
                <Switch>
                    <Route exact path="/" component={LandingPage} />
                    <Route>
                        <div className="app container" style={{marginTop: "4rem"}} id="main-content">
                            <PrivateRoute path="/home" comp={Home} />
                            <PrivateRoute path="/deposit" comp={Deposit} />
                            <PrivateRoute path="/deposit-info" comp={DepositInfo} />
                            <PrivateRoute path="/withdraw" comp={Withdraw} />
                            <PrivateRoute path="/wallet-search/:curr" exact comp={WalletConfirm} />
                            <PrivateRoute path="/wallet-search" exact comp={WalletSearch} />
                            <PrivateRoute path="/:user/transfer-confirm/" comp={TransferConfirm} />
                            <PrivateRoute path="/transfer-search" comp={TransferSearch} />
                            <PrivateRoute path="/currency-exchange/:fromCurr/:fromIso/:amount/:toCurr/:toIso" exact comp={CurrencyExConfirm} />
                            <PrivateRoute path="/currency-exchange" exact comp={CurrencyEx} />
                            <PrivateRoute path="/transactions/:tId" exact comp={TransactionsDetail} />
                            <PrivateRoute path="/transactions/" exact comp={Transactions} />
                            <Route path="/about" component={About} />
                            <Route path="/country-picker" component={CountryPicker} />
                            <Route path="/signup" component={SignUp} />
                            <Route path="/login" component={Login} />
                            <Route path="/logout" component={Logout} />
                            {/* <Route component={NotFound} /> */}
                        </div>
                    </Route>
                </Switch>
            </AuthProvider>
        </Router>
    );
}

export default App;
