class NotifyerController < ApplicationController
	include Sheets
	include NotificationSender

	def index
		render nothing: true
	end

	def watch_event
		users = JSON.parse(params[:users])
		user_ids = []
		users.each do |user|
			user_ids << user["$properties"]["user_id"])
			# send_notification(user["$properties"]["user_id"])
		end
		
		render json: {'status':200}
	end
end
`