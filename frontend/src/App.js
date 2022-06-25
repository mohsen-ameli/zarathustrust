import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import React from "react";

import Home from "./pages/Home";
import NotFound from "./pages/NotFound";
import Navbar from "./components/Navbar";
import LandingPage from "./pages/LandingPage";
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

function App() {
    return (
        <Router>
            <AuthProvider>
                <Navbar />
                <Switch>
                    <Route exact path="/" component={LandingPage} />
                    <div className="app container" style={{marginTop: "4rem"}} id="main-content">
                        <PrivateRoute path="/home" component={Home} />
                        <PrivateRoute path="/deposit" component={Deposit} />
                        <PrivateRoute path="/deposit-info" component={DepositInfo} />
                        <PrivateRoute path="/withdraw" component={Withdraw} />
                        <PrivateRoute path="/wallet-search/:curr" component={WalletConfirm} />
                        <PrivateRoute path="/wallet-search" component={WalletSearch} />
                        <PrivateRoute path="/:user/transfer-confirm/" component={TransferConfirm} />
                        <PrivateRoute path="/transfer-search" component={TransferSearch} />
                        <PrivateRoute path="/currency-exchange/:fromCurr/:fromIso/:amount/:toCurr/:toIso" component={CurrencyExConfirm} />
                        <PrivateRoute path="/currency-exchange" component={CurrencyEx} />
                        <PrivateRoute path="/transactions/:tId" component={TransactionsDetail} />
                        <PrivateRoute path="/transactions/" component={Transactions} />
                        <Route path="/about" component={About} /> 
                        <Route path="/signup" component={SignUp} />
                        <Route path="/login" component={Login} />
                        <Route path="/logout" component={Logout} />
                        {/* <Route component={NotFound} /> */}
                    </div>
                </Switch>
            </AuthProvider>
        </Router>
    );
}

export default App;
