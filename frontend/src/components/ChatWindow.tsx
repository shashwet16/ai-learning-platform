import { useEffect, useRef, useState, type FormEvent } from 'react'
import Markdown from 'react-markdown'
import { ApiError } from '../api/client'
import {
  getConversationMessages,
  sendMessage,
  type MessageRead,
} from '../api/chat'

interface ChatWindowProps {
  conversationId: string
}

export function ChatWindow({ conversationId }: ChatWindowProps) {
  const [messages, setMessages] = useState<MessageRead[] | null>(null)
  const [draft, setDraft] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const threadEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    getConversationMessages(conversationId)
      .then(setMessages)
      .catch((err: unknown) => {
        // A freshly generated conversation ID has no conversation row on
        // the backend yet — it's only created on the first POST (M4.5's
        // get-or-create). A 404 here just means "no history yet," not a
        // real failure.
        if (err instanceof ApiError && err.code === 'conversation_not_found') {
          setMessages([])
        } else {
          setError(
            err instanceof ApiError
              ? err.message
              : 'Failed to load conversation.',
          )
        }
      })
  }, [conversationId])

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isSending])

  async function handleSend(event: FormEvent) {
    event.preventDefault()
    const content = draft.trim()
    if (!content || isSending) return

    setDraft('')
    setError(null)

    // Show the user's own message immediately rather than waiting for
    // the AI reply — the round trip to Mistral can take a couple of
    // seconds, and there's no reason to delay showing what they just typed.
    const optimisticMessage: MessageRead = {
      id: `optimistic-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...(prev ?? []), optimisticMessage])
    setIsSending(true)

    try {
      const assistantMessage = await sendMessage(conversationId, content)
      setMessages((prev) => [...(prev ?? []), assistantMessage])
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : 'Failed to send message.',
      )
    } finally {
      setIsSending(false)
    }
  }

  if (error) {
    return <p className="form-error">{error}</p>
  }

  if (messages === null) {
    return <p>Loading…</p>
  }

  return (
    <div className="chat-window">
      <div className="chat-thread">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message chat-message--${message.role}`}
          >
            {message.role === 'assistant' ? (
              // Only assistant replies go through Markdown — the model is
              // prompted/expected to format with headers, lists, and code
              // fences, but the user's own input is a plain single-line
              // text field, never markdown-authored, so it stays as raw text.
              <div className="chat-markdown">
                <Markdown>{message.content}</Markdown>
              </div>
            ) : (
              message.content
            )}
          </div>
        ))}
        {isSending && (
          <div className="chat-message chat-message--assistant chat-message--loading">
            Thinking…
          </div>
        )}
        <div ref={threadEndRef} />
      </div>
      <form className="chat-input" onSubmit={handleSend}>
        <input
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask your AI tutor anything…"
          disabled={isSending}
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSending || !draft.trim()}
        >
          Send
        </button>
      </form>
    </div>
  )
}
