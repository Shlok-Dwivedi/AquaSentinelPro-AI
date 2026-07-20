-- Run this in your Supabase SQL Editor to fix the RLS issue

-- Enable RLS on all tables (if not already enabled)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_execution_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.complaints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

-- 1. Policies for public.users
CREATE POLICY "Users can view their own profile" 
ON public.users FOR SELECT 
USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" 
ON public.users FOR INSERT 
WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile" 
ON public.users FOR UPDATE 
USING (auth.uid() = id);

-- 2. Policies for chat_sessions
CREATE POLICY "Users can view their chat sessions" 
ON public.chat_sessions FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert chat sessions" 
ON public.chat_sessions FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- 3. Policies for chat_messages
CREATE POLICY "Users can view messages of their sessions" 
ON public.chat_messages FOR SELECT 
USING (
  session_id IN (
    SELECT id FROM public.chat_sessions WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users can insert messages to their sessions" 
ON public.chat_messages FOR INSERT 
WITH CHECK (
  session_id IN (
    SELECT id FROM public.chat_sessions WHERE user_id = auth.uid()
  )
);

-- 4. Policies for agent_execution_logs
CREATE POLICY "Users can view execution logs for their messages" 
ON public.agent_execution_logs FOR SELECT 
USING (
  chat_message_id IN (
    SELECT id FROM public.chat_messages WHERE session_id IN (
      SELECT id FROM public.chat_sessions WHERE user_id = auth.uid()
    )
  )
);

CREATE POLICY "Users can insert execution logs" 
ON public.agent_execution_logs FOR INSERT 
WITH CHECK (
  chat_message_id IN (
    SELECT id FROM public.chat_messages WHERE session_id IN (
      SELECT id FROM public.chat_sessions WHERE user_id = auth.uid()
    )
  )
);

-- 5. Policies for complaints
CREATE POLICY "Users can view their complaints" 
ON public.complaints FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their complaints" 
ON public.complaints FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their complaints" 
ON public.complaints FOR UPDATE 
USING (auth.uid() = user_id);

-- 6. Policies for reports
CREATE POLICY "Users can view their reports" 
ON public.reports FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their reports" 
ON public.reports FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their reports" 
ON public.reports FOR DELETE 
USING (auth.uid() = user_id);
