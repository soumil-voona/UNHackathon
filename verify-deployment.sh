#!/bin/bash
# Vercel Deployment Helper Script
# Run this script to validate and prepare your project for Vercel deployment

set -e  # Exit on error

echo "🚀 CoughNet Vercel Deployment Checker"
echo "======================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi
echo "✅ npm: $(npm --version)"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

echo ""
echo "📁 Checking file structure..."

# Check critical files
FILES_TO_CHECK=(
    "vercel.json"
    "ReactFrontend/.env.production"
    "ReactFrontend/package.json"
    "ReactFrontend/vite.config.ts"
    "backend/main.py"
    "backend/inference.py"
    "api/predict.py"
    "api/health.py"
    "api/classes.py"
    "api/requirements.txt"
    ".vercelignore"
)

MISSING_FILES=()
for FILE in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$FILE" ]; then
        echo "✅ $FILE"
    else
        echo "⚠️  Missing: $FILE"
        MISSING_FILES+=("$FILE")
    fi
done

echo ""
echo "🔍 Checking for model file..."
if [ -f "best_cough_classifier.pt" ]; then
    SIZE=$(du -h "best_cough_classifier.pt" | cut -f1)
    echo "✅ Model file found (Size: $SIZE)"
    if [ $(stat -f%z "best_cough_classifier.pt" 2>/dev/null || stat -c%s "best_cough_classifier.pt" 2>/dev/null) -gt 52428800 ]; then
        echo "⚠️  Warning: Model file is larger than 50MB. Consider using Git LFS."
    fi
elif [ -f "backend/cough_classifier.pt" ]; then
    echo "✅ Model file found in backend/"
else
    echo "⚠️  Model file not found. The API will use mock predictions."
fi

echo ""
echo "📦 Checking dependencies..."

# Check package.json
if grep -q '"@vitejs/plugin-react"' ReactFrontend/package.json; then
    echo "✅ React dependencies configured"
else
    echo "⚠️  React dependencies may be incomplete"
fi

# Check Python requirements
if grep -q "torch" backend/requirements.txt 2>/dev/null || grep -q "torch" api/requirements.txt 2>/dev/null; then
    echo "✅ PyTorch dependencies configured"
else
    echo "⚠️  PyTorch not found in requirements"
fi

echo ""
echo "🔐 Checking environment variables..."

if grep -q "VITE_API_URL" ReactFrontend/.env.production; then
    API_URL=$(grep "VITE_API_URL" ReactFrontend/.env.production | cut -d'=' -f2)
    echo "✅ VITE_API_URL set to: $API_URL"
else
    echo "⚠️  VITE_API_URL not configured"
fi

echo ""
echo "✨ Deployment readiness summary:"
echo "======================================"

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "✅ All critical files present"
else
    echo "⚠️  ${#MISSING_FILES[@]} file(s) missing:"
    printf '%s\n' "${MISSING_FILES[@]}" | sed 's/^/   - /'
fi

echo ""
echo "📝 Next steps:"
echo "  1. Ensure your code is committed to Git"
echo "  2. Push to GitHub: git push origin main"
echo "  3. Go to https://vercel.com/new"
echo "  4. Import your GitHub repository"
echo "  5. Deploy!"
echo ""
echo "📖 For detailed instructions, see VERCEL_DEPLOYMENT.md"
echo ""
