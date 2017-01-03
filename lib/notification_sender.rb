module NotificationSender
	def send_notification(user)
		RubyPython.start
			sys = RubyPython.import('sys')
			sys.path.append("#{Rails.root}/lib")
			frameless = RubyPython.import('frameless')

			frameless.testCSV()

		RubyPython.stop
	end
end