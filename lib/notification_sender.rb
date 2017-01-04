module NotificationSender
	require 'URI'
	require 'net/http'

	def send_notifications(user_ids)
		RubyPython.start
			sys = RubyPython.import('sys')
			sys.path.append("#{Rails.root}/lib")
			frameless = RubyPython.import('frameless')

			frameless.testCSV(user_ids)

		RubyPython.stop
	end

	def update_ids_and_send(user_ids)

		ids = user_ids.map {|x| {'trackingId': x} }
		uri = URI("http://mumbai-production.lab.mtl/api/v1/user/lookup")
		http = Net::HTTP.new(uri.host,uri.port)

		updated_ids = []
		data = { "uniqueIds": ids }.to_json
		response = http.post(uri.path, data)
		parsed_response = JSON.parse(response.body)

		parsed_response['success']['responses'].each do |user|
			updated_ids << user['success']['user_id']
		end

		send_notifications(updated_ids)

	end
end