# Pink Noise Generator

A bash script that generates high-quality pink noise for background sound, sleep enhancement, and focus improvement.

## What is Pink Noise?

Pink noise emphasizes lower frequencies, creating a deeper, more soothing sound similar to gentle rainfall. Research shows pink noise is excellent for:

- **Sleep Enhancement**: Speeds up transition to deep sleep and improves sleep quality
- **Focus & Productivity**: Better for work performance than white noise
- **Stress Reduction**: Helps reduce anxiety and create a calming environment
- **Sound Masking**: Blocks out distracting environmental noises

Pink noise matches natural brain wave patterns better than white noise, making it more stabilizing for the brain.

## Installation

1. Ensure `sox` is installed:
   - macOS: `brew install sox`
   - Ubuntu/Debian: `sudo apt-get install sox`
   - CentOS/RHEL: `sudo yum install sox`

2. Download the script:
   ```bash
   curl -O https://raw.githubusercontent.com/YOUR_USERNAME/pink-noise-generator/main/pink
   chmod +x pink
   ```

3. Optionally, move to your PATH:
   ```bash
   sudo mv pink /usr/local/bin/
   ```

## Usage

### Basic Usage
```bash
./pink # Play pink noise for 1 hour
./pink 30:00 # Play for 30 minutes
./pink 1800 # Play for 1800 seconds (30 minutes)
```

### Advanced Options
```bash
./pink -e # Enhanced pink noise with reverb and filters
./pink -q 45:00 # Quiet mode for 45 minutes
./pink -v -5 # Custom volume level (-5dB)
./pink -m # Mono output instead of stereo
```

### Save to File
```bash
./pink -s -f sleep.wav # Save to specific file
./pink -s 30:00 # Save 30 minutes (auto-generates filename)
```

### Get Help
```bash
./pink --help # Show complete usage information
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message |
| `-q, --quiet` | Quiet mode (reduce output) |
| `-v, --volume` | Volume level in dB (default: -10) |
| `-m, --mono` | Mono output instead of stereo |
| `-s, --save` | Save to file instead of playing |
| `-f, --file` | Output filename (requires -s) |
| `-e, --enhanced` | Enhanced pink noise with reverb and filters |

## Research Background

Based on scientific research, pink noise offers several advantages over other noise types:

- **Sleep Studies**: Pink noise improved deep sleep and memory in older adults
- **Cognitive Performance**: Better than white noise for improving work performance
- **Brain Wave Alignment**: Matches natural brain wave patterns for better stability
- **Frequency Response**: Emphasizes lower frequencies that are more naturally soothing

## Technical Details

The script uses the SoX (Sound eXchange) audio processing library to generate high-quality pink noise with:

- **Standard Mode**: Pure pink noise with volume control
- **Enhanced Mode**: Pink noise with band-pass filtering, reverb, and tremolo effects
- **Flexible Duration**: Supports both MM:SS and seconds format
- **Multiple Outputs**: Real-time playback or file saving
- **Cross-Platform**: Works on macOS, Linux, and Windows (with WSL)

## Dependencies

- **sox**: Sound processing library
- **play**: Audio playback utility (included with sox)

## License

MIT License - feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.