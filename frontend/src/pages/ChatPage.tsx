import { useState } from 'react'
import { ChatWindow } from '../components/ChatWindow'

const CONVERSATION_ID_STORAGE_KEY = 'active_conversation_id'

function getOrCreateConversationId(): string {
  const stored = localStorage.getItem(CONVERSATION_ID_STORAGE_KEY)
  if (stored) return stored

  const fresh = crypto.randomUUID()
  localStorage.setItem(CONVERSATION_ID_STORAGE_KEY, fresh)
  return fresh
}

export function ChatPage() {
  // Lazy initializer: runs getOrCreateConversationId() once, on first
  // render, not on every re-render.
  const [conversationId] = useState(getOrCreateConversationId)

  return (
    <div className="chat-page">
      <span className="kicker">AI Tutor</span>
      <h1>Chat</h1>
      <ChatWindow conversationId={conversationId} />
    </div>
  )
}
