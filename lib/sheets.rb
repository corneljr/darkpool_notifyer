module Sheets
	def output_to_spreadsheet(user_id)
		session = GoogleDrive::Session.from_config("config.json")
		ws = session.spreadsheet_by_key("1tJ_1LvZ_k_tYSt2ZtionIoTt2EaPNlYNvPmZHsZ5un4").worksheets[0]

		sheet_hash = {"user" => user_id}
		ws.list.push(sheet_hash)

		ws.save
	end
end