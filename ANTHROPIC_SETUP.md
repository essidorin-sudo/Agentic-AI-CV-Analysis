# 🤖 Anthropic Claude Setup for JD Parser Agent

This guide shows you how to configure Anthropic Claude for the JD Parser Agent.

## 🔑 Getting Your API Key

1. **Sign up for Anthropic**: Visit [console.anthropic.com](https://console.anthropic.com)
2. **Create API Key**: Go to your dashboard and create a new API key
3. **Copy the key**: It will look like `sk-ant-api03-xxxxx...`

## ⚙️ Configuration Options

### Option 1: Environment Variable (Recommended)

```bash
# Set the API key
export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key-here"

# Start the server
cd /Users/eugenes/Desktop/Agentic-AI-CV-Analysis/agents/jd_parser
python3 test_interface.py
```

### Option 2: .env File

1. **Create .env file**:
```bash
cd /Users/eugenes/Desktop/Agentic-AI-CV-Analysis/agents/jd_parser
cp .env.example .env
```

2. **Edit .env file**:
```bash
# Edit with your preferred editor
nano .env
```

3. **Add your API key**:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
LLM_PROVIDER=anthropic
MODEL_NAME=claude-3-haiku-20240307
TEMPERATURE=0.1
```

4. **Start the server**:
```bash
python3 test_interface.py
```

## 🚀 Testing the Setup

1. **Open the interface**: http://localhost:5002
2. **Try a sample**: Click "Tech Senior" or paste a job description
3. **Process with LLM**: Click "🚀 Process with LLM"
4. **Verify**: You should see detailed JSON output and structured content

## 🔧 Model Options

You can configure different Claude models in your .env file:

```bash
# Fast and cost-effective (recommended)
MODEL_NAME=claude-3-haiku-20240307

# More powerful but slower
MODEL_NAME=claude-3-sonnet-20240229

# Most powerful but slowest
MODEL_NAME=claude-3-opus-20240229
```

## 📊 Expected Output

With Claude configured, you should see:
- **Confidence scores**: 0.8-0.95 for well-structured job descriptions
- **Detailed extraction**: Skills, responsibilities, requirements
- **Parsing notes**: Claude's insights about the content quality
- **Rich JSON**: Comprehensive structured data

## 🛠️ Troubleshooting

### "No LLM client configured" Error
- ✅ Check your API key is set correctly
- ✅ Restart the server after setting environment variables
- ✅ Verify the key starts with `sk-ant-api03-`

### "API key not valid" Error
- ✅ Check for typos in your API key
- ✅ Ensure your Anthropic account has credits
- ✅ Verify the key hasn't been revoked

### Demo Mode Still Active
- ✅ Restart the server completely after setting the API key
- ✅ Check the console output for "🧠 Using anthropic model" message

## 🎯 Next Steps

Once Anthropic is working:
1. **Test different job descriptions** to see Claude's parsing quality
2. **Experiment with prompt engineering** by modifying the agent code
3. **Move on to building the CV Parser Agent** for the next step

## 💡 Tips

- **Claude Haiku** is fast and cost-effective for job description parsing
- **Temperature 0.1** ensures consistent, deterministic outputs
- **The interface shows real-time parsing** - perfect for testing prompts
- **JSON and structured views** help you understand what Claude extracts

Happy parsing! 🎉