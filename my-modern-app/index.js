import React from 'react'
import ReactDOM from 'react-dom'
import App from './App'
import { Auth0Provider } from '@auth0/auth0-react'

ReactDOM.render(
    <Auth0Provider
        domain="dev-at224k8a2ogrommd.us.auth0.com"
        clientId="IefTLeMujYKplDQHDtrJR6I7oIeR1i4I"
        redirectUri={window.location.origin}
    >
        <App />
    </Auth0Provider>,
    document.getElementById('root')
)