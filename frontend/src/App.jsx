import { useState } from 'react'
import axios from 'axios'
import './App.css'

// Set up axios base URL from env or fallback
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://nseprofitmaker.onrender.com';

function App() {
  const [videoIdea, setVideoIdea] = useState('')
  const [thumbnails, setThumbnails] = useState([])
  const [textData, setTextData] = useState({})
  const [selectedIndex, setSelectedIndex] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [originalImageUrls, setOriginalImageUrls] = useState([])
  const [fullscreenImage, setFullscreenImage] = useState(null)

  // Get current date in format "6th July, 2025"
  const getCurrentDate = () => {
    const now = new Date()
    const day = now.getDate()
    const month = now.toLocaleString('en-US', { month: 'long' })
    const year = now.getFullYear()
    
    // Add ordinal suffix to day
    const getOrdinalSuffix = (day) => {
      if (day > 3 && day < 21) return 'th'
      switch (day % 10) {
        case 1: return 'st'
        case 2: return 'nd'
        case 3: return 'rd'
        default: return 'th'
      }
    }
    
    return `${day}${getOrdinalSuffix(day)} ${month}, ${year}`
  }

  const generateThumbnails = async () => {
    if (!videoIdea.trim()) {
      setError('Please enter a video idea')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await axios.post(`${API_BASE_URL}/api/generate-thumbnails`, {
        video_idea: videoIdea
      })

      // Set current date if not provided by AI
      const textWithDate = {
        ...response.data.text_data,
        date: response.data.text_data.date || getCurrentDate()
      }

      setThumbnails(response.data.thumbnails)
      setOriginalImageUrls(response.data.original_urls) // Store original Unsplash URLs
      setTextData(textWithDate)
      setSelectedIndex(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error generating thumbnails')
    } finally {
      setLoading(false)
    }
  }

  const regenerateImages = async () => {
    if (selectedIndex === null) {
      setError('Please select a thumbnail first')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await axios.post(`${API_BASE_URL}/api/regenerate-images`, {
        video_idea: videoIdea,
        text_data: textData,
        selected_index: selectedIndex
      })

      setThumbnails(response.data.thumbnails)
      setOriginalImageUrls(response.data.original_urls) // Store original URLs
      setSelectedIndex(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error regenerating images')
    } finally {
      setLoading(false)
    }
  }

  const regenerateAll = async () => {
    if (!videoIdea.trim()) {
      setError('Please enter a video idea')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await axios.post(`${API_BASE_URL}/api/regenerate-all`, {
        video_idea: videoIdea
      })

      // Set current date if not provided by AI
      const textWithDate = {
        ...response.data.text_data,
        date: response.data.text_data.date || getCurrentDate()
      }

      setThumbnails(response.data.thumbnails)
      setOriginalImageUrls(response.data.original_urls) // Store original URLs
      setTextData(textWithDate)
      setSelectedIndex(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error regenerating all')
    } finally {
      setLoading(false)
    }
  }

  const updateThumbnails = async () => {
    setLoading(true)
    setError('')
    try {
      // Use the original Unsplash URLs for text updates
      const response = await axios.post(`${API_BASE_URL}/api/update-thumbnails`, {
        image_urls: originalImageUrls, // Use original Unsplash URLs
        text_data: textData
      })
      setThumbnails(response.data.thumbnails)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error updating thumbnails')
    } finally {
      setLoading(false)
    }
  }

  const openFullscreen = (imageSrc, index) => {
    setFullscreenImage({ src: imageSrc, index })
  }

  const closeFullscreen = () => {
    setFullscreenImage(null)
  }

  const downloadImage = (imageSrc, index) => {
    const link = document.createElement('a')
    link.href = imageSrc
    link.download = `thumbnail-${index + 1}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎬 AI Thumbnail Generator</h1>
        <p>Generate stunning YouTube thumbnails with AI</p>
      </header>

      <main className="app-main">
        <div className="input-section">
          <div className="input-group">
            <label htmlFor="video-idea">Video Idea:</label>
            <textarea
              id="video-idea"
              value={videoIdea}
              onChange={(e) => setVideoIdea(e.target.value)}
              placeholder="Enter your YouTube video idea (e.g., 'How to make the perfect pizza at home')"
              rows={3}
            />
          </div>
          
          <button 
            onClick={generateThumbnails}
            disabled={loading || !videoIdea.trim()}
            className="generate-btn"
          >
            {loading ? 'Generating...' : '🚀 Generate Thumbnails'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {thumbnails.length > 0 && (
          <div className="thumbnails-section">
            <h2>Generated Thumbnails</h2>
            
            <div className="text-data">
              <h3>Edit Text Data:</h3>
              <div className="text-grid">
                <div>
                  <strong>Heading:</strong>
                  <input
                    type="text"
                    value={textData.heading || ''}
                    onChange={e => setTextData({ ...textData, heading: e.target.value })}
                  />
                </div>
                <div>
                  <strong>Subheading:</strong>
                  <input
                    type="text"
                    value={textData.subheading || ''}
                    onChange={e => setTextData({ ...textData, subheading: e.target.value })}
                  />
                </div>
                <div>
                  <strong>Label:</strong>
                  <input
                    type="text"
                    value={textData.label || ''}
                    onChange={e => setTextData({ ...textData, label: e.target.value })}
                  />
                </div>
                <div>
                  <strong>Date:</strong>
                  <input
                    type="text"
                    value={textData.date || getCurrentDate()}
                    onChange={e => setTextData({ ...textData, date: e.target.value })}
                  />
                </div>
              </div>
              <button
                onClick={updateThumbnails}
                disabled={loading}
                className="regenerate-btn"
                style={{ marginTop: 16 }}
              >
                🖊️ Update Text Only
              </button>
            </div>

            <div className="thumbnails-grid">
              {thumbnails.map((thumbnail, index) => (
                <div 
                  key={index} 
                  className={`thumbnail-container ${selectedIndex === index ? 'selected' : ''}`}
                >
                  <img 
                    src={thumbnail} 
                    alt={`Thumbnail ${index + 1}`}
                    className="thumbnail-image"
                    onClick={() => setSelectedIndex(index)}
                  />
                  
                  {/* Action buttons positioned at top-right */}
                  <div className="thumbnail-actions-top-right">
                    <button 
                      className="action-btn view-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        openFullscreen(thumbnail, index)
                      }}
                      title="View fullscreen"
                    >
                      <i className="fas fa-expand"></i>
                    </button>
                    <button 
                      className="action-btn download-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        downloadImage(thumbnail, index)
                      }}
                      title="Download image"
                    >
                      <i className="fas fa-download"></i>
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {selectedIndex !== null && (
              <div className="action-buttons">
                <button 
                  onClick={regenerateImages}
                  disabled={loading}
                  className="regenerate-btn"
                >
                  🔁 Regenerate Images
                </button>
                <button 
                  onClick={regenerateAll}
                  disabled={loading}
                  className="regenerate-btn"
                >
                  ✏️ Regenerate All
                </button>
              </div>
            )}
          </div>
        )}

        {/* Fullscreen Modal */}
        {fullscreenImage && (
          <div className="fullscreen-modal" onClick={closeFullscreen}>
            <div className="fullscreen-content" onClick={(e) => e.stopPropagation()}>
              <div className="fullscreen-header">
                <h3>Thumbnail {fullscreenImage.index + 1}</h3>
                <button className="close-btn" onClick={closeFullscreen}>
                  <i className="fas fa-times"></i>
                </button>
              </div>
              <img 
                src={fullscreenImage.src} 
                alt={`Thumbnail ${fullscreenImage.index + 1}`}
                className="fullscreen-image"
              />
              <div className="fullscreen-actions">
                <button 
                  className="download-btn-large"
                  onClick={() => downloadImage(fullscreenImage.src, fullscreenImage.index)}
                >
                  <i className="fas fa-download"></i> Download Image
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
