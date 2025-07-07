# Moment AI - AI-Powered Video Content Creator

Transform your long-form videos and podcasts into engaging short clips using AI. Automatically generate captions, translate content, and create viral-ready content for social media.

## Features

- 🎥 **AI Video Processing**: Convert long videos into multiple short clips
- 🗣️ **Language Dubbing**: Translate and dub videos in multiple languages
- 📝 **Auto Captions**: Generate and customize captions automatically
- ☁️ **Cloud Storage**: Integrated with Cloudinary for video hosting
- 🔐 **User Authentication**: Secure login with Supabase Auth
- 📱 **Responsive UI**: Modern, mobile-friendly interface

## Tech Stack

**Frontend:**
- Next.js 15 with TypeScript
- Tailwind CSS + shadcn/ui components
- Supabase for authentication
- Framer Motion for animations

**Backend:**
- Django REST Framework
- OpenAI API for AI processing
- Faster Whisper for transcription
- Cloudinary for video storage
- SQLite/Supabase for database

## Quick Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- OpenAI API key
- Supabase account
- Cloudinary account

### 1. Clone the Repository
```bash
git clone https://github.com/Diveshmahajan4/MomentAI.git
cd MomentAI
```

### 2. Client Setup
```bash
cd client
npm install
```

Create `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Start development server:
```bash
npm run dev
```

### 3. Server Setup
```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:
```env
OPENAI_API_KEY=your_openai_api_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
DEBUG=True
SECRET_KEY=your_django_secret_key
```

Run migrations and start server:
```bash
python manage.py migrate
python manage.py runserver
```

### 4. Database Setup (Optional - Supabase)

For production or if you prefer Supabase over SQLite:

1. Create tables in Supabase using the schema in `server/supabase_migrations/`
2. Set `USE_SUPABASE=True` in your server `.env`


## Usage

1. **Sign up/Login** using Google OAuth or email
2. **Upload a YouTube URL** or video file
3. **Select number of clips** to generate
4. **Choose language** for dubbing (optional)
5. **Download or share** your processed clips


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
 