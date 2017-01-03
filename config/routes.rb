Rails.application.routes.draw do
  root to: 'notifyer#index'

  post '/mixpanel_webhook', to: 'notifyer#watch_event'
end
