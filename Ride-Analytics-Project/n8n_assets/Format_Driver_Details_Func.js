// Get the API response data
const apiResponse = $input.first().json;

// Get chat ID from the Telegram Trigger
const chatId = $('Telegram Trigger').first().json.message.chat.id;

// Format driver details into readable text
let message = "🚗 *Driver Details*\n\n";

if (apiResponse && apiResponse.driver_id) {
  const driverInfo = apiResponse.driver_info || {};
  const performance = apiResponse.performance || {};
  
  message += `🆔 *Driver ID:* ${apiResponse.driver_id}\n\n`;
  
  message += `👤 *Driver Information*\n`;
  message += `• Name: ${driverInfo.name || 'N/A'}\n`;
  message += `• Email: ${driverInfo.email || 'N/A'}\n`;
  message += `• Vehicle Type: ${driverInfo.vehicle_type || 'N/A'}\n`;
  message += `• City: ${driverInfo.city || 'N/A'}\n`;
  message += `• Rating: ${driverInfo.rating || 'N/A'}\n`;
  message += `• Status: ${driverInfo.is_active ? 'Active ✅' : 'Inactive ❌'}\n\n`;
  
  message += `📊 *Performance Metrics*\n`;
  message += `• Total Trips: ${performance.total_trips || 0}\n`;
  message += `• Total Earnings: $${performance.total_earnings || 0}\n`;
  message += `• Total Tips: $${performance.total_tips || 0}\n`;
  message += `• Average Rating: ${performance.avg_rating || 'N/A'}\n`;
  message += `• Avg Trip Duration: ${performance.avg_trip_duration_minutes || 0} minutes\n`;
  message += `• Avg Trip Distance: ${performance.avg_trip_distance_km || 0} km\n`;
  message += `• Completion Rate: ${performance.completion_rate || 0}%\n`;
} else {
  message += "❌ Unable to fetch driver details. Please try again later.";
}

// Return formatted message with chat ID
return [{
  json: {
    chatId: chatId,
    message: message
  }
}];