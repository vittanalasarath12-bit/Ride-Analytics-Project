# Telegram Bot Setup Guide for n8n Integration

## 1️⃣ Create the bot & get the token

1. Open **Telegram** → search **@BotFather** → Start.
2. Send `/newbot`.
3. Give it a **name** (e.g., *Ride Analytics Bot*).
4. Give it a **username** ending in `bot` (e.g., *ride_analytics_bot*).
5. BotFather replies with an **HTTP API token** like `123456:ABC-DEF...` → **Save this token** (you’ll paste it in n8n Telegram credentials).

---

## 2️⃣ (Optional but recommended) Set bot profile

- `/setdescription` → short description users see.
- `/setabouttext` → about text in profile.
- `/setuserpic` → upload an avatar.

---

## 3️⃣ Add slash commands (so users get autocomplete)

1. In **BotFather**: send `/setcommands`
2. Choose your bot.
3. Paste the following (one per line):

```
health - Check API health
driver - Get driver performance by driver ID (e.g. /driver DRV000001)
daily - Get daily ride metrics (e.g. /daily 2025-01-31)
revenue - Revenue summary for a date range (e.g. /revenue 2025-01-01 2025-01-31)
help - Show available commands and usage examples
```

---

## 4️⃣ Add Telegram credentials in n8n

1. Open **n8n** → go to **Credentials**.
2. Click **New Credential → Telegram API Token**.
3. Paste the **Bot Token** you got from BotFather.
4. Click **Save**.

---

## 5️⃣ Test your bot

1. Open Telegram and start a chat with your bot.
2. Send `/start` or `/help`.
3. You should get a welcome message once your n8n workflow is active.

---

## 6️⃣ Important Notes

- Telegram slash commands **don’t support parameter fields**.  
  Users must type parameters inline, for example:
  - `/driver DRV000001`
  - `/daily 2025-01-31`
  - `/revenue 2025-01-01 2025-01-31`

- The command list only adds autocomplete hints. Actual logic (like calling APIs) is handled inside **n8n**.

---

## ✅ Example Summary

**Name:** Ride Analytics Bot  
**Username:** @ride_analytics_bot  
**Purpose:** Provides real-time analytics insights from API via Telegram commands  
**Key Commands:**
```
/health   - API health check
/driver   - Driver details
/daily    - Daily ride metrics
/revenue  - Revenue summary
/help     - Show all commands
```
