// Get the API response data
const apiResponse = $input.first().json;

// Get chat ID from the Telegram Trigger
const chatId = $('Telegram Trigger').first().json.message.chat.id;

// Format the daily rides message
let message = "📊 *Daily Rides Summary*\n\n";

if (apiResponse && apiResponse.date && apiResponse.data) {
  const data = apiResponse.data;
  
  message += `📅 *Date:* ${apiResponse.date}\n\n`;
  message += `🚗 *Total Rides:* ${data.total_rides || 0}\n`;
  message += `💰 *Total Revenue:* $${(data.total_revenue || 0).toFixed(2)}\n`;
  message += `💵 *Total Tips:* $${(data.total_tips || 0).toFixed(2)}\n`;
  message += `💸 *Total Fare (with Tips):* $${(data.total_fare_with_tips || 0).toFixed(2)}\n`;
  message += `⏱️ *Avg Duration:* ${(data.avg_duration_minutes || 0).toFixed(1)} minutes\n`;
  message += `📏 *Avg Distance:* ${(data.avg_distance_km || 0).toFixed(2)} km\n`;
  message += `📈 *Avg Fare:* $${(data.avg_fare || 0).toFixed(2)}\n`;
} else {
  message += "❌ No daily rides data available.";
}

// Return formatted data
return [{
  json: {
    chatId: chatId,
    message: message
  }
}];