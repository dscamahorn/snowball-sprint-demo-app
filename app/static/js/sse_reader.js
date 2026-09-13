// Reads a server-sent events (SSE) response from fetch() and calls
// handleEvent(event) for every JSON message the server sends.
// Shared by the research card on the home page and the review page.

// Every SSE message line starts with this prefix.
const SSE_DATA_PREFIX = "data: ";

async function readServerSentEvents(response, handleEvent) {
  // The body arrives as chunks of bytes. We decode each chunk to text, split
  // it into lines, and keep any unfinished last line for the next chunk.
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    // "await" pauses here until the next chunk arrives from the server.
    const chunk = await reader.read();
    if (chunk.done) {
      break;
    }

    buffer += decoder.decode(chunk.value, { stream: true });
    const lines = buffer.split("\n");
    // The last piece may be an incomplete line, so hold it back.
    buffer = lines.pop();

    for (const line of lines) {
      if (!line.startsWith(SSE_DATA_PREFIX)) {
        continue;
      }
      const eventJson = line.slice(SSE_DATA_PREFIX.length);
      const serverEvent = JSON.parse(eventJson);
      handleEvent(serverEvent);
    }
  }
}
