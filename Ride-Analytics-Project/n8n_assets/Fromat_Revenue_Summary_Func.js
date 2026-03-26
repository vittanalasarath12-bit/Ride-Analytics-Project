// Get the API response data
const apiResponse = $input.first().json;

// Get chat ID from the Telegram Trigger
const chatId = $('Telegram Trigger').first().json.message.chat.id;

// Format revenue summary message
let message = "📊 *Revenue Summary*\n\n";

if (apiResponse && apiResponse.summary) {
  const summary = apiResponse.summary;
  
  // Add date range if available
  if (apiResponse.start_date && apiResponse.end_date) {
    message += `📅 *Period:* ${apiResponse.start_date} to ${apiResponse.end_date}\n\n`;
  }
  
  // Add summary statistics
  message += `🚗 *Total Rides:* ${summary.total_rides || 0}\n`;
  message += `💰 *Total Revenue:* $${(summary.total_revenue || 0).toFixed(2)}\n`;
  message += `💵 *Total Tips:* $${(summary.total_tips || 0).toFixed(2)}\n`;
  message += `📈 *Average Fare:* $${(summary.avg_fare || 0).toFixed(2)}\n`;
  message += `💸 *Total Fare (with Tips):* $${(summary.total_fare_with_tips || 0).toFixed(2)}\n`;
  
  // Add daily breakdown if available
  if (apiResponse.daily_breakdown && Array.isArray(apiResponse.daily_breakdown) && apiResponse.daily_breakdown.length > 0) {
    message += `\n📊 *Daily Breakdown:*\n\n`;
    
    apiResponse.daily_breakdown.forEach(day => {
      message += `📅 ${day.date}\n`;
      message += `  🚗 Rides: ${day.rides || 0}\n`;
      message += `  💰 Revenue: $${(day.revenue || 0).toFixed(2)}\n`;
      message += `\n`;
    });
  }
} else {
  message += "❌ Unable to fetch revenue summary. Please try again later.";
}

// Return formatted message with chat ID
return [
  {
    json: {
      chatId: chatId,
      message: message
    }
  }
];