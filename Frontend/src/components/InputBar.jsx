export function InputBar({ input, loading, onChange, onSubmit }) {
  return (
    <form onSubmit={onSubmit} className="input-bar">
      <input
        value={input}
        onChange={onChange}
        placeholder="Type a message…"
      />
      <button type="submit" disabled={loading}>
        Send
      </button>
    </form>
  );
}
