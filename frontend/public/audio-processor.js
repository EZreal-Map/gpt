class AudioProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const input = inputs[0]
    if (input.length > 0) {
      const audioData = input[0]
      const int16Array = new Int16Array(audioData.length)
      for (let i = 0; i < audioData.length; i++) {
        int16Array[i] = Math.min(1, audioData[i]) * 0x7fff
      }
      this.port.postMessage(int16Array.buffer)
    }
    return true
  }
}

registerProcessor('audio-processor', AudioProcessor)
