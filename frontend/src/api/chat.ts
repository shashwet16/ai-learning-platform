import { apiRequest } from './client'

export interface MessageRead {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface ConversationSummary {
  id: string
  created_at: string
}

export function listConversations(): Promise<ConversationSummary[]> {
  return apiRequest<ConversationSummary[]>('/chat/conversations')
}

export function getConversationMessages(
  conversationId: string,
): Promise<MessageRead[]> {
  return apiRequest<MessageRead[]>(`/chat/${conversationId}/messages`)
}

export function sendMessage(
  conversationId: string,
  content: string,
): Promise<MessageRead> {
  return apiRequest<MessageRead>(`/chat/${conversationId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  })
}
